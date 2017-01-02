# -*- coding: utf-8 -*-

import urllib2
import lxml.html


def scrape(html):
    tree = lxml.html.fromstring(html)
    td = tree.cssselect('tr#places_area__row > td.w2p_fw')[0]
    area = td.text_content()
    return area

if __name__ == '__main__':
    html = urllib2.urlopen('http://127.0.0.1:8000/places/default/view/China-47').read()
    print scrape(html)
