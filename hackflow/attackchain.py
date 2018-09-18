from base import coroutine, bcolors


InfoGatherStack = ['CheckSystemCommand', 'ScanItCommand']
ExploitStack = ['ByPassItCommand', 'PocItCommand', 'DeployHostCommand']
CleanStack = []


@coroutine
def InfoGather(target):
    """
        get information, eg: subdomain, port, or something
    """
    while True:
        action = yield
        actioname = action.__class__.__name__
        if actioname in InfoGatherStack:
            print(f"{bcolors.HEADER} {actioname.split('Command')[0]} {bcolors.ENDC}", end="")
            action.execute()
        else:
            target.send(action)


@coroutine
def PreScan(target):
    """
        scan target get your want, eg: dirbuster, sql injection, xss detection, weak password
    """
    while True:
        action = yield
        actioname = action.__class__.__name__

        if actioname in InfoGatherStack:
            print("Now we are ready to scan target {}".format(actioname))
        else:
            target.send(action)


@coroutine
def GainAccess(target):
    """
        exploit it and get access
        may be lot of command :  bypass waf, poc try, and so on.
    """
    while True:
        action = yield
        actioname = action.__class__.__name__

        if actioname in ExploitStack:
            print("Now we are ready to gain access target {}".format(actioname))
        else:
            target.send(action)


@coroutine
def ElevatePrivilege(target):
    """
        from comman user to root
    """
    while True:
        action = yield
        actioname = action.__class__.__name__

        if actioname in ExploitStack:
            print("Now we are try to elevate privilege from target {}".format(actioname))
        else:
            target.send(action)


@coroutine
def CleanAndEscape(target):
    """
        from comman user to root
    """
    while True:
        action = yield
        actioname = action.__class__.__name__

        if actioname in ExploitStack:
            print("Now we are ready to clean history and leave target {}".format(actioname))
        else:
            target.send(action)


@coroutine
def AutoReport():
    while True:
        action = yield
        print('end of chain, no coroutine for {}'.format(action))
