
from colorama import Fore

def poc(ip):
    print("Checking" + Fore.GREEN + "[+] :" + Fore.RESET,ip)
    
    if ip.endswith("3"):
        return True , ip+"Details"
    else:
        return False, ip+"Details"