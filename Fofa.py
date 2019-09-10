#coding=utf8

import requests
import base64
import re
import sys
from bs4 import BeautifulSoup

class Fofa(object):

    def __init__(self):
        self.rule_list = []
        self.app = ''
        self.app_count = 0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0"
        }

    def get_host_list(self, rule):
        host_list = []
        qbase64 = base64.b64encode(rule.encode('utf-8'))
        url = 'https://fofa.so/result?qbase64=' + str(qbase64, 'utf-8')
        resp = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(resp.text, 'html5lib')
        items = soup.find_all('div', class_='list_mod_t')
        for item in items:
            host = item.find('a').get('href')
            host_list.append(host)
        return host_list

    def get_text(self, host):
        # 数据清洗
        headers = {}
        white_header = ['Cache-Control', 'Connection', 'Content-Encoding', 'Content-Type', 'Date', 'Transfer-Encoding', 'Content-Length', 'Pragma', 'X-Frame-Options', 'X-XSS-Protection', 'Expires']
        resp = requests.get(host, headers=self.headers, verify=False)
        text = resp.text.replace('\n', '').replace('\t', '')
        with open('write_body.txt', 'r') as f:
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
        print(rule)
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
        count1 = self.get_ip_count(sub_rule)
        if count1 > self.app_count:
            return False
        count2 = self.get_ip_count(sub_rule+'&&'+self.app)
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
        for sub_rule in sub_list:
            sub_rule = 'body=\"' + sub_rule.replace('\"', '\\\"') + '\"'
            if self.is_sub_rule(sub_rule):
                print('[+] Found sub_rule: ' + sub_rule)
                self.rule_list.append(sub_rule)
        return 

    def check_header(self, headers1, headers2):
        for k,v in headers1.items():
            if k in headers2.keys():
                sub_list = self.get_same_str(headers1[k], headers2[k], min_len=4)
                for sub_rule in sub_list:
                    sub_rule = 'header=\"' + sub_rule.replace('\"', '\\\"') + '\"'
                    if self.is_sub_rule(sub_rule):
                        print('[+] Found sub_rule: ' + sub_rule)
                        self.rule_list.append(sub_rule)    
        return 


    def get_rule(self, app):
        self.app = app
        self.app_count = self.get_ip_count(app)
#       ip_list = self.get_ip_list
#       text1 = get_text(ip_list[0])
#       text2 = get_text(ip_list[1])
        text1, headers1 = self.get_text('https://77.87.215.179/')
        text2, headers2 = self.get_text('http://202.152.60.53:81/')
        self.check_header(headers1, headers2)
        self.check_body(text1, text2)
        return self.rule_list



if __name__ == '__main__':
    fofa = Fofa()
    print(fofa.get_host_list("app=\"Zabbix\""))



