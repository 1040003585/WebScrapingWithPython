# -*- coding: utf-8 -*-

import urllib2

def download1(url):
    """Simple downloader"""
    return urllib2.urlopen(url).read()

if __name__ == '__main__':
    print download1('https://www.baidu.com')
