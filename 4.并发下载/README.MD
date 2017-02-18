# 并发并行下载
[TOC]
这篇将介绍使用多线程和多进程这两种方式并发并行下载网页，并将它们与串行下载的性能进行比较。
# 1一百万个网站
亚马逊子公司Alexa提供了最受欢迎的100万个网站列表（http://www.alexa.com/topsites ），我们也可以通过http://s3.amazonaws.com/alexa-static/top-1m.csv.zip 直接下载这一列表的压缩文件，这样就不用去提取Alexa网站的数据了。
|排名|域名|
|---:|:---|
|1|google.com|
|2|youtube.com|
|3|facebook.com|
|4|baidu.com|
|5|yahoo.com|
|6|wikipedia.com|
|7|google.co.in|
|8|amazon.com|
|9|qq.com|
|10|google.co.jp|
|11|live.com|
|12|taobao.com|
## 1.1用普通方法解析Alexa列表
提取数据的4个步骤：
- 下载.zip文件；
- 从.zip文件中提取出CSV文件；
- 解析CSV文件；
- 遍历CSV文件中的每一行，从中提取出域名数据。
```python
# -*- coding: utf-8 -*-

import csv
from zipfile import ZipFile
from StringIO import StringIO
from downloader import Downloader

def alexa():
    D = Downloader()
    zipped_data = D('http://s3.amazonaws.com/alexa-static/top-1m.csv.zip')
    urls = [] # top 1 million URL's will be stored in this list
    with ZipFile(StringIO(zipped_data)) as zf:
        csv_filename = zf.namelist()[0]
        for _, website in csv.reader(zf.open(csv_filename)):
            urls.append('http://' + website)
    return urls

if __name__ == '__main__':
    print len(alexa())
```
下载得到的压缩数据是使用StringIO封装之后，才传给ZipFile，是因为ZipFile需要一个相关的接口，而不是字符串。由于这个zip文件只包含一个文件，所以直接选择第一个文件即可。然后在域名数据前添加http://协议，附加到URL列表中。
## 1.2复用爬虫代码解析Alexa列表
要复用上述功能，需要修改scrape_callback接口。
```python
# -*- coding: utf-8 -*-

import csv
from zipfile import ZipFile
from StringIO import StringIO
from mongo_cache import MongoCache

class AlexaCallback:
    def __init__(self, max_urls=1000):
        self.max_urls = max_urls
        self.seed_url = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'

    def __call__(self, url, html):
        if url == self.seed_url:
            urls = []
            #cache = MongoCache()
            with ZipFile(StringIO(html)) as zf:
                csv_filename = zf.namelist()[0]
                for _, website in csv.reader(zf.open(csv_filename)):
                    if 'http://' + website not in cache:
                        urls.append('http://' + website)
                        if len(urls) == self.max_urls:
                            break
            return urls
```
这里添加了一个新的输入参数max_urls，用于设定从Alexa文件中提取的URL数量。如果真要下载100万个网页，那要消耗11天的时间，所以这里只设置为1000个URL。
# 2串行爬虫
```python
# -*- coding: utf-8 -*-

from link_crawler import link_crawler
from mongo_cache import MongoCache
from alexa_cb import AlexaCallback

def main():
    scrape_callback = AlexaCallback()
    cache = MongoCache()
    #cache.clear()
    link_crawler(scrape_callback.seed_url, scrape_callback=scrape_callback, cache=cache, timeout=10, ignore_robots=True)

if __name__ == '__main__':
    main()
```
# `time python ...`
 
# 3并发并行爬虫
为了加快下载网页速度，我们用多进程和多线程将串行下载扩展成并发下载，并将delay标识最小时间间隔为1秒，以免造成服务器过载，或导致IP地址封禁。
## 3.0并发并行工作原理
**并行**是基于多处理器多核而言的，让多个处理器多核真正同时跑多个程序或多个进程。而**并发**是单个处理器而言的，同一时刻每个处理器只会执行一个进程，然后在不同进程间快速切换，宏观上给人以多个程序同时运行的感觉，但微观上单个处理器还是串行工作的。同理，在一个进程中，程序的执行也是不同线程间进行切换的，每个线程执行程序的的不同部分。这就意味着当一个线程`等待`网页下载时，进程可以切换到其他线程执行，避免浪费处理器时间。因此，为了充分利用计算机中的所有资源尽可能快地下载数据，我们需要将下载分发到多个进程和线程中。
## 3.1多线程爬虫
我们可以修改第一篇文章链接爬虫队列结构的代码，修改为多个线程中启动爬虫循环`process_queue()`，以便并发下载这些链接。
```python
import time
import threading
import urlparse
from downloader import Downloader

SLEEP_TIME = 1

def threaded_crawler(seed_url, delay=5, cache=None, scrape_callback=None, user_agent='Wu_Being', proxies=None, num_retries=1, max_threads=10, timeout=60):
    """Crawl this website in multiple threads
    """
    # the queue of URL's that still need to be crawled
    #crawl_queue = Queue.deque([seed_url])
    crawl_queue = [seed_url]
    # the URL's that have been seen 
    seen = set([seed_url])
    D = Downloader(cache=cache, delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries, timeout=timeout)

    def process_queue():
        while True:
            try:
                url = crawl_queue.pop()
            except IndexError:
                # crawl queue is empty
                break
            else:
                html = D(url)
                if scrape_callback:
                    try:
                        links = scrape_callback(url, html) or []
                    except Exception as e:
                        print 'Error in callback for: {}: {}'.format(url, e)
                    else:
                        for link in links:
                            link = normalize(seed_url, link)
                            # check whether already crawled this link
                            if link not in seen:
                                seen.add(link)
                                # add this new link to queue
                                crawl_queue.append(link)

    # wait for all download threads to finish
    threads = []
    while threads or crawl_queue:
        # the crawl is still active
        for thread in threads:
            if not thread.is_alive():
                # remove the stopped threads
                threads.remove(thread)
        while len(threads) < max_threads and crawl_queue:
            # can start some more threads
            thread = threading.Thread(target=process_queue)
            thread.setDaemon(True) # set daemon so main thread can exit when receives ctrl-c
            thread.start()
            threads.append(thread)
        # all threads have been processed
        # sleep temporarily so CPU can focus execution on other threads
        time.sleep(SLEEP_TIME)

def normalize(seed_url, link):
    """Normalize this URL by removing hash and adding domain
    """
    link, _ = urlparse.urldefrag(link) # remove hash to avoid duplicates
    return urlparse.urljoin(seed_url, link)
```
上面代码在循环会不断创建线程，直到达到线程池`threads`的最大值。在爬取过程中，如果当前列队没有更多可以爬取的URL时，该线程会提前停止。
`例如当前有两个线程以及两个待下载的URL，当第一个线程完成下载时，待爬取队列为空，则该线程退出。第二个线程稍后也完成了下载，但又发现了另一个待下载的URL。此时，thread循环注意到还有URL需要下载，并且线程数未达到最大值，因些创建一个新的下载线程。`
```python
# -*- coding: utf-8 -*-

import sys
from threaded_crawler import threaded_crawler
from mongo_cache import MongoCache
from alexa_cb import AlexaCallback

def main(max_threads):
    scrape_callback = AlexaCallback()
    cache = MongoCache()
    #cache.clear()
    threaded_crawler(scrape_callback.seed_url, scrape_callback=scrape_callback, cache=cache, max_threads=max_threads, timeout=10)

if __name__ == '__main__':
    max_threads = int(sys.argv[1])
    main(max_threads)
```
# `$time python 3threaded_test.py 5`
上面使用了5个线程，因此下载速度几乎是串行版本的5倍。
## 3.2多进程爬虫
对于有多核的中央处理器，则可以启动多进程。
```python
# -*- coding: utf-8 -*-
import sys
from process_crawler import process_crawler
from mongo_cache import MongoCache
from alexa_cb import AlexaCallback

def main(max_threads):
    scrape_callback = AlexaCallback()
    cache = MongoCache()
    cache.clear()
    process_crawler(scrape_callback.seed_url, scrape_callback=scrape_callback, cache=cache, max_threads=max_threads, timeout=10) ##process_crawler

if __name__ == '__main__':
    max_threads = int(sys.argv[1])
    main(max_threads)
```
下面代码首先获取中央处理器内核个数，然后启动相应的进程个数，在每进程启动多个线程爬虫。之前的爬虫队列是存储在本地内存中，其他进程都无法处理这一爬虫，为了解决这一问题，需要把爬虫队列转移到MongoDB当中。单独存储队列，意味着即使是不同服务器上的爬虫也能够协同处理同一个爬虫任务。我们可以使用更加健壮的队列，比如专用的消息传输工具`Celery`，这里我们利用MongoDB实现的队列代码。在`threaded_crawler`需要做如下修改：
- 内建的队列换成基于MongoDB的新队列`MongoQueue`；
- 由于队列内部实现中处理重复URL的问题，因此不再需要seen变量；
- 在URL处理结束后调用`complete()`方法，用于记录该URL已经被成功解析。

```python
import time
import urlparse
import threading
import multiprocessing
from mongo_cache import MongoCache
from mongo_queue import MongoQueue
from downloader import Downloader

SLEEP_TIME = 1

### process_crawler(scrape_callback.seed_url, scrape_callback=scrape_callback, cache=cache, max_threads=max_threads, timeout=10)
def process_crawler(args, **kwargs):	#args:number of args, kwargs:args list
    num_cpus = multiprocessing.cpu_count()
    #pool = multiprocessing.Pool(processes=num_cpus)
    print 'Starting {} processes...'.format(num_cpus)	######################
    processes = []
    for i in range(num_cpus):
        p = multiprocessing.Process(target=threaded_crawler, args=[args], kwargs=kwargs)### threaded_crawler
        #parsed = pool.apply_async(threaded_link_crawler, args, kwargs)
        p.start()
        processes.append(p)
    # wait for processes to complete
    for p in processes:
        p.join()

def threaded_crawler(seed_url, delay=5, cache=None, scrape_callback=None, user_agent='wu_being', proxies=None, num_retries=1, max_threads=10, timeout=60):
    """Crawl using multiple threads
    """
    # the queue of URL's that still need to be crawled
    crawl_queue = MongoQueue()	######################
    crawl_queue.clear()		######################
    crawl_queue.push(seed_url)	######################
    D = Downloader(cache=cache, delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries, timeout=timeout)

    def process_queue():
        while True:
            # keep track that are processing url
            try:
                url = crawl_queue.pop()	######################
            except KeyError:
                # currently no urls to process
                break
            else:
                html = D(url)
                if scrape_callback:
                    try:
                        links = scrape_callback(url, html) or []
                    except Exception as e:
                        print 'Error in callback for: {}: {}'.format(url, e)
                    else:
                        for link in links:		#############
                            # add this new link to queue######################
                            crawl_queue.push(normalize(seed_url, link))######################
                crawl_queue.complete(url)		######################

    # wait for all download threads to finish
    threads = []
    while threads or crawl_queue:			######################
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        while len(threads) < max_threads and crawl_queue.peek():	#######################
            # can start some more threads
            thread = threading.Thread(target=process_queue)
            thread.setDaemon(True) # set daemon so main thread can exit when receives ctrl-c
            thread.start()
            threads.append(thread)
        time.sleep(SLEEP_TIME)

def normalize(seed_url, link):
    """Normalize this URL by removing hash and adding domain
    """
    link, _ = urlparse.urldefrag(link) # remove hash to avoid duplicates
    return urlparse.urljoin(seed_url, link)
```
在`MongoQueue`定义了三种状态：
- `OUTSTANDING`：添加一人新URL时；
- `PROCESSING`：队列中取出准备下载时；
- `COMPLETE`：完成下载时。

由于大部分线程都在从队列准备取出未完成处理的URL，比如处理的URL线程被终止的情况。所以在该类中使用了`timeout`参数，默认为300秒。在`repaire()`方法中，如果某个URL的处理时间超过了这个timeout值，我们就认定处理过程出现了错误，URL的状态将被重新设为`OUTSTANDING`，以便再次处理。
```python
from datetime import datetime, timedelta
from pymongo import MongoClient, errors

class MongoQueue:
    """
    >>> timeout = 1
    >>> url = 'http://example.webscraping.com'
    >>> q = MongoQueue(timeout=timeout)
    >>> q.clear() # ensure empty queue
    >>> q.push(url) # add test URL
    >>> q.peek() == q.pop() == url # pop back this URL
    True
    >>> q.repair() # immediate repair will do nothin
    >>> q.pop() # another pop should be empty
    >>> q.peek() 
    >>> import time; time.sleep(timeout) # wait for timeout
    >>> q.repair() # now repair will release URL
    Released: test
    >>> q.pop() == url # pop URL again
    True
    >>> bool(q) # queue is still active while outstanding
    True
    >>> q.complete(url) # complete this URL
    >>> bool(q) # queue is not complete
    False
    """

    # possible states of a download
    OUTSTANDING, PROCESSING, COMPLETE = range(3)

    def __init__(self, client=None, timeout=300):
        """
        host: the host to connect to MongoDB
        port: the port to connect to MongoDB
        timeout: the number of seconds to allow for a timeout
        """
        self.client = MongoClient() if client is None else client
        self.db = self.client.cache
        self.timeout = timeout

    def __nonzero__(self):
        """Returns True if there are more jobs to process
        """
        record = self.db.crawl_queue.find_one(
            {'status': {'$ne': self.COMPLETE}} 
        )
        return True if record else False

    def push(self, url):
        """Add new URL to queue if does not exist
        """
        try:
            self.db.crawl_queue.insert({'_id': url, 'status': self.OUTSTANDING})
        except errors.DuplicateKeyError as e:
            pass # this is already in the queue

    def pop(self):
        """Get an outstanding URL from the queue and set its status to processing.
        If the queue is empty a KeyError exception is raised.
        """
        record = self.db.crawl_queue.find_and_modify(
            query={'status': self.OUTSTANDING}, 
            update={'$set': {'status': self.PROCESSING, 'timestamp': datetime.now()}}
        )
        if record:
            return record['_id']
        else:
            self.repair()
            raise KeyError()

    def peek(self):
        record = self.db.crawl_queue.find_one({'status': self.OUTSTANDING})
        if record:
            return record['_id']

    def complete(self, url):
        self.db.crawl_queue.update({'_id': url}, {'$set': {'status': self.COMPLETE}})

    def repair(self):
        """Release stalled jobs
        """
        record = self.db.crawl_queue.find_and_modify(
            query={
                'timestamp': {'$lt': datetime.now() - timedelta(seconds=self.timeout)},
                'status': {'$ne': self.COMPLETE}
            },
            update={'$set': {'status': self.OUTSTANDING}}
        )
        if record:
            print 'Released:', record['_id']

    def clear(self):
        self.db.crawl_queue.drop()
```
# 4性能对比
|脚本|线程数|进程数|时间|与串行时间比|
|--:|:--:|:--:|:--:|:--:|
|串行|1|1|||
|多线程|5|1|||
|多线程|10|1|||
|多线程|20|1|||
|多进程|5|2|||
|多进程|10|2|||
|多进程|20|2|||

此外，下载的带宽是有限的，最终添加新线程将无法加快的下载速度。因此要想获得更好性能的爬虫，就需要在多台服务器上分布式部署爬虫，并且所有服务器都要指向同一个MongoDB队列实例中。
