"""
Written by Benjamin Jack Cullen aka Holographic_Sol
"""
import os
import sys
from pylibgen import Library
import requests
from bs4 import BeautifulSoup
import urllib.request
import urllib3

failed = []
ids_ = []
search_q = ''
page_max = 0
dl_method = ''
update_max = 0
i_update = 0
start_page = False
i_page = 1


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
            print('[PAGE]', i_page)
            print('[BOOK IDs]', ids)
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
    print('[KEYWORD]', search_q)
    print('[BOOKS]', len(ids_n))
    print('-' * 100)


def compile_ids(search_q, i_page):
    global ids_
    ids_ = []
    f_dir = './library_genesis/' + search_q + '/'

    library_ = Library()
    try:
        ids = library_.search(query=search_q, mode='title', page=i_page, per_page=100)
        print('[PAGE]', i_page)
        print('[BOOK IDs]', ids)
        ids_ = ids

    except Exception as e:
        print(e)

    lookup_ids = library_.lookup(ids_)
    print('-' * 100)
    print('[PAGE]', i_page)
    print('[BOOKS]', len(ids_))
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
                print('[PAGE]', i_page, '/', page_max)
                print('[PROGRESS]', i, '/', len(ids_))
            elif dl_method == 'update':
                print('[UPDATE]', search_q)
                print('[PROGRESS]', i_update, '/', update_max)

            # print(_.__dict__)

            title = _.title
            if title == '':
                title = str(i) + '_unknown_title'
            print('[TITLE]', title)

            author = _.author
            if author == '':
                author = str(i) + '_unknown_author'
            print('[AUTHOR]', author)

            year = _.year
            if not year:
                year = ''
            print('[YEAR]', year)

            filesize = _.filesize
            print('[FILE SIZE]', filesize)

            md5 = _.md5
            if md5 == '':
                print('-- could not find md5, skipping')
                failed.append([title, author, year])
                break
            print('[md5]', md5)
            
            url = ('http://library.lol/main/' + str(md5))
            rHead = requests.get(url)
            data = rHead.text
            soup = BeautifulSoup(data, "html.parser")
            href = ''
            ext = ''
            for link in soup.find_all('a'):
                href = (link.get('href'))
                if href.endswith('.pdf'):
                    ext = '.pdf'
                    break
                elif href.endswith('.epub'):
                    ext = '.epub'
                    break
                elif href.endswith('.djvu'):
                    ext = '.djvu'
                    break
                elif href.endswith('.azw3'):
                    ext = '.azw3'
                    break
                elif href.endswith('.mobi'):
                    ext = '.mobi'
                    break
                elif href.endswith('.rar'):
                    ext = '.rar'
                    break
                else:
                    print('[UNHANDLED HREF]', href)
            if ext:
                print('[EXTENSION]', ext)
                save_path = f_dir + "".join([c for c in title if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
                save_path = save_path + ' (by ' + "".join([c for c in author if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
                save_path = save_path + ' ' + "".join([c for c in year if c.isalpha() or c.isdigit() or c == ' ']).rstrip() + ')' + ext
                if not os.path.exists(save_path):
                    print('[SAVING]', save_path)
                    try:
                        http = urllib3.PoolManager()
                        r = http.request('GET', href, preload_content=False)
                        with open(save_path, 'wb') as out:
                            while True:
                                data = r.read(int(filesize))
                                if not data:
                                    break
                                out.write(data)
                        r.release_conn()
                    except Exception as e:
                        print(e)
                        failed.append([title, author, year, href])
                else:
                    print('[SKIPPING]')
            else:
                failed.append([title, author, year, href])
        except Exception as e:
            print(e)
            try:
                failed.append([_.title, _.author, _.year, href])
            except Exception as e:
                print(e)


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
        print('[Search]', str_)
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
        print('\nmay have failed (check to confirm):')
        for _ in failed:
            print('   ', _)
        print('may have failed:', len(failed))
    else:
        print('-- use -h for help.')
    print('-- completed.')

elif run_function == 1:
    banner()
    print('[Update Library]')
    update_max = 0
    search_q = []
    for dirname, dirnames, filenames in os.walk('./library_genesis'):
        for subdirname in dirnames:
            fullpath = os.path.join(subdirname)
            search_q.append(fullpath)
            print('    [update]', fullpath)
            update_max += 1
    i_query = 0
    dl_method = 'update'
    for _ in search_q:
        i_page = 1
        print('[updating]', _)
        compile_ids(search_q[i_query], i_page)
        i_query += 1
print('\n\n')
