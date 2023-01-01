--------------------------------------------------------------------------------------------------------

 [LIBRARY GENESIS DOWNLOAD & RESEARCH TOOL]


 [DESCRIPTION]
              Downloads and researches a digital library.
              Intended as an intelligence tool for archiving information in an uncertain world.
              Written by Benjamin Jack Cullen.


 [DOWNLOAD]

   [-h]              [Displays this help message]
   [-k]              [Keyword. Specify keyword(s). Should always be the last argument]
                     [Anything after -k will be treated as a keyword(s). (MUST be specified last)]
   [-p]              [Page. Specify start page number. Default is 0]
   [-u]              [Update. Update an existing library genesis directory]
                     [Each directory name in an existing ./library_genesis directory will
                      be used as a search term during update process. (EXPERIMENTAL)]
   [--download-mode] [Instructs program to run in download mode]
   [--retry-max]     [Max number of retries for an incomplete download]
                     [Can be set to no-limit to keep trying if an exception is encountered]
                     [Default is 3. Using no-limit is always recommended]
                     [If issues are encountered then specify number]
   [--search-mode]   [Specify search mode. Default is title if --search-mode is unspecified]
                     [--search-mode title]
                     [--search-mode author]
                     [--search-mode isbn]
   [--throttle]      [Throttle download speed. Specify bytes per second in digits]
                     [1024 bytes = 1KB. Use a calculator if you need it]
                     [Example: --throttle 1024]
                     [Default is 0 (unlimited)]


 [RESEARCH]

   [--research-mode] [Specify research mode. Instructs program to run in research mode]
   [-t]              [Threads. Specify number of files that will be processed simultaneously]
                     [Default is 2 if -t is unspecified]
   [-d]              [Specify directory to research. Used with --research-mode]
   [--research]      [Specify research query. Used with --research-mode]
                     [This argument MUST be specified last]


 [EXAMPLES]

    library_genesis --download-mode -k human
    library_genesis --download-mode -p 3 -k human
    library_genesis --download-mode --throttle 1024 --retry-max no-limit --search-mode title -k human
    library_genesis --download-mode -u
    library_genesis --research-mode -d './library_genesis' --research 1984
    library_genesis --research-mode -t 8 -d './library_genesis' --research 1984

--------------------------------------------------------------------------------------------------------

 [DEVELOPER]

   [PYLIBGEN]
   I have included my modified constants.py and my modified pylibgen.py as the mirrors in the pylibgen version
   available using pip uses outdated mirrors. I hope the creator of pylibgen does not mind this update
   (otherwsise pylibgen will not work due to pylibgen's mirrors being outdated which I have fixed).

   [PYTHON]
   Python 3.10.1

   [OS]
   Created and tested on: Windows 10


 [EXECUTABLE]
 https://drive.google.com/drive/folders/1UaJP2oGpcz6Fo3t7pUUr910Xe7QXSCJw?usp=share_link