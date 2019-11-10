#coding=utf8
from gevent import monkey
monkey.patch_all()

import requests
import base64
import re
import sys
import time
import random
import queue
import json
from gevent.pool import Pool
from bs4 import BeautifulSoup
from difflib import SequenceMatcher


requests.packages.urllib3.disable_warnings()
def get_proxies():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0"
    }
    url = "http://118.24.52.95/get_all/"
    res = requests.get(url)
    ip_list = json.loads(res.text)
    count = 0
    with open('proxies.txt', 'w') as f:
        for ip in ip_list:
            ip = ip.get('proxy')
            print(ip)
            url = "https://fofa.so"
            try:
                res = requests.get(url, headers=headers, verify=False, timeout=10, proxies={'https':'http://'+ip})
                if res.status_code == 200:
                    f.write(ip)
                    f.write('\n')
                count += 1
            except:
                pass
    print(len(ip_list))
    print(count)

class Fofa(object):

    def __init__(self, app):
        self.proxies_Q = queue.Queue()
        self.load_proxies()
        self.check_list_info = []   # 获取的目标网页信息
        self.checked_host_list = []     # 已经比较过的 host
        self.rule_list = []     # 已获取到的子规则
        self.checked_rule_list = []     # 已经验证过的规则，防止重复验证
        self.app = app
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0"
        }
        self.app_count = self.get_ip_count(app)

    def load_proxies(self):
        print('[+] Load proxies')
        with open('proxies.txt') as f:
            for ip in f.readlines():
                self.proxies_Q.put(ip.strip())

        return

    def get_host_list(self, rule):
        host_list = []
        qbase64 = base64.b64encode(rule.encode('utf-8'))
        url = 'https://fofa.so/result?qbase64=' + str(qbase64, 'utf-8')
        resp = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(resp.text, 'html5lib')
        items = soup.find_all('div', class_='list_mod_t')
        for item in items:
            try:
                host = item.find('a', target="_blank").get('href')      # 非 http 协议的 HOST 匹配不到 URL，暂时忽略处理
            except:
                continue
            if host not in self.checked_host_list:
                try:    
                    requests.get(host, timeout=5, verify=False)
                    host_list.append(host)
                except Exception as e:
                    print(e)
                    continue
            else:
                pass
        return host_list

    def get_text(self, host):
        # 数据清洗
        headers = {}
        white_header = ['Keep-Alive', 'X-Content-Type-Options', 'Accept-Encoding', 'Cache-Control', 'Connection', 'Content-Encoding', 'Content-Type', 'Date', 'Transfer-Encoding', 'Content-Length', 'Pragma', 'X-Frame-Options', 'X-XSS-Protection', 'Expires']
        try:
            resp = requests.get(host, headers=self.headers, timeout=5, verify=False)
        except Exception as e:
            print(e)
            return

        text = resp.text.replace('\n', '').replace('\t', '')
        with open('white_body_t.txt', 'r',encoding='utf-8') as f:
            for rule in f.readlines():
                text = text.replace(rule.strip(), '')
        for k,v in resp.headers.items():
            if k not in white_header:
                with open('white_header.txt', 'r') as f:
                    for keywords in f.readlines():
                        v = v.replace(keywords.strip(), '')
                        headers[k] = v
        self.check_list_info.append((host, text, headers, len(text)))

        return 

    def get_ip_count(self, rule):
        if not rule:
            print('[-] rule not exist')
            return 0
        if self.proxies_Q.qsize() <= 10:
            self.load_proxies()
        print('[+] proxies count: ' + str(self.proxies_Q.qsize()))
        proxy_ip = self.proxies_Q.get()
        retry = 5
        ret = 1
        while ret <= retry:
            proxies = {"https": "http:"+proxy_ip}
            qbase64 = base64.b64encode(rule.encode('utf-8'))
            url = 'https://fofa.so/result?qbase64=' + str(qbase64, 'utf-8')

            try:
                resp = requests.get(url, headers=self.headers, timeout=10, verify=False, proxies=proxies)
                count_str = re.search('获得 (.*) 条匹配结果', resp.text).group(1)
            except Exception as e:
                print('[-]Error: ' + url)
                print(e)
                ret += 1
                proxy_ip = self.proxies_Q.get()
                continue

            count = int(count_str.replace(',', ''))
            self.proxies_Q.put(proxy_ip)
            return count
        self.proxies_Q.put(proxy_ip)
        return 0

    def is_sub_rule(self, sub_rule):        
        if sub_rule not in self.checked_rule_list:          
            
            # just test
            # import random
            # print('[+] Test rule: ' + sub_rule)
            # self.checked_rule_list.append(sub_rule)
            # return random.randint(0,1)

            self.checked_rule_list.append(sub_rule)
            count1 = self.get_ip_count(sub_rule)
            time.sleep(random.randint(1,3))
            if count1 > self.app_count:
                return False
            count2 = self.get_ip_count(sub_rule+'&&'+self.app)
            time.sleep(random.randint(1,3))
            print(count1)
            print(count2)
            if count1 != 0 and count1 == count2:
                return True
            else:
                return False
        else:
            return False

    def is_white(self, text):
        RATIO = 0.7
        with open('white_body.txt', encoding='utf-8') as f:
            for white in f.readlines():
                white = white.strip()
                seqm = SequenceMatcher()
                seqm.set_seq1(text)
                seqm.set_seq2(white)
                if seqm.ratio() > RATIO:
                    return True
                else:
                    pass
        return False

    def get_same_str(self, text1, text2, min_len=10, max_len=500):
        pos_list = []
        dp = [([0] * (len(text2)+1)) for i in range(len(text1)+1)]
        _len = index = 0

        for i in range(1, len(text1)+1):
            for j in range(1, len(text2)+1):
                if i == 0 or j == 0:  # 在边界上，自行+1
                        dp[i][j] = 0
                if text1[i-1] == text2[j-1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1         
                    if dp[i][j] > _len:  
                        _len = dp[i][j]
                        index = i - _len
                else:
                    dp[i][j] = 0
            if _len > min_len and _len < max_len:
                pos_list.append([index, _len])
            _len = min_len

        # for dp_line in dp:
        #     print(dp_line)
        result = []
        pos_list.append([-2,0])
        len_list = []
        last_pos = pos_list[0]
        for pos in pos_list:
            if pos[0] == last_pos[0]:
                len_list.append(pos[1])
            else:
                if len_list:
                    same_str = text1[last_pos[0]:last_pos[0] + max(len_list)]
                    for _str in same_str.split('>'):
                        _str = _str.strip()
                        if _str not in result and len(_str) >= min_len:
                            result.append(_str)
                last_pos[0] = pos[0]
                len_list = [pos[1]]

        return result

    def check_body(self, text1, text2):
        sub_list = self.get_same_str(text1, text2)
        print('[+] Get body list')
        print(sub_list)
        for sub_rule in sub_list:
            if self.is_white(sub_rule):
                continue
            sub_rule = 'body=\"' + sub_rule.replace('\"', '\\\"') + '\"'
            if self.is_sub_rule(sub_rule):
                print('[!] Found sub_rule: ' + sub_rule)
                self.rule_list.append(sub_rule)
        return 

    def check_header(self, headers1, headers2):      
        keys1 = set(headers1.keys())
        keys2 = set(headers2.keys())
        keys = keys1 & keys2
        for key in keys:
            sub_rule = 'header=\"' + key.replace('\"', '\\\"') + '\"'
            if self.is_sub_rule(sub_rule):
                print('[!] Found sub_rule: ' + sub_rule)
                self.rule_list.append(sub_rule)  
            sub_list = self.get_same_str(headers1[key], headers2[key], min_len=4)
            for sub_rule in sub_list:
                sub_rule = 'header=\"' + sub_rule.replace('\"', '\\\"') + '\"'
                if self.is_sub_rule(sub_rule):
                    print('[!] Found sub_rule: ' + sub_rule)
                    self.rule_list.append(sub_rule)    
        return 


    def check(self, headers1, headers2, text1, text2):
        # 处理 header
        check_list = []
        keys1 = set(headers1.keys())
        keys2 = set(headers2.keys())
        keys = keys1 & keys2
        for key in keys:
            sub_rule = 'header=\"' + key.replace('\"', '\\\"') + '\"'
            check_list.append(sub_rule)
            sub_list = self.get_same_str(headers1[key], headers2[key], min_len=4)
            for sub_rule in sub_list:
                sub_rule = 'header=\"' + sub_rule.replace('\"', '\\\"') + '\"'
                check_list.append(sub_rule)

        # 处理 body
        sub_list = self.get_same_str(text1, text2)
        for sub_rule in sub_list:
            # if self.is_white(sub_rule):
            #     continue
            sub_rule = 'body=\"' + sub_rule.replace('\"', '\\\"') + '\"'
            check_list.append(sub_rule)

        print(check_list)
        pool = Pool(5)
        pool.map(self.add_rule, check_list)


        return 

    def add_rule(self, rule):
        print('[+] check rule: ' + rule)
        if self.is_sub_rule(rule):
            print('[!] Found ' + rule)
            self.rule_list.append(rule)
        else:
            pass



    def get_rule(self):
        
        # just test
        # rule = self.app
        if self.rule_list:
            rule = '&&'.join(self.rule_list).replace('body=', 'body!=').replace('header=', 'header!=') + '&&'+self.app
        else:
            rule = self.app
        print('[+] Test: '+rule)
        host_list = self.get_host_list(rule)
        print(host_list)
        # host_list = ['http://54.162.93.196:8080', 'http://78.26.140.52:2323'] # just test
        pool = Pool(10)
        pool.map(self.get_text, host_list)
        self.check_list_info.sort(key=lambda x:x[3])

        self.checked_host_list.append(self.check_list_info[0][0])
        self.checked_host_list.append(self.check_list_info[1][0])
        print(self.check_list_info[1][0])
        print(self.check_list_info[0][0])
        text1, headers1 = self.check_list_info[0][1], self.check_list_info[0][2]
        text2, headers2 = self.check_list_info[1][1], self.check_list_info[1][2]

        # self.check_body(text1, text2)
        self.check(headers1, headers2, text1, text2)
        self.check_list_info = []

        if self.get_ip_count('||'.join(self.rule_list)) != self.app_count:
            self.get_rule()
        return self.rule_list

    def start(self):
        return self.get_rule()

if __name__ == '__main__':
    fofa = Fofa("app=\"zabbix\"")
    fofa.start()


