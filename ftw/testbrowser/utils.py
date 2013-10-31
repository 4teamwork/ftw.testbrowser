import re


def normalize_spaces(text):
    return re.sub(r'[\s\xa0]{1,}', ' ', text).strip()
