# 下载缓存
上篇文章，我们学习了如何提取网页中的数据，以及将提取结果存到表格中。如果我们还想提取另一字段，则需要重新再下载整个网页，这对我们这个小型的示例网站问题不大，但对于数百万个网页的网站而言来说就要消耗几个星期的时间。所以，我们可以先对网页进行缓存，就使得每个网页只下载一次。
# 1 为链接爬虫添加缓存支持
- 我们将downloader重构一类，这样参数只需在构造方法中设置一次，就能在后续多次复用，在URL下载之前进行缓存检查，并把限速功能移到函数内部。
- 在Downloader类的__call__特殊方法实现了下载前先检查缓存，如果已经定义该URL缓存则再检查下载中是否遇到了服务端错误，如果都没问题表明缓存结果可用，否则都需要正常下载该URL存到缓存中。
- downloader方法返回添加了HTTP状态码，以便缓存中存储错误机校验。如果不需要限速或缓存的话，你可以直接调用该方法，这样就不会通过__call__方法调用了。

```python

class Downloader:
    def __init__(self, delay=5, user_agent='Wu_Being', proxies=None, num_retries=1, timeout=60, opener=None, cache=None):
        self.throttle = Throttle(delay)
        self.user_agent = user_agent
        self.proxies = proxies
        self.num_retries = num_retries
        self.opener = opener
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

def link_crawler(... cache=None):
    crawl_queue = [seed_url]
    seen = {seed_url: 0}
    # track how many URL's have been downloaded
    num_urls = 0
    rp = get_robots(seed_url)
    D = Downloader(delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries, cache=cache)

    while crawl_queue:
        url = crawl_queue.pop()
        depth = seen[url]
        # check url passes robots.txt restrictions
        if rp.can_fetch(user_agent, url):
            html = D(url)
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

if __name__ == '__main__':
    link_crawler('http://example.webscraping.com', '/(index|view)', delay=0, num_retries=1, user_agent='BadCrawler')
    link_crawler('http://example.webscraping.com', '/(index|view)', delay=0, num_retries=1, max_depth=1, user_agent='GoodCrawler')
```

# 2 磁盘缓存
# 3 数据库缓存
