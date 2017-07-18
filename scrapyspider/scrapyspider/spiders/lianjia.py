# -*- coding: utf-8 -*-
import scrapy


class LianjiaSpider(scrapy.Spider):
    name = 'lianjia'
    allowed_domains = ['sh.lianjia.com']
    start_urls = ['http://sh.lianjia.com/']

    headers = {
        "HOST": "sh.lianjia.com",
        "Referer": "http://sh.lianjia.com/",
        'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36"
    }

    def parse(self, response):
        # [121.578972, 31.24942342, '金杨四街坊']
        Latitude_longitude = response.xpath("//a[@id='actshowMap_xiaoqu']/@xiaoqu").extract()[0]
        pass
