"""
Written by Benjamin Jack Cullen aka Holographic_Sol

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
import fileinput
import sol_ext

socket.setdefaulttimeout(15)

if not os.path.exists('./dl_id.txt'):
    open('./dl_id.txt', 'w').close()


cwd = os.getcwd()
run_function = 0
max_retry = 3
max_retry_i = 0
no_ext = []
no_md5 = []
failed = []
ids_ = []
search_q = ''
page_max = 0
dl_method = ''
update_max = 0
start_page = False
i_page = 1
search_mode = 'title'
total_i = 0

info = subprocess.STARTUPINFO()
info.dwFlags = 1
info.wShowWindow = 0
main_pid = int()
total_books = int()
total_dl_success = 0

retries = urllib3.Retry(total=None).DEFAULT_BACKOFF_MAX = 3
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'text/plain',
    'Accept-Language': 'en-US,en;q=0.9'
    }


def get_dt():
    dt = datetime.datetime.now()
    dt = '[' + str(dt) + '] '
    return dt


def book_id_check(book_id):
    if not os.path.exists('./book_id.txt'):
        open('./book_id.txt', 'w').close()
    bool_book_id_check = False
    with open('./book_id.txt', 'r') as fo:
        for line in fo:
            line = line.strip()
            if line == str(book_id):
                bool_book_id_check = True
                break
    fo.close()
    return bool_book_id_check


def add_book_id(book_id):
    with open('./book_id.txt', 'a') as fo:
        fo.write(str(book_id) + '\n')
    fo.close()


def dl_id_check(book_id):
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
    if not os.path.exists('./dl_id.txt'):
        open('./dl_id.txt', 'w').close()
    with codecs.open(cwd+'/dl_id.txt', 'a', encoding='utf8') as fo:
        fo.write(book_id + '\n')
    fo.close()


def rem_dl_id(book_id):
    new = []
    if not os.path.exists('./dl_id.txt'):
        open('./dl_id.txt', 'w').close()
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
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


def clear_console_line(char_limit):
    print(' '*char_limit, end='\r', flush=True)


def pr_technical_data(technical_data, char_limit):
    technical_data = technical_data[:char_limit]
    print(technical_data, end='\r', flush=True)


def NFD(text):
    return unicodedata.normalize('NFD', text)


def noCase(text):
    return NFD(NFD(text).casefold())


def convert_bytes(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return str(num)+' '+x
        num /= 1024.0


def banner():
    print('\n\n')
    print('[LIBRARY GENESIS DOWNLOAD TOOL]')
    print('')


def enumerate():
    """ Used to measure multiple instances of progress """

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
        dl_books(search_q, f_dir, lookup_ids)


def dl(href, save_path, str_filesize, filesize, title, author, year, book_id):
    global max_retry, max_retry_i, total_dl_success

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
                data = r.read(10000)

                if not data:
                    dl_sz += int(len(data))
                    break

                out.write(data)
                dl_sz += int(len(data))

                clear_console_line(char_limit=char_limit)
                pr_str = str(get_dt() + '[DOWNLOADING BOOK] ' + str(convert_bytes(int(dl_sz))) + str(' / ') + str_filesize)
                pr_technical_data(pr_str, char_limit=int(len(pr_str)))
                char_limit = int(len(pr_str))

        except Exception as e:
            e = str(e)
            clear_console_line(char_limit=char_limit)
            pr_str = str(get_dt() + '[ERROR]')
            pr_technical_data(pr_str, char_limit=int(len(pr_str)))
            char_limit = int(len(pr_str))

    out.close()
    try:
        r.release_conn()
    except:
        pass

    if int(dl_sz) == int(filesize):
        total_dl_success += 1
        print(str(get_dt() + '[DOWNLOADED] ' + str(convert_bytes(int(dl_sz))) + ' / ' + str(convert_bytes(int(filesize)))))
        print(str(get_dt() + '[DOWNLOADED SUCCESSFULLY]'))

        rem_dl_id(book_id=book_id)

        if book_id_check(book_id=book_id) is False:
            add_book_id(book_id)
    else:

        clear_console_line(char_limit=char_limit)
        pr_str = str(get_dt() + '[DOWNLOADED FAILED]')
        pr_technical_data(pr_str, char_limit=int(len(pr_str)))
        char_limit = int(len(pr_str))

        failed.append([title, author, year, href])

        max_retry_i += 1
        if str(max_retry).isdigit():
            if max_retry_i < max_retry:

                clear_console_line(char_limit=char_limit)
                pr_str = str(get_dt() + '[RETRYING] ' + str(max_retry_i)) + ' / ' + str(max_retry)
                pr_technical_data(pr_str, char_limit=int(len(pr_str)))
                char_limit = int(len(pr_str))

                time.sleep(5)
                dl(href, save_path, str_filesize, filesize, title, author, year, book_id)

        elif str(max_retry) == 'no-limit':

            clear_console_line(char_limit=char_limit)
            pr_str = str(get_dt() + '[RETRYING] ' + str(max_retry_i)) + ' / ' + str(max_retry)
            pr_technical_data(pr_str, char_limit=int(len(pr_str)))
            char_limit = int(len(pr_str))

            time.sleep(5)
            dl(href, save_path, str_filesize, filesize, title, author, year, book_id)


def dl_books(search_q, f_dir, lookup_ids):
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
                print(get_dt() + '[PAGE] ' + str(i_page) + ' / ' + str(page_max))
                print(get_dt() + '[PROGRESS] ' + str(i) + ' / ' + str(len(ids_)) + ' (' + str(total_books) + ')')
            elif dl_method == 'update':
                i_update += 1
                print(get_dt() + '[UPDATE] ' + str(search_q))
                print(get_dt() + '[PROGRESS] ' + str(i_update) + ' / ' + str(update_max))

            # print(_.__dict__)

            book_id = _.id
            print(get_dt() + '[ID] ' + str(book_id))

            bool_dl_id_check = dl_id_check(book_id=book_id)
            bool_book_id_check = book_id_check(book_id=book_id)
            print(get_dt() + '[CHECK DL_ID] ' + str(bool_dl_id_check))
            print(get_dt() + '[CHECK BOOK_ID] ' + str(bool_book_id_check))

            if bool_book_id_check is False or bool_dl_id_check is True:

                title = _.title.strip()
                if title == '':
                    title = 'unknown_title'
                print(get_dt() + '[TITLE] ' + str(title))

                author = _.author.strip()
                if author == '':
                    author = 'unknown_author'
                print(get_dt() + '[AUTHOR] ' + str(author))

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
                                print(get_dt() + '[URL] ' + str(href))
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
                        print(get_dt() + '[SAVING] [COVER] ' + str(save_path_img))
                        http = urllib3.PoolManager(retries=retries)
                        r = http.request('GET', img_, preload_content=False, headers=headers)
                        with open(save_path_img, 'wb') as fo:
                            while True:
                                data = r.read(1000)
                                if not data:
                                    break
                                fo.write(data)
                        fo.close()
                        r.release_conn()

                    # dl book
                    allow_dl = False
                    if bool_dl_id_check is False and not os.path.exists(str(save_path)):
                        """ Book ID not in book_id.txt and not in dl_id.txt and save path does not exist """
                        print(get_dt() + '[SAVING] [NEW] ' + str(save_path))
                        allow_dl = True

                    elif bool_dl_id_check is True:
                        """ Book ID in dl_id.txt (overwrite an existing file if save path exists already) """
                        print(get_dt() + '[SAVING] [RETRYING] ' + str(save_path))
                        allow_dl = True

                    if allow_dl is True:
                        """ download book and write """
                        try:
                            dl(href, save_path, str_filesize, filesize, title, author, year, book_id)
                        except Exception as e:
                            print(get_dt() + str(e))
                            failed.append([title, author, year, href])
                            dl_books(search_q, f_dir, lookup_ids)

                    else:
                        """ Block to preserve existing file with the same name that is also not mentioned in dl_id """
                        print(get_dt() + '[SKIPPING] Blocked to preserve')

                else:
                    print(get_dt() + '[SKIPPING] URL with compatible file extension could not be found')

            elif book_id_check(book_id=book_id) is True:
                print(get_dt() + '[SKIPPING] Book is registered in book_id')

        except Exception as e:
            print(get_dt() + str(e))
            dl_books(search_q, f_dir, lookup_ids)


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
    banner()
    print('    Intended as an intelligence tool for archiving information in an uncertain world.')
    print('    Downloads every book on every page for keyword specified.')
    print('    Written by Benjamin Jack Cullen.')
    print('')
    print('Command line arguments:\n')
    print('    -h             Displays this help message.')
    print('    -k             Keyword. Specify keyword(s).')
    print('    -u             Update. Update an existing library genesis directory.')
    print('                   Each directory name in an existing ./library_genesis directory will')
    print('                   be used as a keyword during update process.')
    print('    -p             Page. Specify start page number.')
    print('    --retry-max    Max number of retries for an incomplete download.')
    print('                   Can be set to no-limit to keep trying if an exception is encountered.')
    print('                   Default is 3. If --retry-max unspecified then default value will be used.')
    print('    --search-mode  Specify search mode.')
    print('                   --search-mode title')
    print('                   --search-mode author')
    print('                   --search-mode isbn')
    print('                   Default is title. If --search-mode unspecified then default value will be used.')
    print('')
    print('    Example: library_genesis -k human')
    print('    Example: library_genesis -p 3 -k human')
    print('    Example: library_genesis --retry-max no-limit --search-mode title -k human')
    print('    Example: library_genesis -u')
    print('')
    run_function = 999

# Parse arguments
run_function = ()
i = 0
retry_max_ = ''
search_mode_ = ''
i_page_ = ''
for _ in sys.argv:

    # keyword
    if _ == '-k':
        banner()
        str_ = ''
        i_2 = 0
        for _ in sys.argv:
            if i_2 >= i+1:
                str_ = str_ + ' ' + str(_)
            i_2 += 1
        print(get_dt() + '[Search] ' + str(str_))
        search_q = str_
        run_function = 0
        break

    elif _ == '-p':
        i_page_ = str(sys.argv[i+1])
        if i_page_.isdigit():
            i_page = int(sys.argv[i+1])
            run_function = 0
        else:
            run_function = 4

    elif _ == '--retry-max':
        retry_max_ = sys.argv[i + 1]
        if str(sys.argv[i+1]).isdigit():
            max_retry = int(sys.argv[i+1])
        elif str(sys.argv[i+1]) == 'no-limit':
            max_retry = str(sys.argv[i+1])
            run_function = 0
        else:
            run_function = 2

    elif _ == '--search-mode':
        search_mode_ = sys.argv[i+1]
        if sys.argv[i+1] == 'title':
            search_mode = sys.argv[i+1]
        elif sys.argv[i+1] == 'author':
            search_mode = sys.argv[i+1]
        elif sys.argv[i+1] == 'isbn':
            search_mode = sys.argv[i+1]
            run_function = 0
        else:
            run_function = 3

    # update
    elif _ == '-u':
        if len(sys.argv) == 2:
            run_function = 1
        else:
            run_function = 5
        break
    i += 1

# Keyword download
if run_function == 0:
    search_q = search_q.strip()
    enumerate()
    if page_max >= 1:
        dl_method = 'keyword'
        # i_page = 1
        while i_page <= page_max:
            compile_ids(search_q, i_page)
            i_page += 1
    summary()

elif run_function == 1:
    banner()
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

elif run_function == 2:
    print(get_dt() + '[failed] --retry-max cannot be ' + retry_max_)
elif run_function == 3:
    print(get_dt() + '[failed] --search-mode cannot be ' + search_mode_)
elif run_function == 4:
    print(get_dt() + '[failed] -p cannot be ' + i_page_)
elif run_function == 5:
    print(get_dt() + '[failed] update switch takes no other arguments.')

print('\n')
