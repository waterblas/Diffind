FROM centos:latest
MAINTAINER ldy

WORKDIR /data/client
RUN mkdir logs backup
VOLUME /data/client

WORKDIR /code
ADD ./client.tar.gz /code
# RUN tar -xvzf client.tar.gz
COPY ./client.json /code/crawl/client

# RUN yum check-update && yum install -y python-pip
ADD https://bootstrap.pypa.io/get-pip.py ./
RUN python get-pip.py
RUN yum install -y gcc python-devel

WORKDIR crawl/client
RUN python setup.py install

CMD python run.py >/data/client/logs/debug.log 2>/data/client/logs/error.log