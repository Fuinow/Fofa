#coding=utf8

import requests
import base64

class Fofa(object):

	def __init__(self):
		self.app = ''
		self.headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0"
		}

	def get_ip_list(self, rule):
		return

	def get_text(self, ip):
		# 数据清洗
		return 

	def get_ip_count(self, rule):
		url = 'https://fofa.so/result?qbase64=' + base64.b64encode(sub_rule)
		return

	def is_sub_rule(self, sub_rule):
		if get_ip_count(sub_rule) == get_ip_count(sub_rule+'&&app='+self.app):
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

	def get_rule(self, app):
		self.app = app
		ip_list = self.get_ip_list
		text1 = get_text(ip_list[0])
		text2 = get_text(ip_list[1])
		sub_list = get_same_str(text1, text2)
		return



if __name__ == '__main__':
	text1 = requests.get('http://64.32.8.26/', verify=False).text
	text2 = requests.get('http://121.15.254.143:8888/', verify=False).text
	print(11)
	fofa = Fofa("zabbix")
	res = fofa.get_same_str(text1, text2)
	print(res)


