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
from crawlstuff import CommonHelper, TimeBomb
from commonstuff import Config

# config
default_config = {
    "HOST":         "127.0.0.1",
    "PORT":         5000,
    "RECV_BUFFER":  4096,     # transfer close: beyond limit
    "TMP_DIR":      "./tmp/",
    "QUEUE_FILE":   "queue.pkl",
    "TIME_OUT":      60           # a option: parameter for select is TIMEOUT
}

CONFIG = Config('./', default_config)
CONFIG.from_json('server.json')
TAG_GET = 0
TAG_PUT = 1

class SQueue(object):
    """ queue server to listen request """
    def __init__(self):
        super(SQueue, self).__init__()
        #create a socket
        self.server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.server.setblocking(0)
        #set option reused
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR  , 1)
        self.server.bind((CONFIG['HOST'], CONFIG['PORT']))
        self.server.listen(10)
        #sockets from which we except to read
        self.inputs = [self.server]
        #sockets from which we expect to write
        self.outputs = []
        #Outgoing message queues
        # determine if open backup queue data by time
        if CONFIG.get('BACKUP', 0) == 1:
            self.bomb = TimeBomb(CONFIG['TMP_DIR'] + CONFIG['QUEUE_FILE'], True)
            self.message_queues = self.bomb.q_load()
            self.bomb.q_dump(self.message_queues)
        else:
            self.message_queues = Queue.Queue()
        self.helper = CommonHelper()

    def start(self):
        while self.inputs:
            if CONFIG.get('BACKUP', 0) == 1 and (not self.bomb.is_sleep):
                time.sleep(10)
            print "waiting for next event"
            readable , writable , exceptional = select.select(self.inputs, self.outputs, self.inputs, CONFIG['TIME_OUT'])
            for s in readable :
                if s is self.server:
                    # A "readable" socket is ready to accept a connection
                    connection, client_address = s.accept()
                    print "    connection from ", client_address
                    connection.setblocking(0)
                    self.inputs.append(connection)
                else:
                    data = s.recv(CONFIG['RECV_BUFFER'])
                    if data:
                        tag, data, depth = self.helper.server_unpack(data)
                        if tag == TAG_GET:
                        # Add output channel for response
                            # print " received a request for url"
                            if s not in self.outputs :
                                self.outputs.append(s)
                        elif tag == TAG_PUT:
                            print " received " , data , "from ",s.getpeername()
                            for ele in data:
                                self.message_queues.put([ele,depth])
                            s.send('done')
                    else:
                        #Interpret empty result as closed connection
                        print "  closing", client_address
                        if s in self.outputs :
                            self.outputs.remove(s)
                        self.inputs.remove(s)
                        s.close()
            for s in writable:
                try:
                    next_msg = self.message_queues.get_nowait()
                except Queue.Empty:
                    print " " , s.getpeername() , 'queue empty'
                    s.send('wait')
                else:
                    print " sending " , next_msg , " to ", s.getpeername()
                    s.send(self.helper.pack(next_msg))
                self.outputs.remove(s)
            for s in exceptional:
                print " exception condition on ", s.getpeername()
                #stop listening for input on the connection
                self.inputs.remove(s)
                if s in self.outputs:
                    self.outputs.remove(s)
                s.close()
 