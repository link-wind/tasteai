import re

def split_pieces(text):
    return re.findall(r"[A-Za-z]+|[0-9]{1,3}|\s+|[^A-Za-z0-9\s]", text)
