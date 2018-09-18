import time
import os, sys 
from contextlib import contextmanager

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def coroutine(func):
    def start(*args, **kwargs):
        cr = func(*args, **kwargs)
        next(cr)
        return cr
    return start

def timeit(func):

    def count(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        count._time = time.time() - start
        return res
    return count

@contextmanager
def suppress_stdout():
    try:
        stdout, sys.stdout = sys.stdout, open(os.devnull, 'w')
        yield
    finally:
        sys.stdout = stdout