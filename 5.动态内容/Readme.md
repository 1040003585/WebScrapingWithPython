# 提取JS动态网页数据
[TOC]
现在大部分的主流网站都用JavaScript动态显示网页内容，这样使得我们之前提取技术无法正常运行。本篇将介绍两种提取基于JS动态网页的数据。
- JavaScript逆向工程
- 渲染JavaScript

# 1.动态网页示例
我们先看一个动态网页的示例。在示例网站的中，我们从http://127.0.0.1:8000/places/default/search 搜索国家名包涵`A`的表单。
我们根据按`F12`开发者工具显示的标签，用lxml模块提取数据，发现提取不到什么数据。
```python
>>> import lxml.html
>>> from downloader import Downloader
>>> D=Downloader()
>>> html=D('http://127.0.0.1:8000/places/default/search')
Downloading: http://127.0.0.1:8000/places/default/search
>>> tree=lxml.html.fromstring(html)
>>> tree.cssselect('div#result a')
[]
>>> 
```
我们在浏览器右击查看网页源代码发现我们要提取的div数据是空的。
```html
...
<div id="results">
</div>
...
```
这是因为`F12`的开发者工具是显示的标签是网页当前的状态，也就是使用JavaScript动态加载完搜索结果之后的网页。
# 2.对加载内容进行逆向工程
由于这些网页的数据是JS动态加载的，要想提取该数据，我们需要网页如何加载该数据的，该过程也被称为**逆向工程**。
## 2.1通过开发者工具的逆向工程
我们在上节`F12`的开发者工具的`Network`发现AJAX响应一个json文件，即：http://127.0.0.1:8000/places/ajax/search.json?&search_term=A&page_size=10&page=0 。AJAX响应的返回数据是JSON格式的，因此我们可以使用Python的json模块将解析为一个字典。
```python
>>> import json
>>> html=D('http://127.0.0.1:8000/places/ajax/search.json?&search_term=A&page_size=10&page=0')
Downloading: http://127.0.0.1:8000/places/ajax/search.json?&search_term=A&page_size=10&page=0
>>> json.loads(html)
{u'records': [
  {u'pretty_link': u'<div><a href="/places/default/view/Afghanistan-1"><img src="/places/static/images/flags/af.png" /> Afghanistan</a></div>', u'country': u'Afghanistan', u'id': 3781}, 
  {u'pretty_link': u'<div><a href="/places/default/view/Aland-Islands-2"><img src="/places/static/images/flags/ax.png" /> Aland Islands</a></div>', u'country': u'Aland Islands', u'id': 3782},...], 
u'num_pages': 22, 
u'error': u''}
>>> 
```
我们可以通过分页请求提取json数据存到txt文件中。分页请求会让同一个国家在多次搜索返回多次，但通过`set()`集合会过滤重复的元素。
```python
# -*- coding: utf-8 -*-
import json
import string
import downloader

def main():
    template_url = 'http://127.0.0.1:8000/places/ajax/search.json?&page={}&page_size=10&search_term={}'
    countries = set()
    download = downloader.Downloader()
    for letter in string.lowercase:
        page = 0
        while True:
            html = download(template_url.format(page, letter))
            try:
                ajax = json.loads(html)
            except ValueError as e:
                print e
                ajax = None
            else:
                for record in ajax['records']:
                    countries.add(record['country'])
            page += 1
            if ajax is None or page >= ajax['num_pages']:
                break    
    open('2countries2.txt', 'w').write('\n'.join(sorted(countries)))

if __name__ == '__main__':
    main()
```
## 2.2通过墨盒测试的逆向工程
在不知道源代码的情况下的测试称为**墨盒测试**。我们可以使用一次搜索查询就能匹配所有结果，接下来，我们将尝试使用不同字符测试这种想法是否可行。
### 2.2.1搜索条件为空时
```python
>>> import json
>>> from downloader import Downloader
>>> D=Downloader()
>>> url='http://127.0.0.1:8000/places/ajax/search.json?&page_size=10&page=0&search_term='
>>> json.loads(D(url))['num_pages']
Downloading: http://127.0.0.1:8000/places/ajax/search.json?&page_size=10&page=0&search_term=
0
>>> 
```
搜索条件为空时，这种方法并没有奏效。
### 2.2.2用`*`号匹配时
```python
>>> json.loads(D(url+'*'))['num_pages']
Downloading: http://127.0.0.1:8000/places/ajax/search.json?&page_size=10&page=0&search_term=*
0
```
用`*`号匹配时，这种方法也没有奏效。
### 2.2.2用`.`号匹配时
```python
>>> json.loads(D(url+'.'))['num_pages']
Downloading: http://127.0.0.1:8000/places/ajax/search.json?&page_size=10&page=0&search_term=.
26
```
这种方法测试成功了，看来服务器是通过正则表达式进行匹配的。在搜索界面中包含4、10、20这几种选项，其中默认值是10。我们增加显示数量进行测试。
```python
>>> url='http://127.0.0.1:8000/places/ajax/search.json?&page_size=20&page=0&search_term='
>>> json.loads(D(url+'.'))['num_pages']
Downloading: http://127.0.0.1:8000/places/ajax/search.json?&page_size=20&page=0&search_term=.
13
>>> url='http://127.0.0.1:8000/places/ajax/search.json?&page_size=1000&page=0&search_term='
>>> json.loads(D(url+'.'))['num_pages']
Downloading: http://127.0.0.1:8000/places/ajax/search.json?&page_size=1000&page=0&search_term=.
1
>>> 
```
我们如下整合过完整代码。
```python
# -*- coding: utf-8 -*-

import json
import csv
import downloader

def main():
    writer = csv.writer(open('2.2countries.csv', 'w'))
    D = downloader.Downloader()
    #html = D('http://example.webscraping.com/ajax/search.json?page=0&page_size=1000&search_term=.')
    html = D('http://127.0.0.1:8000/places/ajax/search.json?&page_size=1000&page=0&search_term=.')
    ajax = json.loads(html)
    for record in ajax['records']:
        writer.writerow([record['country']])

if __name__ == '__main__':
    main()
```
# 3.渲染动态网页
一些网站用Google Web Toolkit（GWT）工具开发的，产生的JS代码是压缩的，但可以通过JSbeautifier工具进行还原，但逆向工程效果不是很好。渲染引擎是浏览器加载网页时解析HTML、应用CSS样式并执行JS语句进行渲染显示。本节中我们使用WebKit渲染引擎，并通过Qt框架获得引擎的一个便捷Python接口，也可以用Selenium自定义渲染。
## 3.1使用WebKit渲染引擎
```html
<html>
    <body>
        <div id="result"></div>
        <script>document.getElementById("result").innerText = 'Hello World';</script>
    </body>
</html>
```

```python
# -*- coding: utf-8 -*-
import lxml.html
import downloader
try: 
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide.QtWebKit import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
    from PyQt4.QtWebKit import *

def direct_download(url):
    download = downloader.Downloader()
    return download(url)

def webkit_download(url):
    app = QApplication([])
    webview = QWebView()
    loop=QEventLoop()
    webview.loadFinished.connect(loop.quit)
    webview.load(QUrl(url))
    app.exec_() # delay here until download finished
    return webview.page().mainFrame().toHtml()

def parse(html):
    tree = lxml.html.fromstring(html)
    print tree.cssselect('#result')[0].text_content()

def main(): 
    url = 'http://127.0.0.1:8000/places/default/dynamic'
    #url = 'http://example.webscraping.com/dynamic'
    parse(direct_download(url))
    parse(webkit_download(url))
    return
    print len(r.html)

if __name__ == '__main__':
    main()

```

```python
# -*- coding: utf-8 -*-

try:
    from PySide.QtGui import QApplication
    from PySide.QtCore import QUrl, QEventLoop, QTimer
    from PySide.QtWebKit import QWebView
except ImportError:
    from PyQt4.QtGui import QApplication
    from PyQt4.QtCore import QUrl, QEventLoop, QTimer
    from PyQt4.QtWebKit import QWebView

def main():
    app = QApplication([])
    webview = QWebView()
    loop = QEventLoop()
    webview.loadFinished.connect(loop.quit)
    webview.load(QUrl('http://127.0.0.1:8000/places/default/dynamic'))
    #webview.load(QUrl('http://example.webscraping.com/search'))
    loop.exec_()

    webview.show()
    frame = webview.page().mainFrame()
    frame.findFirstElement('#search_term').setAttribute('value', '.')
    frame.findFirstElement('#page_size option:checked').setPlainText('1000')
    frame.findFirstElement('#search').evaluateJavaScript('this.click()')

    elements = None
    while not elements:
        app.processEvents()
        elements = frame.findAllElements('#results a')
    countries = [e.toPlainText().strip() for e in elements]
    print countries


if __name__ == '__main__':
    main()
```

```python
# -*- coding: utf-8 -*-

import re
import csv
import time
try: 
    from PySide.QtGui import QApplication
    from PySide.QtCore import QUrl, QEventLoop, QTimer
    from PySide.QtWebKit import QWebView
except ImportError:
    from PyQt4.QtGui import QApplication
    from PyQt4.QtCore import QUrl, QEventLoop, QTimer
    from PyQt4.QtWebKit import QWebView
import lxml.html

  
class BrowserRender(QWebView):  
    def __init__(self, display=True):
        self.app = QApplication([])
        QWebView.__init__(self)
        if display:
            self.show() # show the browser

    def open(self, url, timeout=60):
        """Wait for download to complete and return result"""
        loop = QEventLoop()
        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        self.loadFinished.connect(loop.quit)
        self.load(QUrl(url))
        timer.start(timeout * 1000)
        loop.exec_() # delay here until download finished
        if timer.isActive():
            # downloaded successfully
            timer.stop()
            return self.html()
        else:
            # timed out
            print 'Request timed out:', url

    def html(self):
        """Shortcut to return the current HTML"""
        return self.page().mainFrame().toHtml()

    def find(self, pattern):
        """Find all elements that match the pattern"""
        return self.page().mainFrame().findAllElements(pattern)

    def attr(self, pattern, name, value):
        """Set attribute for matching elements"""
        for e in self.find(pattern):
            e.setAttribute(name, value)

    def text(self, pattern, value):
        """Set attribute for matching elements"""
        for e in self.find(pattern):
            e.setPlainText(value)

    def click(self, pattern):
        """Click matching elements"""
        for e in self.find(pattern):
            e.evaluateJavaScript("this.click()")

    def wait_load(self, pattern, timeout=60):
        """Wait for this pattern to be found in webpage and return matches"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.app.processEvents()
            matches = self.find(pattern)
            if matches:
                return matches
        print 'Wait load timed out'


def main(): 
    br = BrowserRender()
    br.open('http://127.0.0.1:8000/places/default/dynamic')
    #br.open('http://example.webscraping.com/search')
    br.attr('#search_term', 'value', '.')
    br.text('#page_size option:checked', '1000')
    br.click('#search')

    elements = br.wait_load('#results a')
    writer = csv.writer(open('countries.csv', 'w'))
    for country in [e.toPlainText().strip() for e in elements]:
        writer.writerow([country])


if __name__ == '__main__':
    main()
```
## 3.2使用Selenium自定义渲染

```python
from selenium import webdriver

def main():
    driver = webdriver.Firefox()
    driver.get('http://127.0.0.1:8000/places/default/dynamic')
    #driver.get('http://example.webscraping.com/search')
    driver.find_element_by_id('search_term').send_keys('.')
    driver.execute_script("document.getElementById('page_size').options[1].text = '1000'");
    driver.find_element_by_id('search').click()
    driver.implicitly_wait(30)
    links = driver.find_elements_by_css_selector('#results a')
    countries = [link.text for link in links]
    driver.close()
    print countries

if __name__ == '__main__':
    main()
```
