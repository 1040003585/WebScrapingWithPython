# -*- coding: utf-8 -*-

from link_crawler import link_crawler
#from crawler import crawler
from mongo_cache import MongoCache
from alexa_cb import AlexaCallback

def main():
    scrape_callback = AlexaCallback()
    cache = MongoCache()
    #cache.clear()
    link_crawler(scrape_callback.seed_url, scrape_callback=scrape_callback, cache=cache, timeout=10, ignore_robots=True)
    #crawler(scrape_callback.seed_url, scrape_callback=scrape_callback, cache=cache, timeout=10, ignore_robots=True)

if __name__ == '__main__':
    main()
