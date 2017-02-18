# -*- coding: utf-8 -*-
import mechanize
import login

#COUNTRY_URL = 'http://example.webscraping.com/edit/United-Kingdom-239'
COUNTRY_URL = 'http://127.0.0.1:8000/places/default/edit/China-47'

def mechanize_edit():
    """Use mechanize to increment population
    """
    # login
    br = mechanize.Browser()
    br.open(login.LOGIN_URL)
    br.select_form(nr=0)
    print br.form
    br['email'] = login.LOGIN_EMAIL
    br['password'] = login.LOGIN_PASSWORD
    response = br.submit()

    # edit country
    br.open(COUNTRY_URL)
    br.select_form(nr=0)
    print 'Population before:', br['population']
    br['population'] = str(int(br['population']) + 1)
    br.submit()

    # check population increased
    br.open(COUNTRY_URL)
    br.select_form(nr=0)
    print 'Population after:', br['population']

if __name__ == '__main__':
    mechanize_edit()
