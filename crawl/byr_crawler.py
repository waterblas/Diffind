# coding=utf8

import requests
from bs4 import BeautifulSoup
import robotexclusionrulesparser as rerp
from urlparse import urlparse, urljoin


class Crawler:
    '''crawl post data in m.byr.cn site'''

    to_crawl = []
    crawled = set()
    robots_cache = {}

    def __init__(self, _scale, _seeds, _connect_time=1, _max_len=10000, _max_depth=3):
        self.scale = _scale
        self.seeds = _seeds
        self.connect_time = _connect_time
        self.max_len = _max_len
        self.max_depth = _max_depth

    def _in_scale(self, url):
        parsed_url = urlparse(url)
        if parsed_url[1] in self.scale:
	    return True
        return False

    def _robots_pass(self, url):
        page_url = urlparse(url)
        if page_url[1] in self.robots_cache:
            rp = self.robots_cache[page_url[1]]
        else:
            base = page_url[0] + '://' + page_url[1]
            robots_url = base + '/robots.txt'
            rp = rerp.RobotExclusionRulesParser()
            rp.user_agent = 'byr'
            try:
                rp.fetch(robots_url)
                self.robots_cache[page_url[1]] = rp
            except:
                print 'robots read error: %s' % robots_url
        return rp.is_allowed('*', url)

    def _get_page(self, url):
        try:
            r = requests.get(url, timeout=self.connect_time)
            return r.text
        except:
            print 'get page content error, url:%s' % url
            return None

    def _get_page_links(self, page, url, depth):
        page_links = []
        if depth >= self.max_depth:
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
            elif parser[1]:
                page_links.append(link)
            else:
                page_links.append(urljoin(base, link))
        return page_links

    def _add_to_crawl(self, page_links, depth):
        for link in page_links:
            if not self._in_scale(link):
                continue
            if not self._robots_pass(link):
                try:
                    print "robots limit: %s" % link
                except:
                    print "robots limit: %s" % link.encode('utf-8')
                continue
            if link in self.crawled:
                continue
            self.to_crawl.append([link, depth+1])

    def run(self):
        for url in self.seeds:
            if self._in_scale(url):
                self.to_crawl.append([url, 0])
        if len(self.to_crawl) < 1:
            print "These seed are not in scale!"
            exit
        while len(self.to_crawl) > 0:
            url, depth = self.to_crawl.pop(0)
            page = self._get_page(url)
            if page is None:
                continue
            insert_db(url, page)
            page_links = self._get_page_links(page, url, depth)
            self._add_to_crawl(page_links, depth)


def insert_db(url, page):
    print url
    pass

if __name__ == '__main__':
    urls_scale = ['m.byr.cn']
    seeds = ['http://m.byr.cn/section']
    byr_c = Crawler(urls_scale, seeds)
    byr_c.run()


