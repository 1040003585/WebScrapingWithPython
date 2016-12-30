# -*- coding: utf-8 -*-

import urllib2
import lxml.html


def scrape(html):
    tree = lxml.html.fromstring(html)
    td = tree.cssselect('tr#places_neighbours__row > td.w2p_fw')[0]
    area = td.text_content()
    return area

if __name__ == '__main__':
    html = urllib2.urlopen('http://example.webscraping.com/view/United-Kingdom-239').read()
    print scrape(html)
