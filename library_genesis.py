"""
Written by Benjamin Jack Cullen aka Holographic_Sol

- cli library genesis mass book downloader.
- attempts to download every book on every page.
- download all books by author
- download all books by title
- download all books by isbn
- downloads book covers
- displays multi-level download progress
- stores books in directory names according to specified title/author/isbn from command line arguments. (categorized).
- optionally choose library genesis search results page to start downloading all books from (default page 1), save time.
- uses various means to keep track of what already exists in the book library:
    - what book should be downloaded
    - what book has been downloaded already
    - what book started downloading and possibly did not finnish (reboots, power etc..)
    - what book/files to leave alone (already exists but book id not in download file, etc..)
        - dl_id.txt and or book_id.txt may be deleted and this program should still pick up where it left off, however
        'skipping' over existing files may take slightly longer as tagged values will have to be used to create the
        save path (among other operations including a file exist check) before the program can ascertain if the book
        will be skipped or downloaded.
        - recommended to keep book_id.txt unless it grows to large.

"""
import datetime
import os
import sys
import time
import codecs
from pylibgen import Library
import requests
from bs4 import BeautifulSoup
import urllib3
import unicodedata
import subprocess
import socket
import sol_ext
import pyprogress
import colorama
import pdfplumber

socket.setdefaulttimeout(15)
colorama.init()

if not os.path.exists('./dl_id.txt'):
    open('./dl_id.txt', 'w').close()


run_function = 1984
max_retry = 3
max_retry_i = 0
total_books = int()
total_dl_success = 0
update_max = 0
i_page = 1
page_max = 0
total_i = 0
limit_speed = 0
human_limit_speed = ''

book_id_store = []
no_ext = []
no_md5 = []
failed = []
ids_ = []

cwd = os.getcwd()
search_q = ''
dl_method = ''
search_mode = 'title'

start_page = False

info = subprocess.STARTUPINFO()
info.dwFlags = 1
info.wShowWindow = 0

retries = urllib3.Retry(total=None).DEFAULT_BACKOFF_MAX = 3
multiplier = pyprogress.multiplier_from_inverse_factor(factor=50)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'text/plain',
    'Accept-Language': 'en-US,en;q=0.9'
    }


def get_dt():
    """ create a datetime string """
    dt = datetime.datetime.now()
    dt = '[' + str(dt) + '] '
    return dt


def search_f(file, query):

    with pdfplumber.open(file) as pdf:
        page_n = pdf.pages
        pdf_page_max = int(str(page_n[-1]).replace('<Page:', '').replace('>', ''))
        pdf_page_i = 0
        for _ in page_n:
            pdf_page_i += 1
            page_cur = str(_).replace('<Page:', '')
            page_cur = int(page_cur.replace('>', ''))
            try:
                page_ = pdf.pages[page_cur]
                page_txt = page_.extract_text()
                page_txt = str(page_txt).strip()
                page_txt = page_txt.split('\n')

                var = False
                i = 0
                for _ in page_txt:
                    if noCase(query) in noCase(_):
                        if not os.path.exists('./research_' + query + '.txt'):
                            open('./research_' + query + '.txt', 'w', encoding='utf8').close()
                        with open('./research_' + query + '.txt', 'a', encoding='utf8') as fo:
                            fo.write('-------------------------------------------------' + '\n')
                            fo.write('[FILE] ' + file + '\n')
                            fo.write('[PAGE] ' + str(pdf_page_i) + '\n')
                            fo.write('[QUERY] ' + query + '\n')
                        fo.close()

                        print('[SEARCHING FILE CONTENTS]', file)
                        print('[QUERY]', query)
                        print('[PAGE]', pdf_page_i, '/', pdf_page_max)
                        print('...')
                        print(_)
                        if not os.path.exists('./research_' + query + '.txt'):
                            open('./research_' + query + '.txt', 'w', encoding='utf8').close()
                        with open('./research_' + query + '.txt', 'a', encoding='utf8') as fo:
                            fo.write(_ + '\n')
                        fo.close()
                        var = True
                    elif var is True:
                        print(_)
                        if not os.path.exists('./research_' + query + '.txt'):
                            open('./research_' + query + '.txt', 'w', encoding='utf8').close()
                        with open('./research_' + query + '.txt', 'a', encoding='utf8') as fo:
                            fo.write(_ + '\n')
                        fo.close()
                        if '.' in _:
                            print('...')
                            var = False
                            print('')
                            print('-' * 200)
                            print('')
                    i += 1
            except:
                break
    pdf.close()

    if os.path.exists('./research_' + query + '.txt'):
        with codecs.open('./research_' + query + '.txt', 'r', encoding='utf-8') as fo:
            for line in fo:
                line = line.strip()
                print(line)
        fo.close()


def search_library(path, query):
    pdf_max = 0
    for dirName, subdirList, fileList in os.walk(path):
        for fname in fileList:
            if fname.endswith('.pdf'):
                pdf_max += 1

    pdf_i = 0
    pdf_page_max = 0
    for dirName, subdirList, fileList in os.walk(path):
        for fname in fileList:
            if fname.endswith('.pdf'):
                pdf_i += 1
                fullpath = os.path.join(dirName, fname)
                try:
                    with pdfplumber.open(fullpath) as pdf:
                        page_n = pdf.pages
                        pdf_page_max = int(str(page_n[-1]).replace('<Page:', '').replace('>', ''))
                        pdf_page_i = 0
                        for _ in page_n:
                            pdf_page_i += 1
                            page_cur = str(_).replace('<Page:', '')
                            page_cur = int(page_cur.replace('>', ''))
                            try:
                                page_ = pdf.pages[page_cur]
                                page_txt = page_.extract_text()
                                page_txt = str(page_txt).strip()
                                page_txt = page_txt.split('\n')

                                var = False
                                for _ in page_txt:
                                    print('')
                                    print('-' * 200)
                                    print('')
                                    print('[PROGRESS]', pdf_i, '/', pdf_max)
                                    print('[SEARCHING FILE CONTENTS]', fullpath)
                                    print('[PAGE]', pdf_page_i, '/', pdf_page_max)
                                    print('[QUERY]', query)
                                    if noCase(query) in noCase(_):
                                        if not os.path.exists('./research_'+query+'.txt'):
                                            open('./research_'+query+'.txt', 'w', encoding='utf8').close()
                                        with open('./research_' + query + '.txt', 'a', encoding='utf8') as fo:
                                            fo.write('-------------------------------------------------' + '\n')
                                            fo.write('[FILE] '+fullpath + '\n')
                                            fo.write('[PAGE] '+str(pdf_page_i) + '\n')
                                            fo.write('[QUERY] '+query + '\n')
                                        fo.close()
                                        print('...')
                                        print(_)
                                        if not os.path.exists('./research_' + query + '.txt'):
                                            open('./research_' + query + '.txt', 'w', encoding='utf8').close()
                                        with open('./research_' + query + '.txt', 'a', encoding='utf8') as fo:
                                            fo.write(_ + '\n')
                                        fo.close()
                                        var = True
                                    elif var is True:
                                        print(_)
                                        if not os.path.exists('./research_' + query + '.txt'):
                                            open('./research_' + query + '.txt', 'w', encoding='utf8').close()
                                        with open('./research_' + query + '.txt', 'a', encoding='utf8') as fo:
                                            fo.write(_ + '\n')
                                        fo.close()
                                        if '.' in _:
                                            print('...')
                                            var = False
                                            print('')
                                            print('-' * 200)
                                            print('')
                            except Exception as e:
                                print(e)
                                break
                    pdf.close()
                except Exception as e:
                    print(e)

    if os.path.exists('./research_' + query + '.txt'):
        with open('./research_' + query + '.txt', 'r', encoding='utf8') as fo:
            for line in fo:
                line = line.strip()
                print(line)
        fo.close()


def book_id_check(book_id, check_type):
    """ check if book id in file/memory """

    global book_id_store
    if not os.path.exists('./book_id.txt'):
        open('./book_id.txt', 'w').close()

    bool_book_id_check = False
    if check_type == 'read-file':
        with open('./book_id.txt', 'r') as fo:
            for line in fo:
                line = line.strip()
                if line == str(book_id):
                    bool_book_id_check = True
                    break
                book_id_store.append(line)
        fo.close()

    elif check_type == 'memory':
        if book_id in book_id_store:
            bool_book_id_check = True
    return bool_book_id_check


def add_book_id(book_id):
    """ add book id to file and list in memory """

    global book_id_store
    if not os.path.exists('./book_id.txt'):
        open('./book_id.txt', 'w').close()

    with open('./book_id.txt', 'a') as fo:
        fo.write(str(book_id) + '\n')
    fo.close()
    book_id_store.append(book_id)


def dl_id_check(book_id):
    """ check if book id in download file  """
    if not os.path.exists('./dl_id.txt'):
        open('./dl_id.txt', 'w').close()

    bool_dl_id_check = False
    if os.path.exists(cwd+'/dl_id.txt'):
        with codecs.open(cwd+'/dl_id.txt', 'r', encoding='utf8') as fo:
            for line in fo:
                line = line.strip()
                if line == str(book_id):
                    bool_dl_id_check = True
                    break
    else:
        print(get_dt() + '[DL_INDEX] is missing.')
    return bool_dl_id_check


def add_dl_id(book_id):
    """" add book id to download file """

    if not os.path.exists('./dl_id.txt'):
        open('./dl_id.txt', 'w').close()

    with codecs.open(cwd+'/dl_id.txt', 'a', encoding='utf8') as fo:
        fo.write(book_id + '\n')
    fo.close()


def rem_dl_id(book_id):
    """" remove book id from download file """

    if not os.path.exists('./dl_id.txt'):
        open('./dl_id.txt', 'w').close()

    new = []
    with open('./dl_id.txt', 'r') as fo:
        for line in fo:
            line = line.strip()
            if line != book_id:
                new.append(line)
    fo.close()

    open('./dl_id.txt', 'w').close()
    with open('./dl_id.txt', 'a') as fo:
        for _ in new:
            fo.write(_ + '\n')
    fo.close()


def clear_console():
    """ clears console """

    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


def clear_console_line(char_limit):
    """ clear n chars from console """

    print(' '*char_limit, end='\r', flush=True)


def pr_technical_data(technical_data):

    """ print n chars to console after running clear_console_line """

    print(technical_data, end='\r', flush=True)


def NFD(text):
    return unicodedata.normalize('NFD', text)


def noCase(text):
    return NFD(NFD(text).casefold())


def convert_bytes(num):
    """ bytes for humans """

    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return str(num)+' '+x
        num /= 1024.0


def enumerate_ids():
    """ Used to measure multiple instances/types of progress during download """

    global page_max, search_q, total_books
    print('-' * 100)
    print(get_dt() + '[ENUMERATION]')
    i_page = 1
    add_page = True
    ids_n = []
    while add_page is True:
        ids = []
        library_ = Library()
        try:
            ids = library_.search(query=search_q, mode=search_mode, page=i_page, per_page=100)
            print(get_dt() + '[PAGE] ' + str(i_page))
            print(get_dt() + '[BOOK IDs] ' + str(ids))
            for _ in ids:
                if _ not in ids_:
                    ids_n.append(_)
        except:
            add_page = False
        if not ids:
            add_page = False
        else:
            page_max += 1
            i_page += 1
    print('-' * 100)
    print(get_dt() + '[ENUMERATION SUMMARY]')
    print(get_dt() + '[KEYWORD] ' + str(search_q))
    print(get_dt() + '[BOOKS] ' + str(len(ids_n)))
    total_books = str(len(ids_n))
    print('-' * 100)


def compile_ids(search_q, i_page):
    """ compile a fresh set of book ids per page (prevents overloading request) """

    global ids_
    print('-' * 100)
    print(get_dt() + '[COMPILE IDS]')
    ids_ = []
    f_dir = './library_genesis/' + search_q + '/'

    library_ = Library()
    try:
        ids = library_.search(query=search_q, mode=search_mode, page=i_page, per_page=100)
        ids_ = ids

    except Exception as e:
        print(get_dt() + str(e))
        time.sleep(5)
        compile_ids(search_q, i_page)

    lookup_ids = library_.lookup(ids_)
    print(get_dt() + '[PAGE] ' + str(i_page))
    print(get_dt() + '[BOOKS] ' + str(len(ids_)))
    print('-' * 100)

    if ids_:
        print('ids_', ids_)
        if not os.path.exists('./library_genesis'):
            os.mkdir('./library_genesis')
        if not os.path.exists(f_dir):
            os.mkdir(f_dir)
        enumerate_book(search_q, f_dir, lookup_ids)


def dl(href, save_path, str_filesize, filesize, title, author, year, book_id):
    """ attempts to download a book with n retries according to --retry-max """

    global max_retry, max_retry_i, total_dl_success, limit_speed

    if dl_id_check(book_id=book_id) is False:
        add_dl_id(book_id=book_id)

    char_limit = 0
    dl_sz = 0

    open(save_path, 'w').close()
    with open(save_path, 'wb') as out:
        try:
            http = urllib3.PoolManager(retries=retries)
            r = http.request('GET', href, preload_content=False, headers=headers)
            while True:

                if limit_speed == 0:
                    data = r.read(1024)
                    pre_append = '[DOWNLOADING BOOK] '
                else:
                    data = r.read(limit_speed)
                    pre_append = '[DOWNLOADING BOOK] [THROTTLING ' + str(human_limit_speed) + '] '

                if not data:
                    dl_sz += int(len(data))
                    break

                out.write(data)
                dl_sz += int(len(data))

                try:
                    pyprogress.progress_bar(part=int(dl_sz), whole=int(filesize),
                                            pre_append=pre_append,
                                            append=str(' ' + str(convert_bytes(int(dl_sz))) + ' / ' + str_filesize),
                                            encapsulate_l='|',
                                            encapsulate_r='|',
                                            encapsulate_l_color='LIGHTCYAN_EX',
                                            encapsulate_r_color='LIGHTCYAN_EX',
                                            progress_char=' ',
                                            bg_color='GREEN',
                                            factor=50,
                                            multiplier=multiplier)
                except Exception as e:
                    print(e)

                if limit_speed != 0:
                    time.sleep(1)

        except Exception as e:
            e = str(e)
            clear_console_line(char_limit=char_limit)
            pr_str = str(get_dt() + '[' + colorama.Style.BRIGHT + colorama.Fore.RED + 'ERROR' + colorama.Style.RESET_ALL + ']')
            pr_technical_data(pr_str)
            char_limit = int(len(pr_str))

    out.close()
    try:
        r.release_conn()
    except:
        pass

    if int(dl_sz) == int(filesize):
        total_dl_success += 1
        pr_technical_data('')
        print('\n')
        print(str(get_dt() + '[' + colorama.Style.BRIGHT + colorama.Fore.GREEN + 'DOWNLOADED SUCCESSFULLY' + colorama.Style.RESET_ALL + ']'))

        rem_dl_id(book_id=book_id)

        if book_id_check(book_id=book_id, check_type='memory') is False:
            add_book_id(book_id)

    else:
        clear_console_line(char_limit=char_limit)
        pr_str = str(get_dt() + '[' + colorama.Style.BRIGHT + colorama.Fore.RED + 'DOWNLOADED FAILED' + colorama.Style.RESET_ALL + ']')
        pr_technical_data(pr_str)
        char_limit = int(len(pr_str))

        failed.append([title, author, year, href])

        max_retry_i += 1
        if str(max_retry).isdigit():
            if max_retry_i < max_retry:

                clear_console_line(char_limit=char_limit)
                pr_str = str(get_dt() + '[RETRYING] ' + str(max_retry_i)) + ' / ' + str(max_retry)
                pr_technical_data(pr_str)
                char_limit = int(len(pr_str))

                time.sleep(5)
                dl(href, save_path, str_filesize, filesize, title, author, year, book_id)

        elif str(max_retry) == 'no-limit':

            clear_console_line(char_limit=char_limit)
            pr_str = str(get_dt() + '[RETRYING] ' + str(max_retry_i)) + ' / ' + str(max_retry)
            pr_technical_data(pr_str)
            char_limit = int(len(pr_str))

            time.sleep(5)
            dl(href, save_path, str_filesize, filesize, title, author, year, book_id)


def enumerate_book(search_q, f_dir, lookup_ids):
    """ obtains book details using book id and calls dl function if certain conditions are met """

    global ids_, dl_method, max_retry_i, no_md5, no_ext, failed, total_books, total_i
    i = 0
    i_update = 0
    save_path = ''
    for _ in lookup_ids:
        try:
            i += 1
            total_i += 1
            max_retry_i = 0
            print('-' * 100)
            if dl_method == 'keyword':
                print(get_dt() + '[KEYWORD] ' + str(search_q))
                print(get_dt() + '[PAGE] ' + colorama.Style.BRIGHT + colorama.Fore.LIGHTCYAN_EX + str(i_page) + colorama.Style.RESET_ALL + ' / ' + colorama.Style.BRIGHT + colorama.Fore.LIGHTCYAN_EX + str(page_max) + colorama.Style.RESET_ALL)
                print(get_dt() + '[PROGRESS] ' + colorama.Style.BRIGHT + colorama.Fore.LIGHTCYAN_EX + str(i) + colorama.Style.RESET_ALL + ' / ' + colorama.Style.BRIGHT + colorama.Fore.LIGHTCYAN_EX + str(len(ids_)) + colorama.Style.RESET_ALL + ' (' + colorama.Style.BRIGHT + colorama.Fore.LIGHTCYAN_EX + str(total_books) + colorama.Style.RESET_ALL + ')')
            elif dl_method == 'update':
                i_update += 1
                print(get_dt() + '[UPDATE] ' + str(search_q))
                print(get_dt() + '[PROGRESS] ' + colorama.Style.BRIGHT + colorama.Fore.LIGHTCYAN_EX + str(i_update) + colorama.Style.RESET_ALL + ' / ' + colorama.Style.BRIGHT + colorama.Fore.LIGHTCYAN_EX + str(update_max) + colorama.Style.RESET_ALL)

            # print(_.__dict__)

            book_id = _.id
            print(get_dt() + '[BOOK ID] ' + str(book_id))

            bool_dl_id_check = dl_id_check(book_id=book_id)
            bool_book_id_check = book_id_check(book_id=book_id, check_type='memory')
            print(get_dt() + '[CHECK DL_ID] ' + str(bool_dl_id_check))
            print(get_dt() + '[CHECK BOOK_ID] ' + str(bool_book_id_check))

            if bool_book_id_check is False or bool_dl_id_check is True:

                title = _.title.strip()
                if title == '':
                    title = 'unknown_title'
                print(get_dt() + '[TITLE] ' + colorama.Style.BRIGHT + colorama.Fore.CYAN + str(title) + colorama.Style.RESET_ALL)

                author = _.author.strip()
                if author == '':
                    author = 'unknown_author'
                print(get_dt() + '[AUTHOR] ' + colorama.Style.BRIGHT + colorama.Fore.CYAN + str(author) + colorama.Style.RESET_ALL)

                year = _.year.strip()
                if year == '0' or not year:
                    year = 'unknown_year'
                print(get_dt() + '[YEAR] ' + str(year))

                filesize = _.filesize.strip()
                print(get_dt() + '[FILE SIZE] ' + str(convert_bytes(int(filesize))))
                str_filesize = str(convert_bytes(int(filesize)))

                md5 = _.md5.strip()
                if md5 == '':
                    print(get_dt() + '[md5] could not find md5, skipping')
                    no_md5.append([title, author, year])
                    break
                print(get_dt() + '[md5] ' + md5)

                url = ('http://library.lol/main/' + str(md5))
                rHead = requests.get(url)
                data = rHead.text
                soup = BeautifulSoup(data, "html.parser")
                href = ''
                ext = ''
                for link in soup.find_all('a'):
                    href = (link.get('href'))
                    idx = str(href).rfind('.')
                    _ext_ = str(href)[idx:]
                    for _ in sol_ext.ext_:
                        if not _ == '.html':
                            if str(noCase(_ext_).strip()) == '.' + str(_).strip().lower():
                                ext = '.' + str(_.lower())
                                # print(get_dt() + '[URL] ' + str(href))
                                break
                    break

                img_ = ''
                for link in soup.find_all('img'):
                    src = (link.get('src'))
                    if src:
                        if src.endswith('.jpg'):
                            print(get_dt() + '[IMAGE] ' + str(src))
                            img_ = 'http://library.lol/' + src
                            break

                if ext:
                    print(get_dt() + '[EXTENSION] ' + str(ext))
                    save_path = f_dir + "".join([c for c in title if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
                    save_path = save_path + ' (by ' + "".join([c for c in author if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
                    save_path = save_path + ' ' + "".join([c for c in year if c.isalpha() or c.isdigit() or c == ' ']).rstrip() + ')_' + book_id + ext
                    save_path_img = save_path + '.jpg'

                    # dl book cover
                    if not os.path.exists(save_path_img):
                        try:
                            # print(get_dt() + '[SAVING] [COVER] ' + str(save_path_img))  # uncomment to display path
                            print(get_dt() + '[SAVING] [COVER]')
                            http = urllib3.PoolManager(retries=retries)
                            r = http.request('GET', img_, preload_content=False, headers=headers)
                            with open(save_path_img, 'wb') as fo:
                                while True:
                                    data = r.read(1000)
                                    if not data:
                                        break
                                    fo.write(data)
                            fo.close()
                        except Exception as e:
                            print(get_dt() + '[SAVING] [COVER] failed')
                        try:
                            r.release_conn()
                        except:
                            pass

                    # dl book
                    allow_dl = False
                    if bool_dl_id_check is False and not os.path.exists(str(save_path)):
                        """ Book ID not in book_id.txt and not in dl_id.txt and save path does not exist """
                        # print(get_dt() + '[SAVING] [NEW] ' + str(save_path))  # uncomment to display path
                        print(get_dt() + '[SAVING] [NEW]')
                        allow_dl = True

                    elif bool_dl_id_check is True:
                        """ Book ID in dl_id.txt (overwrite an existing file if save path exists already) """
                        # print(get_dt() + '[SAVING] [RETRYING] ' + str(save_path))  # uncomment to display path
                        print(get_dt() + '[SAVING] [RETRYING]')
                        allow_dl = True

                    if allow_dl is True:
                        """ download book and write """
                        try:
                            dl(href, save_path, str_filesize, filesize, title, author, year, book_id)
                        except Exception as e:
                            print(get_dt() + str(e))
                            failed.append([title, author, year, href])
                            enumerate_book(search_q, f_dir, lookup_ids)

                    else:
                        """ Block to preserve existing file with the same name that is also not mentioned in dl_id """
                        print(get_dt() + '[SKIPPING] Blocked to preserve')

                else:
                    print(get_dt() + '[SKIPPING] URL with compatible file extension could not be found')

            elif book_id_check(book_id=book_id, check_type='memory') is True:
                print(get_dt() + '[SKIPPING] Book is registered in book_id')

        except Exception as e:
            print(get_dt() + str(e))
            enumerate_book(search_q, f_dir, lookup_ids)


def summary():
    print('')
    print('-' * 100)
    print('')
    print(get_dt() + '[SUMMARY]')
    print('')
    if no_md5:
        print(get_dt() + '[MD5] This list is of urls that had no md5 and so were skipped:')
        for _ in no_md5:
            print('    ' + str(_))
    if no_ext:
        print(get_dt() + '[EXTENSIONS] This list is of urls that had no file extension and so were skipped:')
        for _ in no_ext:
            print('    ' + str(_))
    print(get_dt() + '[TOTAL DOWNLOADED] ' + str(total_dl_success))
    print('')
    print(get_dt() + '[COMPLETE]')
    print('')
    print('-' * 100)


# Help menu
if len(sys.argv) == 2 and sys.argv[1] == '-h':
    print('')
    print('-'*104)
    print('')
    print(colorama.Style.BRIGHT + colorama.Fore.GREEN + '    [ LIBRARY GENESIS DOWNLOAD & RESEARCH TOOL ]' + colorama.Style.RESET_ALL)
    print('')
    print('-' * 104)
    print('')
    print('    Intended as an intelligence tool for archiving information in an uncertain world.')
    print('    Downloads every book on every page for keyword specified.')
    print('    Also provides function to compile and save a list of reading material relative to search terms(s)')
    print('    to aid and assist in research when dealing with large libraries.')
    print('    Written by Benjamin Jack Cullen.')
    print('')
    print('-' * 104)
    print('')
    print(colorama.Style.BRIGHT + colorama.Fore.GREEN + '    [ Download Arguments ]' + colorama.Style.RESET_ALL)
    print('')
    print('    -h                 Displays this help message.\n')
    print('    -k                 Keyword. Specify keyword(s). Should always be the last argument.')
    print('                       Anything after -k will be treated as a keyword(s).\n')
    print('    -p                 Page. Specify start page number. Default is 0.\n')
    print('    -u                 Update. Update an existing library genesis directory.')
    print('                       Each directory name in an existing ./library_genesis directory will')
    print('                       be used as a search term during update process.\n')
    print('    --download-mode    Instructs program to run in download mode.\n')
    print('    --retry-max        Max number of retries for an incomplete download.')
    print('                       Can be set to no-limit to keep trying if an exception is encountered.')
    print('                       Default is 3. Using no-limit is always recommended. ')
    print('                       If issues are encountered then specify number.\n')
    print('    --search-mode      Specify search mode. Default is title')
    print('                       --search-mode title')
    print('                       --search-mode author')
    print('                       --search-mode isbn\n')
    print('    --limit-speed      Throttle download speed. Specify bytes per second in digits.')
    print('                       1024 bytes = 1KB. Use a calculator if you need it.')
    print('                       Example: --limit-speed 1024')
    print('                       Default is 0 (unlimited).')
    print('')
    print('-' * 104)
    print('')
    print(colorama.Style.BRIGHT + colorama.Fore.GREEN + '    [ Research Arguments ]' + colorama.Style.RESET_ALL)
    print('')
    print('    --research-mode    Specify research mode. Specify file/directory to research.')
    print('                       --research-mode file')
    print('                       --research-mode library\n')
    print('    -f                 Specify file to research. Used with --research-mode file.\n')
    print('    -d                 Specify directory to research. Used with --research-mode library.\n')
    print('    --research         Specify research query. Used with --research-mode.')
    print('')
    print('-' * 104)
    print('')
    print(colorama.Style.BRIGHT + colorama.Fore.GREEN + '    [ EXAMPLE USAGE ]' + colorama.Style.RESET_ALL)
    print('')
    print('    library_genesis --download-mode -k human')
    print('    library_genesis --download-mode -p 3 -k human')
    print('    library_genesis --download-mode --limit-speed 1024 --retry-max no-limit --search-mode title -k human')
    print('    library_genesis --download-mode -u')
    print('    library_genesis --research-mode library -d ./library_genesis/ --research 1984')
    print('')
    print('-' * 104)
    run_function = 1984

# Parse arguments
retry_max_ = ''
search_mode_ = ''
i_page_ = ''
print('')
if '--download-mode' in sys.argv:
    print('[MODE] Download')
    i = 0
    run_function = 0
    for _ in sys.argv:

        # keyword
        if _ == '-k':
            str_ = ''
            i_2 = 0
            for _ in sys.argv:
                if i_2 >= i+1:
                    str_ = str_ + ' ' + str(_)
                i_2 += 1
            if str_ != '':
                search_q = str_
            else:
                print(get_dt() + "[failed] user failed to specify a search query.")
                run_function = 1984
                break

        # page
        elif _ == '-p':
            i_page_ = str(sys.argv[i+1])
            if i_page_.isdigit():
                i_page = int(sys.argv[i+1])
            else:
                print(get_dt() + '[failed] -p cannot be ' + i_page_)
                run_function = 1984
                break

        # retry limiter
        elif _ == '--retry-max':
            retry_max_ = sys.argv[i + 1]
            if str(sys.argv[i+1]).isdigit():
                max_retry = int(sys.argv[i+1])
            elif str(sys.argv[i+1]) == 'no-limit':
                max_retry = str(sys.argv[i+1])
            else:
                print(get_dt() + '[failed] --retry-max cannot be ' + retry_max_)
                run_function = 1984
                break

        # search mode
        elif _ == '--search-mode':
            search_mode_ = sys.argv[i+1]
            if sys.argv[i+1] == 'title':
                search_mode = sys.argv[i+1]
            elif sys.argv[i+1] == 'author':
                search_mode = sys.argv[i+1]
            elif sys.argv[i+1] == 'isbn':
                search_mode = sys.argv[i+1]
            else:
                print(get_dt() + '[failed] --search-mode cannot be ' + search_mode_)
                run_function = 1984
                break

        # throttle download speed
        elif _ == '--limit-speed':
            if sys.argv[i+1].isdigit():
                limit_speed = int(sys.argv[i+1])
                human_limit_speed = str(convert_bytes(int(limit_speed)))
            else:
                print(get_dt() + "[failed] --limit-speed accepts digits argument.")
                run_function = 1984
                break

        i += 1

elif '-u' in sys.argv and '--download-mode' in sys.argv:
    print('[MODE] Update')
    # update
    if len(sys.argv) == 3:
        run_function = 1
    else:
        print(get_dt() + '[failed] update switch takes no other arguments.')
        run_function = 1984

elif '--research-mode' in sys.argv:
    print('[MODE] Research')
    run_function = 2
    for _ in sys.argv:

        # research mode
        if _ == '--research-mode':
            r_mode_idx = sys.argv.index('--research-mode')
            r_mode = sys.argv[r_mode_idx+1]

            if r_mode != 'file' and r_mode != 'library':
                print(get_dt() + "[failed] --research-mode accepts either 'file' or 'library' as a valid argument.")
                run_function = 1984
                break

        # file
        elif _ == '-f':
            file_idx = sys.argv.index('-f')
            file = sys.argv[file_idx + 1]
            if os.path.exists(file):
                file_ = sys.argv[file_idx + 1]
            else:
                print(get_dt() + "[failed] file specified appears not to exist.")
                run_function = 1984
                break

        # directory
        elif _ == '-d':
            dir_idx = sys.argv.index('-d')
            dir = sys.argv[dir_idx + 1]
            if os.path.exists(dir):
                dir_ = sys.argv[dir_idx + 1]
            else:
                print(get_dt() + "[failed] directory specified appears not to exist.")
                run_function = 1984
                break

        # research string
        elif _ == '--research':
            research_str_idx = sys.argv.index('--research')
            research_str_ = ''
            i_2 = 0
            for _ in sys.argv:
                if i_2 >= research_str_idx+1:
                    research_str = research_str_ + ' ' + str(_)
                i_2 += 1
            if not research_str == '':
                research_str_ = research_str
            else:
                print(get_dt() + "[failed] please specify research string.")
                run_function = 1984
                break

# download by keyword
if run_function == 0:
    clear_console()
    book_id_check(book_id='', check_type='read-file')
    search_q = search_q.strip()
    enumerate_ids()
    if page_max >= 1:
        dl_method = 'keyword'
        while i_page <= page_max:
            compile_ids(search_q, i_page)
            i_page += 1
    summary()

# download in update mode
elif run_function == 1:
    clear_console()
    book_id_check(book_id='', check_type='read-file')
    print(get_dt() + '[Update Library]')
    update_max = 0
    search_q = []
    for dirname, dirnames, filenames in os.walk('./library_genesis'):
        for subdirname in dirnames:
            fullpath = os.path.join(subdirname)
            search_q.append(fullpath)
            print('    [update] ' + str(fullpath))
            update_max += 1
    i_query = 0
    dl_method = 'update'
    for _ in search_q:
        i_page = 1
        print(get_dt() + '[updating] ' + str(_))
        compile_ids(search_q[i_query], i_page)
        i_query += 1
    summary()

# research
elif run_function == 2:
    print('[research mode]')
    if r_mode == 'file':
        print('[research mode] file')
        search_f(file=file_, query=research_str_.strip())
    elif r_mode == 'library':
        print('[research mode] library')
        search_library(path=dir_, query=research_str_.strip())
    else:
        print('-- research mode unspecified')

else:
    if run_function != 1984:
        print('\nUse -h for help.')

# final
print('\n')
colorama.Style.RESET_ALL
