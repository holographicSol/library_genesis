import codecs
import os
import unicodedata
import pdfplumber
import pyprogress
import colorama

r_file = ''
query = ''
path = ''
pdf_max = 0
i_count_total_pages = 0
page_start = ()
page_end = ()
thread = ''
match = 0
total_matches = 0
verbosity = False
multiplier = pyprogress.multiplier_from_inverse_factor(factor=50)


def NFD(text):
    return unicodedata.normalize('NFD', text)


def noCase(text):
    return NFD(NFD(text).casefold())


def search_library(path='', query=''):
    global i_count_total_pages
    global match, total_matches
    try:

        # preliminary enumeration
        pdf_page_max = int
        with pdfplumber.open(path) as pdf:
            page_n = pdf.pages
            pdf_page_max = int(str(page_n[-1]).replace('<Page:', '').replace('>', ''))
        pdf.close()

        # actual parser
        with pdfplumber.open(path) as pdf:
            page_n = pdf.pages

            for _ in page_n:

                i_count_total_pages += 1

                try:
                    page_cur = str(_).replace('<Page:', '')
                    page_cur = int(page_cur.replace('>', ''))
                    page_ = pdf.pages[page_cur]
                    page_txt = page_.extract_text()
                    page_txt = str(page_txt).strip()
                    page_txt = page_txt.split('\n')
                    var = False
                    for _ in page_txt:
                        if noCase(query.lower().strip()) in noCase(_.lower().strip()):
                            var = True
                            match += 1
                            total_matches += 1

                            if not os.path.exists(r_file):
                                open(r_file, 'w').close()

                            with codecs.open(r_file, 'a', encoding='utf8') as fo:
                                fo.write(str('-'*150) + '\n')
                                fo.write('[MATCH] ' + str(total_matches) + '\n')
                                fo.write('[FILE] ' + str(path) + '\n')
                                fo.write('[PAGE] ' + str(i_count_total_pages) + '\n')
                                fo.write('[CONTEXT] ' + str(_) + '\n')
                            fo.close()

                        elif var is True:

                            with codecs.open(r_file, 'a', encoding='utf8') as fo:
                                fo.write(str(_) + '\n')
                            fo.close()

                            if '.' in _:
                                var = False

                except Exception as e:
                    # print('[ERROR 0]', e)
                    pass

                pyprogress.progress_bar(part=int(i_count_total_pages), whole=int(pdf_page_max),
                                        pre_append='[SCANNING] ',
                                        append=str(' ' + str(i_count_total_pages) + '/' + str(pdf_page_max) +
                                                   ' (matches: ' + colorama.Style.BRIGHT + colorama.Fore.LIGHTCYAN_EX +
                                                   str(match) + colorama.Style.RESET_ALL + ')'),
                                        encapsulate_l='|',
                                        encapsulate_r='|',
                                        encapsulate_l_color='LIGHTCYAN_EX',
                                        encapsulate_r_color='LIGHTCYAN_EX',
                                        progress_char=' ',
                                        bg_color='GREEN',
                                        factor=50,
                                        multiplier=multiplier)

    except Exception as e:
        print('')
        print('[ERROR 1]', e)
    print('')
