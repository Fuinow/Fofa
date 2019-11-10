import requests
import json

def get_proxies():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0"
    }
    url = "http://118.24.52.95/get_all/"
    res = requests.get(url)
    ip_list = json.loads(res.text)
    count = 0
    for ip in ip_list:
        ip = ip.get('proxy')
        print(ip)
        url = "https://fofa.so"
        try:
            res = requests.get(url, headers=headers, verify=False, timeout=10, proxies={'https':'http://'+ip})
            if res.status_code == 200:
                print(res.text[:400])
                count += 1
        except:
            pass
    print(len(ip_list))
    print(count)

get_proxies()