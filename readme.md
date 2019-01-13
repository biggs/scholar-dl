# Scholar DL

A package for easily downloading a list of papers and their references.


Recommended usage:
``` bash
$ pip3 install scholarly
$ alias schdl='python3 $PATH_TO_HERE/scholar_dl.py'
$ cd $DIRECTORY_TO_DOWNLOAD_TO
$ schdl --from-file list_of_papers_to_dl.txt --bib-output references.bib --slow
```

Note that occasional 503 errors are related to CAPTCHAs - try again later with
the slow option, possibly after some usual google scholar usage.
