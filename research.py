import os
import sys
import unicodedata
import pdfplumber

query = ''
path = ''
pdf_max = 0
i_count_total_pages = 0
page_start = ()
page_end = ()
thread = ''
match = 0
verbosity = False


def NFD(text):
    return unicodedata.normalize('NFD', text)


def noCase(text):
    return NFD(NFD(text).casefold())


def search_library():
    global i_count_total_pages
    global page_start, page_end, path, query, thread, match, verbosity
    try:

        if not os.path.exists('./tmp/research_' + query + '_' + thread + '.txt'):
            with open('./tmp/research_' + query + '_' + thread + '.txt', 'w', encoding='utf8') as fo:
                fo.close()

        with open('./tmp/research_' + query + '_' + thread + '.txt', 'a', encoding='utf8') as fo:

            with pdfplumber.open(path) as pdf:
                page_n = pdf.pages
                i = 0
                for _ in page_n:
                    if i >= page_start and i <= page_end:
                        i_count_total_pages += 1
                        with open('./tmp/research_' + query + '_' + thread + '_ipage_.txt', 'w') as fo2:
                            fo2.write(str(i_count_total_pages))
                        fo2.close()
                        try:
                            page_cur = str(_).replace('<Page:', '')
                            page_cur = int(page_cur.replace('>', ''))
                            page_ = pdf.pages[page_cur]
                            page_txt = page_.extract_text()
                            page_txt = str(page_txt).strip()
                            page_txt = page_txt.split('\n')
                            var = False
                            for _ in page_txt:
                                if noCase(query.lower()) in noCase(_.lower()):
                                    fo.write(''+'\n')
                                    fo.write('[FILE]  ' + str(path) + '\n')
                                    fo.write('[PAGE]  ' + str(i) + '\n')
                                    fo.write(str(_) + '\n')
                                    var = True
                                    match += 1
                                elif var is True:
                                    fo.write(str(_) + '\n')
                                    if '.' in _:
                                        var = False
                        except Exception as e:
                            print('[ERROR 0]', e)
                            print('[ERROR 0]', 'i='+str(i), 'page_cur='+str(page_cur), 'i_count_total_pages=' + str(i_count_total_pages))
                            pass
                    i += 1
    except Exception as e:
        print('[ERROR 1]', e)

    if not os.path.exists('./tmp/research_match_' + query + '_' + str(thread) + '.txt'):
        with open('./tmp/research_match_' + query + '_' + str(thread) + '.txt', 'w') as fo:
            fo.close()
    if match > 0:
        with open('./tmp/research_match_' + query + '_' + str(thread) + '.txt', 'a') as fo3:
            fo3.write(str(match)+'\n')


thread = sys.argv[1]
path = sys.argv[2]
page_start = int(sys.argv[3])
page_end = int(sys.argv[4])
verbosity = sys.argv[5]
query = sys.argv[6]

search_library()
with open('./tmp/research_completed_' + query + '_' + thread + '.txt', 'w') as fo:
    fo.close()
