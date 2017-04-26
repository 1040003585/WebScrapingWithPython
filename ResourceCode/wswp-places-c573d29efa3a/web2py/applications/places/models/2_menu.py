# -*- coding: utf-8 -*-

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.title = 'Example web scraping website'

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'Web Scraping with Python'
response.meta.keywords = 'web2py, python, web scraping'
response.meta.generator = 'Web2py Web Framework'

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    (T('Home'), False, URL('default', 'index'), []),
    (T('Search'), False, URL('default', 'search'), [])
]

