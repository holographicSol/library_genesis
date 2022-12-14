import os
import datetime
import time

import colorama
import unicodedata
import pdfplumber
import subprocess
import codecs
import pyprogress


info = subprocess.STARTUPINFO()
info.dwFlags = 1
info.wShowWindow = 0
main_pid = int()


query = 'population control'
path = './library_genesis/club of rome'

pdf_max = 0
pdf_list = []
threads = 8

if not os.path.exists('./tmp'):
    os.mkdir('./tmp')
if not os.path.exists('./research'):
    os.mkdir('./research')


def check_clear():
    global query
    for dirName, subdirList, fileList in os.walk('./tmp'):
        for fname in fileList:
            fullpath = os.path.join(dirName, fname)
            if fname.endswith('.txt'):

                f_exists = False

                if fname.startswith('research_completed_'+query):
                    f_exists = True
                elif fname.startswith('research_'+query):
                    f_exists = True
                elif fname.startswith('research_match_'+query):
                    f_exists = True

                if f_exists is True:
                    while os.path.exists(fullpath):
                        try:
                            os.remove(fullpath)
                        except Exception as e:
                            # print(e)
                            pass


def enumerate():
    print('-- enumerate')
    global pdf_max
    global pdf_list

    for dirName, subdirList, fileList in os.walk(path):
        for fname in fileList:
            if fname.endswith('.pdf'):
                pdf_max += 1
                pdf_list.append(os.path.join(dirName, fname))


def get_pages():
    i_book = 0
    i_match = 0

    for _ in pdf_list:

        tmp_i_match = 0
        i = 0
        while i < threads:
            if os.path.exists('./tmp/research_match_' + query + '_' + str(i) + '.txt'):
                with open('./tmp/research_match_' + query + '_' + str(i) + '.txt', 'r') as fo:
                    for line in fo:
                        line = line.strip()
                        if line.isdigit():
                            tmp_i_match += int(line)
                fo.close()
            i += 1
        i_match = tmp_i_match

        i_book += 1
        print('-'*150)
        print('[RESEARCHING] ' + str(query))
        print('[PROGRESS] ' + str(i_book) + ' / ' + str(len(pdf_list)))
        print('[CURRENT BOOK] ' + str(_))
        if i_match == 0:
            print('[MATCHES] ' + colorama.Style.BRIGHT + colorama.Fore.YELLOW + str(i_match) + colorama.Style.RESET_ALL)
        elif i_match > 0:
            print('[MATCHES] ' + colorama.Style.BRIGHT + colorama.Fore.GREEN + str(i_match) + colorama.Style.RESET_ALL)
        with pdfplumber.open(_) as pdf:
            page_n = pdf.pages
            pdf_page_max = int(str(page_n[-1]).replace('<Page:', '').replace('>', ''))
        pdf.close()
        page_max_divide = round(pdf_page_max / threads)
        page_group_start = []
        page_group_end = []
        i_page_group_end = page_max_divide
        i = 1
        while i_page_group_end < pdf_page_max:
            page_group_start.append(((i-1) * page_max_divide)+1)
            i_page_group_end = (i * page_max_divide)
            if i_page_group_end < pdf_page_max:
                page_group_end.append(i_page_group_end)
            else:
                i_page_group_end = pdf_page_max
                page_group_end.append(i_page_group_end)
            i += 1
        i = 0
        i_xcmd = []
        for page_group_starts in page_group_start:
            cmd = './research.exe ' + str(i) + ' "' + _ + '" ' + str(page_group_start[i]) + ' ' + str(page_group_end[i]) + ' "' + query + '"'
            xcmd = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, startupinfo=info)
            i_xcmd.append(xcmd)
            time.sleep(0.4)
            i += 1
        completed = False
        i_completed = 0
        i_page_count = []
        for _ in page_group_start:
            i_page_count.append(0)
        while completed is False:
            i = 0
            for _ in page_group_start:
                if os.path.exists('./tmp/research_completed_' + query + '_' + str(i) + '.txt'):
                    i_completed += 1
                    while os.path.exists('./tmp/research_completed_' + query + '_' + str(i) + '.txt'):
                        try:
                            os.remove('./tmp/research_completed_' + query + '_' + str(i) + '.txt')
                            break
                        except Exception as e:
                            pass
                if os.path.exists('./tmp/research_' + query + '_' + str(i) + '_ipage_.txt'):
                    with open('./tmp/research_' + query + '_' + str(i) + '_ipage_.txt', 'r') as fo:
                        for line in fo:
                            line = line.strip()
                            i_page_count[i] = int(line)
                    fo.close()
                    while os.path.exists('./tmp/research_' + query + '_' + str(i) + '_ipage_.txt'):
                        try:
                            os.remove('./tmp/research_' + query + '_' + str(i) + '_ipage_.txt')
                            break
                        except Exception as e:
                            pass
                page_count = 0
                for _ in i_page_count:
                    page_count += _
                if int(page_count) <= pdf_page_max:
                    pyprogress.progress_bar(part=int(page_count), whole=int(pdf_page_max),
                                            pre_append='[SCANNING] ',
                                            append=str(' ' + str(page_count) + '/' + str(pdf_page_max)),
                                            encapsulate_l='|',
                                            encapsulate_r='|',
                                            encapsulate_l_color='LIGHTCYAN_EX',
                                            encapsulate_r_color='LIGHTCYAN_EX',
                                            progress_char=' ',
                                            bg_color='GREEN',
                                            factor=50,
                                            multiplier=multiplier)
                if i_completed >= len(page_group_start)-1:
                    pyprogress.progress_bar(part=int(pdf_page_max), whole=int(pdf_page_max),
                                            pre_append='[SCANNING] ',
                                            append=str(' ' + str(pdf_page_max) + ' / ' + str(pdf_page_max)),
                                            encapsulate_l='|',
                                            encapsulate_r='|',
                                            encapsulate_l_color='LIGHTCYAN_EX',
                                            encapsulate_r_color='LIGHTCYAN_EX',
                                            progress_char=' ',
                                            bg_color='GREEN',
                                            factor=50,
                                            multiplier=multiplier)
                    print('')
                    for i_xcmds in i_xcmd:
                        i_xcmds.poll()
                    completed = True
                    break
                time.sleep(0.05)
                i += 1
        # time.sleep(3)
        i = 0
        for _ in page_group_start:

            if os.path.exists('./tmp/research_' + query + '_' + str(i) + '.txt'):

                with codecs.open('./tmp/research_' + query + '_' + str(i) + '.txt', 'r', encoding='utf8') as fo:
                    for line in fo:
                        line = line.strip()
                        with codecs.open('./research/research_' + query + '.txt', 'a', encoding='utf8') as fo2:
                            fo2.write(line + '\n')
                        fo2.close()

                fo.close()

                with open('./tmp/research_' + query + '_' + str(i) + '.txt', 'w') as fo:
                    fo.close()

            i += 1


t1 = datetime.datetime.now()
check_clear()
enumerate()
get_pages()
t2 = datetime.datetime.now()
print('')
print('[COMPLETE]')
time.sleep(3)
print('[CLEANING]')
check_clear()
print('[INITIATION TIME]', t1)
print('[TIME COMPLETED]', t2)
print('')
