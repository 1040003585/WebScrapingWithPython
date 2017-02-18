# -*- coding: utf-8 -*-
import urllib2
import glob
import os
import cookielib
import json
import time
import lxml.html

COUNTRY_URL = 'http://127.0.0.1:8000/places/default/edit/China-47'

def login_firefox():
    """load cookies from firefox
    """
    session_filename = find_ff_sessions()
    cj = load_ff_sessions(session_filename)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    html = opener.open(COUNTRY_URL).read()

    tree = lxml.html.fromstring(html)
    print tree.cssselect('ul#navbar li a')[0].text_content()
    return opener

def load_ff_sessions(session_filename):
    cj = cookielib.CookieJar()
    if os.path.exists(session_filename):  
        try: 
            json_data = json.loads(open(session_filename, 'rb').read())
        except ValueError as e:
            print 'Error parsing session JSON:', str(e)
        else:
            for window in json_data.get('windows', []):
                for cookie in window.get('cookies', []):
                    import pprint; pprint.pprint(cookie)##########pprint
                    c = cookielib.Cookie(0, cookie.get('name', ''), cookie.get('value', ''), 
                        None, False, 
                        cookie.get('host', ''), cookie.get('host', '').startswith('.'), cookie.get('host', '').startswith('.'), 
                        cookie.get('path', ''), False,
                        False, str(int(time.time()) + 3600 * 24 * 7), False, 
                        None, None, {})
                    cj.set_cookie(c)
    else:
        print 'Session filename does not exist:', session_filename
    return cj

def find_ff_sessions():
    paths = [
        '~/.mozilla/firefox/*.default',
        '~/Library/Application Support/Firefox/Profiles/*.default',
        '%APPDATA%/Roaming/Mozilla/Firefox/Profiles/*.default'
    ]
    for path in paths:
        filename = os.path.join(path, 'sessionstore.js')
        matches = glob.glob(os.path.expanduser(filename))
        if matches:
            return matches[0]

def main():
    login_firefox()

if __name__ == '__main__':
    main()
