# Usage


## Manual
按以下顺序启动程序

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