# 数据提取
我们让这个爬虫比每个网页中抽取一些数据，然后实现某些事情，这种做法也被称为**提取（scraping）**。
#1 数据抓取方法
- 正则表达式
- BeautifulSoup模块（流行）
- Lxml（强大）

## 1.1 正则表达式
下面是用正则表达式提取国家面积数据的例子。
正则表达式文档：https://docs.python.org/3/howto/regex.html 
```python
# -*- coding: utf-8 -*-
import urllib2
import re

def scrape(html):
    area = re.findall('<tr id="places_area__row">.*?<td\s*class=["\']w2p_fw["\']>(.*?)</td>', html)[0]
    return area

if __name__ == '__main__':
    html = urllib2.urlopen('http://example.webscraping.com/view/China-47').read()
    print scrape(html)
```
正则表达式容易适应未来网站的变化，但难以构造、可读性差，难于适应布局微小的变化。
## 1.2 BeautifulSoup模块（流行）
安装：` pip install beautifulsoup4` 
有些网页不具备良好的HTML格式，如下面HTML就存在属性两侧引号缺失和标签未闭合问题。
```html
<ul class=country>
	<li>Area
	<li>Population
</ul>
```
这样提取数据往往不能得到预期结果，但可以Beautiful Soup来处理。
```python
>>> from bs4 import BeautifulSoup
>>> brocken_html='<ul class=country><Li>Area<li>Population</ul>'
>>> soup=BeautifulSoup(brocken_html,'html.parser')
>>> fixed_html=soup.prettify()
>>> print fixed_html
<ul class="country">
 <li>
  Area
  <li>
   Population
  </li>
 </li>
</ul>
>>> 
>>> ul=soup.find('ul',attrs={'class':'country'})
>>> ul.find('li')
<li>Area<li>Population</li></li>
>>> ul.find_all('li')
[<li>Area<li>Population</li></li>, <li>Population</li>]
>>> 
```
BeautifulSoup官方文档：https://www.crummy.com/software/BeautifulSoup/bs4/doc/ 
下面是用BeautifulSoup提取国家面积数据的例子。
```python
# -*- coding: utf-8 -*-

import urllib2
from bs4 import BeautifulSoup

def scrape(html):
    soup = BeautifulSoup(html) 
    tr = soup.find(attrs={'id':'places_area__row'}) # locate the area row
    # 'class' is a special python attribute so instead 'class_' is used
    td = tr.find(attrs={'class':'w2p_fw'})  # locate the area tag
    area = td.text  # extract the area contents from this tag
    return area

if __name__ == '__main__':
    html = urllib2.urlopen('http://example.webscraping.com/view/United-Kingdom-239').read()
    print scrape(html)
```
虽然BeautifulSoup正则表达式更加复杂，但容易构造和理解，而且无须担心多余空格和标签属性这样布局上的小变化。
## 1.3 Lxml（强大）
**Lxml**是基于libxml2这个XML解析库的Python封装。该模块用C语言编写的，解析速度比Beautiful Soup更快，不过安装过程也更为复杂。最新的安装说明可以参考http://Lxml.de/installation.html 。
和Beautiful Soup一样，使用lxml模块的第一步也是将有可能不合法的HTML解析为统一格式。
```python
>>> import lxml.html
>>> broken_html='<ul class=country><li>Area<li>Population</ul>'
>>> tree=lxml.html.fromstring(broken_html) #parse the HTML
>>> fixed_html=lxml.html.tostring(tree,pretty_print=True)
>>> print fixed_html
<ul class="country">
<li>Area</li>
<li>Population</li>
</ul>
```
lxml也可以正确解析属性两侧缺失的引号，并闭合标签。解析完输入内容之后，进入选择元素的步骤，此时lxml有几种不用的方法：
- XPath选择器（类似Beautiful Soup的find()方法）
- CSS选择器（类似jQuery选择器）

这里选用**CSS选择器**，它更加简洁，也可以用在解析**动态内容**。
```python
>>> li=tree.cssselect('ul.country > li')[0]
>>> area=li.text_content()
>>> print area
Area
>>> 
```
**常见的选择器示例** 
|说明|示例|
|:---|:---|
|选择所有标签|*|
|选择`<a>`标签|a|
|选择所有`class="link"`的标签|.link|
|选择`class="link"`的`<a>`标签|a.link|
|选择`id="home"`的`<a>`标签|a#home|
|选择父元素为`<a>`标签的所有`<span>`标签|a > span|
|选择`<a>`标签内部的所有`<span>`标签|a span|
|选择title属性为"Home"的所有`<a>`标签|a[title=Home]|

下面是用CSS选择器提取国家面积数据的例子。
```Python
# -*- coding: utf-8 -*-
import urllib2
import lxml.html

def scrape(html):
    tree = lxml.html.fromstring(html)
    td = tree.cssselect('tr#places_area__row > td.w2p_fw')[0]
    area = td.text_content()
    return area

if __name__ == '__main__':
    html = urllib2.urlopen('http://127.0.0.1:8000/places/default/view/China-47').read()
    print scrape(html)
```
W3C已提出CSS3规范，其网址是http://www.w3c.org/TR/2011/REC-css3-selectors-20110929/ 。
Lxml已经实现了大部分CSS3属性，其不支持的功能可以参见http://pythonhosted.org/cssselect/#supported-selectors 。
需要注意的是，lxml在内部实现中，实际上是将CSS选择器转换为等价的XPath选择器。
# 2 性能对比
```python
# -*- coding: utf-8 -*-
import csv
import time
import urllib2
import re
import timeit
from bs4 import BeautifulSoup
import lxml.html

FIELDS = ('area', 'population', 'iso', 'country', 'capital', 'continent', 'tld', 'currency_code', 'currency_name', 'phone', 'postal_code_format', 'postal_code_regex', 'languages', 'neighbours')

def regex_scraper(html):
    results = {}
    for field in FIELDS:
        results[field] = re.search('<tr id="places_{}__row">.*?<td class="w2p_fw">(.*?)</td>'.format(field), html).groups()[0]
    return results

def beautiful_soup_scraper(html):
    soup = BeautifulSoup(html, 'html.parser') 
    results = {}
    for field in FIELDS:
        results[field] = soup.find('table').find('tr', id='places_{}__row'.format(field)).find('td', class_='w2p_fw').text
    return results

def lxml_scraper(html):
    tree = lxml.html.fromstring(html)
    results = {}
    for field in FIELDS:
        results[field] = tree.cssselect('table > tr#places_{}__row > td.w2p_fw'.format(field))[0].text_content()
    return results

def main():
    times = {}
    html = urllib2.urlopen('http://127.0.0.1:8000/places/default/view/China-47').read()
    NUM_ITERATIONS = 1000 # number of times to test each scraper
    for name, scraper in ('Regular expressions', regex_scraper), ('Beautiful Soup', beautiful_soup_scraper), ('Lxml', lxml_scraper):
        times[name] = []
        # record start time of scrape
        start = time.time()
        for i in range(NUM_ITERATIONS):
            if scraper == regex_scraper:
                # the regular expression module will cache results
                # so need to purge this cache for meaningful timings
                re.purge() 
            result = scraper(html)

            # check scraped result is as expected
            assert(result['area'] == '9596960 square kilometres')
            times[name].append(time.time() - start)
        # record end time of scrape and output the total
        end = time.time()
        print '{}: {:.2f} seconds'.format(name, end - start)

    writer = csv.writer(open('times.csv', 'w'))
    header = sorted(times.keys())
    writer.writerow(header)
    for row in zip(*[times[scraper] for scraper in header]):
        writer.writerow(row)

if __name__ == '__main__':
    main()
```
这段代码每个爬虫执行1000次，每次都有会检查结果是否正确，然后打印用时，并把所有记录存入csv文件中。正则表达式模块会用缓存搜索结果，我们用re.purge()方法清除第次的缓存。
```
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/2.数据抓取$ python 2performance.py 
Regular expressions: 6.65 seconds
Beautiful Soup: 61.61 seconds
Lxml: 8.57 seconds
```
|提取方法|性能|使用难度|安装难度|
|:---|:---:|:---:|:---:|:---|
|**正则表达式**|快|困难|简单（内置模块）|
|**Beautiful Soup**|慢|简单|简单（纯Python）|
|**Lxml**|快|简单|相对困难|
# 3 为链接爬虫添加抓取回调
要想把提取数据代码集成到上章链接爬虫代码中，我们需要添加一个回调函数callback，该函数就是调入参数处理用于提取数据行为。本例中，网页下载后调用回调函数，数据提取函数包含url和html两个参数，并返回一个待爬取的URL列表。
```python
def link_crawler(seed_url, link_regex=None,... scrape_callback=None):
	...
	html = download(url, headers, proxy=proxy, num_retries=num_retries)
	links = []
	if scrape_callback:
		links.extend(scrape_callback(url, html) or [])##这里没有返回一个待爬取的URL列表
	...
```
## 3.1 回调函数一
现在我们只需对传入的scrape_callback函数定制化处理。
```python
# -*- coding: utf-8 -*-

import csv
import re
import urlparse
import lxml.html
from link_crawler import link_crawler

FIELDS = ('area', 'population', 'iso', 'country', 'capital', 'continent', 'tld', 'currency_code', 'currency_name', 'phone', 'postal_code_format', 'postal_code_regex', 'languages', 'neighbours')

def scrape_callback(url, html):
    if re.search('/view/', url):
        tree = lxml.html.fromstring(html)
        row = [tree.cssselect('table > tr#places_{}__row > td.w2p_fw'.format(field))[0].text_content() for field in FIELDS]
        print url, row

if __name__ == '__main__':
    link_crawler('http://example.webscraping.com/', '/(index|view)', scrape_callback=scrape_callback)
```
用第一种回调输出：
```
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/2.数据抓取$ python 3scrape_callback1.py 
Downloading: http://example.webscraping.com/
Downloading: http://example.webscraping.com/index/1
...
Downloading: http://example.webscraping.com/index/25
Downloading: http://example.webscraping.com/view/Zimbabwe-252
http://example.webscraping.com/view/Zimbabwe-252 ['390,580 square kilometres', '11,651,858', 'ZW', 'Zimbabwe', 'Harare', 'AF', '.zw', 'ZWL', 'Dollar', '263', '', '', 'en-ZW,sn,nr,nd', 'ZA MZ BW ZM ']
Downloading: http://example.webscraping.com/view/Zambia-251
http://example.webscraping.com/view/Zambia-251 ['752,614 square kilometres', '13,460,305', 'ZM', 'Zambia', 'Lusaka', 'AF', '.zm', 'ZMW', 'Kwacha', '260', '#####', '^(\\d{5})$', 'en-ZM,bem,loz,lun,lue,ny,toi', 'ZW TZ MZ CD NA MW AO ']
Downloading: http://example.webscraping.com/view/Yemen-250
...
```
## 3.2 回调函数二
下面我们对功能进行扩展，把得到的结果数据保存到CSV表格中。这里我们使用了回调类，以便保持csv的writer属性的状态。csv的writer属性在构造方法中进行了实现化处理，然后在__call__方法中多次写操作。*注意，__call__是一个特殊方法，也是链接接爬虫中scrape_callback的调用方法。也就是说scrape_callback(url,html)和scrape_callback.__call__(url,html)是等价的。可以参考https://docs.python.org/3/reference/datamodel.html#special-method-names 。*。
```python
# -*- coding: utf-8 -*-

import csv
import re
import urlparse
import lxml.html
from link_crawler import link_crawler

class ScrapeCallback:
    def __init__(self):
        self.writer = csv.writer(open('countries.csv', 'w'))
        self.fields = ('area', 'population', 'iso', 'country', 'capital', 'continent', 'tld', 'currency_code', 'currency_name', 'phone', 'postal_code_format', 'postal_code_regex', 'languages', 'neighbours')
        self.writer.writerow(self.fields)

    def __call__(self, url, html):
        if re.search('/view/', url):
            tree = lxml.html.fromstring(html)
            row = []
            for field in self.fields:
                row.append(tree.cssselect('table > tr#places_{}__row > td.w2p_fw'.format(field))[0].text_content())
            self.writer.writerow(row)

if __name__ == '__main__':
    link_crawler('http://example.webscraping.com/', '/(index|view)', scrape_callback=ScrapeCallback())
```

## 3.3 复用上章的链接爬虫代码
```python
# -*- coding: utf-8 -*-
import re
import urlparse
import urllib2
import time
from datetime import datetime
import robotparser
import Queue


def link_crawler(seed_url, link_regex=None, delay=5, max_depth=-1, max_urls=-1, headers=None, user_agent='wswp', proxy=None, num_retries=1, scrape_callback=None):
    """Crawl from the given seed URL following links matched by link_regex
    """
    # the queue of URL's that still need to be crawled
    crawl_queue = [seed_url]
    # the URL's that have been seen and at what depth
    seen = {seed_url: 0}
    # track how many URL's have been downloaded
    num_urls = 0
    rp = get_robots(seed_url)
    throttle = Throttle(delay)
    headers = headers or {}
    if user_agent:
        headers['User-agent'] = user_agent

    while crawl_queue:
        url = crawl_queue.pop()
        depth = seen[url]
        # check url passes robots.txt restrictions
        if rp.can_fetch(user_agent, url):
            throttle.wait(url)
            html = download(url, headers, proxy=proxy, num_retries=num_retries)
            links = []
            if scrape_callback:
                links.extend(scrape_callback(url, html) or [])##这里没有返回一个待爬取的URL列表

            if depth != max_depth:
                # can still crawl further
                if link_regex:
                    # filter for links matching our regular expression
                    links.extend(link for link in get_links(html) if re.match(link_regex, link))

                for link in links:
                    link = normalize(seed_url, link)
                    # check whether already crawled this link
                    if link not in seen:
                        seen[link] = depth + 1
                        # check link is within same domain
                        if same_domain(seed_url, link):
                            # success! add this new link to queue
                            crawl_queue.append(link)

            # check whether have reached downloaded maximum
            num_urls += 1
            if num_urls == max_urls:
                break
        else:
            print 'Blocked by robots.txt:', url

class Throttle:
    """Throttle downloading by sleeping between requests to same domain
    """
    def __init__(self, delay):
        # amount of delay between downloads for each domain
        self.delay = delay
        # timestamp of when a domain was last accessed
        self.domains = {}
        
    def wait(self, url):
        """Delay if have accessed this domain recently
        """
        domain = urlparse.urlsplit(url).netloc
        last_accessed = self.domains.get(domain)
        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()

def download(url, headers, proxy, num_retries, data=None):
    print 'Downloading:', url
    request = urllib2.Request(url, data, headers)
    opener = urllib2.build_opener()
    if proxy:
        proxy_params = {urlparse.urlparse(url).scheme: proxy}
        opener.add_handler(urllib2.ProxyHandler(proxy_params))
    try:
        response = opener.open(request)
        html = response.read()
        code = response.code
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = ''
        if hasattr(e, 'code'):
            code = e.code
            if num_retries > 0 and 500 <= code < 600:
                # retry 5XX HTTP errors
                html = download(url, headers, proxy, num_retries-1, data)
        else:
            code = None
    return html

def normalize(seed_url, link):
    """Normalize this URL by removing hash and adding domain
    """
    link, _ = urlparse.urldefrag(link) # remove hash to avoid duplicates
    return urlparse.urljoin(seed_url, link)

def same_domain(url1, url2):
    """Return True if both URL's belong to same domain
    """
    return urlparse.urlparse(url1).netloc == urlparse.urlparse(url2).netloc

def get_robots(url):
    """Initialize robots parser for this domain
    """
    rp = robotparser.RobotFileParser()
    rp.set_url(urlparse.urljoin(url, '/robots.txt'))
    rp.read()
    return rp
        
def get_links(html):
    """Return a list of links from html 
    """
    # a regular expression to extract all links from the webpage
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    # list of all links from the webpage
    return webpage_regex.findall(html)

if __name__ == '__main__':
    link_crawler('http://example.webscraping.com', '/(index|view)', delay=0, num_retries=1, user_agent='BadCrawler')
    link_crawler('http://example.webscraping.com', '/(index|view)', delay=0, num_retries=1, max_depth=1, user_agent='GoodCrawler')
```

