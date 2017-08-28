# -*- coding: utf-8 -*-
import scrapy
import json
import math
import requests
import copy
import csv
from urllib.parse import quote, unquote
from items import LaGouJobItem, LaGouItemLoader
from scrapy_redis.spiders import RedisSpider

class Lagou(RedisSpider):
    name = "lagoujob_json"
    allowed_domains = ['www.lagou.com']
    redis_key = 'lagoujob:start_urls'
    # start_urls = [
    #     'https://www.lagou.com'
    # ]


    cities = ['上海']
    jobs = ['Python']


    headers = {
        "Accept": "application / json, text / javascript, * / *; q = 0.01",
        "Accept - Encoding":"gzip, deflate, br",
        "Accept - Language":"zh - CN, zh;q = 0.8",
        "Connection":"keep - alive",
        "Content - Length":"24",
        "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
        "Host":"www.lagou.com",
        "Origin":"https://www.lagou.com",
        "Referer": "https://www.lagou.com/jobs/list_python?px=default&city={0}",
        "User-Agent":"Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36",

        "X - Anit - Forge - Code":"0",
        "X - Anit - Forge - Token":"None",
        "X - Requested - With":"XMLHttpRequest"
    }

    form_url = 'https://www.lagou.com/jobs/positionAjax.json?px=default&city={0}&needAddtionalResult=false&isSchoolJob=0'
    list_url = 'https://www.lagou.com/jobs/list_{0}?px=default&city={1}#filterBox'


    def parse(self, response):
        for city in self.cities:
            for job in self.jobs:
                new_headers = copy.deepcopy(self.headers)
                quoted_city = quote(city)
                new_headers["Referer"] = new_headers["Referer"].format(quoted_city)
                post_url = requests.post(self.form_url.format(quoted_city), data={"page": "1", "job": job, "first": "true"}, headers=new_headers)
                test_json = json.loads(post_url.text)
                total_jobs = test_json["content"]["positionResult"]["totalCount"]
                total_pages = math.ceil(total_jobs / 15)
                for x in range(total_pages):
                    page = x+1
                    yield scrapy.FormRequest(self.form_url.format(city), meta={"page":page,"job":job,"city":city},
                                             formdata={"page":str(page),"job":job,"first":"true"}, headers=new_headers, callback=self.parse_job)

    def parse_job(self, response):
        response_json = json.loads(response.text)
        page = response.meta.get("page",1)
        job = response.meta.get("job","")
        city = response.meta.get("city","")
        print('>>>>>>>>>>正在爬取【{0}】中的【{1}】的第{2}页...<<<<<<<<<<<'.format(unquote(city), job, page))
        try:
            job_list = response_json["content"]["positionResult"]["result"]
            for job in job_list:
                item_loader = LaGouItemLoader(item=LaGouJobItem())
                item_loader.add_value("PositionName", job["positionName"])
                item_loader.add_value("City", job["city"])
                item_loader.add_value("CompanyShortName", job["companyShortName"])
                item_loader.add_value("CompanyFullName", job["companyFullName"])
                item_loader.add_value("Salary_Max", job["salary"])
                item_loader.add_value("Salary_Min", job["salary"])
                item_loader.add_value("WorkYear_Min", job["workYear"])
                item_loader.add_value("WorkYear_Max", job["workYear"])
                item_loader.add_value("IndustryField", job["industryField"])
                item_loader.add_value("CreateTime", job["createTime"])
                item_loader.add_value("Education", job["education"])
                item_loader.add_value("FirstType", job["firstType"])
                item_loader.add_value("SecondType", job["secondType"])
                item_loader.add_value('PositionLables', job['positionLables'])
                item_loader.add_value('PositionId',job['positionId'])
                item_loader.add_value('PublisherId', job['publisherId'])
                item_loader.add_value('PositionAdvantage', job['positionAdvantage'])
                item_loader.add_value('isSchoolJob', job['isSchoolJob'])
                item_loader.add_value('financeStage', job['financeStage'])
                item_loader.add_value('businessZones', job['businessZones'])
                item_loader.add_value('jobNature', job['jobNature'])


                job_item = item_loader.load_item()
                yield job_item

        except Exception as e:
            print(e)
            with open('scrawl4_fail_info.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([quote(city), job, page])