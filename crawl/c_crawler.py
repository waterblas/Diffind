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
from bs4 import BeautifulSoup
import robotexclusionrulesparser as rerp
from urlparse import urlparse, urljoin
from pybloom import BloomFilter
from helper import CommonHelper


class UrlFilter:
    '''BloomFilter: check elements repetition'''
    def __init__(self, _capacity=50000, _error_rate=0.01):
        self.filter = BloomFilter(capacity=_capacity, error_rate=_error_rate)

    def add(self, links):
        for ele in links:
            self.filter.add(ele)

    def check(self, links):
        res = []
        for ele in links:
            if ele not in self.filter:
                res.append(ele)
        return res


HOST = '127.0.0.1'
PORT = 5000
RECV_BUFFER = 1024
SERVER_BUFFER = 4096
MAX_LINK_TIME = 256
helper = CommonHelper()
Bfilter = UrlFilter()

class Crawler(threading.Thread):
    '''crawl post data in m.byr.cn site'''
    def __init__(self, _scale, _connect_time=5, _host=HOST, _port=PORT, _max_depth=999):
        threading.Thread.__init__(self)
        self.scale = _scale
        self.connect_time = _connect_time
        self.robots_cache = {}
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client.connect((_host, _port))
        # revc throw exception beyond 2 s
        self.client.settimeout(2)
        self.max_depth = _max_depth

    def _in_scale(self, url):
        parsed_url = urlparse(url)
        if parsed_url[1] in self.scale:
            return True
        return False

    def _robots_pass(self, url):
        ''' keep on Robots Exclusion Protocol '''
        page_url = urlparse(url)
        if page_url[1] in self.robots_cache:
            rp = self.robots_cache[page_url[1]]
        else:
            base = page_url[0] + '://' + page_url[1]
            robots_url = base + '/robots.txt'
            rp = rerp.RobotExclusionRulesParser()
            # rp.user_agent = 'byr'
            try:
                rp.fetch(robots_url)
                self.robots_cache[page_url[1]] = rp
            except:
                print 'robots read error: %s' % robots_url
        return rp.is_allowed('*', url)

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
        page_links = []
        if depth > self.max_depth:
            return page_links
        base = '://'.join(urlparse(url)[0:2])
        a_tags = BeautifulSoup(page).find_all('a')
        for tag in a_tags:
            link = tag.get('href')
            if link is None:
                continue
            parser = urlparse(link)
            # 忽略网页的锚的href
            if parser[5] and not parser[2]:
                continue
            elif not parser[1]:
                link = urljoin(base, link)
            if self._robots_pass(link):
                page_links.append(link)
        return page_links

    def enqueue(self, links, depth):
        '''put urls into server queue'''
        time.sleep(0.5)
        print " %s sending %s" % (self.client.getpeername() , '|'.join(links))
        data = {'s':1, 'u':links, 'd': depth}
        # 二次握手
        while True:
            self.client.send(helper.pack(data))
            try:
                message = self.client.recv(RECV_BUFFER)
            except:
                time.sleep(0.5)
            else:
                if message == 'done':
                    break
        
    def dequeue(self):
        '''get the url waiting for crawling from server'''
        time.sleep(0.5)
        # 二次握手
        num = 0
        while True:
            if num > MAX_LINK_TIME:
                break
            self.client.send(helper.get_url())
            try:
                data = self.client.recv(RECV_BUFFER)
            except:
                num += 1
            else:
                break
        if not data:
            print "closing socket ",self.client.getpeername()
            self.client.close()
        elif data == 'wait':
            time.sleep(2)
        url, depth = helper.client_unpack(data)
        print " %s received %s" % (self.client.getpeername(),url)
        return url, depth

    def run(self):
        while True:
            url, depth = self.dequeue()
            if not self._in_scale(url):
                continue
            page = self._get_page(url)
            Bfilter.add([url])
            if page is None:
                continue
            # ignore url beyond assigned depth
            page_links = Bfilter.check(self._get_page_links(page, url, depth))
            # limit send buffer to server receive buffer
            end = -1
            while True:
                if sys.getsizeof(page_links) > SERVER_BUFFER * 0.9:
                    page_links = page_links[:end]
                    end -= 2
                else:
                    break
            if len(page_links) > 0:
                Bfilter.add(page_links)
                self.enqueue(page_links, depth+1)

if __name__ == '__main__':
    urls_scale = ['m.byr.cn']
    seeds = ['http://m.byr.cn/section']
    Bfilter.add(seeds)
    pre_client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    pre_client.connect((HOST, PORT))
    pre_client.send(helper.pack({'s':1, 'u':seeds, 'd':0}))
    pre_client.close()
    for i in range(3):
        time.sleep(0.5)
        t = Crawler(urls_scale)
        t.start()



