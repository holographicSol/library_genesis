import os
import codecs
import time
from datetime import datetime, timedelta


def GetTime(_sec):
    sec = timedelta(seconds=int(_sec))
    d = datetime(1, 1, 1) + sec
    return str("%d:%d:%d:%d" % (d.day-1, d.hour, d.minute, d.second))


def convert_bytes(num):
    """ bytes for humans """

    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return str(num)+' '+x
        num /= 1024.0


def files_enumerate(path='', exclude=[]):
    pdf_max = 0
    pdf_list = []
    for dirName, subdirList, fileList in os.walk(path):
        for fname in fileList:
            if not fname.endswith(tuple(exclude)):
                pdf_max += 1
                pdf_list.append(os.path.join(dirName, fname))
                print('[ENUMERATING] Files: ' + str(pdf_max), end='\r', flush=True)
    print('\n')
    return pdf_list


def covers_enumerate(path=''):
    pdf_max = 0
    files = []
    total_bytes = 0
    for dirName, subdirList, fileList in os.walk(path):
        for fname in fileList:
            if fname.endswith('.jpg'):
                pdf_max += 1
                fullpath = os.path.join(dirName, fname)
                sz_bytes = os.path.getsize(fullpath)
                total_bytes += sz_bytes
                files.append([fullpath, sz_bytes])
                print('[COVERS] Files: ' + str(pdf_max), end='\r', flush=True)
    print('\n')
    return files, total_bytes


def display_covers_enumerate():
    cover_data = covers_enumerate(path='./library_genesis')
    print('[COVERS] ' + str(len(cover_data[0])))
    print('[BYTES] ' + str(cover_data[1]))
    print('[SIZE] ' + str(convert_bytes(cover_data[1])))


def duplicate_enumerate(path='', files=[], exclude=[]):
    i_count = 0
    i_new_files = 0
    new_files = []
    t0 = time.time()
    len_files = len(files)
    i_compare = 0
    for _ in files:

        print('[PROCESSED] [' + str(i_count) + ' / ' + str(len_files) + '] [COMPARING] [' + str(i_compare) + ' / ' + str(len_files) + '] [TIME] [' + str(GetTime(time.time() - t0)) + ']', end='\r', flush=True)

        with open(_, 'rb') as fo:
            fo_read = fo.read()

            for dirName, subdirList, fileList in os.walk(path):
                for fname in fileList:
                    second_fullpath = os.path.join(dirName, fname)

                    with open(second_fullpath, 'rb') as second_fo:
                        second_fo_read = second_fo.read()

                        if fo_read == second_fo_read:
                            new_files.append([_, second_fullpath])

                            i_new_files += 1

                    i_compare += 1
                    print('[PROCESSED] [' + str(i_count) + ' / ' + str(len_files) + '] [COMPARING] [' + str(i_compare) + ' / ' + str(len_files) + '] [TIME] [' + str(GetTime(time.time() - t0)) + ']', end='\r', flush=True)
            i_count += 1
    print('\n')
    return files, i_new_files


def display_clones():
    print('')
    exclude = ['.jpg']
    files = files_enumerate('./library_genesis', exclude=exclude)
    d = duplicate_enumerate(path='./library_genesis', files=files)
    for _ in d[0]:
        print('[CLONE] ', _)
    print('[FILE CONTENT BYTES MATCH] ' + str(len(d[0])))


display_clones()
