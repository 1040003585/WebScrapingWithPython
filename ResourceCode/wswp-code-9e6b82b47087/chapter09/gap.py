# -*- coding: utf-8 -*-

from lxml import etree
from threaded_crawler import threaded_crawler


def scrape_callback(url, html):
    if url.endswith('.xml'):
        # Parse the sitemap XML file
        tree = etree.fromstring(html)
        links = [e[0].text for e in tree]
        return links
    else:
        # Add scraping code here
        pass
        

def main():
    sitemap = 'http://www.gap.com/products/sitemap_index.xml'
    threaded_crawler(sitemap, scrape_callback=scrape_callback)

    
if __name__ == '__main__':
    main() 
