--------------------------------------------------------------------------------------------------------

    [ LIBRARY GENESIS DOWNLOAD & RESEARCH TOOL ]

--------------------------------------------------------------------------------------------------------

    Intended as an intelligence tool for archiving information in an uncertain world.
    Downloads every book on every page for keyword specified.
    Also provides function to compile and save a list of reading material relative to search terms(s)
    to aid and assist in research when dealing with large libraries.
    Written by Benjamin Jack Cullen.

--------------------------------------------------------------------------------------------------------

    [ Download Arguments ]

    -h                 Displays this help message.

    -k                 Keyword. Specify keyword(s). Should always be the last argument.
                       Anything after -k will be treated as a keyword(s).

    -p                 Page. Specify start page number. Default is 0.

    -u                 Update. Update an existing library genesis directory.
                       Each directory name in an existing ./library_genesis directory will
                       be used as a search term during update process.

    --download-mode    Instructs program to run in download mode.

    --retry-max        Max number of retries for an incomplete download.
                       Can be set to no-limit to keep trying if an exception is encountered.
                       Default is 3. Using no-limit is always recommended.
                       If issues are encountered then specify number.

    --search-mode      Specify search mode. Default is title
                       --search-mode title
                       --search-mode author
                       --search-mode isbn

    --limit-speed      Throttle download speed. Specify bytes per second in digits.
                       1024 bytes = 1KB. Use a calculator if you need it.
                       Example: --limit-speed 1024
                       Default is 0 (unlimited).

--------------------------------------------------------------------------------------------------------

    [ Research Arguments ]

    --research-mode    Specify research mode. Instructs program to run in research mode.

    -d                 Specify directory to research. Used with --research-mode.

    --research         Specify research query. Used with --research-mode.

--------------------------------------------------------------------------------------------------------

    [ EXAMPLE USAGE ]

    library_genesis --download-mode -k human
    library_genesis --download-mode -p 3 -k human
    library_genesis --download-mode --limit-speed 1024 --retry-max no-limit --search-mode title -k human
    library_genesis --download-mode -u
    library_genesis --research-mode -d './library_genesis' --research 1984

--------------------------------------------------------------------------------------------------------

pylibgen:
I have included my modified constants.py and my modified pylibgen.py as the mirrors in the pylibgen version
available using pip uses outdated mirrors. I hope the creator of pylibgen does not mind this update
(otherwsise pylibgen will not work).

Python 3.10.1
Created on Platform: Windows 10

--------------------------------------------------------------------------------------------------------
