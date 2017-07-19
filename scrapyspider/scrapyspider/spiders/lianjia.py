# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from urllib import parse
from items import LianJiaItem
from scrapy.loader import ItemLoader
from utils.common_use_func import get_md5


class LianjiaSpider(scrapy.Spider):
    name = 'lianjia'
    allowed_domains = ['sh.lianjia.com/zufang']
    start_urls = ['http://sh.lianjia.com/zufang']

    headers = {
        "HOST": "sh.lianjia.com/zufang",
        "Referer": "http://sh.lianjia.com/zufang",
        'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36"
    }

    def parse(self, response):
        all_urls = response.xpath("//a/@href").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("http") else False, all_urls)
        for url in all_urls:
            match_re = re.match("(.*sh.lianjia.com/zufang/(\w*\d*)(.html$))", url)
            # match_re = re.match("(.*sh.lianjia.com/zufang/(\w[a-z]*$))", url)
            if match_re:
                request_url = match_re.group(1)
                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_lianjia)
            else:
                yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse_lianjia(self, response):
        item_loader = ItemLoader(item=LianJiaItem(), response=response)
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("residential_district_name", "table.aroundInfo tr:nth-child(3) td:nth-child(2) p a::text")
        item_loader.add_css("residential_district_url", "table.aroundInfo tr:nth-child(3) td:nth-child(2) p a::attr(href)")
        item_loader.add_css("region", "table.aroundInfo tr:nth-child(2) td:nth-child(2) a::text")
        item_loader.add_css("address", "table.aroundInfo tr:nth-child(4) td:nth-child(2) p::attr(title)")
        item_loader.add_css("house_area", ".houseInfo .area .mainInfo::text")
        item_loader.add_xpath("room_count", ".houseInfo .room .mainInfo::text")
        item_loader.add_xpath("face_direction", "table.aroundInfo tr:nth-child(1) td:nth-child(4)::text")
        item_loader.add_xpath("rent_price", "//div[@class='mainInfo bold']/text()")
        item_loader.add_xpath("floor", "table.aroundInfo tr td:nth-child(2)::text")
        item_loader.add_xpath("publish_time", "table.aroundInfo tr:nth-child(2) td:nth-child(4)::text")
        item_loader.add_xpath("total_watch_count", ".totalCount span::text")
        item_loader.add_value("crwal_time", datetime.datetime.now())
        item_loader.add_value("crwal_update_time", datetime.datetime.now())

        lianjia = item_loader.load_item()
        Latitude_longitude = response.xpath("//a[@id='actshowMap_xiaoqu']/@xiaoqu").extract()[0]  # [121.578972, 31.24942342, '金杨四街坊'](左经度，右纬度)

        pass




