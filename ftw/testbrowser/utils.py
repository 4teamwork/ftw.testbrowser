import re


def normalize_spaces(text):
    return re.sub(r'\s{1,}', ' ', text).strip()
