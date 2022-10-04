[LIBRARY GENESIS DOWNLOAD TOOL]

Intended as an intelligence tool for archiving information in an uncertain world.
Downloads every book on every page for keyword specified.
Written by Benjamin Jack Cullen.

Command line arguments:

-h      Displays this help message.
-k      Keyword. Specify keyword(s).
-u      Update. Update an existing library genesis directory.
        Each directory name in an existing ./library_genesis directory will
        be used as a keyword during update process.

Example: library_genesis -k human
Example: library_genesis -u


Requirements:
Developed and tested against Python 3.10.1 on Windows 10.

Uses my modified pylibgen module with my modified pylibgen constants.py file:
Copy and paste modified pylibgen.py and constants.py into python directory where applicable.

Non developers may use library_genesis.exe. (portable).

I aslo highly recommend kiwix_serve.exe from:
https://www.kiwix.org/en/downloads/kiwix-serve/

And zim files to compliment kiwix-serve:
https://download.kiwix.org/zim/

Extras:
Query:
    Query a local file/directory(library_genesis directory) for information, like the vampire dude from Blade.
    Intended for use with a local pdf library. Queries the library and saves results to file.

create_sol_library.py:
    Intended for use with kiwix. Runs kiwix manage as a subprocess to auto compile a library.xml from a bag
    of ZIM files.