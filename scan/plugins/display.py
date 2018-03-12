
from colorama import Fore
import random
import time

def poc(ip):
    print("Checking" + Fore.GREEN + "[+]: " + Fore.RESET,ip)
    
    summary = str(random.random())

    

    if ip.endswith("3"):
        time.sleep(3)
        res = {
            "Exist": True,
            "Problility":  summary,
            'Summary' : "JustForFun, For Test",
            "Details" : "HengHengHaHou, I am king, and my summary is:"+summary
        }
    elif ip.endswith("4"):
        time.sleep(4)
        res = {
            "Exist": True,
            "Problility":  summary,
            'Summary': "Tobe or not tobe",
            "Details": "Oh, Shit, I am mad king, and my summary is: "+summary
        }
    else:
        time.sleep(2)
        res = {
            "Exist": True,
            "Problility":  summary,
            'Summary': "Tobe or not tobe",
            "Details": "Oh, Shit, I am mad king, and my summary is: "+summary
        }
    return res
