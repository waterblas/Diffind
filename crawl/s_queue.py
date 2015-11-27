'''
Created on 2015-11-20
The echo server example from the socket section can be extanded to watche for more than
one connection at a time by using select() .The new version starts out by creating a nonblocking
TCP/IP socket and configuring it to listen on an address
@author: ldy
'''
import select
import socket
import Queue
from helper import CommonHelper

HOST = '127.0.0.1'
PORT = 5000
# transfer close beyond limit
RECV_BUFFER = 4096
TAG_GET = 0
TAG_PUT = 1
#create a socket
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.setblocking(0)
#set option reused
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR  , 1)
server.bind((HOST, PORT))
server.listen(10)
#sockets from which we except to read
inputs = [server]
#sockets from which we expect to write
outputs = []
#Outgoing message queues
message_queues = Queue.Queue()
#A optional parameter for select is TIMEOUT
timeout = 60
helper = CommonHelper()

while inputs:
    print "waiting for next event"
    readable , writable , exceptional = select.select(inputs, outputs, inputs, timeout)
    for s in readable :
        if s is server:
            # A "readable" socket is ready to accept a connection
            connection, client_address = s.accept()
            print "    connection from ", client_address
            connection.setblocking(0)
            inputs.append(connection)
        else:
            data = s.recv(RECV_BUFFER)
            if data:
                tag, data, depth = helper.server_unpack(data)
                if tag == TAG_GET:
                # Add output channel for response
                    # print " received a request for url"
                    if s not in outputs :
                        outputs.append(s)
                elif tag == TAG_PUT:
                    print " received " , data , "from ",s.getpeername()
                    for ele in data:
                        message_queues.put([ele,depth])
                    s.send('done')
            else:
                #Interpret empty result as closed connection
                print "  closing", client_address
                if s in outputs :
                    outputs.remove(s)
                inputs.remove(s)
                s.close()
    for s in writable:
        try:
            next_msg = message_queues.get_nowait()
        except Queue.Empty:
            print " " , s.getpeername() , 'queue empty'
            s.send('wait')
        else:
            print " sending " , next_msg , " to ", s.getpeername()
            s.send(helper.pack(next_msg))
        outputs.remove(s)
    for s in exceptional:
        print " exception condition on ", s.getpeername()
        #stop listening for input on the connection
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()
