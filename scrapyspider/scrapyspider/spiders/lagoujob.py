# -*- coding: utf-8 -*-
import scrapy
from utils.common_use_func import get_md5
from urllib import parse
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from items import LaGouJobItem, LaGouItemLoader
from scrapy_redis.spiders import RedisSpider
from pyvirtualdisplay import Display
import datetime
import re


class LagoujobSpider(RedisSpider):
    name = 'lagoujob'
    allowed_domains = ['www.lagou.com']
    redis_key = 'lagoujob:start_urls'
    # start_urls = ['https://www.lagou.com/']

    headers = {
        "HOST": "www.lagou.com",
        "Referer": "https://www.lagou.com",
        "Authorization": "Bearer Mi4wQUREQWlJMkY5QWtBWUFJWGZCUHRDeGNBQUFCaEFsVk5WUDZQV1FBU0ZRcGMybVFReDB"
                         "WbjNsRzN4R3QzcjdqTGZn|1500016980|81289be24b3158df44a24d22e9e682cd1ad3e76c",
        'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36"
    }

    # def __init__(self):
    #     super(LagoujobSpider, self).__init__()
    #     display = Display(visible=0, size=(800, 600))
    #     display.start()
    #     chrome_opt = webdriver.ChromeOptions()
    #     prefs = {"profile.managed_default_content_settings.images": 2}
    #     chrome_opt.add_experimental_option("prefs", prefs)
    #     self.browser = webdriver.Chrome(executable_path="/home/chandler/github/Spider/chromedriver",
    #                                     chrome_options=chrome_opt)
    #     self.browser.implicitly_wait(10)  # 设置超时时间
    #     self.browser.set_page_load_timeout(10)  # 设置超时时间
    #     self.fail_urls = []
    #     dispatcher.connect(self.handle_spider_closed, signals.spider_closed)
    #     dispatcher.connect(self.spider_closed, signals.spider_closed)
    #
    # def handle_spider_closed(self, spider, reason):
    #     self.crawler.stats.set_value("failed_urls", ",".join(self.fail_urls))
    #
    # def spider_closed(self, spider):
    #     # 爬虫退出，关闭chrome
    #     print("spider closed")
    #     self.browser.quit()

    def parse(self, response):
        all_urls = response.xpath("//a/@href").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("http") else False, all_urls)
        for url in all_urls:
            match_re = re.match("(.*lagou.com/jobs(/|$).*)", url)
            if match_re:
                request_url = match_re.group(1)
                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_detail)
            else:
                yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse_detail(self, response):
        item_loader = LaGouItemLoader(item=LaGouJobItem(), response=response)
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_xpath("title", "//div[@class='job-name']/@title")
        item_loader.add_xpath("salary_min", "//dd[@class='job_request']/p/span[@class='salary']/text()")
        item_loader.add_xpath("salary_max", "//dd[@class='job_request']/p/span[@class='salary']/text()")
        item_loader.add_xpath("company_name", "//dl[@id='job_company']/dt/a/img/@alt")
        item_loader.add_xpath("job_city", "//dd[@class='job_request']/p/span[2]/text()")
        item_loader.add_xpath("work_years_min", "//dd[@class='job_request']/p/span[3]/text()")
        item_loader.add_xpath("work_years_max", "//dd[@class='job_request']/p/span[3]/text()")
        item_loader.add_xpath("education_degree", "//dd[@class='job_request']/p/span[4]/text()")
        item_loader.add_xpath("job_type", "//dd[@class='job_request']/p/span[5]/text()")
        item_loader.add_xpath("publish_time", "//p[@class='publish_time']/text()")
        item_loader.add_xpath("tags", "//ul[@class='position-label clearfix']/li/text()")
        item_loader.add_xpath("job_advantage", "//dd[@class='job-advantage']/p/text()")
        item_loader.add_xpath("job_desc", "//dd[@class='job_bt']/div")
        item_loader.add_xpath("job_addr", "//div[@class='work_addr']")
        item_loader.add_xpath("company_url", "//dl[@id='job_company']/dt/a/@href")
        item_loader.add_value("crwal_time", datetime.datetime.now())
        item_loader.add_value("crwal_update_time", datetime.datetime.now())

        lagou_job = item_loader.load_item()
        yield lagou_job

