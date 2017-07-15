# -*- coding: utf-8 -*-
import scrapy


class LagoujobSpider(scrapy.Spider):
    name = 'lagoujob'
    allowed_domains = ['www.lagou.com']
    start_urls = ['http://www.lagou.com/']

    def parse(self, response):
        pass
