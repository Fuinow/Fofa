#coding=utf8

import requests
import base64
import re
import os


def get_text(host):
    # 数据清洗
    text = requests.get(host, verify=False).text.replace('\n', '').replace('\t', '')
    return text


def get_same_str(text1, text2, min_len=10, max_len=500):
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


def get_text():
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0"
        }
    host_list = ['https://vuematerial.io/', 'http://193.2.103.7','http://52.80.142.165:8081','http://ask.zol.com.cn'
                'http://www.ityouknow.com/', 'https://pypi.org/', 'https://blog.51cto.com/','http://admin.dlszywz.cn/',
                'http://learning.cmr.com.cn/', 'http://www.ghost580.com/win10/2019-08-14/28736.html'
    ]
    id =0
    for i in range(len(host_list)):
        url = host_list[i]
        print(url)
        try:
            res = requests.get(url, timeout=5, headers=headers, verify=False)
            with open(str(id)+'.txt', 'w', encoding='utf8') as f:
                f.write(res.text)
            id += 1
        except Exception as e:
            print(e)
        

def get_rule():
    result = set()
    for root, dirs, files in os.walk('.'):
        print(files)
        file_count = len(files) - 1
    for i in range(file_count):
        for j in range(i,file_count):
            if i == j:
                continue
            print(i,j)
            with open(str(i)+'.txt', encoding='utf8') as f:
                text1 = f.read()[:15000]
            with open(str(j)+'.txt', encoding='utf8') as f:
                text2 = f.read()[:15000]
            sub_list = get_same_str(text1, text2)
            for rule in sub_list:
                result.add(rule)
    with open('out.txt', 'w', encoding='utf8') as f:
        for sub_rule in result:
            print(sub_rule)
            f.write(sub_rule)
            f.write('\n')




if __name__ == '__main__':
    get_text()
    get_rule()

 

