tar -cvzf server.tar.gz ../crawl/commonstuff ../crawl/server ../crawl/crawlstuff
tar -cvzf client.tar.gz ../crawl/commonstuff ../crawl/client ../crawl/crawlstuff
mv -f server.tar.gz ./crawl_server
mv -f client.tar.gz ./crawl_client
echo "files ready...start compose..."
docker-compose up -d


