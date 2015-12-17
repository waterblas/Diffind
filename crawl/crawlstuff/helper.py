import threading
import cPickle as pickle
import time
import Queue

class CommonHelper:
    def __init__(self, _fmt='i'):
        self.fmt = _fmt

    def pack(self, _d):
        # _dict: {'s':0,'u':['a','b'], 'd':1}
        # _list: [url, depth]
        return pickle.dumps(_d, -1)

    def server_unpack(self, s):
        try:
            ele = pickle.loads(s)
            tag = ele.get('s', -1)
        except:
            tag, ele = -1, {}
        depth = ele.get('d', 0)
        data = ele.get('u', [])
        return tag, data, depth

    def client_unpack(self, s):
        try:
            url, depth = pickle.loads(s)
        except:
            url, depth = '', 0
            print 'client unpack error:' + s
        return url, depth

    def get_url(self):
        return self.pack({'s':0, 'u':[], 'd':0})

def threaded(_daemon):
    def makedaemon(fn):
        def wrapper(*args, **kwargs):
            th = threading.Thread(target=fn, args=args, kwargs=kwargs)
            th.daemon = _daemon
            th.start()
        return wrapper
    return makedaemon

def qdumper(q):
    while True:
        try:
            yield q.get(False)
        except Queue.Empty:
            break


class TimeBomb:
    '''save crawler Bloom Filter or server queue at regular time'''
    def __init__(self, _path='./tmp/', _daemon=False, _time=600):
        self.file_path = _path
        self.sleep_time = _time
        self.killall = False
        self.sleep = True
        self.daemon = _daemon

    @threaded(False)
    def dump(self, b):
        while True:
            time.sleep(self.sleep_time * 1.5)
            with open(self.file_path, 'w') as f_in:
                pickle.dump(b, f_in)
            if self.killall:
                break

    def load(self):
        res = None
        try:
            with open(self.file_path, 'r') as f_out:
                res = pickle.load(f_out)
        except IOError:
            print '%s not exist' % self.file_path
        return res

    def stop(self):
        self.killall = True

    def is_sleep(self):
        return self.sleep

    @threaded(True)
    def q_dump(self, q):
        while True:
            self.sleep = True
            time.sleep(self.sleep_time)
            self.sleep = False
            remaining = [item for item in qdumper(q)]
            with open(self.file_path, 'w') as f_in:
                pickle.dump(remaining, f_in)
            for item in remaining:
                q.put(item)

    def q_load(self):
        coll = self.load() or []
        q = Queue.Queue()
        for item in coll:
            q.put(item)
        return q
