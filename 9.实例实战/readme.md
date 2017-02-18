#Python网络爬虫实例实战
[TOC]
- 爬取Google真实的搜索表单
- 爬取依赖JavaScript的网站Facebook
- 爬取典型在线商店Gap
- 爬取拥有地图接口的宝马官网
#1.爬Google搜索引擎
```python
# -*- coding: utf-8 -*-

import sys
import urllib
import urlparse
import lxml.html
from downloader import Downloader

def search(keyword):
    D = Downloader()
    url = 'https://www.google.com/search?q=' + urllib.quote_plus(keyword)
    html = D(url)
    tree = lxml.html.fromstring(html)
    links = []
    for result in tree.cssselect('h3.r a'):
        link = result.get('href')
        qs = urlparse.urlparse(link).query
        links.extend(urlparse.parse_qs(qs).get('q', []))
    return links

if __name__ == '__main__':
    try:
        keyword = sys.argv[1]
    except IndexError:
        keyword = 'test'
    print search(keyword)
```
*注意：提取Google搜索结果时注意爬取延时问题，否则下载速度过快会出现验证码处理。*
#2.爬Facebook和Linkein
查看Packt出版本的Facebook页面源代码时，可以找到最开始的几篇日志，但后面的日志只有浏览器滚动时才会通过AJAX加载。
- 电脑网页端：http://www.facebook.com/PacktPub 
- 移动网页端：http://m.facebook.com/PacktPub 

## 2.1自动化登录Facebook
这些AJAX的数据无法简化提取，虽然这些AJAX事件可以被卧逆向工程，但是不同类型的Facebook页面使用了不用的AJAX调用。所以下面用Selenium渲染实现自动化登录Facebook。
```python
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
```
##2.2提取Facebook的API数据
Facebook提供了一些API数据，如果允许访问这些数据，下面就提取Packt出版社页面的数据。
```python
# -*- coding: utf-8 -*-

import sys
import json
import pprint
from downloader import Downloader

def graph(page_id):
    D = Downloader()
    html = D('http://graph.facebook.com/' + page_id)
    return json.loads(html)

if __name__ == '__main__':
    try:
        page_id = sys.argv[1]
    except IndexError:
        page_id = 'PacktPub'
    pprint.pprint(graph(page_id))
```
Facebook开发者文档：https://developers.facebook.com/docs/graph-api 这些API调用多数是设计给已授权的facebook用户交互的facebook应用的，要想提取比如用户日志等更加详细的信息，仍然需要爬虫。
## 2.3自动化登录Linkedin
```python
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
```
#3.爬在线商店Gap
Gap拥有一个结构化良好的网站，通过Sitemap可以帮助网络爬虫定位到最新的内容。从http://www.gap.com/robots.txt 中可以发现网站地图Sitemap: http://www.gap.com/products/sitemap_index.html 
```xml
This XML file does not appear to have any style information associated with it. The document tree is shown below.
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<sitemap>
<loc>http://www.gap.com/products/sitemap_1.xml</loc>
<lastmod>2017-01-30</lastmod>
</sitemap>
<sitemap>
<loc>http://www.gap.com/products/sitemap_2.xml</loc>
<lastmod>2017-01-30</lastmod>
</sitemap>
</sitemapindex>
```
如上网站地图册链接的内容仅仅是索引，其索引的网站地图才是数千种产品类目的链接，比如：http://www.gap.com/products/blue-long-sleeve-shirts-for-men.jsp 。由于这里有大量要爬取的内容，因此我们将使用第4篇开发的多线和爬虫，并支持一人可选的回调参数。
```python
# -*- coding: utf-8 -*-

from lxml import etree
from threaded_crawler import threaded_crawler

def scrape_callback(url, html):
    if url.endswith('.xml'):
        # Parse the sitemap XML file
        tree = etree.fromstring(html)
        links = [e[0].text for e in tree]
        return links
    else:
        # Add scraping code here
        pass       

def main():
    sitemap = 'http://www.gap.com/products/sitemap_index.xml'
    threaded_crawler(sitemap, scrape_callback=scrape_callback)
    
if __name__ == '__main__':
    main() 
```
该回调函数首先下载到的URL扩展名。如果扩展名是.xml，则用lxml的etree模块解析XML文件并从中提取链接。否则，认为这是一个类目URL（这例没有实现提取类目的功能）。
#4.爬宝马官网
宝马官方网站中有一个查询本地经销商的搜索工具，其网址为https://www.bmw.de/de/home.html?entryType=dlo 
该工具将地理位置作为输入参数，然后在地图上显示附近的经销商地点，比如输入`Berlin`按`Look For`。
我们使用开发者工具会发现搜索触发了AJAX请求：
https://c2b-services.bmw.com/c2b-localsearch/services/api/v3/clients/BMWDIGITAL_DLO/DE/pois?country=DE&category=BM&maxResults=99&language=en&lat=52.507537768880056&lng=13.425269635701511 
`maxResults`默认设为99，我们可以增大该值。AJAX请求提供了JSONP格式的数据，其中JSONP是指**填充模式的JSON（JSON with padding）**。这里的填充通常是指要调用的函数，而函数的参数则为纯JSON数据。本例调用的是`callback`函数，要想使用Pythonr的json模块解析该数据，首先需要将填充的部分截取掉。
```python
# -*- coding: utf-8 -*-

import json
import csv
from downloader import Downloader

def main():
    D = Downloader()
    url = 'https://c2b-services.bmw.com/c2b-localsearch/services/api/v3/clients/BMWDIGITAL_DLO/DE/pois?country=DE&category=BM&maxResults=%d&language=en&lat=52.507537768880056&lng=13.425269635701511'
    jsonp = D(url % 1000) ###callback({"status:{...}"})
    pure_json = jsonp[jsonp.index('(') + 1 : jsonp.rindex(')')]
    dealers = json.loads(pure_json) ###
    with open('bmw.csv', 'w') as fp:
        writer = csv.writer(fp)
        writer.writerow(['Name', 'Latitude', 'Longitude'])
        for dealer in dealers['data']['pois']:
            name = dealer['name'].encode('utf-8')
            lat, lng = dealer['lat'], dealer['lng']
            writer.writerow([name, lat, lng])
    
if __name__ == '__main__':
    main() 
```
```python
>>> dealers.keys() #[u'status',u'count',u'data',...]
>>> dealers['count'] #显示个数
>>> dealers['data']['pois'][0] #第一个经销商数据
```

