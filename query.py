"""
Written by Benjamin Jack Cullen aka Holographic_Sol
"""
import os
import sys
import pdfplumber
import unicodedata
import codecs

print('')
print('-'*200)
print('')

search_q = ''

def NFD(text):
    return unicodedata.normalize('NFD', text)


def noCase(text):
    return NFD(NFD(text).casefold())


def banner():
    print('\n\n')
    print('[QUERY]')
    print('')


def search_f(file, query):

    with pdfplumber.open(file) as pdf:
        page_n = pdf.pages
        pdf_page_max = int(str(page_n[-1]).replace('<Page:', '').replace('>', ''))
        pdf_page_i = 0
        for _ in page_n:
            pdf_page_i += 1
            page_cur = str(_).replace('<Page:', '')
            page_cur = int(page_cur.replace('>', ''))
            try:
                page_ = pdf.pages[page_cur]

                page_txt = page_.extract_text()

                page_txt = str(page_txt).strip()
                page_txt = page_txt.split('\n')

                var = False
                i = 0
                for _ in page_txt:
                    if noCase(query) in noCase(_):
                        if not os.path.exists('./query_' + search_q + '.txt'):
                            open('./query_' + search_q + '.txt', 'w', encoding='utf8').close()
                        with open('./query_' + search_q + '.txt', 'a', encoding='utf8') as fo:
                            fo.write('-------------------------------------------------' + '\n')
                            fo.write('[FILE] ' + file + '\n')
                            fo.write('[PAGE] ' + str(pdf_page_i) + '\n')
                            fo.write('[QUERY] ' + search_q + '\n')
                        fo.close()

                        print('[SEARCHING FILE CONTENTS]', file)
                        print('[QUERY]', search_q)
                        print('[PAGE]', pdf_page_i, '/', pdf_page_max)
                        print('...')
                        try:
                            print(page_txt[i - 3])
                            with open('./query_' + search_q + '.txt', 'a', encoding='utf8') as fo:
                                fo.write(page_txt[i - 3] + '\n')
                            fo.close()
                        except:
                            pass
                        try:
                            print(page_txt[i - 2])
                            with open('./query_' + search_q + '.txt', 'a', encoding='utf8') as fo:
                                fo.write(page_txt[i - 2] + '\n')
                            fo.close()
                        except:
                            pass
                        try:
                            print(page_txt[i - 1])
                            with open('./query_' + search_q + '.txt', 'a', encoding='utf8') as fo:
                                fo.write(page_txt[i - 1] + '\n')
                            fo.close()
                        except:
                            pass
                        print(_)
                        with open('./query_' + search_q + '.txt', 'a', encoding='utf8') as fo:
                            fo.write(_ + '\n')
                        fo.close()
                        var = True
                    elif var is True:
                        print(_)
                        with open('./query_' + search_q + '.txt', 'a', encoding='utf8') as fo:
                            fo.write(_ + '\n')
                        fo.close()
                        if '.' in _:
                            print('...')
                            var = False
                            print('')
                            print('-' * 200)
                            print('')
                    i += 1
            except:
                break
    pdf.close()

    if os.path.exists('./query_' + search_q + '.txt'):
        with codecs.open('./query_' + search_q + '.txt', 'r', encoding='utf-8') as fo:
            for line in fo:
                line = line.strip()
                print(line)
        fo.close()


def search_library(path, query):
    pdf_max = 0
    for dirName, subdirList, fileList in os.walk(path):
        for fname in fileList:
            if fname.endswith('.pdf'):
                pdf_max += 1

    pdf_i = 0
    pdf_page_max = 0
    for dirName, subdirList, fileList in os.walk(path):
        for fname in fileList:
            if fname.endswith('.pdf'):
                pdf_i += 1
                fullpath = os.path.join(dirName, fname)
                try:
                    with pdfplumber.open(fullpath) as pdf:
                        page_n = pdf.pages
                        pdf_page_max = int(str(page_n[-1]).replace('<Page:', '').replace('>', ''))
                        pdf_page_i = 0
                        for _ in page_n:
                            pdf_page_i += 1
                            page_cur = str(_).replace('<Page:', '')
                            page_cur = int(page_cur.replace('>', ''))
                            try:
                                page_ = pdf.pages[page_cur]
                                page_txt = page_.extract_text()
                                page_txt = str(page_txt).strip()
                                page_txt = page_txt.split('\n')

                                var = False
                                for _ in page_txt:
                                    print('')
                                    print('-' * 200)
                                    print('')
                                    print('[PROGRESS]', pdf_i, '/', pdf_max)
                                    print('[SEARCHING FILE CONTENTS]', fullpath)
                                    print('[PAGE]', pdf_page_i, '/', pdf_page_max)
                                    print('[QUERY]', search_q)
                                    if noCase(query) in noCase(_):
                                        if not os.path.exists('./query_'+search_q+'.txt'):
                                            open('./query_'+search_q+'.txt', 'w', encoding='utf8').close()
                                        with open('./query_' + search_q + '.txt', 'a', encoding='utf8') as fo:
                                            fo.write('-------------------------------------------------' + '\n')
                                            fo.write('[FILE] '+fullpath + '\n')
                                            fo.write('[PAGE] '+str(pdf_page_i) + '\n')
                                            fo.write('[QUERY] '+search_q + '\n')
                                        fo.close()
                                        print('...')
                                        try:
                                            print(page_txt[i - 3])
                                            with open('./query_'+search_q+'.txt', 'a', encoding='utf8') as fo:
                                                fo.write(page_txt[i - 3] + '\n')
                                            fo.close()
                                        except:
                                            pass
                                        try:
                                            print(page_txt[i - 2])
                                            with open('./query_'+search_q+'.txt', 'a', encoding='utf8') as fo:
                                                fo.write(page_txt[i - 2] + '\n')
                                            fo.close()
                                        except:
                                            pass
                                        try:
                                            print(page_txt[i - 1])
                                            with open('./query_'+search_q+'.txt', 'a', encoding='utf8') as fo:
                                                fo.write(page_txt[i - 1] + '\n')
                                            fo.close()
                                        except:
                                            pass
                                        print(_)
                                        with open('./query_' + search_q + '.txt', 'a', encoding='utf8') as fo:
                                            fo.write(_ + '\n')
                                        fo.close()
                                        var = True
                                    elif var is True:
                                        print(_)
                                        with open('./query_' + search_q + '.txt', 'a', encoding='utf8') as fo:
                                            fo.write(_ + '\n')
                                        fo.close()
                                        if '.' in _:
                                            print('...')
                                            var = False
                                            print('')
                                            print('-' * 200)
                                            print('')
                            except Exception as e:
                                print(e)
                                break
                    pdf.close()
                except Exception as e:
                    print(e)

    if os.path.exists('./query_' + search_q + '.txt'):
        with open('./query_' + search_q + '.txt', 'r', encoding='utf8') as fo:
            for line in fo:
                line = line.strip()
                print(line)
        fo.close()


# search_f('./library_genesis/human rights/ Human Duties and the Limits of Human Rights Discourse (by Eric R Boot auth 2017).pdf', 'Volumes')
# search_library('./library_genesis/post-human', 'panopticon')

# Help menu
if len(sys.argv) == 2 and sys.argv[1] == '-h':
    banner()
    print('    Queries PDF files for information relative to the query.')
    print('    Written by Benjamin Jack Cullen.')
    print('')
    print('Command line arguments:\n')
    print('    -h      Displays this help message.')
    print('    -q      Query. Specify query.')
    print('    -f      File. Specify file to query.')
    print('    -d      Directory. Specify directory to query.')
    print('')
    print('    Example: query -f filepath -q human')
    print('    Example: query -d directory_path -q human')
    print('')

run_function = ()
i = 0
for _ in sys.argv:

    # keyword
    if _ == '-q':
        str_ = ''
        i_2 = 0
        for _ in sys.argv:
            if i_2 >= i+1:
                str_ = str_ + ' ' + str(_)
            i_2 += 1
        print('[Search]', str_)
        search_q = str_

    elif _ == '-f':
        dl_method = 'file'
        f_ = sys.argv[i+1]
        print('[FILE]', f_)

    elif _ == '-d':
        dl_method = 'directory'
        d_ = sys.argv[i+1]
        print('[DIRECTORY]', d_)

    i += 1

if dl_method == 'file':
    search_f(f_, search_q)
elif dl_method == 'directory':
    search_library(d_, search_q)
