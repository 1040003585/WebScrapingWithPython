# 1.网络爬虫简介
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
import urllib2

def download1(url):
    """Simple downloader"""
    return urllib2.urlopen(url).read()
```

`1.4.1download2.py`
```
import urllib2

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
**1.重试下载**
当服务器过载返回503 Service Unavailable错误，我们可以尝试重新下载。如果是404 Not Found这种错误，说明网页目前并不存在，尝试两样的请求也没有。
`1.4.1download3.py`
```
# -*- coding: utf-8 -*-

import urllib2

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

**2.设置用户代理**
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
我们从示例网址的robots.txt文件中发现的网站地图`sitemap.xml`来下载所有网页。为了解析网站地图，我们用一个简单的正则表达式从`<loc>`标签提取出URL。*下一章介绍一种更加键壮的解析方法**CSS选择器***
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

### 1.4.4跟踪网页链接
