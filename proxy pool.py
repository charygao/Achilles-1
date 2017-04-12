#!/usr/bin/env python
#-*- coding:utf8 -*-
#@author: 00theway
#@file: http proxy.py
#@time: 2017/4/12 下午8:04



import signal
import os
import sys
import ctypes

import socket
import thread
import select

import random

BUFLEN=655350

proxys = open('proxy.txt').read().splitlines()


# def get_proxy():
#     lines = len(proxys)
#     rand = random.randint(0, lines-1)
#     proxy = proxys[rand]
#     ip = proxy.split(':')[0]
#     port = int(proxy.split(':')[1])
#     return (ip, port)


class Proxy(object):
    def __init__(self, conn, addr):
        print 'got connection from {}'.format(addr[0])
        self.src_socks = conn
        self.proxy = ('101.37.16.215',8080)
        self.dst_socks = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.default_page = '''HTTP/1.1 200 OK
Connection: close
Cache-control: no-cache
Pragma: no-cache
Cache-control: no-store
X-Frame-Options: DENY

<html><head><title>Proxy Error</title>
<style type="text/css">
body { background: #dedede; font-family: Arial, sans-serif; color: #404042; -webkit-font-smoothing: antialiased; }
#container { padding: 0 15px; margin: 10px auto; background-color: #ffffff; }
table { font-family: Arial, sans-serif; table-layout: fixed; }
p { font-size: padding: 0; margin: 0; word-wrap: break-word; }
td { display:table-cell; vertical-align:top; word-wrap: break-word; }
a { word-wrap: break-word; }
a:link, a:visited { color: #e06228; text-decoration: none; }
a:hover, a:active { color: #404042; text-decoration: underline; }
h1 { font-size: 1.6em; line-height: 1.2em; font-weight: normal; color: #404042; }
h2 { font-size: 1.3em; line-height: 1.2em; padding: 0; margin: 0.8em 0 0.3em 0; font-weight: normal; color: #404042;}
.title, .navbar { color: #ffffff; background: #e06228; padding: 10px 15px; margin: 0 -15px 10px -15px; overflow: hidden; }
.title h1 { color: #ffffff; padding: 0; margin: 0; font-size: 1.8em; }
.request { margin: 20px 0 10px 0; padding: 10px 10px 10px 10px; font-family: "Courier New", Courier, monospace; background-color: #f8f8f8; word-wrap: break-word; }
div.navbar {position: absolute; top: 18px; right: 25px;}div.navbar ul {list-style-type: none; margin: 0; padding: 0;}
div.navbar li {display: inline; margi-left: 20px;}
div.navbar a {color: white; padding: 10px}
div.navbar a:hover, div.navbar a:active {text-decoration: none; background: #404042;}
</style>
</head>
<body>
<div id="container">
<div class="title"><h1>Proxy Error</h1></div>
<h1>Failed to connect to Proxy %s : %%s</h1>
<p>&nbsp;</p>
</div>
</body>
</html>
''' % self.proxy[0]
        self.run()

    def run(self):
        running = True
        try:
            self.dst_socks.connect(self.proxy)
        except Exception,e:
            print e
            self.src_socks.send(self.default_page % e)
            running = False

        sockets = [self.src_socks,self.dst_socks]

        while running:
            data = ''
            (read_socks, write_socks, err_socks) = select.select(sockets, [], [], 3)

            for sock in read_socks:
                if sock is self.src_socks:
                    data = sock.recv(BUFLEN)
                    if len(data) > 0:
                        print '{}:{}->{}:{} len:{}'.format(
                            self.src_socks.getpeername()[0], self.src_socks.getpeername()[1],
                            self.dst_socks.getpeername()[0], self.dst_socks.getpeername()[1],
                            len(data))
                        self.dst_socks.send(data)
                        running = True
                    else:
                        print 'got nothing'
                        print 'kill connection {}:{} to {}:{}'.format(
                            self.src_socks.getpeername()[0],self.src_socks.getpeername()[1],
                            self.dst_socks.getpeername()[0],self.dst_socks.getpeername()[1])
                        running = False
                elif sock is self.dst_socks:
                    data = sock.recv(BUFLEN)
                    if len(data) > 0:
                        print '{}:{}->{}:{} len:{}'.format(
                            self.dst_socks.getpeername()[0], self.dst_socks.getpeername()[1],
                            self.src_socks.getpeername()[0], self.src_socks.getpeername()[1],
                            len(data))
                        self.src_socks.send(data)
                        running = True
                    else:
                        print 'got nothing'
                        print 'kill connection {}:{} to {}:{}'.format(
                            self.src_socks.getpeername()[0], self.src_socks.getpeername()[1],
                            self.dst_socks.getpeername()[0], self.dst_socks.getpeername()[1])
                        running = False

    def __del__(self):
        self.src_socks.close()
        self.dst_socks.close()


class Server(object):
    def __init__(self, host, port, timeout=20, handler=Proxy):
        signal_init()
        socket.setdefaulttimeout(timeout)
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host,port))
        self.server.listen(20)
        self.handler=handler

    def start(self):
        while True:
            try:
                conn, addr = self.server.accept()
                thread.start_new_thread(self.handler,(conn, addr))
            except:
                pass


def killproc(signum=0, frame=0, pid=False):
    if not pid:
        pid = os.getpid()
    if sys.platform.startswith('win'):
        try:
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.OpenProcess(1, 0, pid)
            kernel32.TerminateProcess(handle, 0)
        except:
            pass
    else:
        os.kill(pid, 9)


def signal_init():
    signal.signal(signal.SIGINT, killproc)
    try:
        signal.signal(signal.SIGTSTP, killproc)
        signal.signal(signal.SIGQUIT, killproc)
    except:
        pass


if __name__ == '__main__':
    s=Server('127.0.0.1', 8081)
    print 'proxy server is running at 127.0.0.1:8081'
    s.start()
