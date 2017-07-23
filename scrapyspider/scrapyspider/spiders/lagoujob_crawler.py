# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from items import LaGouItemLoader, LaGouJobItem
from utils.common_use_func import get_md5
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
import datetime


class LagoujobCrawlerSpider(CrawlSpider):
    name = 'lagoujob_crawler'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=("zhaopin/.*",)), follow=True),
        Rule(LinkExtractor(allow=("gongsi/j\d.html",)), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
    )

    headers = {
        "HOST": "www.lagou.com",
        "Referer": "https://www.lagou.com",
        "Authorization": "Bearer Mi4wQUREQWlJMkY5QWtBWUFJWGZCUHRDeGNBQUFCaEFsVk5WUDZQV1FBU0ZRcGMybVFReDB"
                         "WbjNsRzN4R3QzcjdqTGZn|1500016980|81289be24b3158df44a24d22e9e682cd1ad3e76c",
        'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36"
    }

    # handle_httpstatus_list = [401]
    #
    # def __init__(self):
    #     self.fail_urls = []
    #     dispatcher.connect(self.handle_spider_closed, signals.spider_closed)
    #
    # def handle_spider_closed(self, spider, reason):
    #     self.crawler.stats.set_value("failed_urls", ",".join(self.fail_urls))

    def parse_job(self, response):
        item_loader = LaGouItemLoader(item=LaGouJobItem(), response=response)
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_xpath("title", "//dd[@class='job_request']/p/span[@class='salary']/text()")
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
        item_loader.add_xpath("job_desc", "//dd[@class='job_bt']/div/p/text()")
        item_loader.add_xpath("job_addr", "//div[@class='work_addr']")
        item_loader.add_xpath("company_url", "//dl[@id='job_company']/dt/a/@href")
        item_loader.add_value("crwal_time", datetime.datetime.now())
        item_loader.add_value("cral_updatet_time", datetime.datetime.now())

        lagou_job = item_loader.load_item()
        return lagou_job

# title = response.xpath("//div[@class='job-name']/@title").extract()[0]
# salary = response.xpath("//dd[@class='job_request']/p/span[@class='salary']/text()").extract()[0]
# job_city = response.xpath("//dd[@class='job_request']/p/span[2]/text()").extract()[0]
# work_years = response.xpath("//dd[@class='job_request']/p/span[3]/text()").extract()[0]
# education_degree = response.xpath("//dd[@class='job_request']/p/span[4]/text()").extract()[0]
# job_type =  response.xpath("//dd[@class='job_request']/p/span[5]/text()").extract()[0]
# tags = response.xpath("//ul[@class='position-label clearfix']/li/text()").extract()
# publish_time = response.xpath("//p[@class='publish_time']/text()").extract()[0]
# job_advantage = response.xpath("//dd[@class='job-advantage']/p/text()").extract()[0]
# job_desc = response.xpath("//dd[@class='job_bt']/div/p/text()").extract()
# job_addr = response.xpath("//div[@class='work_addr']").extract()[0]
# company_url = response.xpath("//dl[@id='job_company']/dt/a/@href").extract()[0]
# company_name = response.xpath("//dl[@id='job_company']/dt/a/img/@alt").extract()[0]


