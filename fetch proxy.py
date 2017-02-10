# -*- coding: utf-8 -*-
'''
http://www.kuaidaili.com/
http://www.xicidaili.com/
http://ip84.com/
proxies = {
  "http": "http://10.10.1.10:3128",
  "https": "http://10.10.1.10:1080",
}
requests.get('http://127.0.0.1/test.php',proxies=proxy)
http://api.xicidaili.com/free2016.txt	15分钟更新一次
http://www.66ip.cn/nmtq.php?getnum=800&area=1&proxytype=0&api=66ip	10分钟一次
http://www.66ip.cn/mo.php?tqsl=100	100个每次，少量多次
'''
import requests,threading,time,os
import Queue


def verify_proxy(proxy_list,pfile,file_lock,tid):
    global count
    while not proxy_list.empty():
        p = proxy_list.get()
        ip = p.split(":")[0]
        port = p.split(":")[1]
        proxy = {'http': 'http://%s:%s' % (ip, port)}
        try:
            d = requests.get('http://1212.ip138.com/ic.asp', proxies=proxy, timeout=20).text
            if ip in d:
                print 'tid:%s got proxy %s:%s' % (tid,ip, port)
                file_lock.acquire()
                pfile.write(p + '\n')
                pfile.flush()
                count += 1
                print 'total proxys:%d' % count
                file_lock.release()
        except Exception ,e:
            print 'proxy %s:%s error' % (ip, port)
    print 'thread %s stoped' % tid


proxy_list = Queue.Queue()

print 'get http://api.xicidaili.com/free2016.txt'
proxys1 = requests.get('http://api.xicidaili.com/free2016.txt').text
proxys = proxys1.splitlines()
for proxy in proxys:
    proxy_list.put(proxy)

print 'get http://www.66ip.cn/nmtq.php?getnum=800&area=1&proxytype=0&api=66ip'
proxy2 = requests.get('http://www.66ip.cn/nmtq.php?getnum=800&area=1&proxytype=0&api=66ip').text
proxys = proxy2.split('</div>')[0].split('javascript"></script>')[1].split('<br/>\n')

for proxy in proxys:
    if len(proxy)>3:
        proxy_list.put(proxy)



pfile = open('proxy.txt','a+')
file_lock = threading.Lock()

count = 0
t_list = []

for i in range(20):
    print 'start thread %s' % i
    t = threading.Thread(target=verify_proxy, args=(proxy_list, pfile, file_lock,i))
    t_list.append(t)
    t.start()

for t in t_list:
    t.join()