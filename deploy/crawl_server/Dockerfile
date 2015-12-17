FROM centos:latest
MAINTAINER ldy

WORKDIR /mnt
RUN mkdir logs backup
VOLUME /mnt/logs

WORKDIR /code
ADD ./server.tar.gz /code
# RUN tar -xvzf /code/server.tar.gz
COPY ./server.json /code/crawl/server

# RUN yum check-update && yum install -y python-pip
ADD https://bootstrap.pypa.io/get-pip.py ./
RUN python get-pip.py

WORKDIR crawl/server
RUN python setup.py install

EXPOSE 5000
CMD python run.py >/mnt/logs/debug.log 2>/mnt/logs/error.log