# -*- coding: utf-8 -*-

import urllib2

def download3(url, num_retries=2):
    """Download function that also retries 5XX errors"""
    print 'Downloading:', url
    try:
        html = urllib2.urlopen(url).read()
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # retry 5XX HTTP errors
                html = download3(url, num_retries-1)
    return html

download = download3


if __name__ == '__main__':
    print download('http://httpstat.us/500',10)
