[LIBRARY GENESIS DOWNLOAD TOOL]

Intended as an intelligence tool for archiving information in an uncertain world.
Downloads every book on every page for keyword specified.
Written by Benjamin Jack Cullen.

Command line arguments:

-h             Displays this help message.
-k             Keyword. Specify keyword(s).
-u             Update. Update an existing library genesis directory.
               Each directory name in an existing ./library_genesis directory will
               be used as a keyword during update process.
-p             Page. Specify start page number.
--retry-max    Max number of retries for an incomplete download.
               Can be set to no-limit to keep trying if an exception is encountered.
               Default is 3. If --retry-max unspecified then default value will be used.
--search-mode  Specify search mode.
               --search-mode title
               --search-mode author
               --search-mode isbn
               Default is title. If --search-mode unspecified then default value will be used.

Example: library_genesis -k human
Example: library_genesis -p 3 -k human
Example: library_genesis --retry-max no-limit --search-mode title -k human
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
    Query the archive (library_genesis directory) for information, like the vampire dude from Blade.
    Intended for use with a local pdf library. Queries the library and saves results to file.

create_sol_library.py:
    Intended for use with kiwix. Runs kiwix-manage.exe as a subprocess to auto compile a library.xml from a bag
    of ZIM files. The compiled .xml file can then be used with kiwix-serve.exe.