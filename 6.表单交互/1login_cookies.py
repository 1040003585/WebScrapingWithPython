# -*- coding: utf-8 -*-
import urllib
import urllib2
import cookielib
import lxml.html

LOGIN_EMAIL = '1040003585@qq.com'
LOGIN_PASSWORD = 'wu.com'
#LOGIN_URL = 'http://example.webscraping.com/user/login'
LOGIN_URL = 'http://127.0.0.1:8000/places/default/user/login'


def login_basic():
    """fails because not using formkey
    """
    data = {'email': LOGIN_EMAIL, 'password': LOGIN_PASSWORD}
    encoded_data = urllib.urlencode(data)
    request = urllib2.Request(LOGIN_URL, encoded_data)
    response = urllib2.urlopen(request)
    print response.geturl()

def login_formkey():
    """fails because not using cookies to match formkey
    """
    html = urllib2.urlopen(LOGIN_URL).read()
    data = parse_form(html)
    data['email'] = LOGIN_EMAIL
    data['password'] = LOGIN_PASSWORD
    encoded_data = urllib.urlencode(data)
    request = urllib2.Request(LOGIN_URL, encoded_data)
    response = urllib2.urlopen(request)
    print response.geturl()

def login_cookies():
    """working login
    """
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    html = opener.open(LOGIN_URL).read()
    data = parse_form(html)
    data['email'] = LOGIN_EMAIL
    data['password'] = LOGIN_PASSWORD
    encoded_data = urllib.urlencode(data)
    request = urllib2.Request(LOGIN_URL, encoded_data)
    response = opener.open(request)
    print response.geturl()
    return opener

def parse_form(html):
    """extract all input properties from the form
    """
    tree = lxml.html.fromstring(html)
    data = {}
    for e in tree.cssselect('form input'):
        if e.get('name'):
            data[e.get('name')] = e.get('value')
    return data

def main():
    #login_basic()
    #login_formkey()
    login_cookies()

if __name__ == '__main__':
    main()
