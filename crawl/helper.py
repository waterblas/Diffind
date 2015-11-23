import struct

class CommonHelper:
    def __init__(self, _fmt='i'):
        self.fmt = _fmt

    def pack(self, s):
        return struct.pack(self.fmt, len(s)) + s

    def unpack(self, s):
        size = struct.calcsize(self.fmt)
        try:
            temp = struct.unpack(self.fmt, s[:size])
            data = s[size:]
        except:
            tag, data = -1, ''
        else:
            tag = temp[0] if len(temp) > 0 else 0
        return tag, data

    def get_url(self):
        return self.pack('')
