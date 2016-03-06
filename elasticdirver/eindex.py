import time
import sys
from pymongo import MongoClient
from datetime import datetime
from extractext import TagParser
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup


client = MongoClient('localhost', 27187)
db = client['byr']
coll = db['post']
cur = coll.find(no_cursor_timeout=True)
es = Elasticsearch()
total = coll.count()
num = 0
tparser = TagParser()
start_time = time.time()

for post in cur:
    url = post['url']
    content = tparser.extract(post['content'])
    soup = BeautifulSoup(post['content'], "lxml")
    try:
        title = soup.find('title').text;
    except Exception, e:
        continue
    title = (title.split('---')[0]).strip()
    es.index(
        index="index", 
        doc_type="post", 
        id=str(post['_id']),
        body={"content": content, "url": url, "title":title, "timestamp": datetime.now()}
        )
    num += 1
    if num > 5000:
        sys.stdout.write("\r%d%%" % int(num * 100.0 / total))
        sys.stdout.flush()
cur.close()

elapsed_time = time.time() - start_time
print "spend time: %s" % elapsed_time