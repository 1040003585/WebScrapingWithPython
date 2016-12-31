# -*- coding: utf-8 -*-


import itertools
from common import Download

def iteration():
    for page in itertools.count(1):
        url = 'http://example.webscraping.com/view/-%d' % page
        #url = 'http://example.webscraping.com/view/-{}'.format(page)
        html = Download(url)
        if html is None:
            # received an error trying to download this webpage
            # so assume have reached the last country ID and can stop downloading
            break
        else:
            # success - can scrape the result
            # ...
            pass


if __name__ == '__main__':
    iteration()
