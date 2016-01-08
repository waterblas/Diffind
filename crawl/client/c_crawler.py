# coding=utf8
'''
Created on 2015-11-20
The client program uses some sockets to put urls and get url from queue server
@author: ldy
'''
import sys
import socket
import time, threading
import requests
import Queue
from bs4 import BeautifulSoup
import robotexclusionrulesparser as rerp
from urlparse import urlparse, urljoin
from pybloom import BloomFilter
from crawlstuff import CommonHelper, TimeBomb
from db_con import MongoHelper
from commonstuff import Config
from custom_rule import excluder, limiter

# config
default_config = {
    "HOST":               "127.0.0.1",
    "PORT":               5000,
    "MONGO_HOST":         "192.168.99.100",
    "MONGO_PORT":         "32773",
    "RECV_BUFFER":        1024,
    "SERVER_BUFFER":      4096,
    "MAX_LINK_COUNT":     256,
    "PAGE_CACHE_SIZE":    5,
    "TMP_DIR":            "./tmp/",
    "BLOOM_FILE":         "bloom.pkl",
    "CRAWL_MAX_DEPTH":    999,
    "REQUEST_TIME":       5,
    "CRAWL_SCALE":        ["m.byr.cn"],
    "CRAWL_SEEDS":        ["http://m.byr.cn/section"],
    "THREADING_NUM":      3,
    "BLOOM_CAPACITY":     1000000
}

CONFIG = Config('./', default_config)
CONFIG.from_json('client.json')
helper = CommonHelper()
mongo_helper = MongoHelper(CONFIG['MONGO_HOST'], CONFIG['MONGO_PORT'])


class UrlBloom:
    '''BloomFilter: check elements repetition'''
    def __init__(self, _capacity=1000000, _error_rate=0.00001):
        self.is_full = False
        # determine if open backup bloom data by time
        if CONFIG.get('BACKUP', 0) == 1:
            self.bomb = TimeBomb(CONFIG['TMP_DIR'] + CONFIG['BLOOM_FILE'])
            self.filter = self.bomb.load()
            if self.filter is None:
                self.filter = BloomFilter(capacity=_capacity, error_rate=_error_rate)
            self.bomb.dump(self.filter)
        else:
            self.filter = BloomFilter(capacity=_capacity, error_rate=_error_rate)

    def add(self, links):
        if self.is_full:
            return
        try:
            for ele in links:
                self.filter.add(ele)
        except IndexError:
            # rasie IndexError when bloom is at capacity
            self.is_full = True


    def clean(self, links):
        res = []
        for ele in links:
            if ele not in self.filter:
                res.append(ele)
        return res


class Crawler(threading.Thread):

    '''crawl post data in m.byr.cn site'''
    def __init__(self, _scale, _bloom_obj, _connect_time=CONFIG['REQUEST_TIME'], _host=CONFIG['HOST'], _port=CONFIG['PORT'],
                 _max_depth=CONFIG['CRAWL_MAX_DEPTH'], _page_cache_size=CONFIG['PAGE_CACHE_SIZE']):
        threading.Thread.__init__(self)
        self.scale = set(_scale)
        self.connect_time = _connect_time
        self.robots_cache = {}
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client.connect((_host, _port))
        # revc throw exception beyond 2 s
        self.client.settimeout(2)
        self.max_depth = _max_depth
        self.page_cache = Queue.Queue(_page_cache_size)
        self.bloom_obj = _bloom_obj
        self.custom_excluder = excluder()
        self.custom_limiter = limiter()

    def _in_scale(self, parsed_url):
        if parsed_url[1] in self.scale:
            return True
        return False

    def _robots_pass(self, parsed_url):
        ''' keep on Robots Exclusion Protocol '''
        if parsed_url[1] in self.robots_cache:
            rp = self.robots_cache[parsed_url[1]]
        else:
            base = parsed_url[0] + '://' + parsed_url[1]
            robots_url = base + '/robots.txt'
            rp = rerp.RobotExclusionRulesParser()
            # rp.user_agent = 'byr'
            try:
                rp.fetch(robots_url, timeout=3)
            except:
                print 'robots read error: %s' % robots_url
                return True
            else:
                self.robots_cache[parsed_url[1]] = rp
        return rp.is_allowed('*', parsed_url.geturl())

    def _get_page(self, url):
        '''get the web page content based on url'''
        try:
            r = requests.get(url, timeout=self.connect_time)
            return r.text
        except:
            print 'get page content error, url:%s' % url
            return None

    def _get_page_links(self, page, url, depth):
        '''get urls in the web page'''
        page_links = set()
        if depth > self.max_depth:
            return page_links
        base = '://'.join(urlparse(url)[0:2])
        a_tags = BeautifulSoup(page).find_all('a')
        for tag in a_tags:
            link = tag.get('href')
            if link is None:
                continue
            try:
                parser = urlparse(link)
            except ValueError:
                print "urlparse error: Invalid URL"
                continue
            # 忽略网页的锚的href
            if parser[5] and not parser[2]:
                continue
            elif not parser[1]:
                link = urljoin(base, link)
            page_links.add(link)
        return page_links

    def _links_filter(self, links):
        page_links = []
        for link in links:
            parsed_url = urlparse(link)
            if self._in_scale(parsed_url) and self._robots_pass(parsed_url) and \
                not self.custom_excluder.fit(parsed_url):
                page_links.append(link)
        return page_links

    def _limit_links_size(self, links):
        ''' limit send buffer to server receive buffer '''
        end = -1
        while True:
            if sys.getsizeof(links) > CONFIG['SERVER_BUFFER'] * 0.9:
                links = links[:end]
                end -= 2
            else:
                break
        return links

    def enqueue(self, links, depth):
        '''put urls into server queue'''
        time.sleep(0.5)
        # print " %s sending %s" % (self.client.getpeername() , '|'.join(links))
        data = {'s':1, 'u':links, 'd': depth}
        # 二次握手
        num = 0
        while True:
            if num > CONFIG['MAX_LINK_COUNT']:
                break
            self.client.send(helper.pack(data))
            try:
                message = self.client.recv(CONFIG['RECV_BUFFER'])
            except:
                time.sleep(0.5)
                num += 1
            else:
                if message == 'done':
                    break

    def dequeue(self):
        '''get the url waiting for crawling from server'''
        # 二次握手
        num = 0
        while True:
            if num > CONFIG['MAX_LINK_COUNT']:
                break
            self.client.send(helper.get_url())
            try:
                data = self.client.recv(CONFIG['RECV_BUFFER'])
            except:
                num += 1
            else:
                break
        if not data:
            print "closing socket ",self.client.getpeername()
            self.client.close()
        elif data == 'wait':
            time.sleep(2)
            return None, None
        url, depth = helper.client_unpack(data)
        print " %s received %s" % (self.client.getpeername(),url)
        return url, depth

    def save_data(self, url, page):
        ''' dealt with crawled data '''
        if self.page_cache.full():
            coll = {}
            while not self.page_cache.empty():
                coll.update(self.page_cache.get())
            # insert 5 pages into data one time
            mongo_helper.insert_many(coll)
            time.sleep(1)
        self.page_cache.put({url: page})

    def run(self):
        while True:
            url, depth = self.dequeue()
            """ TODO: only crawl page that has assigned features """
            if url is None or not self.custom_limiter.fit(url):
                continue
            # if not self._in_scale(url):
            #     continue
            page = self._get_page(url)
            self.bloom_obj.add([url])
            if page is None:
                continue
            self.save_data(url, page)
            # cancel enqueue crawled url to server
            if self.bloom_obj.is_full:
                continue
            # ignore url beyond assigned depth. 
            page_links = self.bloom_obj.clean(self._links_filter(self._get_page_links(page, url, depth)))
            page_links = self._limit_links_size(page_links)
            if len(page_links) > 0:
                # annotation it if you work for distributive crawlers
                self.bloom_obj.add(page_links)
                self.enqueue(page_links, depth+1)


class CCrawler(object):
    """CCrawler Daemon for crawling web page"""
    def __init__(self):
        super(CCrawler, self).__init__()

    @staticmethod
    def _recover():
        try:
            pre_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            pre_client.connect((CONFIG['HOST'], CONFIG['PORT']))
            pre_client.send(helper.pack({'s':1, 'u':CONFIG['CRAWL_SEEDS'], 'd':0}))
            pre_client.close()
            time.sleep(1)
        except:
            print "recover initialize fail."

    def start(self):
        Bfilter = UrlBloom(_capacity=CONFIG['BLOOM_CAPACITY'])
        CCrawler._recover()
        for i in range(CONFIG['THREADING_NUM']):
            t = Crawler(CONFIG['CRAWL_SCALE'], Bfilter)
            t.setDaemon(True)
            t.start()
            time.sleep(3)
        while t.isAlive():
            time.sleep(10)
        if CONFIG.get('BACKUP', 0) == 1:
            Bfilter.bomb.stop()
        mongo_helper.close()
        print 'stop bomb threading'
