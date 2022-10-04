import os
import subprocess
import unicodedata

info = subprocess.STARTUPINFO()  # Subprocess Control
info.dwFlags = 1
info.wShowWindow = 0


def NFD(text):
    return unicodedata.normalize('NFD', text)


def noCase(text):
    return NFD(NFD(text).casefold())


library = []
print('')
var_input_0 = input('enter library path: ')
if os.path.exists(var_input_0):
    print('-- path exists')

    for dirName, subdirList, fileList in os.walk(var_input_0):
        for fname in fileList:
            if fname.endswith(noCase('.zim')):
                fullpath = os.path.join(var_input_0, dirName, fname)
                print(fullpath)
                library.append(fullpath)

if library:
    print('-- compiled list of library files')

    print('-- looking for kiwix-manage.exe')
    if os.path.exists('./kiwix-manage.exe'):
        print('-- found kiwix-manage.exe')

        for _ in library:
            cmd = 'kiwix-manage.exe sol_library.xml add "' + str(_) + '"'
            print(cmd)
            xcmd = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, startupinfo=info)
            while True:
                output = xcmd.stdout.readline()
                if output == '' and xcmd.poll() is not None:
                    break
                if output:
                    print(str(output.decode("utf-8").strip()))
                else:
                    break
            rc = xcmd.poll()

else:
    print('-- could not find zim files in location specified')
