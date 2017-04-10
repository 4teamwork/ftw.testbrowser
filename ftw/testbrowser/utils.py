from contextlib import contextmanager
from ftw.testbrowser.parser import TestbrowserHTMLParser
import logging
import lxml
import re
import sys


def normalize_spaces(text):
    return re.sub(r'[\s\xa0]{1,}', ' ', text).strip()


@contextmanager
def verbose_logging():
    stdouthandler = logging.StreamHandler(sys.stdout)
    logging.root.addHandler(stdouthandler)
    try:
        yield
    finally:
        logging.root.removeHandler(stdouthandler)


def parse_html(html):
    return lxml.html.parse(html, TestbrowserHTMLParser())
