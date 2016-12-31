# 1.网络爬虫简介
[TOC]
## 1.3背景调研
### 1.3.1检查robots.txt
http://example.webscraping.com/robots.txt
```
# section 1
User-agent: BadCrawler
Disallow: /

# section 2
User-agent: *
Crawl-delay: 5
Disallow: /trap 

# section 3
Sitemap: http://example.webscraping.com/sitemap.xml
```
- section 1 ：禁止用户代理为BadCrawler的爬虫爬取该网站，除非恶意爬虫。
- section 2 ：两次下载请求时间间隔5秒的爬取延迟。/trap 用于封禁恶意爬虫，会封禁1分钟不止。
- section 3 ：定义一个Sitemap文件，下节讲。

### 1.3.2检查网站地图
所有网页链接： http://example.webscraping.com/sitemap.xml
```
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url>
<loc>http://example.webscraping.com/view/Afghanistan-1</loc>
</url>
<url>
<loc>
http://example.webscraping.com/view/Aland-Islands-2
</loc>
</url>
...
<url>
<loc>http://example.webscraping.com/view/Zimbabwe-252</loc>
</url>
</urlset>
```
### 1.3.3估算网站大小
高级搜索参数：http://www.google.com/advanced_search 
Google搜索：`site:http://example.webscraping.com/` 有202个网页 
Google搜索：`site:http://example.webscraping.com/view` 有117个网页 
### 1.3.4识别网站所有技术
用**buildwith模块**可以检查网站构建的技术类型。
安装库：`pip install buildwith`
```
>>> import builtwith
>>> builtwith.parse('http://example.webscraping.com')
{u'javascript-frameworks': [u'jQuery', u'Modernizr', u'jQuery UI'],
 u'web-frameworks': [u'Web2py', u'Twitter Bootstrap'],
 u'programming-languages': [u'Python'],
 u'web-servers': [u'Nginx']}
>>> 
```
示例网址使用了Python的Web2py框架，还使用了JavaScript库，可能是嵌入在HTML中的。这种容易抓取。其他建构类型：
- AngularJS：内容动态加载
- ASP.NET：爬取网页要用到会话管理和表单提交。（第5章和第6章） 

### 1.3.5寻找网站所有者
用**WHOIS协议**查询域名注册者。 
文档：https://pypi.python.org/pypi/python-whois 
安装：`pip install python-whois` 
``` 
>>> import whois
>>> print whois.whois('appspot.com')
{ ......
 "name_servers": [
    "NS1.GOOGLE.COM", 
    ...
    "ns2.google.com", 
    "ns1.google.com"
  ], 
  "org": "Google Inc.", 
  "creation_date": [
    "2005-03-10 00:00:00", 
    "2005-03-09T18:27:55-0800"
  ], 
  "emails": [
    "abusecomplaints@markmonitor.com", 
    "dns-admin@google.com"
  ]
}
```
该域名归属于Google，用Google App Engine服务。*注：Google经常会阻断网络爬虫！*
## 1.4编写第一个网络爬虫
**爬取（Crawling）**一个网站的方法有很多，选用哪种方法更加合适取决于目标网站的结构。
这里先探讨如何安全地`1.4.1下载网页`，然后介绍3种爬取网站方法：
- `1.4.2爬取网站地图`；
- `1.4.3遍历每个网页的数据库ID`；
- `1.4.4跟踪网页链接`。

### 1.4.1下载网页
`1.4.1download1.py`
```
# -*- coding: utf-8 -*-

import urllib2

def download1(url):
    """Simple downloader"""
    return urllib2.urlopen(url).read()

if __name__ == '__main__':
    print download1('https://www.baidu.com')
```

`1.4.1download2.py`
```
def download2(url):
    """Download function that catches errors"""
    print 'Downloading:', url
    try:
        html = urllib2.urlopen(url).read()
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = None
    return html
```
#### 1.重试下载
当服务器过载返回503 Service Unavailable错误，我们可以尝试重新下载。如果是404 Not Found这种错误，说明网页目前并不存在，尝试两样的请求也没有。
`1.4.1download3.py`
```
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
    print download('http://httpstat.us/500')
```

**互联网工程任务组**定义了HTTP错误的完整列表：https://tools.ietf.org/html/rfc7231#section-6
- 4××：错误出现在请求存在问题 
- 5××：错误出现在服务端问题

#### 2.设置用户代理（user_agent）
默认情况下，urllib2使用`Python-urllib/2.7`作为用户代理下载网页内容的，其中2.7是Python的版本号。如果质量不加的Python网络的爬虫（上面的代码）有会造成服务器过载，一些网站还会封禁这个默认用户代理。比如，使用Python默认用户代理的情况下，访问https://www.meetup.com/，会出现：
```
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/1.网络爬虫简介$ python 1.4.1download4.py 
Downloading: https://www.meetup.com/
Download error: [Errno 104] Connection reset by peer
None
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/1.网络爬虫简介$ python 1.4.1download4.py 
Downloading: https://www.meetup.com/
Download error: Forbidden
None

```
为了下载更加可靠，我们需要设定控制用户代理，如下代码设定了一个用户代理`Wu_Being`。
```
def download4(url, user_agent='Wu_Being', num_retries=2):
    """Download function that includes user agent support"""
    print 'Downloading:', url
    headers = {'User-agent': user_agent}
    request = urllib2.Request(url, headers=headers)
    try:
        html = urllib2.urlopen(request).read()
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # retry 5XX HTTP errors
                html = download4(url, user_agent, num_retries-1)
    return html

```
### 1.4.2爬取网站地图
我们从示例网址的`robots.txt`文件中发现的网站地图`sitemap.xml`来下载所有网页。为了解析网站地图，我们用一个简单的正则表达式从`<loc>`标签提取出URL。*下一章介绍一种更加键壮的解析方法——**CSS选择器***
```
# -*- coding: utf-8 -*-

import re
from common import Download

def crawl_sitemap(url):
    # download the sitemap file
    sitemap = Download(url)
#>Downloading: http://example.webscraping.com/sitemap.xml
    # extract the sitemap links
    links = re.findall('<loc>(.*?)</loc>', sitemap)
    # download each link
    for link in links:
        html = Download(link)
        # scrape html here
        # ...
#>Downloading: http://example.webscraping.com/view/Afghanistan-1
#>Downloading: http://example.webscraping.com/view/Aland-Islands-2
#>Downloading: http://example.webscraping.com/view/Albania-3
#>......

if __name__ == '__main__':
    crawl_sitemap('http://example.webscraping.com/sitemap.xml')
```
### 1.4.3遍历每个网页的数据库ID
```
http://example.webscraping.com/view/Afghanistan-1
http://example.webscraping.com/view/China-47
http://example.webscraping.com/view/Zimbabwe-252
```
由于这些URL只有后缀不同，输入http://example.webscraping.com/view/47 也能正常显示China页面，所有我们可以遍历ID下载所有国家页面。
```1.4.3iteration_crawler1.py
import itertools
from common import Download

def iteration():
    for page in itertools.count(1):
        url = 'http://example.webscraping.com/view/-%d' % page
        #url = 'http://example.webscraping.com/view/-{}'.format(page)
        html = Download(url)
        if html is None:
            # received an error trying to download this webpage
            # so assume have reached the last country ID and can stop downloading
            break
        else:
            # success - can scrape the result
            # ...
            pass
```
如果有的ID是不连续的，爬虫到某个断点就会退出，可以修改为连续5次下载错误才会停止遍历。
```1.4.3iteration_crawler2.py
def iteration():
    max_errors = 5 # maximum number of consecutive download errors allowed
    num_errors = 0 # current number of consecutive download errors
    for page in itertools.count(1):
        url = 'http://example.webscraping.com/view/-{}'.format(page)
        html = download(url)
        if html is None:
            # received an error trying to download this webpage
            num_errors += 1
            if num_errors == max_errors:
                # reached maximum amount of errors in a row so exit
                break
            # so assume have reached the last country ID and can stop downloading
        else:
            # success - can scrape the result
            # ...
            num_errors = 0
```
有些网站不使用连续的ID，或不使用数值的ID，这个方法就难于发挥作用了。
### 1.4.4跟踪网页链接
我们需要让爬虫更像普通用户，可以跟踪链接，访问感兴趣的内容。但容易下载大量我们不需要的网页，如我们从一个论坛爬取用户账号详情页，不需要其他页面，我们则需要用`正则表达式`来确定哪个页面。
```
Downloading: http://example.webscraping.com
Downloading: /index/1
Traceback (most recent call last):
  File "1.4.4link_crawler1.py", line 29, in <module>
    link_crawler('http://example.webscraping.com', '/(index|view)')
  File "1.4.4link_crawler1.py", line 11, in link_crawler
    html = Download(url)
...
  File "/usr/lib/python2.7/urllib2.py", line 283, in get_type
    raise ValueError, "unknown url type: %s" % self.__original
ValueError: unknown url type: /index/1
```
由于`/index/1`是相对链接，浏览器可以识别，但urllib2无法知道上下文，所有我们可以用`urlparse`模块来转换为绝对链接。
```
def link_crawler(seed_url, link_regex):
    crawl_queue = [seed_url]
    seen = set(crawl_queue) # keep track which URL's have seen before
    while crawl_queue:
        url = crawl_queue.pop()
        html = Download(url)
        for link in get_links(html):
            if re.match(link_regex, link):	#匹配正则表达式
                link = urlparse.urljoin(seed_url, link)
                crawl_queue.append(link)

```
上面这段代码还是有问题，这些地点相互之间存在链接，澳大利亚链接到南极洲，南极洲链接到澳大利亚，这样爬虫就会在不断循环下载同样的内容。为了避免重复下载，修改上面函数具备存储发现URL的功能。
```
def link_crawler(seed_url, link_regex):
    """Crawl from the given seed URL following links matched by link_regex
    """
    crawl_queue = [seed_url]
    seen = set(crawl_queue) # keep track which URL's have seen before
    while crawl_queue:
        url = crawl_queue.pop()
        html = Download(url)
        for link in get_links(html):
            # check if link matches expected regex
            if re.match(link_regex, link):
                # form absolute link
                link = urlparse.urljoin(seed_url, link)
                # check if have already seen this link
                if link not in seen:
                    seen.add(link)
                    crawl_queue.append(link)
```
#### 高级功能
##### 1.解析robots.txt
robotparser模块首先加载robots.txt文件，然后通过can_fetch()函数确定指定的用户代理是否允许访问网页。
```
>>> import robotparser
>>> rp=robotparser.RobotFileParser()
>>> rp.set_url('http://example.webscraping.com/robots.txt')
>>> rp.read()
>>> url='http://example.webscraping.com'
>>> user_agent='BadCrawler'
>>> rp.can_fetch(user_agent,url)
False
>>> user_agent='GoodCrawler'
>>> rp.can_fetch(user_agent,url)
True
>>> user_agent='Wu_Being'
>>> rp.can_fetch(user_agent,url)
True
```
为了将该功能集成到爬虫中，我们需要在crawl循环中添加该检查。
```
    while crawl_queue:
	url = crawl_queue.pop()
	# check url passes robots.txt restrictions
	if rp.can_fetch(user_agent, url):
	    ...
	else:
	    print 'Blocked by robots.txt:', url

```
##### 2.支持代理（Proxy）
有时我们需要使用代理访问某个网站。比如Netflix屏蔽美国以外的大多数国家。使用urllib2支持代理没有想象中那么容易（可以尝试用更好友的Python HTTP模块`requests`来实现这个功能，文档：http://docs.python-requests.org）。下面是使用urllib2支持代理的代码。
```
def download5(url, user_agent='wswp', proxy=None, num_retries=2):
    """Download function with support for proxies"""
    print 'Downloading:', url
    headers = {'User-agent': user_agent}
    request = urllib2.Request(url, headers=headers)
    opener = urllib2.build_opener()
    if proxy:
        proxy_params = {urlparse.urlparse(url).scheme: proxy}
        opener.add_handler(urllib2.ProxyHandler(proxy_params))
    try:
        html = opener.open(request).read()
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code < 600:
                # retry 5XX HTTP errors
                html = download5(url, user_agent, proxy, num_retries-1)
    return html
```
##### 3.下载限速
当我们爬取的网站过快，可能会被封禁或造成服务器过载的风险。为了降低这些风险，我们可以在两次下载之间添加延时，从而对爬虫限速。
```
class Throttle:
    """Throttle downloading by sleeping between requests to same domain
    """
    def __init__(self, delay):
        # amount of delay between downloads for each domain
        self.delay = delay
        # timestamp of when a domain was last accessed
        self.domains = {}
        
    def wait(self, url):
        domain = urlparse.urlparse(url).netloc
        last_accessed = self.domains.get(domain)

        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.now()
```
Throttle类记录每个上次访问的时间，如果当前时间距离上次访问时间小于指定延时，则执行睡眠操作。我们可以在每次下载之前调用Throttle对爬虫进行限速。
```
throttle = Throttle(delay)
...
throttle.wait(url)
html = download(url, headers, proxy=proxy, num_retries=num_retries)
```
##### 4.避免爬虫陷阱
想要避免陷入爬虫陷阱，一人简单的方法就是记录到达当前网页经过了多少个链接，也就是**深度**。当达到最大尝试就不再向队列中添加该网页中的链接了，我们需要修改seen变量为一个字典，增加页面尝试的记录。如果想禁用该功能，只需将max_depth设为一个负数即可。
```
def link_crawler(..., max_depth=2):
    seen = {seed_url: 0}
    ...
    depth = seen[url]
    if depth != max_depth:
        for link in links:
            if link not in seen:
                seen[link] = depth + 1
                crawl_queue.append(link)
```
##### 5.最终版本
`1.4.4link_crawler4_UltimateVersion.py`
```
import re
import urlparse
import urllib2
import time
from datetime import datetime
import robotparser
import Queue


def link_crawler(seed_url, link_regex=None, delay=5, max_depth=-1, max_urls=-1, headers=None, user_agent='wswp', proxy=None, num_retries=1):
    """Crawl from the given seed URL following links matched by link_regex
    """
    # the queue of URL's that still need to be crawled
    crawl_queue = Queue.deque([seed_url])
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
        # check url passes robots.txt restrictions
        if rp.can_fetch(user_agent, url):
            throttle.wait(url)
            html = download(url, headers, proxy=proxy, num_retries=num_retries)
            links = []

            depth = seen[url]
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
        domain = urlparse.urlparse(url).netloc
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
                return download(url, headers, proxy, num_retries-1, data)
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
    link_crawler('http://example.webscraping.com', '/(index|view)', delay=0, num_retries=1, max_depth=3, user_agent='GoodCrawler')

```

