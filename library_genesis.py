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
        - recommended to keep dl_id.txt unless it grows to large.
        Any book id in dl_id.txt can also be removed and added to book_id.txt manually:
            (issues can be resolved by a manual book downlaod --> then add id to book_id.txt manually and remove book
            id from dl_id.txt manually) then restart the download operation.

"""
import webbrowser
from datetime import datetime, timedelta
import os
import sys
import time
import codecs
import signal
from pylibgen import Library
import requests
from bs4 import BeautifulSoup
import urllib3
import unicodedata
import sol_ext
import pyprogress
import colorama
import pdfplumber
import socket
import subprocess
import research

f_dl_id = './data/dl_id.txt'
f_book_id = './data/book_id.txt'
d_library_genesis = './library_genesis'


def ensure_data_paths():
    if not os.path.exists('./data/'):
        os.mkdir('./data')
    if not os.path.exists(f_dl_id):
        open(f_dl_id, 'w').close()
    if not os.path.exists(f_book_id):
        open(f_book_id, 'w').close()


ensure_data_paths()


def ensure_research_paths():
    if not os.path.exists('./research'):
        os.mkdir('./research')


ensure_research_paths()


def ensure_tmp_paths():
    if not os.path.exists('./tmp'):
        os.mkdir('./tmp')


ensure_tmp_paths()


def ensure_library_path():
    if not os.path.exists(d_library_genesis):
        os.mkdir(d_library_genesis)


ensure_library_path()

info = subprocess.STARTUPINFO()
info.dwFlags = 1
info.wShowWindow = 0
main_pid = int()

socket.setdefaulttimeout(15)

colorama.init()

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

pdf_max = 0
pdf_list = []
threads = 4
i_match = 0
query = ''
verbosity = False
bool_no_cover = False

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

retries = urllib3.Retry(total=None).DEFAULT_BACKOFF_MAX = 10
multiplier = pyprogress.multiplier_from_inverse_factor(factor=50)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'text/plain',
    'Accept-Language': 'en-US,en;q=0.9'
    }


def get_dt():
    """ create a datetime string """
    dt = datetime.now()
    dt = '[' + str(dt) + '] '
    return dt


def check_clear():
    global query
    for dirName, subdirList, fileList in os.walk('./tmp'):
        for fname in fileList:
            fullpath = os.path.join(dirName, fname)
            if fname.endswith('.txt'):
                f_exists = False
                if fname.startswith('research_completed_'+query):
                    f_exists = True
                elif fname.startswith('research_'+query):
                    f_exists = True
                elif fname.startswith('research_match_'+query):
                    f_exists = True
                if f_exists is True:
                    while os.path.exists(fullpath):
                        try:
                            os.remove(fullpath)
                        except Exception as e:
                            pass


def iter_items(_pythonic_list, i):
    return _pythonic_list[i]


def display_progress_unknown(str_progress='', progress_list=[], str_pre_append='', str_append=''):
    """ A simple function to display progress when overall progress is unknown. Useful when a 'whole' is unknown. """

    global i_char_progress
    print(str_progress + str_pre_append + progress_list[i_char_progress] + str_append, end='\r', flush=True)
    if i_char_progress == int(len(progress_list))-1:
        i_char_progress = 0
    else:
        i_char_progress += 1


def files_enumerate(path=''):
    global pdf_max
    global pdf_list

    for dirName, subdirList, fileList in os.walk(path):
        for fname in fileList:
            if fname.endswith('.pdf'):
                pdf_max += 1
                pdf_list.append(os.path.join(dirName, fname))
                print('[ENUMERATING] Files: ' + str(pdf_max), end='\r', flush=True)
    print('\n')


def research_files_enumerate(_path=''):
    """ return a list of files """

    _pdf_list = []
    _pdf_max = 0
    for dirName, subdirList, fileList in os.walk(_path):
        for fname in fileList:
            if fname.endswith('.pdf'):
                _pdf_max += 1
                _pdf_list.append(os.path.join(dirName, fname))
                print('[ENUMERATING] Files: ' + str(_pdf_max), end='\r', flush=True)
    print('')
    return _pdf_list


def chunks(_pdf_list=[], chunk_count=int):
    """Yield successive n-sized chunks from a list (not my function) """

    _chunk_pdf_list = []
    for i in range(0, len(_pdf_list), chunk_count):
        _chunk_pdf_list.append(_pdf_list[i:i + chunk_count])
    return _chunk_pdf_list


def iter_chunk_commands(chunk_pdf_lists=[], search_str=''):
    """ return a list of commands """

    commands = []
    _thread_n = 0
    for _ in chunk_pdf_lists:
        # uncomment for: source code version
        commands.append(str('python ./research_raw.py "' + str(_) + '" ' + str(_thread_n) + ' ' + str(search_str)))
        # uncomment for: compiled version
        # commands.append(str('./research_raw.exe "' + str(_) + '" ' + str(_thread_n) + ' ' + str(search_str)))
        _thread_n += 1
    return commands


def multiplex_commands(commands=[]):
    """ executes n commands as subprocesses and waits until all have completed """
    procs = [subprocess.Popen(i) for i in commands]
    for p in procs:
        p.wait()


def compile_results(search_str=''):
    """ reads n files and compiles a list of entries """

    if os.path.exists('./research/' + str(search_str)):
        new_file = []
        for dirName, subdirList, fileList in os.walk('./research/' + str(search_str)):
            for fname in fileList:
                fullpath = os.path.join(dirName, fname)
                with codecs.open(fullpath, 'r') as fo:
                    for line in fo:
                        pyprogress.display_progress_unknown(str_progress='[COMPILING RESULTS] ', progress_list=pyprogress.arrow_a, color='CYAN')
                        line = line.strip()
                        if line not in new_file:
                            new_file.append(line)
                fo.close()
        print('')
        return new_file


def compiled_results_to_file(search_str='', results=[]):
    """ writes results to final research file """

    print('[WRITING] Research file (this may include results from previous searches). Total Results:', len(results))
    open('./research/' + str(search_str) + '.txt', 'w').close()
    for _ in results:
        with codecs.open('./research/' + str(search_str) + '.txt', 'a', encoding='utf8') as fo:
            pyprogress.display_progress_unknown(str_progress='[WRITING] ', progress_list=pyprogress.arrow_a, color='CYAN')
            fo.write(str(_) + '\n')
        fo.close()
    print('')
    print('[COMPLETED]')


def results_handler(search_str='', re_display_results=True):
    if os.path.exists('./research/' + str(search_str) + '.txt'):
        if re_display_results is True:
            print('')
            print('A selection from the following may be made:')
            print('')
        option_file = []
        with open('./research/' + str(search_str) + '.txt', 'r') as fo:
            i = 0
            for line in fo:
                line = line.strip()
                if re_display_results is True:
                    print(' [' + str(i) + '] ' + line)
                option_file.append(line)
                i += 1
        fo.close()
        if re_display_results is True:
            print(' [Q] Quit')
        print('')
        user_option = input('select: ')
        if user_option == noCase('q'):
            print('')
            print('[EXITING]')
            print('')
        elif user_option.isdigit():
            user_option = int(user_option)
            if user_option < len(option_file):
                # todo: webbrowser may not always open pdf. explore options
                webbrowser.open(option_file[user_option], 2)
        if user_option != noCase('q'):
            results_handler(search_str=search_str, re_display_results=False)


def GetTime(_sec):
    sec = timedelta(seconds=int(_sec))
    d = datetime(1, 1, 1) + sec
    return str("%d:%d:%d:%d" % (d.day-1, d.hour, d.minute, d.second))


def research_progress(i_chunk=int, _commands=[], len_pdf_list=int, _chunk_pdf_list=int, elapsed_time=str):
    # todo: fix percent and parts to display correctly and ensure the whole line is cleared before printing.

    print('[PROGRESS] [chunk: ' + str(i_chunk) + '/' + str(len(_chunk_pdf_list)) + '] [total time taken: ' + str(elapsed_time) + ']', end='\r', flush=True)


def search_library(_path='', search_str='', _threads=2):
    """ search for x in directory x and write results to file for later """

    _path = _path
    _search_str = search_str
    _threads = _threads

    _pdf_list = research_files_enumerate(_path=_path)
    len_pdf_list = int(len(_pdf_list))
    _chunk_pdf_list = chunks(_pdf_list=_pdf_list, chunk_count=_threads)

    t0 = time.time()
    i_chunk = 0
    for _chunk_pdf_lists in _chunk_pdf_list:

        _commands = iter_chunk_commands(chunk_pdf_lists=_chunk_pdf_lists, search_str=_search_str)

        research_progress(i_chunk=i_chunk, _commands=_commands, len_pdf_list=len_pdf_list, _chunk_pdf_list=_chunk_pdf_list, elapsed_time=str(GetTime(time.time() - t0)))

        multiplex_commands(commands=_commands)
        i_chunk += 1

        research_progress(i_chunk=i_chunk, _commands=_commands, len_pdf_list=len_pdf_list, _chunk_pdf_list=_chunk_pdf_list, elapsed_time=str(GetTime(time.time() - t0)))

    print('\n')

    _results = compile_results(search_str=_search_str)

    compiled_results_to_file(search_str=_search_str, results=_results)

    # todo: finnish results handler functionality.
    print('')
    if len(_results) > 0:
        if len(_results) <= 100:
            user_input = input('display results?: ')
            if user_input == noCase('y'):
                results_handler(search_str=search_str)
            else:
                print('')
                print('[COMPLETE]')
                print('[FILE] ./research/' + str(search_str) + '.txt')
        else:
            print('')
            print('[RESULTS] Likely exceed buffer size so please refer to the file to see reults. ')
            print('[FILE] ./research/' + str(search_str) + '.txt')


def book_id_check(book_id, check_type):
    """ check if book id in file/memory """

    global book_id_store
    ensure_data_paths()

    bool_book_id_check = False
    if check_type == 'read-file':
        with open(f_book_id, 'r') as fo:
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
    ensure_data_paths()

    with open(f_book_id, 'a') as fo:
        fo.write(str(book_id) + '\n')
    fo.close()
    book_id_store.append(book_id)


def dl_id_check(book_id):
    """ check if book id in download file  """
    ensure_data_paths()

    bool_dl_id_check = False
    if os.path.exists(f_dl_id):
        with codecs.open(f_dl_id, 'r', encoding='utf8') as fo:
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

    ensure_data_paths()

    with codecs.open(f_dl_id, 'a', encoding='utf8') as fo:
        fo.write(book_id + '\n')
    fo.close()


def rem_dl_id(book_id):
    """" remove book id from download file """

    ensure_data_paths()

    new = []
    with open(f_dl_id, 'r') as fo:
        for line in fo:
            line = line.strip()
            if line != book_id:
                new.append(line)
    fo.close()

    with open(f_dl_id, 'w') as fo:
        fo.close()
    with open(f_dl_id, 'a') as fo:
        for _ in new:
            fo.write(_ + '\n')
    fo.close()


def clear_console():
    """ clears console """

    command = 'clear'
    if os.name in ('nt', 'dos'):
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
        except Exception as e:
            print(e)
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
    f_dir = d_library_genesis + '/' + search_q + '/'

    try:
        library_ = Library()
        ids = library_.search(query=search_q, mode=search_mode, page=i_page, per_page=100)
        ids_ = ids

    except Exception as e:
        print(get_dt() + str(e))
        time.sleep(1)
        compile_ids(search_q, i_page)

    lookup_ids = library_.lookup(ids_)
    print(get_dt() + '[PAGE] ' + str(i_page))
    print(get_dt() + '[BOOKS] ' + str(len(ids_)))
    print('-' * 100)

    if ids_:
        print('ids_', ids_)
        ensure_library_path()
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

    with open(save_path, 'w') as fo:
        fo.close()
    with open(save_path, 'wb') as out:
        try:
            http = urllib3.PoolManager(retries=retries)
            r = http.request('GET', href, preload_content=False, headers=headers)
            _data = []
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
                    time.sleep(3)

                if limit_speed != 0:
                    time.sleep(1)

        except Exception as e:
            e = str(e)
            print(e)
            time.sleep(3)
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

                time.sleep(3)
                dl(href, save_path, str_filesize, filesize, title, author, year, book_id)

        elif str(max_retry) == 'unlimited':

            clear_console_line(char_limit=char_limit)
            pr_str = str(get_dt() + '[RETRYING] ' + str(max_retry_i)) + ' / ' + str(max_retry)
            pr_technical_data(pr_str)
            char_limit = int(len(pr_str))

            time.sleep(3)
            dl(href, save_path, str_filesize, filesize, title, author, year, book_id)


def enumerate_book(search_q, f_dir, lookup_ids):
    """ obtains book details using book id and calls dl function if certain conditions are met """

    global ids_, dl_method, max_retry_i, no_md5, no_ext, failed, total_books, total_i, bool_no_cover
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

                if bool_no_cover is False:
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
                    if bool_no_cover is False:
                        save_path_img = save_path + '.jpg'

                    if len(save_path) >= 255:
                        save_path = save_path[:259+len(ext)]
                        save_path = save_path + '...)' + ext
                        print(get_dt() + '[LIMITING FILENAME LENGTH]' + str(save_path))

                    # dl book cover
                    if bool_no_cover is False:
                        if not os.path.exists(save_path_img):
                            try:
                                # print(get_dt() + '[SAVING] [COVER] ' + str(save_path_img))  # uncomment to display path
                                print(get_dt() + '[SAVING] [COVER]')
                                http = urllib3.PoolManager(retries=retries)
                                r = http.request('GET', img_, preload_content=False, headers=headers)
                                with open(save_path_img, 'wb') as fo:
                                    while True:
                                        data = r.read(1024)
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
                    else:
                        print(get_dt() + '[COVER] Skipping cover download.')

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
    print(' [LIBRARY GENESIS DOWNLOAD & RESEARCH TOOL]')
    print('')
    print('')
    print(' [DESCRIPTION]')
    print('')
    print('               [In the name of intelligence]')
    print('               [Downloads and researches a digital library]')
    print('               [Intended as an intelligence tool for archiving information in an uncertain world]')
    print('')
    print('               [AUTHOR] [Benjamin Jack Cullen]')
    print('')
    # print('')
    print(' [DOWNLOAD]')
    print('')
    print('   [-h]              [Displays this help message]')
    print('   [-k]              [Keyword. Specify keyword(s). Should always be the last argument]')
    print('                     [Anything after -k will be treated as a keyword(s). (MUST be specified last)]')
    print('   [-p]              [Page. Specify start page number. Default is 0]')
    # print('   [-u]              [Update. Update an existing library genesis directory]')  # todo: update
    # print('                     [Each directory name in an existing ./library_genesis directory will')
    # print('                      be used as a search term during update process. (EXPERIMENTAL)]')
    print('   [--download-mode] [Instructs program to run in download mode]')
    print('   [--retry-max]     [Max number of retries for an incomplete download]')
    print('                     [Can be set to unlimited to keep trying if an exception is encountered]')
    print('                     [Default is 3. Using unlimited is always recommended]')
    print('                     [If issues are encountered then specify number]')
    print('   [--search-mode]   [Specify search mode. Default is title if --search-mode is unspecified]')
    print('                     [--search-mode title]')
    print('                     [--search-mode author]')
    print('                     [--search-mode isbn]')
    print('   [--no-cover]      [No Cover. Book covers will not be downloaded.]')
    print('                     [Covers are downloaded by default.]')
    print('   [--throttle]      [Throttle download speed. Specify bytes per second in digits]')
    print('                     [1024 bytes = 1KB. Use a calculator if you need it]')
    print('                     [Example: --throttle 1024]')
    print('                     [Default is 0 (unlimited)]')
    print('')
    print(' [RESEARCH]')
    print('')
    print('   [--research-mode] [Specify research mode. Instructs program to run in research mode]')
    print('   [-t]              [Threads. Specify number of files that will be processed simultaneously]')
    print('                     [Default is 2 if -t is unspecified]')
    print('   [-d]              [Specify directory to research. Used with --research-mode]')
    print('   [--research]      [Specify research query. Used with --research-mode]')
    print('                     [This argument MUST be specified last]')
    print('')
    print(' [EXAMPLES]')
    print('')
    print('   library_genesis --download-mode -k robots')
    print('   library_genesis --download-mode -p 3 -k robots')
    print('   library_genesis --download-mode --throttle 1024 --retry-max unlimited --search-mode title -k robots')
    # print('    library_genesis --download-mode -u')
    print("   library_genesis --research-mode -d './library_genesis' --research robots")
    print("   library_genesis --research-mode -t 8 -d './library_genesis' --research robots")
    print('')
    run_function = 1984

# Parse arguments
retry_max_ = ''
search_mode_ = ''
research_str = ''
i_page_ = ''
print('')
print('-'*100)
print('')
if '--download-mode' in sys.argv and not '-u' in sys.argv:
    print('[LIBRARY GENESIS EXE]')
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
            elif str(sys.argv[i+1]) == 'unlimited':
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
        elif _ == '--throttle':
            if sys.argv[i+1].isdigit():
                limit_speed = int(sys.argv[i+1])
                human_limit_speed = str(convert_bytes(int(limit_speed)))
            else:
                print(get_dt() + "[failed] --throttle accepts digits argument.")
                run_function = 1984
                break

        elif _ == '--no-cover':
            bool_no_cover = True

        i += 1

# todo: update before final integration
# elif '-u' in sys.argv and '--download-mode' in sys.argv:
#     print('[LIBRARY GENESIS EXE]')
#     print('[MODE] Update')
#     # update
#     if len(sys.argv) == 3:
#         run_function = 1
#     else:
#         print(get_dt() + '[failed] update switch takes no other arguments.')
#         run_function = 1984

elif '--research-mode' in sys.argv:
    print('[LIBRARY GENESIS EXE]')
    print('[MODE] Research')
    run_function = 2
    for _ in sys.argv:

        # thread
        if _ == '-t':
            thread_idx = sys.argv.index('-t')
            _thread = sys.argv[thread_idx + 1]
            if _thread.isdigit():
                threads = int(_thread)
            else:
                print(get_dt() + "[failed] -t takes digit argument")
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
            i_2 = 0
            for _ in sys.argv:
                if i_2 >= research_str_idx+1:
                    research_str = research_str + ' ' + str(_)
                i_2 += 1

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

# todo --> update before final integration
# # download in update mode
# elif run_function == 1:
#     clear_console()
#     book_id_check(book_id='', check_type='read-file')
#     print(get_dt() + '[Update Library]')
#     update_max = 0
#     search_q = []
#     for dirname, dirnames, filenames in os.walk(d_library_genesis):
#         for subdirname in dirnames:
#             fullpath = os.path.join(subdirname)
#             search_q.append(fullpath)
#             print('    [update] ' + str(fullpath))
#             update_max += 1
#     i_query = 0
#     dl_method = 'update'
#     for _ in search_q:
#         i_page = 1
#         print(get_dt() + '[updating] ' + str(_))
#         compile_ids(search_q[i_query], i_page)
#         i_query += 1
#     summary()

# research
elif run_function == 2:
    path = dir_
    query = research_str.strip()
    search_library(_path=path, search_str=query, _threads=threads)

else:
    if run_function != 1984:
        print('\nUse -h for help.')

# final
print('')
colorama.Style.RESET_ALL
