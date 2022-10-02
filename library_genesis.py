"""
Written by Benjamin Jack Cullen aka Holographic_Sol
"""
import os
from pylibgen import Library
import requests
from bs4 import BeautifulSoup
import urllib.request

failed = []
ids_ = []
cloud_flare_found_ = []


def enter_query():
    search_q = input('download using search query: ')
    f_dir = './library_genesis/' + search_q + '/'
    compile_ids(f_dir, search_q)


def compile_ids(f_dir, search_q):
    i_page = 1
    add_page = True
    while add_page is True:
        ids = []
        l = Library()
        try:
            ids = l.search(query=search_q, mode='title', page=i_page, per_page=100)
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

    lookup_ids = l.lookup(ids_)
    print('found:', len(ids_), 'books')

    if ids_:
        user_dl_books = input('would you like to download?(y/n): ')
        if user_dl_books == 'y' or user_dl_books == 'Y':
            if not os.path.exists(f_dir):
                os.mkdir(f_dir)
            dl_books(f_dir, lookup_ids)


def dl_books(f_dir, lookup_ids):
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
            if year == '':
                year = str(i) + '_unknown_year'
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
            ext = ''
            for link in soup.find_all('a'):
                href = (link.get('href'))

                # if 'cloudflare' in href:

                if href.endswith('.pdf'):
                    ext = '.pdf'
                    break
                elif href.endswith('.djvu'):
                    ext = '.djvu'
                    break
                elif href.endswith('.epub'):
                    ext = '.epub'
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
                    if href.endswith(tuple(['.pdf', '.djvu', '.epub', '.azw3', '.mobi'])):
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


enter_query()

print('-' * 100)
if failed:
    print('\nmay have failed (check to confirm):')
    for _ in failed:
        print('   ', _)
    print('may have failed:', len(failed))

print('-- completed.')
