#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" scholar_dl.py: Quick script to download papers from Google Scholar.

Examples:
    $ python3 scholar_dl.py --help
    $ python3 scholar_dl.py $PAPER_NAME
    $ python3 scholar_dl.py --from-file paper_list.txt --bib-output references.bib

Requires:
    Packages 'scholarly' and 'BeautifulSoup' from pip3.
"""
from sys import stderr
from sys import exit
import argparse
import string
import requests
import random
from functools import partial
import time

import scholarly
from scholarly import _get_page

printerr = partial(print, file=stderr, flush=True)



class PdfTooSmallError(Exception):
    """ Raise if downloaded pdf is too small."""
    pass


def fuzzy_1_in_2(str1, str2):
    """ Fuzzy match if str1 is a sub-string of str2."""
    def cleanup(text):
        ascii_only = filter(lambda i: i in string.ascii_letters, text)
        return ''.join(list(ascii_only)).lower()
    return cleanup(str1) in cleanup(str2)



def download_pdf(pdf_url, title):
    """ Download and save paper as {title}.pdf."""

    # Handle occasional strange format:
    if pdf_url[0:26] == 'https://scholar.google.com':
        pdf_url = pdf_url[26:]

    # Download and check length.
    pdf = requests.get(pdf_url, allow_redirects=True)
    if len(pdf.content) < 10000:
        raise PdfTooSmallError

    # Write to file.
    with open(title + '.pdf', 'wb') as f:
        f.write(pdf.content)



def get_first_paper_info(search_str):
    """ Get paper information from Google Scholar."""
    print("Searching for: ", search_str)
    search = scholarly.search_pubs_query(search_str)
    first_paper = next(search)
    title = first_paper.bib['title']

    time.sleep(random.uniform(2, 4))
    bibtex = _get_page(first_paper.url_scholarbib)

    if not fuzzy_1_in_2(title, search_str):
        printerr("%% ERROR\t\t TITLE NOT IN SEARCH - MAY BE WRONG PAPER")

    try:
        pdf_url = first_paper.bib['eprint']
    except KeyError:
        printerr("ERROR\t\t PDF URL NOT FOUND: " + title)
        pdf_url = None

    return title, bibtex, pdf_url



def retrive_paper(search_str, bibtex_file=None):
    """ Save paper, print bibtex (to file if provided)."""

    # Try to download from scholar.
    try:
        title, bibtex, pdf_url = get_first_paper_info(search_str)
    except StopIteration:
        printerr("ERROR: COULD NOT ACCESS. CAPTCHA or paper does not exist.")
        exit(1)

    # Save to bibtex file and print.
    print(bibtex)
    if bibtex_file:
        with open(bibtex_file, "a") as f:
            f.write(bibtex)

    # Try to download PDF.
    try:
        if pdf_url:
            download_pdf(pdf_url, title)
    except requests.exceptions.ConnectionError:
        printerr("ERROR\t\t INVALID PDF URL: " + pdf_url)
    except PdfTooSmallError:
        printerr("ERROR\t\t PDF MAY BE TOO SMALL: " + title)
    print("")



def main(args):
    if args.search:
        retrive_paper(args.search, args.bib_output)
    elif args.from_file:
        try:
            with open(args.from_file, 'r') as f:
                searches = f.read()
            for search in searches.split('\n'):
                retrive_paper(search, args.bib_output)
                if args.slow:
                    wait = random.uniform(50, 100)
                    print(f"Waiting {wait:4.0f} seconds")
                    time.sleep(wait)
        except FileNotFoundError:
            printerr("ERROR:\t\t File Not Found.")
    else:
        parser.print_help()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Papers from Google Scholar.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--search", type=str,
                        help="Enter a single paper search query.")
    group.add_argument("--from-file", type=str,
                        help="Read search strings, one per line from file.")
    parser.add_argument("--bib-output", type=str,
                        help="Append the BibTex output to a file.")
    parser.add_argument("--slow", action="store_true", default=False,
                        help="Go much slower in an attempt to avoid CAPTCHAs.")
    args = parser.parse_args()
    main(args)
