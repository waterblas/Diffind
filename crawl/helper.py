import cPickle as pickle

class CommonHelper:
    def __init__(self, _fmt='i'):
        self.fmt = _fmt

    def pack(self, _dict):
        # _dict: {'s':0,'d':['a','b']}
        return pickle.dumps(_dict, -1)  

    def unpack(self, s):
        try:
            ele = pickle.loads(s)
            tag = ele.get('s', -1)
        except:
            tag, ele = -1, {}
        counter = ele.get('c', 0)
        data = ele.get('d', [])
        return tag, data, counter

    def get_url(self):
        return self.pack({'s':0, 'd':[]})
