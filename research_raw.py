""" Written by Benjamin Jack Cullen

Codename: Research

Description:
    Reads file X looking for a string which if found will be written to file.

"""

import os
import sys
import unicodedata
import PyPDF2

from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
import io


def NFD(text):
    return unicodedata.normalize('NFD', text)


def noCase(text):
    return NFD(NFD(text).casefold())


def check_make_paths(search_str='', thread_n=''):
    """ make directory and file if not exists """

    if not os.path.exists('./research/' + str(search_str)):
        os.mkdir('./research/' + str(search_str))
    if not os.path.exists('./research/' + str(search_str) + '/' + str(search_str) + '_' + str(thread_n) + '.txt'):
        open('./research/' + str(search_str) + '/' + str(search_str) + '_' + str(thread_n) + '.txt', 'w').close()


def results_to_file(file_in='', search_str='', thread_n=''):
    """ append a result to relevant file """

    check_make_paths(search_str=search_str, thread_n=thread_n)
    try:
        with open('./research/' + str(search_str) + '/' + str(search_str) + '_' + str(thread_n) + '.txt', 'a') as fo:
            fo.write(str(file_in) + '\n')
    except Exception as e:
        print(e)


def str_in_pdf(file_in='', _search_str=''):
    """ look for search_str in file """

    match = False
    try:

        pdf_file = open(file_in, 'rb')
        pdf_reader = PyPDF2.PdfFileReader(pdf_file, strict=False)
        pages = pdf_reader.numPages
        for pageNum in range(pages):
            page_text = pdf_reader.getPage(pageNum).extractText()
            if _search_str in noCase(page_text):
                match = True
                break
    except Exception as e:
        print(e)
    return match


def main(file_in='', search_str='', thread_n=''):

    search_str = noCase(search_str)
    if str_in_pdf(file_in=file_in, _search_str=search_str) is True:
        results_to_file(file_in=file_in, search_str=search_str, thread_n=thread_n)


_file_in = ''
_thread_n = ''
_search_str = ''
i = 0
for _ in sys.argv:
    if i == 1:
        _file_in = _
    elif i == 2:
        _thread_n = _
    elif i >= 3:
        if _search_str == '':
            _search_str = _
        else:
            _search_str = _search_str + ' ' + _
    i += 1

# uncomment to check sys.argv input
# print('_file_in:', _file_in)
# print('_thread_n:', _thread_n)
# print('_search_str:', _search_str)

if _file_in != '':
    if _search_str != '':
        main(file_in=_file_in, thread_n=_thread_n, search_str=_search_str)
