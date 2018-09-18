import os

class ScanItCommand(object):
    """
        Try to scan target
    """

    def __init__(self):
        print('Scan host')


class CheckSystemCommand(object):
    """
        Check environment MacOS/Unix/Windows Or Not
    """

    def __init__(self, host):
        self.host = host
    
    def execute(self):
        self.scan()
    def undo(self):
        print("Undo Command")

    def scan(self):
        print("Scanning Host: {}".format(self.host))
        os.system(f'nmap -A {self.host}')