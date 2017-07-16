# -*- coding: utf-8 -*-
import scrapy
from items import LaGouItemLoader, LaGouJobItem
from utils.common_use_func import get_md5
from urllib import parse
import datetime
import re


class LagoujobSpider(scrapy.Spider):
    name = 'lagoujob'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    headers = {
        "HOST": "www.lagou.com",
        "Referer": "https://www.lagou.com",
        'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36"
    }

    def parse(self, response):
        all_urls = response.xpath("//a/@href").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("http") else False, all_urls)
        for url in all_urls:
            match_re = re.match("(.*lagou.com/jobs(/|$).*)", url)
            if match_re:
                request_url = match_re.group(1)
                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_detail)
                break
            else:
                # yield scrapy.Request(url, headers=self.headers, callback=self.parse)
                pass

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
