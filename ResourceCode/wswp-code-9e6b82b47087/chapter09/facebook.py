# -*- coding: utf-8 -*-

import sys
from selenium import webdriver


def facebook(username, password, url):
    driver = webdriver.Firefox()
    driver.get('https://www.facebook.com')
    driver.find_element_by_id('email').send_keys(username)
    driver.find_element_by_id('pass').send_keys(password)
    driver.find_element_by_id('login_form').submit()
    driver.implicitly_wait(30)
    # wait until the search box is available,
    # which means have succrssfully logged in
    search = driver.find_element_by_id('q')
    # now are logged in so can navigate to the page of interest
    driver.get(url)
    # add code to scrape data of interest here
    #driver.close()
 
    
if __name__ == '__main__':
    try:
        username = sys.argv[1]
        password = sys.argv[2]
        url = sys.argv[3]
    except IndexError:
        print 'Usage: %s <username> <password> <url>' % sys.argv[0]
    else:
        facebook(username, password, url)
