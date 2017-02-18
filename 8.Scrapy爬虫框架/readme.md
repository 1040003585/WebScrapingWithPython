# Scrapy 爬虫框架
[TOC]
# 1.安装Scrapy
用pip命令安装Scrapy：`pip install Scrapy`
```python
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython$ scrapy -h
Scrapy 1.3.0 - no active project

Usage:
  scrapy <command> [options] [args]

Available commands:
  bench         Run quick benchmark test
  commands      
  fetch         Fetch a URL using the Scrapy downloader
  genspider     Generate new spider using pre-defined templates
  runspider     Run a self-contained spider (without creating a project)
  settings      Get settings values
  shell         Interactive scraping console
  startproject  Create new project
  version       Print Scrapy version
  view          Open URL in browser, as seen by Scrapy

  [ more ]      More commands available when run from project directory

Use "scrapy <command> -h" to see more info about a command
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython$ 
```
本篇会用到下面几个命令：
- startproject：创建一人新项目
- genspider：根据模板生成一个新爬虫
- crawl：执行爬虫
- shell：启动交互式提取控制台

文档：http://doc.scrapy.org/latest/topics/commands.html 
# 2.新建项目
输入`scrapy startproject <project_name>`新建项目，这里使用`example_wu`为项目名。
```python
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/8.Scrapy爬虫框架
$ scrapy startproject 
Usage
=====
  scrapy startproject <project_name> [project_dir]
...
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/8.Scrapy爬虫框架
$ scrapy startproject example_wu
New Scrapy project 'example_wu', using template directory '/usr/local/lib/python2.7/dist-packages/scrapy/templates/project', created in:
    /home/wu_being/GitHub/WebScrapingWithPython/8.Scrapy爬虫框架/example_wu

You can start your first spider with:
    cd example_wu
    scrapy genspider example example.com
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/8.Scrapy爬虫框架/example_wu
$ ls
example_wu  scrapy.cfg
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/8.Scrapy爬虫框架/example_wu
$ 
```
下面是新建项目的默认目录结构：
```python
scrapy.cfg
example_wu/
	__init__.py
	items.py
	middlewares.py
	pipelines.py
	setting.py
	spiders/
		__init__.py
```
下面是重要的几个文件说明：
- scrapy.cfg：设置项目配置（不用修改）
- items.py：定义待提取域的模型
- pipelines.py：处理要提取的域（不用修改）
- setting.py：定义一些设置，如用户代理、提取延时等
- spiders/：该目录存储实际的爬虫代码
## 2.1定义模型
`example_wu/items.py`默认代码如下：
```python
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ExampleWuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
```
`ExampleWuItem`类是一个模板，需要将其中的内容替换为爬虫运行时想要存储的待提取的国家信息，我们这里设置只提取国家名称和人口数量，把默认代码修改为：
```python
import scrapy

class ExampleWuItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    population=scrapy.Field()
```
## 2.2创建爬虫
现在我们开始编写真正的爬虫代码，又称为**spider**，通过genspider命令，传入爬虫名、域名和可选模板参数：
`scrapy genspider country 127.0.0.1:8000/places --template=crawl`
```python
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/8.Scrapy爬虫框架/example_wu
$ scrapy genspide
Usage
=====
  scrapy genspider [options] <name> <domain>

Generate new spider using pre-defined templates

Options
=======
--help, -h              show this help message and exit
--list, -l              List available templates
--edit, -e              Edit spider after creating it
--dump=TEMPLATE, -d TEMPLATE
                        Dump template to standard output
--template=TEMPLATE, -t TEMPLATE
                        Uses a custom template.
--force                 If the spider already exists, overwrite it with the
                        template
...
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/8.Scrapy爬虫框架/example_wu
$ scrapy genspider --list
Available templates:
  basic
  crawl
  csvfeed
  xmlfeed
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/8.Scrapy爬虫框架/example_wu
$ scrapy genspider country 127.0.0.1:8000/places --template=crawl
Created spider 'country' using template 'crawl' in module:
  example_wu.spiders.country
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/8.Scrapy爬虫框架/example_wu
$
```
这里使用内置`crawl`模板，可以生成更加接近我们想要的国家爬虫初始版本。运行genspider命令之后，将会生成代码`example_wu/spiders/country.py`。
```python
# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

class CountrySpider(CrawlSpider):
    name = 'country'
    #allowed_domains = ['127.0.0.1:8000/places'] ###!!!!这个不是域名
    start_urls = ['http://127.0.0.1:8000/places/']

    rules = (
        Rule(LinkExtractor(allow=r'Items/'), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        i = {}
        #i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        #i['name'] = response.xpath('//div[@id="name"]').extract()
        #i['description'] = response.xpath('//div[@id="description"]').extract()
        return i
```
该类的属性名：
- name：定义爬虫的名称
- allowed_domains：定义可以提取的域名列表。如果没有则表示可以提取任何域名!!!!!!
- start_urls：定义爬虫起始的URL列表。意思为可用的URL!!!!!!
- rules：定义正则表达式集合，用于告知爬虫需要跟踪哪些链接。还有一个callback函数，用于解析下载得到的响应，而`parse_urls()`示例方法给我们提供了一个从响应中获取数据的例子。

文档：http://doc.scrapy.org/en/latest/topics/spiders.html 
## 2.3优化设置
默认情况下，Scrapy对同一个域名允许最多16个并发下载，并且再次下载之间没有延时，这样爬虫容易被服务器检测到并被封禁，所以要在`example_wu/settings.py`添加几行代码：
```python
# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 5
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 1
#CONCURRENT_REQUESTS_PER_IP = 16
```
这里的延时不是精确的，精确的延时有时也可能被服务器检测到被封禁，而Scrapy实际在两次请求的延时添加随机的偏移量。文档：http://doc.scrapy.org/en/latest/topics/settings.html 
## 2.4测试爬虫
使用`crawl`运行爬虫，并附上爬虫名称。
```python
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/8.Scrapy爬虫框架/example_wu
$ scrapy crawl country -s LOG_LEVEL=ERROR
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/8.Scrapy爬虫框架/example_wu
$ 
```
发现终端日志没有输出错误信息，命令的参数`LOG_LEVEL=ERROR`等同于在`settings.py`加一行`LOG_LEVEL='ERROR'`，默认是在终端显示所有日志信息。
```python
rules = (
	Rule(LinkExtractor(allow='/index/'), follow=True),
	Rule(LinkExtractor(allow='/view/'), callback='parse_item'),
)
```
上面我们添加了两条规则。第一条规则爬取索引页并跟踪其中的链接(递归爬取链接，默认是True)，而第二条规则爬取国家页面并将下载响应传给callback函数用于提取数据。
```python
...
2017-01-30 00:12:47 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://127.0.0.1:8000/places/> (referer: None)
2017-01-30 00:12:52 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://127.0.0.1:8000/places/default/view/Afghanistan-1> (referer: http://127.0.0.1:8000/places/)
2017-01-30 00:12:57 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://127.0.0.1:8000/places/default/index/1> (referer: http://127.0.0.1:8000/places/)
2017-01-30 00:12:58 [scrapy.dupefilters] DEBUG: Filtered duplicate request: <GET http://127.0.0.1:8000/places/default/index/1> - no more duplicates will be shown (see DUPEFILTER_DEBUG to show all duplicates)
2017-01-30 00:13:03 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://127.0.0.1:8000/places/default/view/Antigua-and-Barbuda-10> (referer: http://127.0.0.1:8000/places/)
......
2017-01-30 00:14:11 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://127.0.0.1:8000/places/default/user/login?_next=%2Fplaces%2Fdefault%2Findex%2F1> (referer: http://127.0.0.1:8000/places/default/index/1)
2017-01-30 00:14:17 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://127.0.0.1:8000/places/default/user/register?_next=%2Fplaces%2Fdefault%2Findex%2F1> (referer: http://127.0.0.1:8000/places/default/index/1)
......
```
我们发现已经自动过滤了重复链接，但结果有多余的登录页和注册页，我们可以用正则表达式过滤。
```python
rules = (
	Rule(LinkExtractor(allow='/index/', deny='/user/'), follow=True), #False
	Rule(LinkExtractor(allow='/view/', deny='/user/'), callback='parse_item'),
)
```
使用该类的文档：http://doc.scrapy.org/en/latest/topics/linkextractors.html 
## 2.5使用shell命令提取数据
scrapy提供了shell命令可以下载URL并在python解释器中给出结果状态。
```python
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/8.Scrapy爬虫框架/example_wu
$ scrapy shell http://127.0.0.1:8000/places/default/view/47
...
2017-01-30 11:24:21 [scrapy.core.engine] INFO: Spider opened
2017-01-30 11:24:21 [scrapy.core.engine] DEBUG: Crawled (400) <GET http://127.0.0.1:8000/robots.txt> (referer: None)
2017-01-30 11:24:22 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://127.0.0.1:8000/places/default/view/47> (referer: None)
[s] Available Scrapy objects:
[s]   scrapy     scrapy module (contains scrapy.Request, scrapy.Selector, etc)
[s]   crawler    <scrapy.crawler.Crawler object at 0x7fd8e6d5cbd0>
[s]   item       {}
[s]   request    <GET http://127.0.0.1:8000/places/default/view/47>
[s]   response   <200 http://127.0.0.1:8000/places/default/view/47>
[s]   settings   <scrapy.settings.Settings object at 0x7fd8e6d5c5d0>
[s]   spider     <DefaultSpider 'default' at 0x7fd8e5b24c50>
[s] Useful shortcuts:
[s]   fetch(url[, redirect=True]) Fetch URL and update local objects (by default, redirects are followed)
[s]   fetch(req)                  Fetch a scrapy.Request and update local objects 
[s]   shelp()           Shell help (print this help)
[s]   view(response)    View response in a browser
>>> 
```
下面我们来测试一下。
```python
>>> 
>>> response
<200 http://127.0.0.1:8000/places/default/view/47>
>>> response.url
'http://127.0.0.1:8000/places/default/view/47'
>>> response.status
200
>>> item
{}
>>> 
>>> 
```
scrapy可以使用lxml提取数据，这里用CSS选择器。用`extract()`提取数据。
```python
>>> response.css('#places_country__row > td.w2p_fw::text')
[<Selector xpath=u"descendant-or-self::*[@id = 'places_country__row']/td[@class and contains(concat(' ', normalize-space(@class), ' '), ' w2p_fw ')]/text()" data=u'China'>]
>>> name_css='#places_country__row > td.w2p_fw::text'
>>> response.css(name_css)
[<Selector xpath=u"descendant-or-self::*[@id = 'places_country__row']/td[@class and contains(concat(' ', normalize-space(@class), ' '), ' w2p_fw ')]/text()" data=u'China'>]
>>> response.css(name_css).extract()
[u'China']
>>> 
>>> pop_css='#places_population__row > td.w2p_fw::text'
>>> response.css(pop_css).extract()
[u'1330044000']
>>> 
```
## 2.6提取数据保存到文件中
下面是该爬虫的完整代码。
```python
# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from example_wu.items import ExampleWuItem ###wu

class CountrySpider(CrawlSpider):
    name = 'country'
    #allowed_domains = ['127.0.0.1:8000/places']####domains!!!!这个不是域名
    start_urls = ['http://127.0.0.1:8000/places/']

    rules = (
        Rule(LinkExtractor(allow='/index/', deny='/user/'), follow=True), #False
        Rule(LinkExtractor(allow='/view/', deny='/user/'), callback='parse_item'),
    )

    def parse_item(self, response):
        item = ExampleWuItem() ###wu
        item['name'] = response.css('tr#places_country__row td.w2p_fw::text').extract()
        item['population'] = response.css('tr#places_population__row td.w2p_fw::text').extract()
        return item
```
要想保存结果，我们可以在`parse_item()`方法中添加保存提取数据的代码，或是**定义管道**。不过scrapy提供了一个方便的**`--output`**选项，用于自动保存提取的数据到CSV、JSON和XML文件中。
```python
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/8.Scrapy爬虫框架/example_wu
$ scrapy crawl country -s LOG_LEVEL=DEBUG
2017-01-30 13:09:52 [scrapy.utils.log] INFO: Scrapy 1.3.0 started (bot: example_wu)
...
2017-01-30 13:09:52 [scrapy.middleware] INFO: Enabled item pipelines:
[]
2017-01-30 13:09:52 [scrapy.core.engine] INFO: Spider opened
2017-01-30 13:09:52 [scrapy.extensions.logstats] INFO: Crawled 0 pages (at 0 pages/min), scraped 0 items (at 0 items/min)
2017-01-30 13:09:52 [scrapy.extensions.telnet] DEBUG: Telnet console listening on 127.0.0.1:6023
2017-01-30 13:09:52 [scrapy.core.engine] DEBUG: Crawled (400) <GET http://127.0.0.1:8000/robots.txt> (referer: None)
2017-01-30 13:09:53 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://127.0.0.1:8000/places/> (referer: None)
2017-01-30 13:09:53 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://127.0.0.1:8000/places/default/view/Afghanistan-1> (referer: http://127.0.0.1:8000/places/)
2017-01-30 13:09:53 [scrapy.core.scraper] DEBUG: Scraped from <200 http://127.0.0.1:8000/places/default/view/Afghanistan-1>
{'name': [u'Afghanistan'], 'population': [u'29121286']}
2017-01-30 13:09:53 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://127.0.0.1:8000/places/default/index/1> (referer: http://127.0.0.1:8000/places/)
2017-01-30 13:09:53 [scrapy.dupefilters] DEBUG: Filtered duplicate request: <GET http://127.0.0.1:8000/places/default/index/1> - no more duplicates will be shown (see DUPEFILTER_DEBUG to show all duplicates)
2017-01-30 13:09:53 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://127.0.0.1:8000/places/default/view/Antigua-and-Barbuda-10> (referer: http://127.0.0.1:8000/places/)
2017-01-30 13:09:54 [scrapy.core.scraper] DEBUG: Scraped from <200 http://127.0.0.1:8000/places/default/view/Antigua-and-Barbuda-10>
{'name': [u'Antigua and Barbuda'], 'population': [u'86754']}
2017-01-30 13:09:54 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://127.0.0.1:8000/places/default/view/Antarctica-9> (referer: http://127.0.0.1:8000/places/)
2017-01-30 13:09:54 [scrapy.core.scraper] DEBUG: Scraped from <200 http://127.0.0.1:8000/places/default/view/Antarctica-9>
{'name': [u'Antarctica'], 'population': [u'0']}
... ...
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/8.Scrapy爬虫框架/example_wu
$ scrapy crawl country -s LOG_LEVEL=INFO --output=countries.csv
...
2017-01-30 13:11:33 [scrapy.extensions.feedexport] INFO: Stored csv feed (252 items) in: countries.csv
2017-01-30 13:11:33 [scrapy.statscollectors] INFO: Dumping Scrapy stats:
{'downloader/request_bytes': 160417,
 'downloader/request_count': 280,
 'downloader/request_method_count/GET': 280,
 'downloader/response_bytes': 2844451,
 'downloader/response_count': 280,
 'downloader/response_status_count/200': 279,
 'downloader/response_status_count/400': 1,
 'dupefilter/filtered': 61,
 'finish_reason': 'finished',
 'finish_time': datetime.datetime(2017, 1, 30, 5, 11, 33, 487258),
 'item_scraped_count': 252,
 'log_count/INFO': 8,
 'request_depth_max': 26,
 'response_received_count': 280,
 'scheduler/dequeued': 279,
 'scheduler/dequeued/memory': 279,
 'scheduler/enqueued': 279,
 'scheduler/enqueued/memory': 279,
 'start_time': datetime.datetime(2017, 1, 30, 5, 10, 34, 304933)}
2017-01-30 13:11:33 [scrapy.core.engine] INFO: Spider closed (finished)
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/8.Scrapy爬虫框架/example_wu$ 
...
```
提取过程最后还输出一些统计信息。我们查看输出文件countries.csv的信息，结果和预期一样。
```
name,population
Andorra,84000
American Samoa,57881
Algeria,34586184
Albania,2986952
Aland Islands,26711
Afghanistan,29121286
Antigua and Barbuda,86754
Antarctica,0
Anguilla,13254
... ...
```
## 2.7中断和恢复爬虫
我们只需要定义用于保存爬虫当前状态目录的JOBDIR设置即可。
```python
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/8.Scrapy爬虫框架/example_wu
$ scrapy crawl country -s LOG_LEVEL=DEBUG -s JOBDIR=2.7crawls/country
...
^C2017-01-30 13:31:27 [scrapy.crawler] INFO: Received SIGINT, shutting down gracefully. Send again to force 
2017-01-30 13:33:13 [scrapy.core.scraper] DEBUG: Scraped from <200 http://127.0.0.1:8000/places/default/view/Albania-3>
{'name': [u'Albania'], 'population': [u'2986952']}
2017-01-30 13:33:15 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://127.0.0.1:8000/places/default/view/Aland-Islands-2> (referer: http://127.0.0.1:8000/places/)
2017-01-30 13:33:16 [scrapy.core.scraper] DEBUG: Scraped from <200 http://127.0.0.1:8000/places/default/view/Aland-Islands-2>
{'name': [u'Aland Islands'], 'population': [u'26711']}
...
```
我们通过按**Ctrl+C**发送终止信号，然后等待爬虫再下载几个条目后自动终止，注意不能再按一次**Ctrl+C**强行终止，否则爬虫保存状态不成功。
我们运行同样的命令恢复爬虫运行。
```python
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/8.Scrapy爬虫框架/example_wu $
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/8.Scrapy爬虫框架/example_wu
$ scrapy crawl country -s LOG_LEVEL=DEBUG -s JOBDIR=2.7crawls/country
...
2017-01-30 13:33:21 [scrapy.core.engine] DEBUG: Crawled (400) <GET http://127.0.0.1:8000/robots.txt> (referer: None)
2017-01-30 13:33:23 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://127.0.0.1:8000/places/default/view/Barbados-20> (referer: http://127.0.0.1:8000/places/default/index/1)
2017-01-30 13:33:23 [scrapy.core.scraper] DEBUG: Scraped from <200 http://127.0.0.1:8000/places/default/view/Barbados-20>
{'name': [u'Barbados'], 'population': [u'285653']}
2017-01-30 13:33:25 [scrapy.core.engine] DEBUG: Crawled (200) <GET http://127.0.0.1:8000/places/default/view/Bangladesh-19> (referer: http://127.0.0.1:8000/places/default/index/1)
2017-01-30 13:33:25 [scrapy.core.scraper] DEBUG: Scraped from <200 http://127.0.0.1:8000/places/default/view/Bangladesh-19>
{'name': [u'Bangladesh'], 'population': [u'156118464']}
...
^C2017-01-30 13:33:43 [scrapy.crawler] INFO: Received SIGINT, shutting down gracefully. Send again to force 
2017-01-30 13:33:43 [scrapy.core.engine] INFO: Closing spider (shutdown)
^C2017-01-30 13:33:44 [scrapy.crawler] INFO: Received SIGINT twice, forcing unclean shutdown
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/8.Scrapy爬虫框架/example_wu$ 
```
恢复时注意cookie过期问题。文档：http://doc.scrapy.org/en/latest/topics/jobs.html
# 3.使用Portia编写可视化爬虫
Portia是一款基于scrapy开发的开源工具，该工具可以通过点击要提取的网页部分来创建爬虫，这样就比手式创建CSS选择器的方式更加方便。文档：https://github.com/scrapinghub/portia#running-portia 
## 3.1安装
先使用virtualenv创建一个虚拟python环境，环境名为`portia_examle`。
`pip install virtualenv`
```python
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython$ virtualenv portia_examle --no-site-packages
New python executable in /home/wu_being/GitHub/WebScrapingWithPython/portia_examle/bin/python
Installing setuptools, pip, wheel...done.
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython$ source portia_examle/bin/activate
(portia_examle) wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython$ 
(portia_examle) wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython$ cd portia_examle/
(portia_examle) wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/portia_examle$ 
```
在virtualenv中安装Portia及依赖。
```
(portia_examle) wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/portia_examle$ 
git clone https://github.com/scrapinghub/portia
cd portia
pip install -r requirements.txt
pip install -e ./slybot
cd slyd
twistd -n slyd
```
如果安装成功，在浏览器中访问到Portia工具http://localhost:9001/static/main.html 
## 3.2标注
- Portia启动项，有一个用于输入提取网页URL的文本框，输入http://127.0.0.1:8000/places/ 。默认情况下，项目名被设为`new_project`，而爬虫名被设为待爬取域名`127.0.0.1:8000/places/`，这两项都通过单击相应标签进行修改。
- 单击`Annotate this page`按钮，然后单击国家人口数量。
- 单击`+field`按钮创建一个名为population的新域，然后单击`Done`保存。其他的域也是相同操作。
- 完成标注后，单击顶部的蓝色按钮`Continue Browsing`。

## 3.3优化爬虫
标注完成后，Portia会生成一个scrapy项目，并将产生的文件保存到data/projects目录中，要运行爬虫，只需执行portiacrawl命令，并带上项目名和爬虫名。
```
(portia_examle) wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/portia_examle$ 
portiacrawl portia/slyd/data/projects/new_project 
如果爬虫默认设置运行太快就遇到服务器错误
portiacrawl portia/slyd/data/projects/new_project 127.0.0.1:8000/places/ -s DOWNLOAD_DELAY = 2 -s CONCURRENT_REQUESTS_PER_DOMAIN = 1
```
配置右边栏面板中的`Crawling`选项卡中，可以添加`/index/`和`/view/`为爬虫跟踪模式，将`/user/`为排除模式，并勾选`Overlay blocked links`复选框。
## 3.4检查结果
```
(portia_examle) wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/portia_examle$ 
portiacrawl portia/slyd/data/projects/new_project 127.0.0.1:8000/places/ --output=countries.csv -s DOWNLOAD_DELAY = 2 -s CONCURRENT_REQUESTS_PER_DOMAIN = 1
```
Portia是一个非常方便的与Scrapy配合的工具。对于简单的网站，使用Portia开发爬虫通常速度更快。而对于复杂的网站（比如依赖JavaScript的界面），则可以选择使用Python直接开发Scrapy爬虫。
# 4.使用Scrapely实现自动化提取
Portia使用了Scrapely库来训练数据建立从网页中提取哪些内容的模型，并在相同结构的其他网页应用该模型。
https://github.com/scrapy/scrapely 
```
(portia_examle) wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/portia_examle$ python
Python 2.7.12 (default, Nov 19 2016, 06:48:10) 
[GCC 5.4.0 20160609] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> from scrapely import Scraper
>>> s=Scraper()
>>> train_url='http://127.0.0.1:8000/places/default/view/47'
>>> s.train(train_url,{'name':'China','population':'1330044000'})
>>> test_url='http://127.0.0.1:8000/places/default/view/239'
>>> s.scrape(test_url)
[{u'name':[u'United Kingdom'],u'population':[u'62,348,447']}]

```
