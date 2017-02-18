# -*- coding: utf-8 -*-

try: 
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide.QtWebKit import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
    from PyQt4.QtWebKit import *

import lxml.html
import downloader

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

'''
try: 
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide.QtWebKit import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
    from PyQt4.QtWebKit import *

import lxml.html

url = 'http://127.0.0.1:8000/places/default/dynamic'
app = QApplication([])
webview = QWebView()
loop=QEventLoop()
webview.loadFinished.connect(loop.quit)
webview.load(QUrl(url))
app.exec_() # delay here until download finished
html=webview.page().mainFrame().toHtml()
tree = lxml.html.fromstring(html)
tree.cssselect('#result')[0].text_content()

'''
