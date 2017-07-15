# -*- coding: utf-8 -*-
import scrapy


class LagoujobSpider(scrapy.Spider):
    name = 'lagoujob'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    def parse(self, response):
        pass
