"""
Written by Benjamin Jack Cullen aka Holographic_Sol
"""
import datetime
import os
import sys
from pylibgen import Library
import requests
from bs4 import BeautifulSoup
import urllib.request
import urllib3
import socket
import unicodedata
import subprocess
import sol_ext

failed = []
ids_ = []
search_q = ''
page_max = 0
dl_method = ''
update_max = 0
i_update = 0
start_page = False
i_page = 1

info = subprocess.STARTUPINFO()
info.dwFlags = 1
info.wShowWindow = 0
main_pid = int()


def get_dt():
    dt = datetime.datetime.now()
    dt = '[' + str(dt) + '] '
    return dt


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
    # every page
    global page_max, search_q
    i_page = 1
    add_page = True
    ids_n = []
    while add_page is True:
        ids = []
        library_ = Library()
        try:
            ids = library_.search(query=search_q, mode='title', page=i_page, per_page=100)
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
    print(get_dt() + '[KEYWORD] ' + str(search_q))
    print(get_dt() + '[BOOKS] ' + str(len(ids_n)))
    print('-' * 100)


def compile_ids(search_q, i_page):
    global ids_
    ids_ = []
    f_dir = './library_genesis/' + search_q + '/'

    library_ = Library()
    try:
        ids = library_.search(query=search_q, mode='title', page=i_page, per_page=100)
        print(get_dt() + '[PAGE] ' + str(i_page))
        print(get_dt() + '[BOOK IDs] ' + str(ids))
        ids_ = ids

    except Exception as e:
        print(get_dt() + str(e))

    lookup_ids = library_.lookup(ids_)
    print('-' * 100)
    print(get_dt() + '[PAGE] ' + str(i_page))
    print(get_dt() + '[BOOKS] ' + str(len(ids_)))
    print('-' * 100)

    if ids_:

        if not os.path.exists(f_dir):
            os.mkdir(f_dir)
        dl_books(search_q, f_dir, lookup_ids)


def dl_books(search_q, f_dir, lookup_ids):
    global ids_, dl_method, i_update
    i = 0
    i_update += 1
    for _ in lookup_ids:
        try:
            i += 1
            print('-' * 100)
            if dl_method == 'keyword':
                print(get_dt() + '[PAGE] ' + str(i_page) + ' / ' + str(page_max))
                print(get_dt() + '[PROGRESS] ' + str(i) + ' / ' + str(len(ids_)))
            elif dl_method == 'update':
                print(get_dt() + '[UPDATE] ' + str(search_q))
                print(get_dt() + '[PROGRESS] ' + str(i_update) + ' / ' + str(update_max))

            # print(_.__dict__)

            title = _.title
            if title == '':
                title = str(i) + '_unknown_title'
            print(get_dt() + '[TITLE] ' + str(title))

            author = _.author
            if author == '':
                author = str(i) + '_unknown_author'
            print(get_dt() + '[AUTHOR] ' + str(author))

            year = _.year
            if year == '0':
                year = ''
            print(get_dt() + '[YEAR] ' + str(year))

            filesize = _.filesize
            try:
                print(get_dt() + '[FILE SIZE] ' + str(convert_bytes(int(filesize))))
            except:
                pass

            md5 = _.md5
            if md5 == '':
                print(get_dt() + 'could not find md5, skipping')
                failed.append([title, author, year])
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
                    # print(get_dt() + 'comparing:', _ext_, '--> list item:', str(_).strip().lower())
                    if not _ == '.html':
                        if str(noCase(_ext_).strip()) == '.' + str(_).strip().lower():
                            ext = '.' + str(_.lower())
                            print(get_dt() + '[HREF] ' + str(href))
                            break
                break

            # http://library.lol/covers/183000/9859fc9115a0b616218bcaa692ca87ca-d.jpg
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
                save_path = save_path + ' ' + "".join([c for c in year if c.isalpha() or c.isdigit() or c == ' ']).rstrip() + ')' + ext
                save_path_img = save_path + ' ' + "".join([c for c in year if c.isalpha() or c.isdigit() or c == ' ']).rstrip() + ').jpg'

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                    'Accept-Encoding': 'text/plain',
                    'Accept-Language': 'en-US,en;q=0.9'
                    }
                retries = urllib3.Retry(connect=5, read=2, redirect=5)
                if not os.path.exists(save_path_img):
                    print(get_dt() + '[SAVING] ' + str(save_path_img))
                    http = urllib3.PoolManager(retries=retries)
                    r = http.request('GET', img_, preload_content=False, headers=headers)
                    with open(save_path_img, 'wb') as out:
                        while True:
                            data = r.read(1000000000)
                            if not data:
                                break
                            out.write(data)
                    r.release_conn()

                if not os.path.exists(save_path):
                    print(get_dt() + '[SAVING] ' + str(save_path))
                    try:

                        http = urllib3.PoolManager(retries=retries)
                        r = http.request('GET', href, preload_content=False, headers=headers)
                        with open(save_path, 'wb') as out:
                            while True:
                                data = r.read(int(filesize))
                                if not data:
                                    break
                                out.write(data)
                        r.release_conn()

                    except Exception as e:
                        print(get_dt() + str(e))
                        failed.append([title, author, year, href])
                else:
                    print(get_dt() + '[SKIPPING]')
            else:
                failed.append([title, author, year, href])
        except Exception as e:
            print(get_dt() + str(e))
            try:
                failed.append([_.title, _.author, _.year, href])
            except Exception as e:
                print(get_dt() + str(e))


# Help menu
if len(sys.argv) == 2 and sys.argv[1] == '-h':
    banner()
    print('    Intended as an intelligence tool for archiving information in an uncertain world.')
    print('    Downloads every book on every page for keyword specified.')
    print('    Written by Benjamin Jack Cullen.')
    print('')
    print('Command line arguments:\n')
    print('    -h      Displays this help message.')
    print('    -k      Keyword. Specify keyword(s).')
    print('    -u      Update. Update an existing library genesis directory.')
    print('            Each directory name in an existing ./library_genesis directory will')
    print('            be used as a keyword during update process.')
    print('    -p      Page. Specify start page number.')
    print('')
    print('    Example: library_genesis -k human')
    print('    Example: library_genesis -p 3 -k human')
    print('    Example: library_genesis -u')
    print('')

# Parse arguments
run_function = ()
i = 0
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
        i_page = int(sys.argv[i+1])

    # update
    elif _ == '-u':
        run_function = 1
        break
    i += 1

# Keyword download
if run_function == 0:
    search_q = search_q.strip()
    enumerate()
    if page_max >= 1:
        dl_method = 'keyword'
        # i_page = 1
        while i_page < page_max:
            compile_ids(search_q, i_page)
            i_page += 1
    print('')
    print('-' * 100)
    if failed:
        print('')
        print(get_dt() + 'may have failed (check to confirm):')
        for _ in failed:
            print('   ', _)
        print(get_dt() + 'may have failed: ' + str(len(failed)))

    print(get_dt() + 'completed.')

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
print('\n\n')
