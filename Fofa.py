#coding=utf8

import requests
import base64
import re
import sys
import time
import random
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings()

class Fofa(object):

    def __init__(self, app):
        self.checked_host_list = []
        self.rule_list = []
        self.app = app
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0"
        }
        self.app_count = self.get_ip_count(app)


    def get_host_list(self, rule):
        host_list = []
        qbase64 = base64.b64encode(rule.encode('utf-8'))
        url = 'https://fofa.so/result?qbase64=' + str(qbase64, 'utf-8')
        resp = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(resp.text, 'html5lib')
        items = soup.find_all('div', class_='list_mod_t')
        for item in items:
            if len(host_list) == 2:
                return host_list
            else:
                host = item.find('a').get('href')
                if host not in self.checked_host_list:
                    try:
                        requests.get(host, timeout=5)
                        host_list.append(host)
                        self.checked_host_list.append(host)
                    except:
                        continue
                else:
                    pass
        return

    def get_text(self, host):
        # 数据清洗
        headers = {}
        white_header = ['Cache-Control', 'Connection', 'Content-Encoding', 'Content-Type', 'Date', 'Transfer-Encoding', 'Content-Length', 'Pragma', 'X-Frame-Options', 'X-XSS-Protection', 'Expires']
        resp = requests.get(host, headers=self.headers, verify=False)
        text = resp.text.replace('\n', '').replace('\t', '')
        with open('write_body_t.txt', 'r',encoding='utf-8') as f:
            for rule in f.readlines():
                text = text.replace(rule.strip(), '')
        for k,v in resp.headers.items():
            if k not in white_header:
                with open('white_header.txt', 'r') as f:
                    for keywords in f.readlines():
                        v = v.replace(keywords.strip(), '')
                        headers[k] = v

        return text, headers

    def get_ip_count(self, rule):
        qbase64 = base64.b64encode(rule.encode('utf-8'))
        url = 'https://fofa.so/result?qbase64=' + str(qbase64, 'utf-8')
        resp = requests.get(url, headers=self.headers)
        try:
            count_str = re.search('获得 (.*) 条匹配结果', resp.text).group(1)
        except:
            print('[-]Error: ' + url)
            return 0
        count = int(count_str.replace(',', ''))
        return count

    def is_sub_rule(self, sub_rule):
        
        # just test
        # import random
        # print('[+] Test rule: ' + sub_rule)
        # return random.randint(0,1)

        print('[+] Test rule: ' + sub_rule)
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
                print('[+] Found sub_rule: ' + sub_rule)
                self.rule_list.append(sub_rule)  
            sub_list = self.get_same_str(headers1[key], headers2[key], min_len=4)
            for sub_rule in sub_list:
                sub_rule = 'header=\"' + sub_rule.replace('\"', '\\\"') + '\"'
                if self.is_sub_rule(sub_rule):
                    print('[+] Found sub_rule: ' + sub_rule)
                    self.rule_list.append(sub_rule)    
        return 


    def get_rule(self):
        if self.rule_list:
            rule = '&&'.join(self.rule_list).replace('body=', 'body!=').replace('header=', 'header!=') + '&&'+self.app
        else:
            rule = self.app
        print('[+] Test: '+rule)
        host_list = self.get_host_list(rule)
        print('[+] Test host: ' + host_list[0] + ',' + host_list[1])

        # host_list = ['http://54.162.93.196:8080', 'http://78.26.140.52:2323'] # just test

        text1, headers1 = self.get_text(host_list[0])
        text2, headers2 = self.get_text(host_list[1])
        self.check_header(headers1, headers2)
        self.check_body(text1, text2)
        if self.get_ip_count('||'.join(self.rule_list)) != self.app_count:
            self.get_rule()
        return self.rule_list

    def start(self):
        return self.get_rule()

if __name__ == '__main__':
    fofa = Fofa("app=\"zabbix\"")
    fofa.start()



# "测试过的ip白名单"
# 