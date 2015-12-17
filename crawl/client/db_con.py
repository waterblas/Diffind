import sys
from pymongo import MongoClient, errors
from datetime import datetime

class MongoHelper:
    def __init__(self, _host, _port, _db='byr', _coll='post'):
        self.client = MongoClient("mongodb://%s:%s" % (_host, _port))
        self.db = self.client[_db]
        self.coll = self.db[_coll]
        self._prepare()

    def __remove(self):
        self.coll.drop()

    def _prepare(self):
        try:
            self.coll.create_index("url", unique=True)
        except Exception, e:
            print "error info: %s" % e
            sys.exit(1)
            raise

    def close(self):
        self.client.close()

    def insert_one(self, _url, _content):
        try:
            self.coll.insert_one({
                "url": _url,
                "content": _content,
                "created": datetime.now(),
                "updated": datetime.now()
            })
        except errors.DuplicateKeyError:
            self.coll.update_one(
                {"url": _url},
                {
                    "$set": {"content": _content},
                    "$currentDate": {"updated": True}
                }
            )
        except:
            print "insert error"

    def insert_many(self, _dict):
        try:
            _list = [{"url": k, "content": v, "created": datetime.now(), \
                      "updated":datetime.now()} for k,v in _dict.iteritems()]
            self.coll.insert_many(_list)
        except errors.BulkWriteError:
            for k,v in _dict.iteritems():
                self.insert_one(k, v)
        except:
            print "bulk insert error"
