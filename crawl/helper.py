import cPickle as pickle

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
