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

(PROGRAM MIDPOINT) Handler.
|
| (PROGRAM ENTRY POINT) CLI.     (PROGRAM MIDPOINT) Handler.             (PROGRAM ENDPOINT)
| library_genesis.py         --> library_genesis_handler.py          --> library_genesis.downloader.py
| sys.argv menu/control.         harnesses and utilizes downloader.      does all the heavy lifting.
|
|
|

"""

import time
from datetime import datetime
import socket
import urllib3
import colorama
import pyprogress
import library_genesis_downloader


debug_level = [False, False, False]

# paths
f_dl_id = './data/dl_id.txt'
f_book_id = './data/book_id.txt'
d_library_genesis = './library_genesis'

# configure socket timeout
socket.setdefaulttimeout(15)

# initialize colorama
colorama.init()

# set default backoff time in module
urllib3.Retry.DEFAULT_BACKOFF_MAX = 10
retries = urllib3.Retry(total=None, connect=1, backoff_factor=0.5)

# set pyprogress factor in module
multiplier = pyprogress.multiplier_from_inverse_factor(factor=50)

sub_i_page = 1
_all_pages_ids = []


def get_dt():
    """ create a datetime string """
    dt = datetime.now()
    dt = ' [' + str(dt) + '] '
    return dt


def color(s=str, c=str):
    if c == 'LC':
        return colorama.Style.BRIGHT + colorama.Fore.LIGHTCYAN_EX + str(s) + colorama.Style.RESET_ALL
    elif c == 'G':
        return colorama.Style.BRIGHT + colorama.Fore.GREEN + str(s) + colorama.Style.RESET_ALL
    elif c == 'R':
        return colorama.Style.BRIGHT + colorama.Fore.RED + str(s) + colorama.Style.RESET_ALL
    elif c == 'Y':
        return colorama.Style.BRIGHT + colorama.Fore.YELLOW + str(s) + colorama.Style.RESET_ALL


def get_page_ids(_search_q=str, _search_mode=str):
    """ takes starting page as argument (>= 1) """

    global debug_level
    global sub_i_page, _all_pages_ids

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_handler.get_page_ids)', c='Y') + ']')

    max_or_fail = False

    while max_or_fail is False:
        try:
            print(get_dt() + '[SEARCHING] [PAGE] [' + str(sub_i_page) + ']')
            pages_ids = library_genesis_downloader.iter_get_page_ids(_i_page=sub_i_page, _search_q=_search_q,
                                                                     _search_mode=_search_mode)
            if pages_ids:
                if pages_ids not in _all_pages_ids:
                    _all_pages_ids.append(pages_ids)

            if debug_level[1] is True:
                print(get_dt() + '[library_genesis_handler.main] [' + color(s='SUBPAGE_I', c='Y') + '] ' + str(sub_i_page))
                print(get_dt() + '[library_genesis_handler.main] [' + color(s='_all_pages_ids[sub_i_page-1]',
                                                                            c='Y') + '] ' + str(len(_all_pages_ids)))
            sub_i_page += 1

        except Exception as e:
            if debug_level[0] is True:
                print(get_dt() + '[' + color(s='ERROR (library_genesis_handler.get_page_ids)', c='R') + '] ' + color(s=str(e), c='R'))
            max_or_fail = True

    return _all_pages_ids


def get_pages(_all_pages_ids=[]):
    global debug_level

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_handler.get_pages)', c='Y') + ']')
    page_max = len(_all_pages_ids)
    print(get_dt() + '[PAGES]', page_max)
    return page_max


def get_book_count(_all_pages_ids=[]):
    global debug_level

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_handler.get_book_count)', c='Y') + ']')
    total_books = 0
    for _ in _all_pages_ids:
        for x in _:
            total_books += 1
    print(get_dt() + '[TOTAL BOOKS]', total_books)
    return total_books


def get_range(start=int, end=int, value=int):
    global debug_level

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_handler.get_range)', c='Y') + ']')
    if value in range(start, end):
        print(get_dt() + '[SKIPPING TO PAGE]', value)
        return True


def perform_checks(_i_page=int, _search_q=str, _search_mode=str):
    global debug_level

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_handler.perform_checks)', c='Y') + ']')

    page_max = 0
    total_books = 0
    bool_perform_checks = False
    all_pages_ids = get_page_ids(_search_q=_search_q, _search_mode=_search_mode)

    if all_pages_ids:

        # check populated
        if all_pages_ids:

            # check pages
            page_max = get_pages(_all_pages_ids=all_pages_ids)
            if page_max > 0:

                # check total books
                total_books = get_book_count(_all_pages_ids=all_pages_ids)
                if total_books > 0:

                    # check start page in range
                    if get_range(start=1, end=page_max, value=_i_page) is True:
                        bool_perform_checks = True
    else:
        all_pages_ids = []

    return bool_perform_checks, all_pages_ids, page_max, total_books


def start_download_main(_all_pages_ids=[], _i_page=int,
                        _search_q=str,
                        _download_location=str,
                        _lookup_ids=[],
                        _page_max=int,
                        _total_books=int):
    global debug_level

    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_handler.start_download_main)', c='Y') + ']')
    _download_location = './library_genesis/' + str(_search_q) + '/'

    i_progress = 0
    for _ in _all_pages_ids:
        print(get_dt() + '[SKIPPING PAGE]', i_progress)

        # skip to page
        if int(i_progress) >= int(_i_page):
            print(get_dt() + '[STARTING PAGE]', i_progress)
            lookup_ids = library_genesis_downloader.lookup_ids(_ids_=_)
            library_genesis_downloader.download_main(_i_page=_i_page,
                                                     _search_q=_search_q,
                                                     _download_location=_download_location,
                                                     _lookup_ids=lookup_ids,
                                                     _page_max=_page_max,
                                                     _total_books=_total_books)
        i_progress += 1

    if i_progress == _page_max-1:
        return True


def main(_i_page=int, _search_q=str, _search_mode=str):
    global debug_level
    global sub_i_page, _all_pages_ids
    if debug_level[2] is True:
        print(get_dt() + '[' + color(s='Plugged-In (library_genesis_handler.main)', c='Y') + ']')

    # flush each time main is run.
    sub_i_page = 1
    _all_pages_ids = []

    while True:
        if _search_q:
            if _search_mode:
                # try:

                # perform multiple checks before handing over to the downloader
                bool_perform_checks, all_pages_ids, max_page, total_books = perform_checks(_i_page=_i_page,
                                                                                           _search_q=_search_q,
                                                                                           _search_mode=_search_mode)
                if bool_perform_checks is False:
                    print(get_dt() + '[library_genesis_handler.main] [perform_checks] [' + color(s='FAILED', c='R') + ']')

                elif bool_perform_checks is True:
                    print(get_dt() + '[library_genesis_handler.main] [perform_checks] [' + color(s='PASSED', c='G') + ']')

                    # start downloading
                    download_progress_max = start_download_main(_all_pages_ids=all_pages_ids, _i_page=_i_page,
                                                                _search_q=_search_q,
                                                                _page_max=max_page,
                                                                _total_books=total_books)
                    if download_progress_max is True:
                        break

                # except Exception as e:
                #     if debug_level[0] is True:
                #         print(get_dt() + '[' + color(s='ERROR (library_genesis_handler.main)', c='R') + '] ' + color(s=str(e), c='R'))
            else:
                print(get_dt() + '[' + color(s='MISSING (library_genesis_handler.main)', c='Y') + '] Specify search mode.')
                break
        else:
            print(get_dt() + '[' + color(s='MISSING (library_genesis_handler.main)', c='Y') + '] Specify search query.')
            break
        print(get_dt() + '[library_genesis_handler.main] [' + color(s='RETRYING', c='Y') + ']')
        time.sleep(10)
