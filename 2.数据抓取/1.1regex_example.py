# -*- coding: utf-8 -*-

import urllib2
import re

def scrape(html):
    area = re.findall('<tr id="places_area__row">.*?<td\s*class=["\']w2p_fw["\']>(.*?)</td>', html)[0]
    return area

if __name__ == '__main__':
    html = urllib2.urlopen('http://example.webscraping.com/view/China-47').read()
    print scrape(html)
