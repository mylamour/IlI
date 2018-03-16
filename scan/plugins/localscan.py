import requests
import random
import re

from colorama import Fore, Back, Style

Exist = None
_ = {
    "Exist": Exist,
    "Problility":  "",
    'Summary': "",
    "Details": ""
}



USER_AGENT_LIST = [
    {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'},
    {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1'},
    {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/28.0.1469.0 Safari/537.36'},
    {'User-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/28.0.1469.0 Safari/537.36'},
    {'User-agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'},
    {'User-agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36'},
    {'User-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'},
    {'User-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'},
    {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:35.0) Gecko/20100101 Firefox/35.0'},
    {'User-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'},
    {'User-agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; Maxthon 2.0)'},
    {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML like Gecko) Maxthon/4.0.0.2000 Chrome/22.0.1229.79 Safari/537.1'},
    {'User-agent': 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.7.62 Version/11.01'},
    {'User-agent': 'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14'},
    {'User-agent': 'Opera/9.80 (Windows NT 6.1; WOW64) Presto/2.12.388 Version/12.16'},
    {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.12 Safari/537.36 OPR/14.0.1116.4'},
    {'User-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.29 Safari/537.36 OPR/15.0.1147.24 (Edition Next)'},
    {'User-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36 OPR/18.0.1284.49'},
    {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.76 Safari/537.36 OPR/19.0.1326.56'},
    {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36 OPR/20.0.1387.91'},
    {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.19.4 (KHTML, like Gecko) Version/5.0.2 Safari/533.18.5'},
    {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.2; es-US ) AppleWebKit/540.0 (KHTML like Gecko) Version/6.0 Safari/8900.00'},
    {'User-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.71 (KHTML like Gecko) WebVideo/1.0.1.10 Version/7.0 Safari/537.71'}
]


def get_random_header():
    return random.choice(USER_AGENT_LIST)


def formathost(ip,port):
    return {"http": "http://{}:{}".format(ip,port), "https": "https://{}:{}".format(ip,port)}


def poc(ip):
    print("Checking" + Fore.GREEN + "[+]: " + Fore.RESET, ip)

    host = formathost(ip,80)

    try:
        header = get_random_header()
        res = requests.get(
            host.get('http'), headers=header, timeout=3)

        if res.status_code == 200:
            _['Exist'] = True
            _['Details'] = res.text
            
            return _

    except Exception as e:
        _['Exist'] = False
        return _
