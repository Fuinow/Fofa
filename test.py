import requests
import json
import time
from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool

def a(a):
    print(a)
    time.sleep(4)

l = ['1','2','3']
p = Pool()
p.map(a,l)