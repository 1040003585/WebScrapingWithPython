# -*- coding: utf-8 -*-

import urllib2

def download2(url):
    """Download function that catches errors"""
    print 'Downloading:', url
    try:
        html = urllib2.urlopen(url).read()
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = None
    return html

download = download2

if __name__ == '__main__':
    print download('https://www.youtube.com/')
