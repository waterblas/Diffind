# Diffind

A search engine with common crawler, index engine and [**Docker**](https://www.docker.com/) deploy support data to [diffind-web](https://github.com/waterblas/diffind-web) in backgroud. It contain four module: crawl, deploy, elasticdriver and index.

## Crawl
The crawl module is a small commom crawler at search engine pattern. It is divided into server and client to support distributed crawler. 

### Server
Server work as message queue in fact, distributing url to clients as task to crawl and collecting new url to put into queue. It achieve nonblocking I/O by using **Select**, and consider **data disaster tolerance**.

change `crawl/server/server.json` config file

```
{
    "HOST":         "127.0.0.1",    // server host
    "PORT":         5000,           // server socket port
    "RECV_BUFFER":  4096,           // the biggest data receive from client in every sending
    "TMP_DIR":      "../backup/",   // backup file dir for queue initialization to continue
    "TIME_OUT":      60,            // parameter for select TIMEOUT
    "LOG_PATH":     "./logs/",      // logs file path
    "BACKUP":       1               // open backup for data disaster tolerance
}
```

### Client
Each client work as independent crawler to crawl page, save into database and communicate with Server by Sockect. It has the followings demanding attention:

- use mongoDB to save the crawled data;
- use bloom filter to measure if a link need to put into queue;
- each client use three **multi-thread** to crawl by default;


```
{
    ...

    "MAX_LINK_COUNT":       256,                // times reconnection to server when no reply
    "PAGE_CACHE_SIZE":      5,                  // write cache in db once time
    "BLOOM_FILE":           "bloom.pkl",        // backup file for bloom filter
    "CRAWL_MAX_DEPTH":      999,                // crawl depth based on seed url
    "REQUEST_TIME":         5,                  // request timeout for each crawling
    "CRAWL_SCALE":          ["m.byr.cn"],       // limit scale for crawling
    "CRAWL_SEEDS":          ["http://m.byr.cn/section"],    // initial seeds url
    "THREADING_NUM":        3,
    "BLOOM_CAPACITY":       3000000             // bloom filter capacity
}
```
### Manual

For manual deploy detail see `crawl` module dir.


## Deploy

I provide docker to deploy, more convenient and fast. 

Requirement:

- docker >= 1.9.1
- docker-compose


Docker can get from [docker.com](https://www.docker.com/), docker-compose installtion: `pip install -U docker-compose`

and then at the path of deploy module dir, run

```
./deploy.sh
```

## Elasticdriver

This module main work is to extract useful info from mixed web page contain and to index documment into [Elasticsearch](https://www.elastic.co/) engine, For more detail see `elasticdriver` module dir.

## License
Copyright (c) 2015 Donvan

Licensed under the Mozilla Public License Version 2.0,
You may obtain a copy of the License at [MPL](https://www.mozilla.org/en-US/MPL/2.0/).

