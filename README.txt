[LIBRARY GENESIS DOWNLOAD TOOL]

Intended as an intelligence tool for archiving information in an uncertain world.
Written by Benjamin Jack Cullen.

Command line arguments:

-h      Displays this help message.
--all   Searches every page.
--page  Specify page number. (Use if page quantity exceeds a max using --all, instead use --page).
-k      Keyword. Specify keyword(s) to search for.
-u      Update. Update an existing library genesis directory.

Example: library_genesis --all -k human
Example: library_genesis --page 1 -k human


Requirements:
Developed and tested against Python 3.10.1 on Windows 10.

Uses my modified pylibgen module with my modified pylibgen constants.py file:
Copy and paste modified pylibgen.py and constants.py into python directory where applicable.

Non developers may use library_genesis.exe. (portable).

I aslo highly recommend kiwix_serve.exe from:
https://www.kiwix.org/en/downloads/kiwix-serve/

And zim files to compliment kiwix-serve:
https://download.kiwix.org/zim/

