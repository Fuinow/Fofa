#coding=utf8
#url长度超过3500服务器无法解析


import urllib2
import base64
import re
import time
import random
from bs4 import BeautifulSoup

class CountParser(object):

	def __init__(self, rule):
		self.rule = rule
		self.buf = self.request()
		self.soup = BeautifulSoup(self.buf, "html5lib")
		self.ports = []
		self.country = []
		self.ip_count = 0

	def filter(self, buf):
		buf = buf.replace("\\/","/").replace("\\\"","\"")
		return buf


	def request(self):
		buf = ""
		rule = base64.b64encode(self.rule)
		url = "https://fofa.so/search/result_stats?qbase64=" + rule
		headers = {
					"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0",
					"X-Requested-With": "XMLHttpRequest"
					}
		req = urllib2.Request(url,headers=headers)
		try:
			buf = urllib2.urlopen(req).read()
		except Exception as e:
			print(e)
			print("Network error")
		if buf:
			return self.filter(buf)
		else:
			return None
		time.sleep(1)

	def get_port(self):
		for i in self.soup.find("div",class_="modl mar_b30 mar_t30").find("div", class_="modl_c").ul.find_all("li"):
			port = i.a.get_text()
			self.ports.append(port)
		return self.ports

	def get_country(self):
		for i in self.soup.find("div", class_="modl mar_b30").find("div", class_="modl_c").ul.find_all("img"):
			country = i.get("src").split("/")[-1].split(".")[0].upper()
			self.country.append(country)
		return self.country

	def get_ip_count(self):
		count = re.search("var ip_count = (\d*)", self.buf)
		self.ip_count = int(count.group(1))
		return self.ip_count



class Fofa(object):

	def __init__(self, rule):
		self.root_rule = rule
		self.temp_rule = rule
		self.rule_list = []
		self.count = 0
		self.over = 0
		self.temp_host = set()
		self.host_list = set()
		self.MAX_COUNT = 100

	def test(self):
		a = CountParser("header=\"JDWS/2.0\"")
		print(a.get_country())

	def _make_rule_time(self, after, before, rule):
		before = time.localtime(before)
		after = time.localtime(after)
		rule = rule + "&&after=\"" + str(after[0]) + "-" + str(after[1]) + "\"&&before=\"" + str(before[0]) + "-" + str(before[1]) + "\"" 
		return rule		

	def rule_base_time(self, root_rule):
		print("[!] Start rule base time")
		max_time = time.time()
		min_time = max_time - 31536000
		temp_time = max_time - 31536000
		time_list = []	
		while True:
			print("[!] Test rule : " + self._make_rule_time(temp_time, max_time, root_rule))
			if max_time - temp_time <= 5000000:
				rule = self._make_rule_time(temp_time, max_time, root_rule)
				print("[+] Get rule : " + rule)
				self.rule_list.append(rule)
				if temp_time == min_time:
					break
				max_time = temp_time
				temp_time = min_time
				continue
			else:
				pass
			if CountParser(self._make_rule_time(temp_time, max_time, root_rule)).get_ip_count() <= self.MAX_COUNT:
				rule = self._make_rule_time(temp_time, max_time, root_rule)
				print(rule)
				self.rule_list.append(rule)
				if temp_time == min_time:
					break
				else:
					max_time = temp_time
					temp_time = min_time
			else:
				temp_time = temp_time + 2592000
	
	def make_rule(self):
		print("[!] Start make rule")
		counts = CountParser(self.root_rule)
		country_list = counts.get_country()		
		count = counts.get_ip_count()
		if count > self.MAX_COUNT:
			for country in country_list:
				temp_rule = self.root_rule
				temp_rule = self.root_rule + "&&country=" + country
				counts = CountParser(temp_rule)
				ports = counts.get_port()
				count = counts.get_ip_count()
				if count > self.MAX_COUNT:
					for port in ports:
						temp_rule = self.root_rule + "&&country=" + country + "&&port=" + port
						counts = CountParser(temp_rule)
						count = counts.get_ip_count()
						if count > self.MAX_COUNT:
							self.rule_base_time(temp_rule)
						else:
							print("[+] Get rule : " + temp_rule)
							self.rule_list.append(temp_rule)
				else:
					print("[+] Get rule : " + temp_rule)
					self.rule_list.append(temp_rule)
		else:
			print("[+] Get rule : " + self.root_rule)
			self.rule_list.append(self.root_rule)
		return self.rule_list

	def get_ip_list(self, rule):
		rule = base64.b64encode(rule)
		url = "https://fofa.so/result?qbase64=" + rule
		print("URL Length : %d"%len(url))
#		print url
#		print self.temp_rule
		buf = urllib2.urlopen(url).read()
		count = re.search(" 获得 (.*) 条匹配结果",buf).group(1)
		if count == "0":
			self.over = 1
		soup = BeautifulSoup(buf,"html5lib")
		items = soup.find_all("div", class_="list_mod")
		for item in items:
			ip = item.find("a", {"href":re.compile("/host.*")})
			ip = ip.get_text()
#			domain = item.find("div", class_="list_mod_t")
#			a = domain.find("a")
#			host = a.get("href")
			print("[+] Get IP: %s"%ip)
			self.temp_host.add(ip)
			self.host_list.add(ip)

	def get_count(self, rule):
		rule = base64.b64encode(rule)
		url = "https://fofa.so/result?qbase64=" + rule
		buf = urllib2.urlopen(url).read()
		count = re.search(" 获得 (.*) 条匹配结果",buf).group(1)
		self.count = int(count.replace(",",""))
		print("get host count : %s" %count)

	def output(self, filename):
		f = open(filename, "w")
		for host in self.host_list:
			f.write(host)
			f.write("\n")
		f.close()

	def start(self):
		self.make_rule()
		for rule in self.rule_list:
			print("[!] Start get rule : " + rule)
			self.over = 0
			self.temp_rule = rule
			while not self.over:
				try:
					self.get_ip_list(self.temp_rule)
				except Exception as err:
					print(err)
					break
				for host in self.temp_host:
					rule_padd = " &&ip!=\"%s\"" %host
					self.temp_rule += rule_padd
				self.temp_host.clear()
				print("Get host : %d"%len(self.host_list))
				time.sleep(random.randint(2,4))
		self.output("out.txt")
		print("[+] Down")

	def test_get_list(self):
		self.temp_rule = self.root_rule
		while not self.over:
			try:
				self.get_ip_list(self.temp_rule)
			except Exception as err:
				print(err)
				break
			for host in self.temp_host:
				rule_padd = " &&ip!=\"%s\"" %host
				self.temp_rule += rule_padd
			self.temp_host.clear()
			print("Get host : %d"%len(self.host_list))
			time.sleep(random.randint(2,4))
		self.output("out.txt")
		print("[+] Down")

#f = open("ip.txt","w")
#rule = "header=\"JDWS/2.0\""
#fofa = fofa(rule)
#fofa.start()
#for ip in fofa.host_list:
#	f.write(ip)
#	f.write("\n")
#f.close()

a = Fofa("app=\"Jenkins\"")
print(a.test_get_list())
#a.start()