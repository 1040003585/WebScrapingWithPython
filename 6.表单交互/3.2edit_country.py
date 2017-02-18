# -*- coding: utf-8 -*-
import urllib
import urllib2
import login

#COUNTRY_URL = 'http://example.webscraping.com/edit/United-Kingdom-239'
COUNTRY_URL = 'http://127.0.0.1:8000/places/default/edit/China-47'
	
def edit_country():
    opener = login.login_cookies()
    country_html = opener.open(COUNTRY_URL).read()
    data = login.parse_form(country_html)
    import pprint; pprint.pprint(data)
    print 'Population before: ' + data['population']
    data['population'] = int(data['population']) + 1
    encoded_data = urllib.urlencode(data)
    request = urllib2.Request(COUNTRY_URL, encoded_data)
    response = opener.open(request)

    country_html = opener.open(COUNTRY_URL).read()
    data = login.parse_form(country_html)
    print 'Population after:', data['population']

if __name__ == '__main__':
    edit_country()
