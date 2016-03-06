# elasticdriver

elasticdriver is used to create [elasticsearch](https://www.elastic.co) index from mongodb documents crawled by crawl module.



## Prepare

### Elasticsearch Config

Download and extract [elasticsearch archive](https://www.elastic.co/downloads/elasticsearch), e.g.: elasticsearch-2.1.1.tar.gz

At root path to elasticsearch-x.x.x, change config file `vim config/elasticsearch.yml`

```
# Use a diff name for your cluster:
cluster.name: byr-application

# allow remote contact to debug, java api use 9300 port default
network.host: 0.0.0.0
```

Start elasticsearch cluster in background(Note: Don't run as root user): `bin/elasticsearch -d`

checkout cluster status

```
# Cluster Health
curl 'localhost:9200/_cat/health?v'
curl 'localhost:9200/_cat/nodes?v'
# List All Indices
curl 'localhost:9200/_cat/indices?v'
```

### IK analyzer

Use [IK analyzer](https://github.com/medcl/elasticsearch-analysis-ik) to improve Chinese segment.
After install elasticsearch-analysis-ik, run the following script to set index:

```
curl -XPOST http://localhost:9200/index/post/_mapping -d'
{
    "post": {
        "properties": {
            "content": {
                "type": "string",
                "store": "no",
                "term_vector": "with_positions_offsets",
                "analyzer": "ik_max_word",
                "search_analyzer": "ik_max_word",
                "include_in_all": "true",
                "boost": 2
            },
            "url":{
                "type": "string",
                "index": "no"
            },
            "title":{
                "type": "string",
                "store": "no",
                "term_vector": "with_positions_offsets",
                "analyzer": "ik_max_word",
                "search_analyzer": "ik_max_word",
                "include_in_all": "true",
                "boost": 6
            },
            "timestamp":{
                "type": "date"
            }
        }
    }
}'
```

## Run

elasticsearch python module is needed, use following script to test

```
from datetime import datetime
from elasticsearch import Elasticsearch
# by default we connect to localhost:9200
es = Elasticsearch()
es.index(index="my-index", doc_type="test-type", id=42, body={"any": "data", "timestamp": datetime.now()})
es.get(index="my-index", doc_type="test-type", id=42)['_source']
```


if elasticsearch python module is not installed run `pip install -r requirements.txt`, and then run `nohup python eindex.py >run.log 2>&1 &`

## Test

Test index document over, run:

```
curl -XPOST 'http://localhost:9200/index/post/_search?pretty'  -d'
{
    "query" : { "term" : { "content" : "byr" }},
    "highlight" : {
        "pre_tags" : ["<tag1>", "<tag2>"],
        "post_tags" : ["</tag1>", "</tag2>"],
        "fields" : {
            "content" : {"number_of_fragments" : 3}
        }
    },
    "_source":["url"]
}
'

curl -XPOST 'http://localhost:9200/index/post/_search?pretty'  -d'
{
    "query":{
        "multi_match" : {
            "query":    "byr", 
            "fields": [ "title", "content" ] 
        }
    },
    "highlight" : {
        "pre_tags" : ["<em>"],
        "post_tags" : ["</em>"],
        "fields" : {
            "content" : {"number_of_fragments" : 3}
        }
    },
    "_source":["url", "title"]
}
'

curl -XPOST 'http://localhost:9200/index/post/_search?pretty'  -d'
{
    "query" : { "terms" : { "content" : ["byr", "貌似"] }},
    "highlight" : {
        "pre_tags" : ["<tag1>", "<tag2>"],
        "post_tags" : ["</tag1>", "</tag2>"],
        "fields" : {
            "content" : {"number_of_fragments" : 3}
        }
    },
    "_source":["url"]
}
'
```
