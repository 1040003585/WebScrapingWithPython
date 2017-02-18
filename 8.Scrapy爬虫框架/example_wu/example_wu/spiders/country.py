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
