# coding=utf8

import requests
from bs4 import BeautifulSoup
import robotexclusionrulesparser as rerp
from urlparse import urlparse, urljoin

max_len = 10000
max_depth = 6
max_cache_len = 1000
urls_scale = ['m.byr.cn']
seeds = ['http://m.byr.cn/section']
to_crawl = []
crawled = set()
cache = {'page':{}, 'list':[]}
robots_cache = {}
limit_connect_time = 1

def join_cache(cache, url, page):
    if len(cache) > max_cache_len:
        del_cache_url = cache['list'].pop(0)
        del cache['page'][del_cache_url]
    cache['page'][url] = page
    cache['list'].append(url)

def is_in_scale(url):
    parsed_url = urlparse(url)
    if parsed_url[1] in urls_scale:
	return True
    return False

def robots_pass(url, robots_cache):
    page_url = urlparse(url)
    if page_url[1] in robots_cache:
        rp = robots_cache[page_url[1]]
    else:
        base = page_url[0] + '://' + page_url[1]
        robots_url = base + '/robots.txt'
        rp = rerp.RobotExclusionRulesParser()
        try:
            rp.fetch(robots_url)
            robots_cache[page_url[1]] = rp
        except:
            print 'robots read error: %s' % robots_url
    return rp.is_allowed('*', url)


def get_page(url):
    if url in cache['page']:
        return cache['page'][url]
    else:
        try:
            r = requests.get(url, timeout=limit_connect_time)
            return r.text
        except:
            print 'get page content error, url:%s' % url
            return None

def insert_db(url, page):
    print url
    pass

def get_page_links(page, url):
    page_links = []
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

def add_to_crawl(to_crawl, page_links, depth):
    for link in page_links:
        if not is_in_scale(link):
            continue
        if not robots_pass(url, cache):
            print "robots limit: %s" % url
            continue
        if link in crawled:
            continue
        to_crawl.append([link, depth+1])

for url in seeds:
    if is_in_scale(url):
        to_crawl.append([url, 0])
if len(to_crawl) < 1:
    print "This seed is not a byr site!"
    exit


while len(to_crawl) > 0:
    url, depth = to_crawl.pop()
    if depth > max_depth:
        continue
    page = get_page(url)
    if page is None:
        continue
    insert_db(url, page)
    join_cache(cache, page,url)
    page_links = get_page_links(page, url)
    add_to_crawl(to_crawl, page_links, depth)
