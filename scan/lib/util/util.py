#!/usr/bin/python

"""
    Util Fuction
    example:
        text clean
        html parser output
"""


def md5sumfile(file_full_path):
    if(os.path.isfile(file_full_path)):
        return hashlib.md5(open(file_full_path, 'rb').read()).hexdigest()
    else:
        return None


def sha1sumfile(file_full_path):
    if(os.path.isfile(file_full_path)):
        return hashlib.sha1(open(file_full_path, 'rb').read()).hexdigest()
    else:
        return None
