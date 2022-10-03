"""
Written by Benjamin Jack Cullen aka Holographic_Sol
"""
import os
import sys
from pylibgen import Library
import requests
from bs4 import BeautifulSoup
import urllib.request

failed = []
ids_ = []
search_q = ''


def banner():
    print('\n\n')
    print('[LIBRARY GENESIS DOWNLOAD TOOL]')
    print('')


def compile_ids(dl_method, search_q, i_page):
    global ids_
    ids_ = []
    f_dir = './library_genesis/' + search_q + '/'

    # every page
    if dl_method == 'all' or dl_method == 'all_update':
        add_page = True
        while add_page is True:
            ids = []
            library_ = Library()
            try:
                ids = library_.search(query=search_q, mode='title', page=i_page, per_page=100)
                print('[page:', i_page, '] book IDs:', ids)
                for _ in ids:
                    if _ not in ids_:
                        ids_.append(_)
            except:
                add_page = False
            if not ids:
                add_page = False
            else:
                i_page += 1

    # specific page
    elif dl_method == 'page':
        library_ = Library()
        try:
            ids = library_.search(query=search_q, mode='title', page=i_page, per_page=100)
            print('[page:', i_page, '] book IDs:', ids)
            ids_ = ids

        except Exception as e:
            print(e)

    lookup_ids = library_.lookup(ids_)
    print('found:', len(ids_), 'books')

    if ids_:
        if dl_method != 'all_update':
            user_dl_books = input('would you like to download?(y/n): ')
        else:
            user_dl_books = 'y'
        if user_dl_books == 'y' or user_dl_books == 'Y':
            if not os.path.exists(f_dir):
                os.mkdir(f_dir)
            dl_books(f_dir, lookup_ids)


def dl_books(f_dir, lookup_ids):
    global ids_
    i = 0
    for _ in lookup_ids:
        try:
            i += 1
            print('-' * 100)
            print('progress:', i, '/', len(ids_))
            # print(_.__dict__)

            title = _.title
            if title == '':
                title = str(i) + '_unknown_title'
            print('title:', _.title)

            author = _.author
            if author == '':
                author = str(i) + '_unknown_author'
            print('author:', _.author)

            year = _.year
            if not year:
                year = ''
            print('year:', _.year)

            md5 = _.md5
            if md5 == '':
                print('-- could not find md5, skipping')
                failed.append([title, author, year])
                break
            print('md5:', _.md5)

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
                else:
                    print('unhandled href:', href)

            if ext:
                print('extension:', ext)
                print('download:', href)

                save_path = f_dir + "".join([c for c in title if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
                save_path = save_path + ' (by ' + "".join([c for c in author if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
                save_path = save_path + ' ' + "".join([c for c in year if c.isalpha() or c.isdigit() or c == ' ']).rstrip() + ')' + ext

                if not os.path.exists(save_path):
                    print('saving file:', save_path)
                    try:
                        urllib.request.urlretrieve(href, save_path)
                    except Exception as e:
                        print(e)
                        failed.append([title, author, year, href])
                else:
                    print('-- skipping:', href)
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
    print('    Written by Benjamin Jack Cullen.')
    print('')
    print('Command line arguments:\n')
    print('    -h      Displays this help message.')
    print('    --all   Searches every page.')
    print('    --page  Specify page number. (Use if page quantity exceeds a max using --all, instead use --page).')
    print('    -k      Keyword. Specify keyword(s) to search for.')
    print('    -u      Update. Update an existing library genesis directory.')
    print('')
    print('    Example: library_genesis --all -k human')
    print('    Example: library_genesis --page 1 -k human')
    print('')

# Parse arguments
run_function = ()
search_q = ''
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

    # update
    elif _ == '-u':
        banner()
        print('[Update Library]')
        search_q = []
        for dirname, dirnames, filenames in os.walk('./library_genesis'):
            for subdirname in dirnames:
                fullpath = os.path.join(subdirname)
                search_q.append(fullpath)
                print('    [update]', fullpath)
        dl_method = 'all_update'
        i_query = 0
        for _ in search_q:
            i_page = 1
            print('[updating]', _)
            compile_ids(dl_method, search_q[i_query], i_page)
            i_query += 1
        break
    i += 1

# Function selection
if run_function == 0:
    i = 0
    for _ in sys.argv:

        dl_method = ''

        # every page
        if _ == '--all':
            dl_method = 'all'
            i_page = 1
            break

        # specific page
        elif _ == '--page':
            dl_method = 'page'
            i_page = int(sys.argv[i + 1])
            print('Page:', i_page)
            break

        i += 1

    if dl_method:
        search_q = search_q.strip()
        compile_ids(dl_method, search_q, i_page)

        # Summary
        print('')
        print('-' * 100)
        if failed:
            print('\nmay have failed (check to confirm):')
            for _ in failed:
                print('   ', _)
            print('may have failed:', len(failed))

        print('-- completed.')
    else:
        print('-- use -h for help.')
print('\n\n')
