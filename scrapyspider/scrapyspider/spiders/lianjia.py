# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from urllib import parse
from items import LianJiaItem, LianJiaItemLoader, LianJia_latitude_longitude
from scrapy.loader import ItemLoader
from utils.common_use_func import get_md5
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from pyvirtualdisplay import Display


class LianjiaSpider(scrapy.Spider):
    name = 'lianjia'
    allowed_domains = ['sh.lianjia.com']
    start_urls = ['http://sh.lianjia.com/zufang/']

    headers = {
        "HOST": "sh.lianjia.com/zufang/",
        "Referer": "http://sh.lianjia.com/zufang/",
        "Authorization": "Bearer Mi4wQUREQWlJMkY5QWtBWUFJWGZCUHRDeGNBQUFCaEFsVk5WUDZQV1FBU0ZRcGMybVFReDB"
                         "WbjNsRzN4R3QzcjdqTGZn|1500016980|81289be24b3158df44a24d22e9e682cd1ad3e76c",
        'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36"
    }

    custom_settings = {
        "COOKIES_ENABLED": False
    }

    def __init__(self):
        super(LianjiaSpider, self).__init__()
        display = Display(visible=0, size=(800, 600))
        display.start()
        chrome_opt = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_opt.add_experimental_option("prefs", prefs)
        self.browser = webdriver.Chrome(executable_path="/home/chandler/github/Spider/chromedriver",
                                        chrome_options=chrome_opt)
        self.browser.implicitly_wait(10)  # 设置超时时间
        self.browser.set_page_load_timeout(10)  # 设置超时时间
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        # 爬虫退出，关闭chrome
        print("spider closed")
        self.browser.quit()

    def parse(self, response):
        all_urls = response.xpath("//a/@href").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("http://sh.lianjia.com/zufang/") else False, all_urls)
        for url in all_urls:
            match_re = re.match("(.*sh.lianjia.com/zufang/(\w*\d*)(.html$))", url)
            # match_re = re.match("(.*sh.lianjia.com/zufang/(\w[a-z]*$))", url)
            if match_re:
                request_url = match_re.group(1)
                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_lianjia)

            else:
                yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse_lianjia(self, response):
        lianjia_id = 0
        match_re = re.match("(.*sh.lianjia.com/zufang/shz(\d+)).*", response.url)
        if match_re:
            lianjia_id = int(match_re.group(2))
        item_loader = ItemLoader(item=LianJiaItem(), response=response)
        item_loader.add_value("url", response.url)
        item_loader.add_value("lianjia_id", lianjia_id)
        item_loader.add_css("residential_district_name", "table.aroundInfo tr:nth-child(3) td:nth-child(2) p a::text")
        item_loader.add_css("region", "table.aroundInfo tr:nth-child(2) td:nth-child(2) a::text")
        item_loader.add_css("address", "table.aroundInfo tr:nth-child(4) td:nth-child(2) p::attr(title)")
        item_loader.add_css("house_area", ".houseInfo .area .mainInfo::text")
        item_loader.add_css("room_count", ".houseInfo .room .mainInfo::text")
        item_loader.add_css("face_direction", "table.aroundInfo tr:nth-child(1) td:nth-child(4)::text")
        item_loader.add_xpath("rent_price", "//div[@class='mainInfo bold']/text()")
        item_loader.add_css("floor", "table.aroundInfo tr td:nth-child(2)::text")
        item_loader.add_css("publish_time", "table.aroundInfo tr:nth-child(2) td:nth-child(4)::text")
        item_loader.add_css("total_watch_count", ".totalCount span::text")

        lianjia = item_loader.load_item()
        residential_district_url = response.css("table.aroundInfo tr:nth-child(3) td:nth-child(2) p a::attr(href)").extract_first("")
        residential_district_url = parse.urljoin(response.url, residential_district_url)
        lianjia["residential_district_url"] = residential_district_url
        residential_district_name = lianjia.get("residential_district_name", "")
        yield scrapy.Request(residential_district_url, headers=self.headers,
                             meta={
                                 "residential_district_name": residential_district_name,
                                 "residential_district_url": residential_district_url,
                                 "lianjia_id": lianjia_id
                             },
                             callback=self.parse_Latitude_longitude)

        yield lianjia

    def parse_Latitude_longitude(self, response):
        item_loader = ItemLoader(item=LianJia_latitude_longitude(), response=response)
        residential_district_name = response.meta.get("residential_district_name")
        residential_district_url = response.meta.get("residential_district_url")
        lianjia_id = response.meta.get("lianjia_id", "")
        # [121.578972, 31.24942342, '金杨四街坊'](左经度，右纬度)
        item_loader.add_xpath("longitude", "//a[@id='actshowMap_xiaoqu']/@xiaoqu")
        item_loader.add_xpath("latitude", "//a[@id='actshowMap_xiaoqu']/@xiaoqu")
        latitude_longitude = item_loader.load_item()
        latitude_longitude["residential_district_name"] = residential_district_name[0]
        latitude_longitude["residential_district_url"] = residential_district_url
        latitude_longitude["lianjia_id"] = lianjia_id

        yield latitude_longitude



