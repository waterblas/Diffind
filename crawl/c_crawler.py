'''
Created on 2015-11-20
The example client program uses some sockets to demonstrate how the server
with select() manages multiple connections at the same time . The client
starts by connecting each TCP/IP socket to the server
@author: ldy
'''

import socket
from helper import CommonHelper

HOST = '127.0.0.1'
PORT = 5000
helper = CommonHelper()
messages = ["http://m.byr.cn/section/1" ,
            "http://m.byr.cn/section/2" ,
            "http://m.byr.cn/section/3"]
print "Connect to the server"

#Create a TCP/IP sock 
socks = []
for i in range(10):
    socks.append(socket.socket(socket.AF_INET,socket.SOCK_STREAM))
for s in socks:
    s.connect((HOST, PORT))

counter = 0
for message in messages :
    #Sending message from different sockets
    for s in socks:
        counter+=1
        print "  %s sending %s" % (s.getpeername(),message+" version "+str(counter))
        data = helper.pack(message+" version "+str(counter))
        s.send(data)
    #Read responses on both sockets
for s in socks:
    s.send(helper.get_url())
    data = s.recv(1024)
    print " %s received %s" % (s.getpeername(),data)
    if not data:
        print "closing socket ",s.getpeername()
        s.close()
