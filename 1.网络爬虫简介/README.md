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
section 1 ：禁止用户代理为BadCrawler的爬虫爬取该网站，除非恶意爬虫。
section 2 ：两次下载请求时间间隔5秒的爬取延迟。/trap 用于封禁恶意爬虫，会封禁1分钟不止。
section 3 ：定义一个Sitemap文件，下节讲。
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
搜索：`site:http://example.webscraping.com/` 有202个网页
搜索：`site:http://example.webscraping.com/view` 有117个网页
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
