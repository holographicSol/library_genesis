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
import os
import sys
import time
from datetime import datetime, timedelta
import codecs
import socket
import urllib3
import colorama
import requests
import subprocess
import webbrowser
import unicodedata
from pylibgen import Library
from bs4 import BeautifulSoup
import sol_ext
import pyprogress

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


def ensure_research_paths():
    if not os.path.exists('./research'):
        os.mkdir('./research')


def ensure_tmp_paths():
    if not os.path.exists('./tmp'):
        os.mkdir('./tmp')


def ensure_library_path():
    if not os.path.exists(d_library_genesis):
        os.mkdir(d_library_genesis)


# initialize paths
ensure_data_paths()
ensure_research_paths()
ensure_tmp_paths()
ensure_library_path()

# initiate subprocess argument
info = subprocess.STARTUPINFO()
info.dwFlags = 1
info.wShowWindow = 0

# configure socket timeout
socket.setdefaulttimeout(15)

# initialize colorama
colorama.init()

# set default backoff time in module
retries = urllib3.Retry(total=None).DEFAULT_BACKOFF_MAX = 10

# set pyprogress factor in module
multiplier = pyprogress.multiplier_from_inverse_factor(factor=50)

# set user agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
                  '73.0.3683.103 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/'
              'signed-exchange;v=b3',
    'Accept-Encoding': 'text/plain',
    'Accept-Language': 'en-US,en;q=0.9'
    }

# set and initiate
run_function = 1984
max_retry = 3
max_retry_i = 0
i_page = 1
page_max = 0
total_i = 0
limit_speed = 0
pdf_max = 0
threads = 4
i_match = 0
total_books = int()
verbosity = False
bool_no_cover = False
start_page = False
bool_failed_once = False
book_id_store = []
dl_id_store = []
no_ext = []
no_md5 = []
# failed = []
ids_ = []
pdf_list = []
cwd = os.getcwd()
search_q = ''
search_mode = 'title'
human_limit_speed = ''
query = ''


def color(s=str, c=str):
    if c == 'LC':
        return colorama.Style.BRIGHT + colorama.Fore.LIGHTCYAN_EX + str(s) + colorama.Style.RESET_ALL
    elif c == 'G':
        return colorama.Style.BRIGHT + colorama.Fore.GREEN + str(s) + colorama.Style.RESET_ALL
    elif c == 'R':
        return colorama.Style.BRIGHT + colorama.Fore.RED + str(s) + colorama.Style.RESET_ALL
    elif c == 'Y':
        return colorama.Style.BRIGHT + colorama.Fore.YELLOW + str(s) + colorama.Style.RESET_ALL


def get_dt():
    """ create a datetime string """
    dt = datetime.now()
    dt = ' [' + str(dt) + '] '
    return dt


def GetTime(_sec):
    sec = timedelta(seconds=int(_sec))
    d = datetime(1, 1, 1) + sec
    return str("%d:%d:%d:%d" % (d.day-1, d.hour, d.minute, d.second))


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


def display_progress_unknown(str_progress='', progress_list=[], str_pre_append='', str_append=''):
    """ A simple function to display progress when overall progress is unknown. Useful when a 'whole' is unknown. """

    global i_char_progress
    print(str_progress + str_pre_append + progress_list[i_char_progress] + str_append, end='\r', flush=True)
    if i_char_progress == int(len(progress_list))-1:
        i_char_progress = 0
    else:
        i_char_progress += 1


def display_progress(_part=int, _whole=int, _pre_append=str):
    pyprogress.progress_bar(part=int(_part), whole=int(_whole),
                            pre_append=_pre_append,
                            append=str(''),
                            encapsulate_l='|',
                            encapsulate_r='|',
                            encapsulate_l_color='LIGHTWHITE_EX',
                            encapsulate_r_color='LIGHTWHITE_EX',
                            progress_char=' ',
                            bg_color='GREEN',
                            factor=50,
                            multiplier=multiplier)


def research_files_enumerate(_path=''):
    """ return a list of files """

    _pdf_list = []
    _pdf_max = 0
    print('')
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
        # commands.append(str('python ./research_raw.py "' + str(_) + '" ' + str(_thread_n) + ' ' + str(search_str)))
        # uncomment for: compiled version
        commands.append(str('./research_raw.exe "' + str(_) + '" ' + str(_thread_n) + ' ' + str(search_str)))
        _thread_n += 1
    return commands


def multiplex_commands(commands=[]):
    """ executes n commands as subprocesses and waits until all have completed """

    if os.path.exists('./research_raw.exe') or os.path.exists('./research_raw.py'):
        procs = [subprocess.Popen(i_command) for i_command in commands]
        for p in procs:
            p.wait()


def compile_results(search_str=''):
    """ reads n files and compiles a list of entries """

    if os.path.exists('./research/' + str(search_str)):
        print('')
        new_file = []
        for dirName, subdirList, fileList in os.walk('./research/' + str(search_str)):
            for fname in fileList:
                fullpath = os.path.join(dirName, fname)
                with codecs.open(fullpath, 'r') as fo:
                    for line in fo:
                        pyprogress.display_progress_unknown(str_progress='[COMPILING RESULTS] ',
                                                            progress_list=pyprogress.arrow_a,
                                                            color='CYAN')
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
            pyprogress.display_progress_unknown(str_progress='[WRITING] ',
                                                progress_list=pyprogress.arrow_a,
                                                color='CYAN')
            fo.write(str(_) + '\n')
        fo.close()
    print('')
    print('[COMPLETED]')


def results_handler(search_str='', re_display_results=True):
    """ optionally display results and some extra switches """

    if os.path.exists('./research/' + str(search_str) + '.txt'):
        if re_display_results is True:
            print('')
            print('A selection from the following may be made:')
            print('')
        option_file = []
        with open('./research/' + str(search_str) + '.txt', 'r') as fo:
            i_results = 0
            for line in fo:
                line = line.strip()
                if re_display_results is True:
                    print(' [' + str(i_results) + '] ' + line)
                option_file.append(line)
                i_results += 1
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
                # todo: webbrowser may not always open pdf. explore options.
                webbrowser.open(option_file[user_option], 2)
        if user_option != noCase('q'):
            results_handler(search_str=search_str, re_display_results=False)


def research_progress(i_chunk=int, _commands=[], len_pdf_list=int, _chunk_pdf_list=int, elapsed_time=str):
    # todo: possibly add more detail to progress monitor.
    print('[PROGRESS] [chunk: ' + str(i_chunk) + '/' + str(len(_chunk_pdf_list)) +
          '] [total time taken: ' + str(elapsed_time) + ']', end='\r', flush=True)


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
        _commands = iter_chunk_commands(chunk_pdf_lists=_chunk_pdf_lists,
                                        search_str=_search_str)
        research_progress(i_chunk=i_chunk,
                          _commands=_commands,
                          len_pdf_list=len_pdf_list,
                          _chunk_pdf_list=_chunk_pdf_list,
                          elapsed_time=str(GetTime(time.time() - t0)))
        multiplex_commands(commands=_commands)
        i_chunk += 1
        research_progress(i_chunk=i_chunk,
                          _commands=_commands,
                          len_pdf_list=len_pdf_list,
                          _chunk_pdf_list=_chunk_pdf_list,
                          elapsed_time=str(GetTime(time.time() - t0)))
    print('\n')
    _results = compile_results(search_str=_search_str)
    compiled_results_to_file(search_str=_search_str, results=_results)
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
                if line not in book_id_store:
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
    if book_id not in book_id_store:
        book_id_store.append(book_id)


def dl_id_check(book_id=str, check_type=str):
    """ check if book id in download file  """

    global dl_id_store
    ensure_data_paths()
    bool_dl_id_check = False
    if check_type == 'read-file':
        if os.path.exists(f_dl_id):
            with codecs.open(f_dl_id, 'r', encoding='utf8') as fo:
                for line in fo:
                    line = line.strip()
                    if line not in dl_id_store:
                        dl_id_store.append(line)
        else:
            print(get_dt() + '[DL_INDEX] is missing.')
    elif check_type == 'memory':
        if book_id in dl_id_store:
            bool_dl_id_check = True
    return bool_dl_id_check


def add_dl_id(book_id):
    """" add book id to download file """

    global dl_id_store
    ensure_data_paths()
    with codecs.open(f_dl_id, 'a', encoding='utf8') as fo:
        fo.write(book_id + '\n')
    fo.close()
    dl_id_store.append(book_id)


def rem_dl_id(book_id):
    """" remove book id from download file """

    global dl_id_store
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
    dl_id_store.remove(book_id)


def enumerate_ids():
    """ Used to measure multiple instances/types of progress during download """
    # todo: simplify/reduce function size

    global page_max, search_q, total_books
    print('')
    i_page = 1
    add_page = True
    ids_n = []
    while add_page is True:
        ids = []
        library_ = Library()
        try:
            ids = library_.search(query=search_q, mode=search_mode, page=i_page, per_page=100)
            print(get_dt() + '[SEARCHING] [PAGE] [' + str(i_page-1) + ']', end='\r', flush=True)
            for _ in ids:
                if _ not in ids_:
                    ids_n.append(_)
        except Exception as e:
            # todo: expand handling
            add_page = False
            if 'Connection aborted.' in str(e):
                print(e, end='\r', flush=True)
                time.sleep(5)
                enumerate_ids()
        if not ids:
            add_page = False
        else:
            page_max += 1
            i_page += 1
    print('\n')
    print(get_dt() + '[KEYWORD] ' + str(search_q))
    print(get_dt() + '[BOOKS] ' + str(len(ids_n)))
    print(get_dt() + '[PAGES] ' + str(i_page-1))
    total_books = str(len(ids_n))


def compile_ids(search_q, i_page):
    """ compile a fresh set of book ids per page (prevents overloading request) """

    global ids_
    print('_' * 88)
    print('')
    print(get_dt() + '[PAGE] ' + str(i_page))
    ids_ = []
    f_dir = d_library_genesis + '/' + search_q + '/'
    try:
        library_ = Library()
        ids = library_.search(query=search_q, mode=search_mode, page=i_page, per_page=100)
        ids_ = ids
    except Exception as e:
        # todo: expand handling
        print(get_dt() + str(e))
        time.sleep(3)
        compile_ids(search_q, i_page)
    lookup_ids = library_.lookup(ids_)

    print(get_dt() + '[BOOKS] ' + str(len(ids_)))
    if ids_:
        ensure_library_path()
        if not os.path.exists(f_dir):
            os.mkdir(f_dir)
        download_main(search_q, f_dir, lookup_ids)


def download_cover(_save_path=str, _url=str):
    """ merge after dl refinement with a single download function """

    _download_finished = False
    if not os.path.exists(_save_path):
        try:
            http = urllib3.PoolManager(retries=retries)
            r = http.request('GET', _url, preload_content=False, headers=headers)
            with open(_save_path, 'wb') as fo:
                while True:
                    data = r.read(1024)
                    if not data:
                        break
                    fo.write(data)
            fo.close()
            _download_finished = True
        except Exception as e:
            # todo: expand handling
            _download_finished = False
        try:
            r.release_conn()
        except:
            # todo: expand handling
            pass
    return _download_finished


def download(_href=str, _save_path=str, _filesize=int, _book_id=str):
    """ downloader """
    # todo: refine, write once
    global max_retry, max_retry_i, limit_speed
    if dl_id_check(book_id=_book_id, check_type='memory') is False:
        add_dl_id(book_id=_book_id)
    dl_sz = 0
    open(_save_path, 'w').close()
    with open(_save_path, 'wb') as out:
        try:
            http = urllib3.PoolManager(retries=retries)
            r = http.request('GET', _href, preload_content=False, headers=headers)
            print('')
            while True:
                if limit_speed == 0:
                    data = r.read(1024)
                    pre_append = ' [DOWNLOADING BOOK] '
                else:
                    data = r.read(limit_speed)
                    pre_append = ' [DOWNLOADING BOOK] [THROTTLING ' + str(human_limit_speed) + '] '
                if not data:
                    dl_sz += int(len(data))
                    break
                out.write(data)
                dl_sz += int(len(data))
                display_progress(_part=dl_sz, _whole=_filesize, _pre_append=pre_append)
                if limit_speed != 0:
                    time.sleep(1)
            try:
                r.release_conn()
            except Exception as e:
                # todo: expand handling
                pass

        except Exception as e:
            # todo: expand handling
            time.sleep(3)
            clear_console_line(char_limit=100)
            print(get_dt() + '[' + color(s='ERROR', c='R') + ']', end='\r', flush=True)
    out.close()
    return dl_sz


def download_handler(_href=str, _save_path=str, _str_filesize=str, _filesize=int, _title=str, _author=str, _year=str, _book_id=str):
    """ attempts to download a book with n retries according to --retry-max """
    # todo: refine
    global max_retry, max_retry_i, limit_speed, bool_failed_once

    _download = download(_href=_href, _save_path=_save_path, _filesize=_filesize, _book_id=_book_id)

    if int(_download) == int(_filesize):
        print('\n')
        print(get_dt() + '[' + color(s='DOWNLOADED SUCCESSFULLY', c='G') + ']')

        rem_dl_id(book_id=_book_id)
        if book_id_check(book_id=_book_id, check_type='memory') is False:
            add_book_id(_book_id)
    else:
        clear_console_line(char_limit=100)
        if bool_failed_once is False:
            print(get_dt() + '[' + color(s='DOWNLOAD FAILED', c='R') + ']')
        bool_failed_once = True
        time.sleep(3)

        max_retry_i += 1
        if max_retry_i < max_retry or max_retry == int(0):
            clear_console_line(char_limit=100)
            if max_retry == int(0):
                print(get_dt() + '[' + color(s='RETRYING', c='Y') + '] ' + str(max_retry_i) + ' / ' +
                      str('(unlimited)'), end='\r', flush=True)
            else:
                print(get_dt() + '[' + color(s='RETRYING', c='Y') + '] ' + str(max_retry_i) + ' / ' +
                      str(max_retry), end='\r', flush=True)
            time.sleep(3)
            download_handler(_href=_href, _save_path=_save_path, _str_filesize=_str_filesize, _filesize=_filesize,
                             _title=_title, _author=_author, _year=_year, _book_id=_book_id)

    bool_failed_once = False


def get_book_details(id=str):
    """ use book ID to return book details """

    title = id.title.strip()
    author = id.author.strip()
    year = id.year.strip()
    md5 = id.md5.strip()
    filesize = id.filesize.strip()
    if title == '':
        title = 'unknown_title'
    if author == '':
        author = 'unknown_author'
    if year == '0' or not year:
        year = 'unknown_year'
    return title, author, year, md5, filesize


def get_soup(_md5=str):
    """ return soup """

    url = ('http://library.lol/main/' + str(_md5))
    rHead = requests.get(url)
    data = rHead.text
    soup = BeautifulSoup(data, "html.parser")
    return soup


def get_extension(_soup=[]):
    """ return file extension from soup """

    href = ''
    ext = ''
    for link in _soup.find_all('a'):
        href = (link.get('href'))
        idx = str(href).rfind('.')
        _ext_ = str(href)[idx:]
        for _ in sol_ext.ext_:
            if not _ == '.html':
                if str(noCase(_ext_).strip()) == '.' + str(_).strip().lower():
                    ext = '.' + str(_.lower())
                    break
        break
    return href, ext


def get_cover_href(_soup=[]):
    """ return image url from soup """

    global bool_no_cover
    img_ = ''
    for link in _soup.find_all('img'):
        src = (link.get('src'))
        if src:
            if src.endswith('.jpg'):
                img_ = 'http://library.lol/' + src
                break
    return img_


def make_filenames(_f_dir=str, _ext=str, _title=str, _author=str, _year=str, _book_id=str):
    """ create a Windows safe filename """

    save_path = ''
    save_path_img = ''
    print(get_dt() + '[EXTENSION] ' + str(_ext))
    save_path = _f_dir + "".join([c for c in _title if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
    save_path = save_path + ' (by ' + "".join([c for c in _author if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
    save_path = save_path + ' ' + "".join([c for c in _year if c.isalpha() or c.isdigit() or c == ' ']).rstrip() + ')_' + _book_id + _ext

    if bool_no_cover is False:
        save_path_img = save_path + '.jpg'

    if len(save_path) >= 255:
        save_path = save_path[:259 + len(_ext)]
        save_path = save_path + '...)' + _ext

    return save_path, save_path_img


def display_book_details(_i_page=int, _page_max=int, _i_progress=int, _ids_=[], _total_books=int, _search_q=str, _book_id=str, _title=str, _author=str, _year=str, _filesize=str):
    print(get_dt() + '[PAGE] ' + color(s=str(_i_page), c='LC') + ' / ' + color(s=str(_page_max), c='LC'))
    print(get_dt() + '[PROGRESS] ' + color(s=str(_i_progress), c='LC') + ' / ' + color(s=str(len(_ids_)), c='LC') + ' (' + color(s=str(_total_books), c='LC') + ')')
    print(get_dt() + '[KEYWORD] ' + str(_search_q))
    print(get_dt() + '[BOOK ID] ' + str(_book_id))
    print(get_dt() + '[TITLE] ' + color(s=str(_title), c='LC'))
    print(get_dt() + '[AUTHOR] ' + color(s=str(_author), c='LC'))
    print(get_dt() + '[YEAR] ' + str(_year))
    print(get_dt() + '[FILE SIZE] ' + str(convert_bytes(int(_filesize))))


def download_main(search_q, f_dir, lookup_ids):
    """ obtains book details using book id and calls dl function if certain conditions are met """
    # todo: simplify/reduce function size

    global ids_, max_retry_i, no_md5, no_ext, total_books, total_i, bool_no_cover
    i_progress = 0
    i_skipped = 0
    for _ in lookup_ids:
        try:
            i_progress += 1
            total_i += 1
            max_retry_i = 0

            book_id = _.id

            bool_book_id_check = book_id_check(book_id=book_id, check_type='memory')
            if bool_book_id_check is False:
                print('_' * 88)
                print('')

                # uncomment to display entire dictionary
                # print(_.__dict__)

                title, author, year, md5, filesize = get_book_details(id=_)

                display_book_details(_i_page=i_page, _page_max=page_max, _i_progress=i_progress, _ids_=ids_,
                                     _total_books=total_books, _search_q=search_q, _book_id=book_id, _title=title,
                                     _author=author, _year=year, _filesize=filesize)

                str_filesize = str(convert_bytes(int(filesize)))

                if md5 == '':
                    print(get_dt() + '[MD5] could not find md5, skipping.')
                    no_md5.append([title, author, year])
                    break

                bool_dl_id_check = dl_id_check(book_id=book_id, check_type='memory')
                # bool_book_id_check = book_id_check(book_id=book_id, check_type='memory')

                # if bool_dl_id_check is True:

                _soup = get_soup(_md5=md5)
                href, ext = get_extension(_soup=_soup)
                img_ = get_cover_href(_soup=_soup)

                if ext:
                    # create filenames
                    save_path, save_path_img = make_filenames(_f_dir=f_dir, _ext=ext, _title=title, _author=author,
                                                              _year=year, _book_id=book_id)

                    # dl book cover
                    if bool_no_cover is False:
                        print(get_dt() + '[SAVING] [COVER]')
                        _download_finished = download_cover(_save_path=save_path_img, _url=img_)
                        if _download_finished is False:
                            print(get_dt() + '[SAVING] [COVER] failed.')

                    # dl book convey new
                    allow_dl = False
                    if bool_dl_id_check is False and not os.path.exists(str(save_path)):
                        """ Book ID not in book_id.txt and not in dl_id.txt and save path does not exist """
                        print(get_dt() + '[SAVING] [NEW]')
                        allow_dl = True

                    # dl book convey retry
                    elif bool_dl_id_check is True:
                        """ Book ID in dl_id.txt (overwrite an existing file if save path exists already) """
                        print(get_dt() + '[SAVING] [RETRYING]')
                        allow_dl = True

                    # download book
                    if allow_dl is True:
                        """ download book and write """
                        try:
                            download_handler(href, save_path, str_filesize, filesize, title, author, year, book_id)
                        except Exception as e:
                            # todo: expand handling
                            print(get_dt() + str(e))
                            # failed.append([title, author, year, href])
                            download_main(search_q, f_dir, lookup_ids)

                    else:
                        """ Block to preserve existing file with the same name that is also not mentioned in dl_id """
                        print(get_dt() + '[SKIPPING] File already exists and is not in download list.')

                else:
                    print(get_dt() + '[SKIPPING] URL with compatible file extension could not be found.')

            elif bool_book_id_check is True:
                i_skipped += 1

        except Exception as e:
            # todo: expand handling
            print(get_dt() + str(e))
            download_main(search_q, f_dir, lookup_ids)

    if i_skipped > 0:
        # todo: separate from 'downloaded successfully'
        print('_' * 88)
        print('')
        print(get_dt() + '[SKIPPED] Books already registered in book_id: ' + str(i_skipped))


def summary():
    print('')
    print('_' * 88)
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
    print('')
    print(get_dt() + '[COMPLETE]')
    print('')
    print('_' * 88)


# Help menu
if len(sys.argv) == 2 and sys.argv[1] == '-h':
    print('')
    print('_' * 88)
    print('')
    print(' [LIBRARY GENESIS DOWNLOAD & RESEARCH TOOL]')
    print('')
    print('')
    print(' [DESCRIPTION]')
    print('')
    print('               [In the name of intelligence]')
    print('               [Downloads and researches a digital library]')
    print('')
    print('               [AUTHOR] [Benjamin Jack Cullen]')
    print('')
    print(' [DOWNLOAD]')
    print('')
    print('   [-h]              [Displays this help message]')
    print('   [-k]              [Specify keyword(s). Must be the last argument]')
    print('                     [Anything after -k will be treated as keyword(s)]')
    print('   [-p]              [Page. Specify start page number. Default is 0]')
    print('   [--download-mode] [Instructs program to run in download mode]')
    print('   [--retry-max]     [Max retries for an incomplete download]')
    print('                     [Can be set to unlimited to keep trying]')
    print('                     [Default is 3]')
    print('                     [If issues encountered then specify number]')
    print('   [--search-mode]   [Specify search mode]')
    print('                      [Default is title if --search-mode is unspecified]')
    print('                     [--search-mode title]')
    print('                     [--search-mode author]')
    print('                     [--search-mode isbn]')
    print('   [--no-cover]      [No Cover. Book covers will not be downloaded.]')
    print('                     [Covers are downloaded by default.]')
    print('   [--throttle]      [Throttle download speed. Specify bytes per second]')
    print('                     [1024 bytes = 1KB. Use a calculator if you need it]')
    print('                     [Example: --throttle 1024]')
    print('                     [Default is 0 (unlimited)]')
    print('')
    print(' [RESEARCH]')
    print('')
    print('   [--research-mode] [Instructs program to run in research mode]')
    print('   [-t]              [Threads. (N files to be processed simultaneously)]')
    print('                     [Default is 2 if -t is unspecified]')
    print('   [-d]              [Specify directory to research]')
    print('   [--research]      [Specify research query]')
    print('                     [This argument MUST be specified last]')
    print('')
    print(' [EXAMPLES]')
    print('')
    print('   --download-mode -k robots')
    print('   --download-mode -p 3 -k robots')
    print('   --download-mode --throttle 1024 --retry-max unlimited --search-mode title -k robots')
    print("   --research-mode -d './library_genesis' --research robots")
    print("   --research-mode -t 16 -d './library_genesis' --research robots")
    print('')
    run_function = 1984

# Parse arguments
retry_max_ = ''
search_mode_ = ''
research_str = ''
i_page_ = ''
print('')
print('_' * 88)
print('')
if '--download-mode' in sys.argv and not '-u' in sys.argv:
    print(' [LIBRARY GENESIS EXE]')
    print('')
    print(' [MODE] Download')
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
                # max_retry = str(sys.argv[i+1])
                max_retry = int(0)
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
    # clear_console()
    book_id_check(book_id='', check_type='read-file')
    dl_id_check(book_id='', check_type='read-file')
    search_q = search_q.strip()
    enumerate_ids()
    if page_max >= 1:
        while i_page <= page_max:
            compile_ids(search_q, i_page)
            i_page += 1
    summary()

# research
elif run_function == 2:
    path = dir_
    query = research_str.strip()
    search_library(_path=path, search_str=query, _threads=threads)

else:
    if run_function != 1984:
        print('\nUse -h for help.')

# final
print('\n')
colorama.Style.RESET_ALL
