import threading
import cPickle as pickle
import time

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


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

class TimeBomb:
    '''save crawler Bloom Filter or server queue at regular time'''
    def __init__(self, _path='./tmp/', _time=6):
        self.file_path = _path
        self.sleep_time = _time
        self.killall = False

    @threaded
    def dump(self, b):
        while True:
            time.sleep(self.sleep_time)
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
