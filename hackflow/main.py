
import os
import sys
import click


from base import timeit, bcolors
from contextlib import contextmanager
from lib import ByPassItCommand, DeployHostCommand, ReverseShellCommand,\
    ScanItCommand, TransferDataCommand, CheckSystemCommand, PocItCommand
from attackchain import InfoGather, PreScan, GainAccess, ElevatePrivilege, CleanAndEscape, AutoReport


# if os.getuid() != 0:
#     print("You need root permissions to do this!")
#     sys.exit(1)

class PentestCoroutine:

    def __init__(self):
        self.target = InfoGather(GainAccess(ElevatePrivilege(AutoReport())))

    def delegate(self, steps):
        for step in steps:
            self.target.send(step)


@click.command()
@click.option('--host', '-h', help="Your target host ip")
def main(host):
    pentest = PentestCoroutine()
    # steps = [CheckSystemCommand(), ScanItCommand(), ByPassItCommand(),
    #             ReverseShellCommand()]

    steps = [CheckSystemCommand(host)]
    pentest.delegate(steps)

    # runtime = timeit(pentest.delegate)

    # with suppress_stdout():
    #     runtime(steps)

    # print(runtime._time)


if __name__ == "__main__":
    main()
