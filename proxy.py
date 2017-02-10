#-*- coding: utf-8 -*-
import socket,thread,select

TerminateAll = False


proxys = open('proxy.txt').read().splitlines()

def GetProxy():
    lines = len(proxys)
    rand = random.randint(0,lines-1)
    proxy = proxys[rand]
    ip = proxy.split(':')[0]
    port = int(proxy.split(':')[1])
    return (ip,port)



class Proxy(object):
    def __init__(self,ClientSocket):
        self.ClientSocket = ClientSocket
        self.ProxySocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.ProxyHost,self.ProxyPort = GetProxy()
        self.ClientData = ''
        self.ProxyData = ''
        self.Terminate = False
        self.Timeout = 10
        self.run()

    def run(self):
        self.ClientSocket.setblocking(0)

        self.ProxySocket.connect((self.ProxyHost,self.ProxyPort))
        self.ProxySocket.setblocking(0)

        while not self.Terminate and not TerminateAll:
            Inputs = [self.ClientSocket,self.ProxySocket]
            Outputs = []

            if len(self.ClientData) > 0:
                Outputs.append(self.ClientSocket)

            if len(self.ProxySocket) > 0:
                Outputs.append(self.ProxySocket)

            try:
                InputReady, OutputReady, ErrorReady = select.select(Inputs,Outputs,[],self.Timeout)
            except Exception, e:
                print e
                break

            for inp in InputReady:
                if inp == self.ClientSocket:
                    try:
                        data = self.ClientSocket.recv(4096)
                    except Exception, e:
                        print e

                    if data != None:
                        if len(data) > 0:
                            self.ProxyData += data
                        else:
                            self.Terminate = True
                    else:
                        self.Terminate = True

                elif inp == self.ProxySocket:
                    try:
                        data = self.ProxySocket.recv(4096)
                    except Exception, e:
                        print e

                    if data != None:
                        if len(data) > 0:
                            self.ClientData += data
                        else:
                            self.Terminate = True
                    else:
                        self.Terminate = True


            for out in OutputReady:
                if out == self.ClientSocket and len(self.ClientData) > 0:
                    BytesWritten = self.ClientSocket.send(self.ClientData)
                    if BytesWritten > 0:
                        self.ClientData = self.ClientData[BytesWritten:]
                elif out == self.ProxySocket and len(self.ProxyData) > 0:
                    BytesWritten = self.ProxySocket.send(self.ProxyData)
                    if BytesWritten > 0:
                        self.ProxyData = self.ProxyData[BytesWritten:]

        self.ClientSocket.close()
        self.ProxySocket.close()
        print 'closing two sockets'


class Server(object):
    def __init__(self,host,port):
        self.host=host
        self.port=port
        self.ServerSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.ServerSocket.bind((host,port))
        self.ServerSocket.listen(100)

    def start(self):
        while True:
            try:
                ClientSocket,addr = self.ServerSocket.accept()
                print 'connect from %s' % addr[0]
                thread.start_new_thread(Proxy,(ClientSocket))
            except KeyboardInterrupt:
                print "Terminating..."
                TerminateAll = True
                break
            except:
                pass
        ServerSocket.close()


if __name__=='__main__':
    s=Server('127.0.0.1',8081)
    print 'proxy server is running at 127.0.0.1:8081'
    s.start()
    