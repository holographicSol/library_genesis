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

(PROGRAM ENTRY POINT) CLI.
|
| (PROGRAM ENTRY POINT) CLI.     (PROGRAM MIDPOINT) Handler.             (PROGRAM ENDPOINT)
| library_genesis.py         --> library_genesis_handler.py          --> library_genesis.downloader.py
| sys.argv menu/control.         harnesses and utilizes downloader.      does all the heavy lifting.
|
|
|

"""

import sys
from datetime import datetime
import colorama
import library_genesis_handler
import library_genesis_downloader


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


def summary():
    print('')
    print('_' * 88)
    print('')
    print(get_dt() + '[SUMMARY]')
    print('')
    print('')
    print(get_dt() + '[COMPLETE]')
    print('')
    print('_' * 88)


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
    print('               [Downloads a digital library]')
    print('')
    print('               [AUTHOR] [Benjamin Jack Cullen]')
    print('')
    print(' [DOWNLOAD]')
    print('')
    print('   [-h]              [Displays this help message]')
    print('   [-k]              [Specify keyword(s). Must be the last argument]')
    print('                     [Anything after -k will be treated as keyword(s)]')
    print('   [-p]              [Page. Specify start page number. Default is 0]')
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
    print(' [DEBUG]')
    print('')
    print('   [--debug]         [Enables debug mode level 1. Show more errors]')
    print('   [--debug-level-2] [Enables debug mode level 2. Increases debug verbosity]')
    print('   [--debug-level-3] [Enables debug mode level 3. Further increases debug verbosity]')
    print('')
    print(' [EXAMPLES]')
    print('')
    print('   -k robots')
    print('   -p 3 -k robots')
    print('   --throttle 1024 --retry-max unlimited --search-mode title -k robots')
    print("   -d './library_genesis' --research robots")
    print('')


# Parse arguments
print('')
print('_' * 88)
print('')
i_page = 1
search_q = ''
search_mode = ''
debug_level = [False, False, False]

if '--debug' in sys.argv:
    debug_level[0] = True
elif '--debug-level-2' in sys.argv:
    debug_level[0] = True
    debug_level[1] = True
elif '--debug-level-3' in sys.argv:
    debug_level[0] = True
    debug_level[1] = True
    debug_level[2] = True


print(' [LIBRARY GENESIS EXE]')
print('')
print(' [MODE] Download')
if True in debug_level:
    print(' [' + color(s='DEBUG ENABLED', c='R') + ']')
print('')
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
            search_q = str_.strip()
        else:
            print(get_dt() + "[failed] user failed to specify a search query.")
            break

    # page
    elif _ == '-p':
        i_page_ = str(sys.argv[i+1])
        if i_page_.isdigit():
            i_page = int(sys.argv[i+1])
        else:
            print(get_dt() + '[failed] -p cannot be ' + i_page_)
            break

    # retry limiter
    elif _ == '--retry-max':
        retry_max_ = sys.argv[i + 1]
        if str(sys.argv[i+1]).isdigit():
            library_genesis_downloader.max_retry = int(sys.argv[i+1])
        elif str(sys.argv[i+1]) == 'unlimited':
            library_genesis_downloader.max_retry = int(0)
        else:
            print(get_dt() + '[failed] --retry-max cannot be ' + retry_max_)
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
            break

    # throttle download speed
    elif _ == '--throttle':
        if sys.argv[i+1].isdigit():
            library_genesis_downloader.limit_speed = int(sys.argv[i+1])
            _throttle = True
        else:
            print(get_dt() + "[failed] --throttle accepts digits argument.")
            break

    elif _ == '--no-cover':
        library_genesis_downloader.bool_no_cover = True

    i += 1

# print(sys.argv)

# debug
# i_page = 9
# search_q = 'C Programming'
# search_mode = 'title'
# debug_level = [True, True, False]

# initialize
library_genesis_downloader.book_id_check(book_id='', check_type='read-file')
library_genesis_downloader.dl_id_check(book_id='', check_type='read-file')
library_genesis_downloader.debug_level = debug_level
library_genesis_handler.debug_level = debug_level

# run handler
library_genesis_handler.main(_i_page=i_page, _search_q=search_q, _search_mode=search_mode)
