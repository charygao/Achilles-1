# -*- coding: utf-8 -*-
import sys
import requests
proxys = open('file.txt').read().splitlines()

p = open('proxy.txt','a+')
for i in proxys:
	ip = i.split(':')[0]
	port = i.split(':')[1]
	proxy = {'http': 'http://%s:%s' % (ip, port)}
	try:
		d = requests.get('http://1212.ip138.com/ic.asp', proxies=proxy, timeout=5).text
		if ip in d:
			print 'got proxy %s:%s' % (ip, port)
			p.write(i+'\n')
		else:
			print 'got proxy %s:%s' % (ip, port)
			p.write(i+'\n')
	except Exception ,e:
		print 'proxy %s:%s error' % (ip, port)
		pass