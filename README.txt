[LIBRARY GENESIS DOWNLOAD & RESEARCH TOOL]

Intended as an intelligence tool for archiving information in an uncertain world.
Downloads every book on every page for keyword specified.
Also provides function to compile and save a list of reading material relative to search terms(s)
to aid and assist in research when dealing with large libraries.

Written by Benjamin Jack Cullen.

Command line arguments:

-h             Displays this help message.

[DOWNLOAD OPTIONS]
-k             Keyword. Specify keyword(s).

-u             Update. Update an existing library genesis directory.
               Each directory name in an existing ./library_genesis directory will
               be used as a keyword during update process.

-p             Page. Specify start page number.

--retry-max    Max number of retries for an incomplete download.
               Can be set to no-limit to keep trying if an exception is encountered.
               Default is 3. If --retry-max unspecified then default value will be used.
               Using no-limit is always recommended. If issues are encountered then specify number.

--search-mode  Specify search mode.
               --search-mode title
               --search-mode author
               --search-mode isbn
               Default is title. If --search-mode unspecified then default value will be used.

--limit-speed  Throttle download speed. Specify bytes per second in digits.
               1024 bytes = 100KB. Use a calculator if you need it.
               Example: --limit-speed 1024
               Default is 0 (unlimited). If --limit-speed is unspecified then default value will be used.

[RESEARCH OPTIONS]
--research-mode    Specify research mode. Specify file/directory to research.
                   --research-mode file
                   --research-mode library
-f                 Specify file to research. Used with --research-mode file.
-d                 Specify directory to research. Used with --research-mode library.
--research         Specify research query. Used with --research-mode.

[EXAMPLE USAGE]
	library_genesis --download-mode -k human
	library_genesis --download-mode -p 3 -k human
	library_genesis --download-mode --limit-speed 1024 --retry-max no-limit --search-mode title -k human
	library_genesis --download-mode -u
	library_genesis --research-mode library -d ./library_genesis/ --research 1984


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
    Intended for use with a local pdf library. Queries the library and saves results to file for
    later reference.

create_sol_library.py:
    Intended for use with kiwix. Runs kiwix-manage.exe as a subprocess to auto compile a library.xml from a bag
    of ZIM files. The compiled .xml file can then be used with kiwix-serve.exe.