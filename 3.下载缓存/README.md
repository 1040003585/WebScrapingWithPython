# 下载缓存
上篇文章，我们学习了如何提取网页中的数据，以及将提取结果存到表格中。如果我们还想提取另一字段，则需要重新再下载整个网页，这对我们这个小型的示例网站问题不大，但对于数百万个网页的网站而言来说就要消耗几个星期的时间。所以，我们可以先对网页进行缓存，就使得每个网页只下载一次。
# 1为链接爬虫添加缓存支持
- 我们将downloader重构一类，这样参数只需在构造方法中设置一次，就能在后续多次复用，在URL下载之前进行缓存检查，并把限速功能移到函数内部。
- 在Downloader类的__call__特殊方法实现了下载前先检查缓存，如果已经定义该URL缓存则再检查下载中是否遇到了服务端错误，如果都没问题表明缓存结果可用，否则都需要正常下载该URL存到缓存中。
- downloader方法返回添加了HTTP状态码，以便缓存中存储错误机校验。如果不需要限速或缓存的话，你可以直接调用该方法，这样就不会通过__call__方法调用了。

```python

class Downloader:
    def __init__(self, delay=5, user_agent='Wu_Being', proxies=None, num_retries=1, cache=None):
        self.throttle = Throttle(delay)
        self.user_agent = user_agent
        self.proxies = proxies
        self.num_retries = num_retries
        self.cache = cache

    def __call__(self, url):
        result = None
        if self.cache:
            try:
                result = self.cache[url]
            except KeyError:
                # url is not available in cache 
                pass
            else:
                if self.num_retries > 0 and 500 <= result['code'] < 600:
                    # server error so ignore result from cache and re-download
                    result = None
        if result is None:
            # result was not loaded from cache so still need to download
            self.throttle.wait(url)
            proxy = random.choice(self.proxies) if self.proxies else None
            headers = {'User-agent': self.user_agent}
            result = self.download(url, headers, proxy=proxy, num_retries=self.num_retries)
            if self.cache:
                # save result to cache
                self.cache[url] = result
        return result['html']

    def download(self, url, headers, proxy, num_retries, data=None):
        print 'Downloading:', url
	...
        return {'html': html, 'code': code}

class Throttle:
    def __init__(self, delay):
	...
    def wait(self, url):
	...
```
为了支持缓存功能，链接爬虫代码也需用一些微调，包括添加cache参数、移除限速以及将download函数替换为新的类。
```python
from downloader import Downloader

def link_crawler(... cache=None):
    crawl_queue = [seed_url]
    seen = {seed_url: 0}
    # track how many URL's have been downloaded
    num_urls = 0
    rp = get_robots(seed_url)
    #cache.clear()			###############################
    D = Downloader(delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries, cache=cache)

    while crawl_queue:
        url = crawl_queue.pop()
        depth = seen[url]
        # check url passes robots.txt restrictions
        if rp.can_fetch(user_agent, url):
            html = D(url)				###def __call__(self, url):
            links = []
	...

def normalize(seed_url, link):
	...
def same_domain(url1, url2):
	...
def get_robots(url):
	...
def get_links(html):
	...
"""
if __name__ == '__main__':
    link_crawler('http://example.webscraping.com', '/(index|view)', delay=0, num_retries=1, user_agent='BadCrawler')
    link_crawler('http://example.webscraping.com', '/(index|view)', delay=0, num_retries=1, max_depth=1, user_agent='GoodCrawler')
"""
```
现在，这个支持缓存的网络爬虫的基本架构已经准备好了，下面就要开始构建实际的缓存功能了。
# 2磁盘缓存
|操作系统|文件系统|非法文件名字符|文件名最大长度|
|:------:|:------:|:------:|:------:|
|Linux|Ext3/Ext4|`/`和`\0`|255个字节|
|OS X|HFS Plus|`:`和`\0`|255个UTF-16编码单元|
|Windows|NTFS|`\`、`/`、`?`、`:`、`*`、`"`、`>`、`<`和`|`|255个字节|
为了保证在不同文件系统中，我们的文件路径都是安全的，就需要把除数字、字母和基本符号的其他字符替换为下划线。
```python
>>> import re
>>> url="http://example.webscraping.com/default/view/australia-1"
>>> re.sub('[^/0-9a-zA-Z\-,.;_ ]','_',url)
'http_//example.webscraping.com/default/view/australia-1'
```
此外，文件名及其目录长度需要限制在255个字符以内。
```python
>>> filename=re.sub('[^/0-9a-zA-Z\-,.;_ ]','_',url)
>>> filename='/'.join(segment[:255] for segment in filename.split('/'))
>>> print filename
http_//example.webscraping.com/default/view/australia-1
>>> print '#'.join(segment[:5] for segment in filename.split('/'))
http_##examp#defau#view#austr
>>> 
```
还有一种边界情况，就是URL以斜杠结尾。这样分割URL后就会造成一个非法的文件名。例如：
- http://example.webscraping.com/index/
- http://example.webscraping.com/index/1

对于第一个URL可以在后面添加index.html作为文件名，所以可以把index作为目录名，1为子目录名，index.html为文件名。
```python
>>> import urlparse
>>> components=urlparse.urlsplit('http://exmaple.scraping.com/index/')
>>> print components
SplitResult(scheme='http', netloc='exmaple.scraping.com', path='/index/', query='', fragment='')
>>> print components.path
/index/
>>> path=components.path
>>> if not path:
...     path='/index.html'
... elif path.endswith('/'):
...     path+='index.html'
... 
>>> filename=components.netloc+path+components.query
>>> filename
'exmaple.scraping.com/index/index.html'
>>> 
```
## 2.1用磁盘缓存的实现
现在可以把URL到目录和文件名完整映射逻辑结合起来，就形成了磁盘缓存的主要部分。该构造方法传入了用于设定缓存位置的参数，然后在url_to_path方法中应用了前面讨论的文件名限制。
```python
from link_crawler import link_crawler

class DiskCache:

    def __init__(self, cache_dir='cache', ...):
        """
        cache_dir: the root level folder for the cache
        """
        self.cache_dir = cache_dir
	...

    def url_to_path(self, url):
        """Create file system path for this URL
        """
        components = urlparse.urlsplit(url)
        # when empty path set to /index.html
        path = components.path
        if not path:
            path = '/index.html'
        elif path.endswith('/'):
            path += 'index.html'
        filename = components.netloc + path + components.query
        # replace invalid characters
        filename = re.sub('[^/0-9a-zA-Z\-.,;_ ]', '_', filename)
        # restrict maximum number of characters
        filename = '/'.join(segment[:255] for segment in filename.split('/'))
        return os.path.join(self.cache_dir, filename) #拼接当前目录和文件名为完整目录
    
    def __getitem__(self, url):
        ...
    def __setitem__(self, url, result):
        ...
    def __delitem__(self, url):
        ...
    def has_expired(self, timestamp):
        ...
    def clear(self):
	...

if __name__ == '__main__':
    link_crawler('http://example.webscraping.com/', '/(index|view)', cache=DiskCache())
```
现在我们还缺少根据文件名存取数据的方法，就是Downloader类`result=cache[url]`和`cache[url]=result`的接口方法：`__getitem__()`和`__setitem__()`两个特殊方法。
```python
import pickle

class DiskCache:

    def __init__(self, cache_dir='cache', expires=timedelta(days=30), compress=True):
	...    
    def url_to_path(self, url):
	...
    def __getitem__(self, url):
	...
    def __setitem__(self, url, result):
        """Save data to disk for this url
        """
        path = self.url_to_path(url)
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(path, 'wb') as fp:
            fp.write(pickle.dumps(result))
```
在`__setitem__()`中，我们使用url_to_path()方法将URL映射为安全文件名，在必要情况下还需要创建目录。这里使用的pickle模块会把输入转化为字符串（序列化），然后保存到磁盘中。
```python
import pickle

class DiskCache:

    def __init__(self, cache_dir='cache', expires=timedelta(days=30), compress=True):
	...    
    def url_to_path(self, url):
	...
    def __getitem__(self, url):
        """Load data from disk for this URL
        """
        path = self.url_to_path(url)
        if os.path.exists(path):
            with open(path, 'rb') as fp:
                return pickle.loads(fp.read())
        else:
            # URL has not yet been cached
            raise KeyError(url + ' does not exist')

    def __setitem__(self, url, result):
	...
```
在`__getitem__()`中，还是先用url_to_path()方法将URL映射为安全文件名。然后检查文件是否存在，如果存在则加载内容，并执行反序列化，恢复其原始数据类型；如果不存在，则说明缓存中还没有该URL的数据，此时会抛出KeyError异常。
## 2.2缓存测试
可以在python命令前加`time`计时。我们可以发现，如果是在本地服务器的网站，当缓存为空时爬虫实际耗时`0m58.710s`，第二次运行全部从缓存读取花了`0m0.221s`,快了`265`多倍。如果是爬取远程服务器的网站的数据时，将会耗更多时间。
```
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/3.下载缓存$ time python 2disk_cache_Nozip127.py 
Downloading: http://127.0.0.1:8000/places/
Downloading: http://127.0.0.1:8000/places/default/index/1
...
Downloading: http://127.0.0.1:8000/places/default/view/Afghanistan-1
real	0m58.710s
user	0m0.684s
sys	0m0.120s
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/3.下载缓存$ time python 2disk_cache_Nozip127.py 

real	0m0.221s
user	0m0.204s
sys	0m0.012s
```
## 2.3节省磁盘空间
为节省缓存占用空间，我们可以对下载的HTML文件进行压缩处理，使用zlib压缩序列化字符串即可。
```python
fp.write(zlib.compress(pickle.dumps(result)))
```
从磁盘加载后解压的代码如下：
```python
return pickle.loads(zlib.decompress(fp.read()))
```
压缩所有网页之后，缓存占用大小`2.8 MB`下降到`821.2 KB`，耗时略有增加。
```
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/3.下载缓存$ time python 2disk_cache.py 
Downloading: http://127.0.0.1:8000/places/
Downloading: http://127.0.0.1:8000/places/default/index/1
...
Downloading: http://127.0.0.1:8000/places/default/view/Afghanistan-1

real	1m0.011s
user	0m0.800s
sys	0m0.104s
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/3.下载缓存$ 
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/3.下载缓存$ time python 2disk_cache.py 

real	0m0.252s
user	0m0.228s
sys	0m0.020s
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/3.下载缓存$ 
```
## 2.4清理过期数据
本节中，我们将为缓存数据添加过期时间，以便爬虫知道何时需要重新下载网页。在构造方法中，我们使用timedelta对象将默认过期时间设置为30天，在`__set__`方法中把当前时间戳保存在序列化数据中，在`__get__`方法中对比当前时间和缓存时间，检查是否过期。
```python
from datetime import datetime, timedelta

class DiskCache:

    def __init__(self, cache_dir='cache', expires=timedelta(days=30), compress=True):
        """
        cache_dir: the root level folder for the cache
        expires: timedelta of amount of time before a cache entry is considered expired
        compress: whether to compress data in the cache
        """
        self.cache_dir = cache_dir
        self.expires = expires
        self.compress = compress

    def __getitem__(self, url):
        """Load data from disk for this URL
        """
        path = self.url_to_path(url)
        if os.path.exists(path):
            with open(path, 'rb') as fp:
                data = fp.read()
                if self.compress:
                    data = zlib.decompress(data)
                result, timestamp = pickle.loads(data)
                if self.has_expired(timestamp):
                    raise KeyError(url + ' has expired')
                return result
        else:
            # URL has not yet been cached
            raise KeyError(url + ' does not exist')

    def __setitem__(self, url, result):
        """Save data to disk for this url
        """
        path = self.url_to_path(url)
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
            os.makedirs(folder)

        data = pickle.dumps((result, datetime.utcnow()))
        if self.compress:
            data = zlib.compress(data)
        with open(path, 'wb') as fp:
            fp.write(data)

	...
    def has_expired(self, timestamp):
        """Return whether this timestamp has expired
        """
        return datetime.utcnow() > timestamp + self.expires
```
为了测试时间功能，我们可以将其缩短为5秒，如下操作：
```python
    """
    Dictionary interface that stores cached 
    values in the file system rather than in memory.
    The file path is formed from an md5 hash of the key.
    """
>>> from disk_cache import DiskCache
>>> cache=DiskCache()
>>> url='http://www.baidu.com'
>>> result={'html':'<html>...','code':200}
>>> cache[url]=result
>>> cache[url]
{'code': 200, 'html': '<html>...'}
>>> cache[url]['html']==result['html']
True
>>> 
>>> from datetime import timedelta
>>> cache2=DiskCache(expires=timedelta(seconds=5))
>>> url2='https://www.baidu.sss'
>>> result2={'html':'<html>..ss.','code':500}
>>> cache2[url2]=result2
>>> cache2[url2]
{'code': 200, 'html': '<html>...'}
>>> cache2[url2]
{'code': 200, 'html': '<html>...'}
>>> cache2[url2]
{'code': 200, 'html': '<html>...'}
>>> cache2[url2]
{'code': 200, 'html': '<html>...'}
>>> cache2[url2]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "disk_cache.py", line 57, in __getitem__
    raise KeyError(url + ' has expired')
KeyError: 'http://www.baidu.com has expired'
>>> cache2.clear()

```
## 2.5用磁盘缓存的缺点
由于受制于文件系统的限制，之前我们将URL映射为安全文件名，然而这样又会引发一些问题：
- 有些URL会被映射为相同的文件名。比如URL：`.../count.asp?a+b`,`.../count.asp?a*b`。
- URL截断255个字符的文件名也可能相同。因为URL可以超过2000下字符。

使用URL哈希值为文件名可以带来一定的改善。这样也有一些问题：
- 每个卷和每个目录下的文件数量是有限制的。FAT32文件系统每个目录的最大文件数65535，但可以分割到不同目录下。
- 文件系统可存储的文件总数也是有限的。ext4分区目前支持略多于1500万个文件，而一个大型网站往往拥有超过1亿个网页。

要想避免这些问题，我们需要把多个缓存网页合并到一个文件中，并使用类似B+树的算法进行索引。但我们不会自己实现这种算法，而是在下一节中介绍已实现这类算法的数据库。
# 3数据库缓存
爬取时，我们可能需要缓存大量数据，但又无须任何复杂的连接操作，因此我们将选用NoSQL数据库，这种数据库比传统的关系型数据库更容易扩展。在本节中，我们将选用目前非常流行的MongoDB作为缓存数据库。
## 3.1NoSQL是什么
	NoSQL全称为Not Only SQL，是一种相对较新的数据库设计方式。传统的关系模型使用是固定模式，并将数据分割到各个表中。然而，对于大数据集的情况，数据量太大使其难以存放在单一服务器中，此时就需要扩展到多台服务器。不过，关系模型对于这种扩展的支持并不够好，因为在查询多个表时，数据可能在不同的服务器中。相反，NoSQL数据库通常是无模式的，从设计之初就考虑了跨服务器无缝分片的问题。在NoSQL中，有多种方式可以实现该目标，分别是：
- 列数据存储（如HBase）；
- 键值对存储（如Redis）；
- 图形数据库（如Neo4j）；
- 面向文档的数据库（如MongoDB）。

## 3.2安装MongoDB
MongoDB可以从https://www.mongodb.org/downloads 下载。然后安装其Python封装库：
```
pip install pymongo
```
检测安装是否成功，在本地启动MongoDB服务器：
```
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/3.下载缓存$ mongod -dbpath MongoD
2017-01-17T21:20:46.224+0800 [initandlisten] MongoDB starting : pid=1978 port=27017 dbpath=MongoD 64-bit host=ubuntukylin64
2017-01-17T21:20:46.224+0800 [initandlisten] db version v2.6.10
2017-01-17T21:20:46.224+0800 [initandlisten] git version: nogitversion
2017-01-17T21:20:46.225+0800 [initandlisten] OpenSSL version: OpenSSL 1.0.2g  1 Mar 2016
2017-01-17T21:20:46.225+0800 [initandlisten] build info: Linux lgw01-12 3.19.0-25-generic #26~14.04.1-Ubuntu SMP Fri Jul 24 21:16:20 UTC 2015 x86_64 BOOST_LIB_VERSION=1_58
2017-01-17T21:20:46.225+0800 [initandlisten] allocator: tcmalloc
2017-01-17T21:20:46.225+0800 [initandlisten] options: { storage: { dbPath: "MongoD" } }
2017-01-17T21:20:46.269+0800 [initandlisten] journal dir=MongoD/journal
2017-01-17T21:20:46.270+0800 [initandlisten] recover : no journal files present, no recovery needed
2017-01-17T21:20:49.126+0800 [initandlisten] preallocateIsFaster=true 33.72
2017-01-17T21:20:51.932+0800 [initandlisten] preallocateIsFaster=true 32.7
2017-01-17T21:20:55.729+0800 [initandlisten] preallocateIsFaster=true 32.36
2017-01-17T21:20:55.730+0800 [initandlisten] preallocateIsFaster check took 9.459 secs
2017-01-17T21:20:55.730+0800 [initandlisten] preallocating a journal file MongoD/journal/prealloc.0
2017-01-17T21:20:58.042+0800 [initandlisten] 		File Preallocator Progress: 608174080/1073741824	56%
2017-01-17T21:21:03.290+0800 [initandlisten] 		File Preallocator Progress: 744488960/1073741824	69%
2017-01-17T21:21:08.043+0800 [initandlisten] 		File Preallocator Progress: 954204160/1073741824	88%
2017-01-17T21:21:18.347+0800 [initandlisten] preallocating a journal file MongoD/journal/prealloc.1
2017-01-17T21:21:21.166+0800 [initandlisten] 		File Preallocator Progress: 639631360/1073741824	59%
2017-01-17T21:21:26.328+0800 [initandlisten] 		File Preallocator Progress: 754974720/1073741824	70%
...
```
然后，在Python中，使用MongoDB的默认端口尝试连接MongoDB：
```python
>>> from pymongo import MongoClient
>>> client=MongoClient('localhost',27017)
```
## 3.3MongoDB概述
下面是MongoDB示例代码：
```python
>>> from pymongo import MongoClient
>>> client=MongoClient('localhost',27017)
>>> url='http://www.baidu.com/view/China-47'
>>> html='...<html>...'
>>> db=client.cache
>>> db.webpage.insert({'url':url,'html':html})
ObjectId('587e2cb26b00c10b956e0be9')
>>> db.webpage.find_one({'url':url})
{u'url': u'http://www.baidu.com/view/China-47', u'_id': ObjectId('587e2cb26b00c10b956e0be9'), u'html': u'...<html>...'}
>>> db.webpage.find({'url':url})
<pymongo.cursor.Cursor object at 0x7fcde0ca60d0>
>>> db.webpage.find({'url':url}).count()
1
```
当插入同一条记录时，MongoDB会欣然接受并执行这次操作，但通过查找发现记录没更新。
```python
>>> db.webpage.insert({'url':url,'html':html})
ObjectId('587e2d546b00c10b956e0bea')
>>> db.webpage.find({'url':url}).count()
2
>>> db.webpage.find_one({'url':url})
{u'url': u'http://www.baidu.com/view/China-47', u'_id': ObjectId('587e2cb26b00c10b956e0be9'), u'html': u'...<html>...'}
```
为了存储最新的记录，并避免重复记录，我们将ID设置为URL，并执行`upsert`操作。该操作表示当记录存在时则更新记录，否则插入新记录。
```python
>>> 
>>> new_html='<...>...'
>>> db.webpage.update({'_id':url},{'$set':{'html':new_html}},upsert=True)
{'updatedExisting': True, u'nModified': 1, u'ok': 1, u'n': 1}
>>> db.webpage.find_one({'_id':url})
{u'_id': u'http://www.baidu.com/view/China-47', u'html': u'<...>...'}
>>> db.webpage.find({'_id':url}).count()
1
>>> db.webpage.update({'_id':url},{'$set':{'html':new_html}},upsert=True)
{'updatedExisting': True, u'nModified': 0, u'ok': 1, u'n': 1}
>>> db.webpage.find({'_id':url}).count()
1
>>> 
```
MongoDB官方文档：http://docs.mongodb.org/manual/ 
## 3.4MongoDB缓存实现
现在我们已经准备好创建基于MongoDB的缓存了，这里使用了和之前的DiskCache类相同的接口。我们在下面构造方法中创建了`timestamp`索引，在达到给定的时间戳之后，MongoDB的这一便捷功能可以自动过期删除记录。
```python
import pickle
from datetime import datetime, timedelta
from pymongo import MongoClient

class MongoCache:
    def __init__(self, client=None, expires=timedelta(days=30)):
        """
        client: mongo database client
        expires: timedelta of amount of time before a cache entry is considered expired
        """
        # if a client object is not passed 
        # then try connecting to mongodb at the default localhost port 
        self.client = MongoClient('localhost', 27017) if client is None else client
        #create collection to store cached webpages,
        # which is the equivalent of a table in a relational database
        self.db = self.client.cache
        self.db.webpage.create_index('timestamp', expireAfterSeconds=expires.total_seconds())

    def __getitem__(self, url):
        """Load value at this URL
        """
        record = self.db.webpage.find_one({'_id': url})
        if record:
            return record['result']
        else:
            raise KeyError(url + ' does not exist')

    def __setitem__(self, url, result):
        """Save value for this URL
        """
        record = {'result': result, 'timestamp': datetime.utcnow()}
        self.db.webpage.update({'_id': url}, {'$set': record}, upsert=True)
```
下面我们来测试一下这个MongoCache类，我们用默认0时间间隔`timedelta()`对象进行测试，此时记录创建后应该会马上会被删除，但实际却没有。这是因为MongoDB运行机制造成的，MongoDB后台运行了一个每分钟检查一次过期记录的任务。所以我们可以再等一分钟，就会发现缓存过期机制已经运行成功了。
```python
>>> from mongo_cache import MongoCache
>>> from datetime import timedelta
>>> cache=MongoCache(expires=timedelta())
>>> result={'html':'.....'}
>>> cache[url]=result
>>> cache[url]
{'html': '.....'}
>>> cache[url]
{'html': '.....'}
>>> import time
>>> import time;time.sleep(60)
>>> cache[url]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "mongo_cache.py", line 62, in __getitem__
    raise KeyError(url + ' does not exist')
KeyError: 'http://www.baidu.com/view/China-47 does not exist'
>>> 
```
## 3.5压缩存储
```python
import pickle
import zlib
from bson.binary import Binary

class MongoCache:
    def __getitem__(self, url):
        """Load value at this URL
        """
        record = self.db.webpage.find_one({'_id': url})
        if record:
            #return record['result']
            return pickle.loads(zlib.decompress(record['result']))
        else:
            raise KeyError(url + ' does not exist')

    def __setitem__(self, url, result):
        """Save value for this URL
        """
        #record = {'result': result, 'timestamp': datetime.utcnow()}
        record = {'result': Binary(zlib.compress(pickle.dumps(result))), 'timestamp': datetime.utcnow()}
        self.db.webpage.update({'_id': url}, {'$set': record}, upsert=True)
```
## 3.6缓存测试
```
wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/3.下载缓存$ time python 3mongo_cache.py 
Downloading: http://127.0.0.1:8000/places/
Downloading: http://127.0.0.1:8000/places/default/index/1
Downloading: http://127.0.0.1:8000/places/default/index/2
...
Downloading: http://127.0.0.1:8000/places/default/view/Algeria-4
Downloading: http://127.0.0.1:8000/places/default/view/Albania-3
Downloading: http://127.0.0.1:8000/places/default/view/Aland-Islands-2
Downloading: http://127.0.0.1:8000/places/default/view/Afghanistan-1

real	0m59.239s
user	0m1.164s
sys	0m0.108s


wu_being@ubuntukylin64:~/GitHub/WebScrapingWithPython/3.下载缓存$ time python 3mongo_cache.py 

real	0m0.695s
user	0m0.408s
sys	0m0.044s

```
可以看出，用数据库缓存的读取时间是磁盘缓存的两倍，但成功地避免了磁盘缓存的缺点。
## 3.7MongoDB缓存完整代码
```python
try:
    import cPickle as pickle
except ImportError:
    import pickle
import zlib
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson.binary import Binary

from link_crawler import link_crawler


class MongoCache:
    """
    Wrapper around MongoDB to cache downloads

    >>> cache = MongoCache()
    >>> cache.clear()
    >>> url = 'http://example.webscraping.com'
    >>> result = {'html': '...'}
    >>> cache[url] = result
    >>> cache[url]['html'] == result['html']
    True
    >>> cache = MongoCache(expires=timedelta())
    >>> cache[url] = result
    >>> # every 60 seconds is purged http://docs.mongodb.org/manual/core/index-ttl/
    >>> import time; time.sleep(60)
    >>> cache[url] 
    Traceback (most recent call last):
     ...
    KeyError: 'http://example.webscraping.com does not exist'
    """
    def __init__(self, client=None, expires=timedelta(days=30)):
        """
        client: mongo database client
        expires: timedelta of amount of time before a cache entry is considered expired
        """
        # if a client object is not passed 
        # then try connecting to mongodb at the default localhost port 
        self.client = MongoClient('localhost', 27017) if client is None else client
        #create collection to store cached webpages,
        # which is the equivalent of a table in a relational database
        self.db = self.client.cache
        self.db.webpage.create_index('timestamp100s', expireAfterSeconds=expires.total_seconds())		#timestamp

    def __contains__(self, url):
        try:
            self[url]
        except KeyError:
            return False
        else:
            return True
    
    def __getitem__(self, url):
        """Load value at this URL
        """
        record = self.db.webpage.find_one({'_id': url})
        if record:
            #return record['result']
            return pickle.loads(zlib.decompress(record['result']))
        else:
            raise KeyError(url + ' does not exist')


    def __setitem__(self, url, result):
        """Save value for this URL
        """
        #record = {'result': result, 'timestamp': datetime.utcnow()}
        record = {'result': Binary(zlib.compress(pickle.dumps(result))), 'timestamp100s': datetime.utcnow()}	#timestamp
        self.db.webpage.update({'_id': url}, {'$set': record}, upsert=True)


    def clear(self):
        self.db.webpage.drop()
        print 'drop() successful'



if __name__ == '__main__':	
    #link_crawler('http://example.webscraping.com/', '/(index|view)', cache=MongoCache())
    #link_crawler('http://127.0.0.1:8000/places/', '/places/default/(index|view)/', cache=MongoCache())
    link_crawler('http://127.0.0.1:8000/places/', '/places/default/(index|view)/', cache=MongoCache(expires=timedelta(seconds=100)))

```
