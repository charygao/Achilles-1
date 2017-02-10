#-*- coding: utf-8 -*-
import socket
import thread
import select
import random

BUFLEN=655350

proxys = open('proxy.txt').read().splitlines()

def GetProxy():
	lines = len(proxys)
	rand = random.randint(0,lines-1)
	proxy = proxys[rand]
	ip = proxy.split(':')[0]
	port = int(proxy.split(':')[1])
	return (ip,port)


class Proxy(object):
    def __init__(self,conn,addr):
        self.source=conn
        self.destnation=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.run()

    def run(self):
        self.destnation.connect(GetProxy())
        #receive from source send to destnation

        data = self.source.recv(BUFLEN)
        print 'receive from source'
        self.destnation.send(data)
        
        
        readsocket=[self.destnation]
        #receive from destnation return to source
        while True:
            data = ''
            (rlist,wlist,elist)=select.select(readsocket,[],[],3)
            if rlist:
                data=rlist[0].recv(BUFLEN)
                if len(data)>0:
                    print 'receive from destnation'
                    self.source.send(data)
                else:
                    break

class Server(object):
    def __init__(self,host,port,handler=Proxy):
        self.host=host
        self.port=port
        self.server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host,port))
        self.server.listen(20)
        self.handler=handler

    def start(self):
        while True:
            try:
                conn,addr=self.server.accept()
                thread.start_new_thread(self.handler,(conn,addr))
            except:
                pass


if __name__=='__main__':
    s=Server('127.0.0.1',8081)
    print 'proxy server is running at 127.0.0.1:8081'
    s.start()
    
