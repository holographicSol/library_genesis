"""
 Written by Benjamin Jack Cullen aka Holographic_Sol

 * Downloads every book on every page of library genesis for keyword(s) specified.

 * Downloaded books are automatically categorized being placed into a subdirectory named as keyword(s) specified.

 * Uses various means to keep track of what already exists in the book library:
        (1) skip past books in book_id.
        (2) continue downloading books in dl_id.
        (3) (care) skip books/files filenames already exist in said download directory when book id also not in dl_id.

 Extra Notes:
    * dl_id.txt and or book_id.txt can be deleted and this program is able to continue from where it left off
      and will not retry any partially downloaded books/files.

    * recommended to keep book_id.txt.
    * recommended to keep dl_id.txt.

(PROGRAM ENDPOINT) Downloader.
|
| (PROGRAM ENTRY POINT) CLI.     (PROGRAM MIDPOINT) Handler.             (PROGRAM ENDPOINT)
| library_genesis.py         --> library_genesis_handler.py          --> library_genesis.downloader.py
| sys.argv menu/control.         harnesses and utilizes downloader.      does all the heavy lifting.
|
|
|

"""
import os
import time
from datetime import datetime, timedelta
import codecs
import socket
import urllib3
import colorama
import requests
import unicodedata
from pylibgen import Library
from bs4 import BeautifulSoup
import sol_ext
import pyprogress

f_dl_id = './data/dl_id.txt'
f_book_id = './data/book_id.txt'
skip_book_id = './data/skip_book_id.txt'
d_library_genesis = './library_genesis'

# set and initiate
max_retry = 0
max_retry_i = 0
i_page = 1
limit_speed = 1024
threads = 4
i_char_progress = 0
bool_failed_once = False
_throttle = False
bool_no_cover = False
book_id_store = []
dl_id_store = []
skip_book_id_store = []
debug_level = [False, False, False]


def ensure_data_paths():
    global debug_level

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.ensure_data_paths)', c='Y') + ']')

    if not os.path.exists('./data/'):
        os.mkdir('./data')
    if not os.path.exists(f_dl_id):
        open(f_dl_id, 'w').close()
    if not os.path.exists(f_book_id):
        open(f_book_id, 'w').close()
    if not os.path.exists(skip_book_id):
        open(skip_book_id, 'w').close()


def ensure_library_path():
    global debug_level

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.ensure_library_path)', c='Y') + ']')

    if not os.path.exists(d_library_genesis):
        os.mkdir(d_library_genesis)


# initialize paths
ensure_data_paths()
ensure_library_path()

# initialize colorama
colorama.init()

# configure socket timeout
socket.setdefaulttimeout(3)

# set default backoff time in module
urllib3.Retry.DEFAULT_BACKOFF_MAX = 10
retries = urllib3.Retry(total=None, connect=300, backoff_factor=0.5)

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
                            encapsulate_l='[',
                            encapsulate_r=']',
                            encapsulate_l_color='LIGHTWHITE_EX',
                            encapsulate_r_color='LIGHTWHITE_EX',
                            progress_char=' ',
                            bg_color='GREEN',
                            factor=50,
                            multiplier=multiplier)


def iter_ids(_search_q=str, _search_mode='title', _i_page=1):
    """ Used to measure multiple instances/types of progress during download and returns all ids for search query """

    global debug_level

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.iter_ids)', c='Y') + ']')

    _all_pages_ids = []

    try:
        library_ = Library()
        ids = library_.search(query=_search_q, mode=_search_mode, page=_i_page, per_page=100)
        if ids:
            _all_pages_ids.append(ids)

    except Exception as e:
        if debug_level[0] is True:
            print(get_dt() + '[' + color(s='ERROR (library_genesis_downloader.iter_ids)', c='R') + '] ' + color(s=str(e), c='R'))

    return _all_pages_ids


def iter_get_page_ids(_i_page=1, _search_q=str, _search_mode=str):

    global debug_level

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.iter_get_page_ids)', c='Y') + ']')

    pages_ids, = iter_ids(_search_q=_search_q,
                          _search_mode=_search_mode,
                          _i_page=_i_page)
    return pages_ids


def lookup_ids(_ids_=[]):
    """ lookup n ids (prevents overloading lookup request) """

    global debug_level

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.lookup_ids)', c='Y') + ']')

    try:
        library_ = Library()
    except Exception as e:
        if debug_level[0] is True:
            print(get_dt() + '[' + color(s='ERROR (library_genesis_downloader.lookup_ids.Library)', c='R') + '] ' + color(s=str(e), c='R'))

    try:
        ids_lookup = _ids_
        _lookup_ids_ = library_.lookup(ids_lookup, per_page=100)
        if _lookup_ids_:
            return _lookup_ids_

    except Exception as e:
        if debug_level[0] is True:
            print(get_dt() + '[' + color(s='ERROR (library_genesis_downloader.lookup_ids.lookup)', c='R') + '] ' + color(s=str(e), c='R'))


def skip_book_id_check(book_id, check_type):
    """ check if book id in file/memory """

    global skip_book_id_store
    global debug_level

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.skip_book_id_check)', c='Y') + ']')

    bool_skip_book_id_check = False
    if check_type == 'read-file':
        ensure_data_paths()
        with open(skip_book_id, 'r') as fo:
            for line in fo:
                line = line.strip()
                if line not in skip_book_id_store:
                    skip_book_id_store.append(line)
        fo.close()
    elif check_type == 'memory':
        if book_id in skip_book_id_store:
            bool_skip_book_id_check = True

    return bool_skip_book_id_check


def add_skip_id(book_id):
    """ add book id to file and list in memory """

    global skip_book_id_store
    global debug_level

    if debug_level[1] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.add_skip_id)', c='Y') + ']')

    ensure_data_paths()
    with open(skip_book_id, 'a') as fo:
        fo.write(str(book_id) + '\n')
    fo.close()

    if book_id not in skip_book_id_store:
        skip_book_id_store.append(book_id)

    if debug_level[1] is True:
        print(get_dt() + '[' + color(s='(library_genesis_downloader.add_skip_id) skip_book_id_store:', c='Y') +
              str(len(skip_book_id_store)) + ']')


def rem_skip_id(book_id):
    """" remove book id from download file """

    global skip_book_id_store
    global debug_level

    if debug_level[1] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.rem_skip_id)', c='Y') + ']')

    ensure_data_paths()
    new = []
    with open(skip_book_id, 'r') as fo:
        for line in fo:
            line = line.strip()
            if line != book_id:
                new.append(line)
    fo.close()
    with open(skip_book_id, 'w') as fo:
        fo.close()
    with open(skip_book_id, 'a') as fo:
        for _ in new:
            fo.write(_ + '\n')
    fo.close()
    skip_book_id_store.remove(book_id)

    if debug_level[1] is True:
        print(get_dt() + '[' + color(s='(library_genesis_downloader.rem_skip_id) skip_book_id_store:', c='Y') + str(
            len(skip_book_id_store)) + ']')


def book_id_check(book_id, check_type):
    """ check if book id in file/memory """

    global book_id_store
    global debug_level

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.book_id_check)', c='Y') + ']')

    bool_book_id_check = False
    if check_type == 'read-file':
        ensure_data_paths()
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
    global debug_level

    if debug_level[1] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.add_book_id)', c='Y') + ']')

    ensure_data_paths()
    with open(f_book_id, 'a') as fo:
        fo.write(str(book_id) + '\n')
    fo.close()
    if book_id not in book_id_store:
        book_id_store.append(book_id)

    if debug_level[1] is True:
        print(get_dt() + '[' + color(s='(library_genesis_downloader.add_book_id) book_id_store:', c='Y') +
              str(len(book_id_store)) + ']')


def dl_id_check(book_id=str, check_type=str):
    """ check if book id in download file  """

    global dl_id_store
    global debug_level

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.dl_id_check)', c='Y') + ']')

    bool_dl_id_check = False
    if check_type == 'read-file':
        ensure_data_paths()
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
    global debug_level

    if debug_level[1] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.add_dl_id)', c='Y') + ']')

    ensure_data_paths()
    with codecs.open(f_dl_id, 'a', encoding='utf8') as fo:
        fo.write(book_id + '\n')
    fo.close()
    dl_id_store.append(book_id)

    if debug_level[1] is True:
        print(get_dt() + '[' + color(s='(library_genesis_downloader.add_dl_id) dl_id_store:', c='Y') + str(
            len(dl_id_store)) + ']')


def rem_dl_id(book_id):
    """" remove book id from download file """

    global dl_id_store
    global debug_level

    if debug_level[1] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.rem_dl_id)', c='Y') + ']')

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

    if debug_level[1] is True:
        print(get_dt() + '[' + color(s='(library_genesis_downloader.rem_dl_id) dl_id_store:', c='Y') + str(
            len(dl_id_store)) + ']')


def get_request(_href=str):
    """ posts GET request """

    global debug_level

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.get_request)', c='Y') + ']')

    try:
        http = urllib3.PoolManager(retries=retries)
        r = http.request('GET', _href, preload_content=False, headers=headers)
        return r
    except Exception as e:
        if debug_level[0] is True:
            print(get_dt() + '[' + color(s='ERROR (library_genesis_downloader.get_request)', c='R') + '] ' + color(s=str(e), c='R'))


def save_download(_save_path=str, _data=bytes, _filesize=int, _mode=''):
    """ writes bytes to file """

    global debug_level

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.save_download)', c='Y') + ']')

    dl_complete = False
    open(_save_path, 'w').close()
    with open(_save_path, 'wb') as out:
        out.write(_data)
    out.close()

    if _mode == 'check_size':
        sz_file = os.path.getsize(_save_path)
        if int(sz_file) == int(_filesize):
            dl_complete = True
        return dl_complete


def download_cover(_save_path=str, _url=str):
    """ merge after dl refinement with a single download function """
    global debug_level
    global limit_speed, _throttle

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.download_cover)', c='Y') + ']')

    _download_finished = False
    _data = bytes()
    if not os.path.exists(_save_path):
        try:
            r = get_request(_href=_url)
            while True:
                data = r.read(limit_speed)
                if data:
                    _data += data
                    if _throttle is True:
                        time.sleep(1)
                else:
                    break
            _download_finished = True
        except Exception as e:
            if debug_level[0] is True:
                print(get_dt() + '[' + color(s='ERROR (library_genesis_downloader.download_cover)', c='R') + '] ' + color(s=str(e), c='R'))
            _download_finished = False
        try:
            if r:
                r.release_conn()
        except Exception as e:
            if debug_level[0] is True:
                print(get_dt() + '[' + color(s='ERROR (library_genesis_downloader.download_cover.release_conn)', c='R') + '] ' + color(s=str(e), c='R'))
            pass
    if _download_finished is True:
        save_download(_save_path=_save_path, _data=_data)
    return _download_finished


def display_download_progress(_dl_sz=int, _filesize=int, _limit_speed=limit_speed):
    """ sets some strings for pyprogress """

    pre_append = ' [DOWNLOADING BOOK] '
    if _throttle is True:
        pre_append = ' [DOWNLOADING BOOK] [THROTTLING ' + str(convert_bytes(_limit_speed)) + '] '
    display_progress(_part=_dl_sz, _whole=_filesize, _pre_append=pre_append)


def download(_href=str, _save_path=str, _filesize=int, _book_id=str):
    """ downloader """

    global debug_level
    global max_retry, max_retry_i, limit_speed, _throttle

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.download)', c='Y') + ']')

    if dl_id_check(book_id=_book_id, check_type='memory') is False:
        add_dl_id(book_id=_book_id)
    dl_sz = int(0)
    _data = bytes()
    try:
        r = get_request(_href=_href)
        while True:
            data = r.read(limit_speed)
            if data:
                _data += data
                dl_sz += int(len(data))
                display_download_progress(_dl_sz=dl_sz, _filesize=_filesize)
                if _throttle is True:
                    time.sleep(1)
            else:
                break
    except Exception as e:
        if debug_level[0] is True:
            print('')
            print(get_dt() + '[' + color(s='ERROR (library_genesis_downloader.download)', c='R') + '] ' + color(s=str(e), c='R'))
    try:
        if r:
            r.release_conn()
    except Exception as e:
        if debug_level[0] is True:
            print('')
            print(get_dt() + '[' + color(s='ERROR (library_genesis_downloader.download)', c='R') + '] ' + color(s=str(e), c='R'))

        pass
    return dl_sz, _data


def download_handler(_href=str, _save_path=str, _str_filesize=str, _filesize=int, _title=str, _author=str, _year=str,
                     _book_id=str):
    """ attempts to download a book with n retries according to --retry-max """

    global debug_level
    global max_retry, max_retry_i, limit_speed, bool_failed_once

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.download_handler)', c='Y') + ']')

    # handle download attempt
    dl_sz, _data = download(_href=_href, _save_path=_save_path, _filesize=_filesize, _book_id=_book_id)

    # handle successful download
    if int(dl_sz) == int(_filesize):
        print(get_dt() + '[' + color(s='DOWNLOADED SUCCESSFULLY', c='G') + ']')

        # handle check for a successful save. note: may return false negatives depending on os/platform and filesize
        # returned from library genesis mirror. buts its worth conveying the true positives.
        download_saved = save_download(_save_path=_save_path, _data=_data, _filesize=_filesize, _mode='check_size')
        if download_saved is True:
            # convey successful save: download 100% bytes, saved 100% bytes. note: this does not reflect file integrity.
            print(get_dt() + '[' + color(s='SAVE SUCCESSFUL', c='G') + ']')
            rem_dl_id(book_id=_book_id)
            if book_id_check(book_id=_book_id, check_type='memory') is False:
                add_book_id(_book_id)
        else:
            # convey possible issue saving that may under many circumstances be ignored.
            print(get_dt() + '[' + color(s='SAVE SUCCESSFUL', c='Y') + ']')

    # handle download failed
    else:
        if bool_failed_once is False:
            print(get_dt() + '[' + color(s='DOWNLOAD FAILED', c='R') + ']')
        bool_failed_once = True
        time.sleep(3)

        # handle restart download
        max_retry_i += 1
        if max_retry_i < max_retry or max_retry == int(0):
            if max_retry == int(0):
                print(get_dt() + '[' + color(s='RETRYING', c='Y') + '] ' + str(max_retry_i) + ' / ' +
                      str('(unlimited)'))
            else:
                print(get_dt() + '[' + color(s='RETRYING', c='Y') + '] ' + str(max_retry_i) + ' / ' +
                      str(max_retry))

            time.sleep(10)
            download_handler(_href=_href, _save_path=_save_path, _str_filesize=_str_filesize,
                             _filesize=_filesize,
                             _title=_title, _author=_author, _year=_year, _book_id=_book_id)
    bool_failed_once = False


def get_book_details(_id=str):
    """ returns book details from a dictionary (_id) """

    global debug_level
    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.get_book_details)', c='Y') + ']')

    title = _id.title.strip()
    author = _id.author.strip()
    year = _id.year.strip()
    md5 = _id.md5.strip()
    filesize = _id.filesize.strip()
    if title == '':
        title = 'unknown_title'
    if author == '':
        author = 'unknown_author'
    if year == '0' or not year:
        year = 'unknown_year'
    return title, author, year, md5, filesize


def get_soup(_md5=str):
    """ return soup """

    global debug_level

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.get_soup)', c='Y') + ']')

    try:
        url = ('http://library.lol/main/' + str(_md5))
        rHead = requests.get(url)
        data = rHead.text
        soup = BeautifulSoup(data, "html.parser")
    except Exception as e:
        if debug_level[0] is True:
            print(get_dt() + '[' + color(s='ERROR (library_genesis_downloader.get_soup)', c='R') + '] ' + color(s=str(e), c='R'))
    return soup


def get_extension(_soup=[]):
    """ return file extension from soup """

    global debug_level

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.get_extension)', c='Y') + ']')

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

    global debug_level

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.get_cover_href)', c='Y') + ']')

    img_ = ''
    for link in _soup.find_all('img'):
        src = (link.get('src'))
        if src:
            if src.endswith('.jpg'):
                img_ = 'http://library.lol/' + src
                break
    return img_


def make_filenames(_download_location=str, _ext=str, _title=str, _author=str, _year=str, _book_id=str):
    """ create a Windows safe filename """

    global debug_level
    global bool_no_cover

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.make_filenames)', c='Y') + ']')

    save_path_img = ''
    print(get_dt() + '[EXTENSION] ' + str(_ext))
    save_path = _download_location + "".join([c for c in _title if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
    save_path = save_path + ' (by ' + "".join([c for c in _author if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
    save_path = save_path + ' ' + "".join([c for c in _year if c.isalpha() or c.isdigit() or c == ' ']).rstrip() + ')_' + _book_id + _ext

    if bool_no_cover is False:
        save_path_img = save_path + '.jpg'

    if len(save_path) >= 255:
        save_path = save_path[:259 + len(_ext)]
        save_path = save_path + '...)' + _ext

    return save_path, save_path_img


def display_book_details(_i_page=int, _page_max=int, _i_progress=int, _total_books=int, _search_q=str, _book_id=str, _title=str, _author=str, _year=str, _filesize=str):
    global debug_level

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.display_book_details)', c='Y') + ']')

    print(get_dt() + '[PAGE] ' + color(s=str(_i_page), c='LC') + ' / ' + color(s=str(_page_max), c='LC'))
    print(get_dt() + '[PROGRESS] ' + color(s=str(_i_progress), c='LC') + ' / ' + color(s=str(_total_books), c='LC'))
    print(get_dt() + '[KEYWORD] ' + str(_search_q))
    print(get_dt() + '[BOOK ID] ' + str(_book_id))
    print(get_dt() + '[TITLE] ' + color(s=str(_title), c='LC'))
    print(get_dt() + '[AUTHOR] ' + color(s=str(_author), c='LC'))
    print(get_dt() + '[YEAR] ' + str(_year))
    print(get_dt() + '[FILE SIZE] ' + str(convert_bytes(int(_filesize))))


def download_main(_search_q=str, _download_location=str, _lookup_ids=[], _page_max=int, _total_books=int,
                  _i_page=int):
    """ obtains book details using book id and calls dl function if certain conditions are met """

    global debug_level
    global max_retry_i
    global bool_no_cover

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_downloader.download_main)', c='Y') + ']')

    i_progress = 0

    for _ in _lookup_ids:

        i_progress += 1
        max_retry_i = 0

        # check book id first for performance
        book_id = _.id
        # print('book_id', book_id)
        bool_book_id_check = book_id_check(book_id=book_id, check_type='memory')
        bool_skip_book_id_check = skip_book_id_check(book_id=book_id, check_type='memory')

        if bool_book_id_check is False and bool_skip_book_id_check is False:

            # uncomment to display entire dictionary
            # print(_.__dict__)

            print('_'*88)
            print('')

            title, author, year, md5, filesize = get_book_details(_id=_)

            display_book_details(_i_page=_i_page, _page_max=_page_max, _i_progress=i_progress,
                                 _total_books=_total_books, _search_q=_search_q, _book_id=book_id, _title=title,
                                 _author=author, _year=year, _filesize=filesize)

            str_filesize = str(convert_bytes(int(filesize)))

            if md5 == '':
                print(get_dt() + '[MD5] could not find md5, skipping.')
                break

            bool_dl_id_check = dl_id_check(book_id=book_id, check_type='memory')

            _soup = get_soup(_md5=md5)
            if _soup:
                href, ext = get_extension(_soup=_soup)
                img_ = get_cover_href(_soup=_soup)

                if ext:
                    # create filenames
                    if not os.path.exists(_download_location):
                        os.mkdir(_download_location)
                    save_path, save_path_img = make_filenames(_download_location=_download_location, _ext=ext, _title=title, _author=author,
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

                    # start downloading!
                    if allow_dl is True:
                        """ download book and write """
                        download_handler(_href=href, _save_path=save_path, _str_filesize=str_filesize,
                                         _filesize=filesize,
                                         _title=title, _author=author, _year=year, _book_id=book_id)

                    else:
                        """ Preserve existing file with the same name that is also not mentioned in dl_id """
                        print(get_dt() + '[SKIPPING] File already exists and is not in download list.')

                else:
                    print(get_dt() + '[SKIPPING] URL with compatible file extension could not be found.')
                    time.sleep(5)

            else:
                print(get_dt() + '[ISSUE] Problem obtaining HTML soup')
