# -*- coding: utf-8 -*-

import sys
from selenium import webdriver


def search(username, password, keyword):
    driver = webdriver.Firefox()
    driver.get('https://www.linkedin.com/')
    driver.find_element_by_id('session_key-login').send_keys(username)
    driver.find_element_by_id('session_password-login').send_keys(password)
    driver.find_element_by_id('signin').click()
    driver.implicitly_wait(30)
    driver.find_element_by_id('main-search-box').send_keys(keyword)
    driver.find_element_by_class_name('search-button').click()
    driver.find_element_by_css_selector('ol#results li a').click()
    # Add code to scrape data of interest from LinkedIn page here
    #driver.close()
 
    
if __name__ == '__main__':
    try:
        username = sys.argv[1]
        password = sys.argv[2]
        keyword = sys.argv[3]
    except IndexError:
        print 'Usage: %s <username> <password> <keyword>' % sys.argv[0]
    else:
        search(username, password, keyword)
