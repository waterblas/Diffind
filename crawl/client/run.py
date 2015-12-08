import sys
from c_crawler import CCrawler
from commonstuff import Daemon


class SubDaemon(Daemon):
    def run(self):
		a = CCrawler()
		a.start()


if __name__ == '__main__':
    daemon = SubDaemon('/tmp/daemon-crawl-client.pid', '/dev/null', 
    	'./logs/debug.log', './logs/error.log')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)