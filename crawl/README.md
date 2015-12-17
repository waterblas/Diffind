# Usage


## Manual

单节点运行要求环境：
- mongodb:3.0 及以上
- python2.7
- pip

client的pymongo模块要求： `yum install python-devel`

1. 建立持久化文件存储目录和log目录，根据实际修改client和server目录下的配置文件 client.json server.json

2. 安装依赖：

```
cd cd /to/path/Diffind/crawl/server
python setup.py install

cd cd /to/path/Diffind/crawl/client
python setup.py install
```

3. 按以下顺序启动程序：

- Server

```
cd /to/path/Diffind/crawl/server
python run.py start
```


- Client

```
cd /to/path/Diffind/crawl/client
python run.py start
```

Note:  `setuptools`和`distutils.core`的package管理不一致，两者混用可能导致开发时更新出错，如果使用了`distutils`需要手工移除module(e.g. /usr/lib/python2.7/site-packages/crawlstuff), `setuptools`管理则可以通过`pip uninstall packagename`移除

若要进行***分布式***爬取试验，则需要修改 ./client/c_crawler.py 中Crawler类run方法 bloom过滤器的判断顺序