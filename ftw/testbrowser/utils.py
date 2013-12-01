from contextlib import contextmanager
import logging
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
