# -*- coding: utf-8 -*-

import re
from common import Download


def crawl_sitemap(url):
    # download the sitemap file
    sitemap = Download(url)
#>Downloading: http://example.webscraping.com/sitemap.xml
    # extract the sitemap links
    links = re.findall('<loc>(.*?)</loc>', sitemap)
    # download each link
    for link in links:
        html = Download(link)
        # scrape html here
        # ...
#>Downloading: http://example.webscraping.com/view/Afghanistan-1
#>Downloading: http://example.webscraping.com/view/Aland-Islands-2
#>Downloading: http://example.webscraping.com/view/Albania-3
#>......


if __name__ == '__main__':
    crawl_sitemap('http://example.webscraping.com/sitemap.xml')
