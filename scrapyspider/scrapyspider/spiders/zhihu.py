# -*- coding: utf-8 -*-
import scrapy
import re
import json
import time
import os
import datetime
from PIL import Image
from urllib import parse
from scrapyspider.items import ZhiHuQuestionItem, ZhiHuAnswerItem
from scrapy.loader import ItemLoader
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent': "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Ubuntu Chromium/58.0.3029.110 Chrome/58.0.3029.110 Safari/537.36"
    }

    custom_settings = {
        "COOKIES_ENABLED": True
    }

    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort" \
                       "_by=default&include=data%5B%2A%5D.is_normal%2Cis" \
                       "_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse" \
                       "_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment" \
                       "_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup" \
                       "_count%2Creshipment_settings%2Ccomment_permission%2Cmark" \
                       "_infos%2Ccreated_time%2Cupdated_time%2Creview" \
                       "_info%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis" \
                       "_thanked%2Cis_nothelp%2Cupvoted_" \
                       "followees%3Bdata%5B%2A%5D.author." \
                       "follower_count%2Cbadge%5B%3F%28type%3Dbest_" \
                       "answerer%29%5D.topics&limit={1}&offset={2}"

    handle_httpstatus_list = [401]

    def __init__(self):
        self.fail_urls = []
        dispatcher.connect(self.handle_spider_closed, signals.spider_closed)

    def handle_spider_closed(self, spider, reason):
        self.crawler.stats.set_value("failed_urls", ",".join(self.fail_urls))

    def parse(self, response):
        if response.status == 401:
            self.fail_urls.append(response.url)
            self.crawler.stats.inc_value("failed_url")

        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            match_re = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_re:
                request_url = match_re.group(1)
                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question)
                break

            else:
                # yield scrapy.Request(url, headers=self.headers, callback=self.parse)
                pass

    def parse_question(self, response):
        question_id = 0
        match_re = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
        if match_re:
            question_id = int(match_re.group(2))
        item_loader = ItemLoader(item=ZhiHuQuestionItem(), response=response)
        item_loader.add_value("zhihu_id", question_id)
        item_loader.add_xpath("question_topics", "//div[@class='Popover']/div/text()")
        item_loader.add_value("question_url", response.url)
        item_loader.add_xpath("question_title", "//h1[@class='QuestionHeader-title']/text()")
        item_loader.add_xpath("question_content", "//div[@class='QuestionHeader-detail']/div/div/span/text()")
        item_loader.add_xpath("question_answer_num", "//h4[@class='List-headerText']/span/text()")
        item_loader.add_xpath("question_comments_num", "//div[@class='QuestionHeader-Comment']/button/text()")
        item_loader.add_xpath("question_watch_user_num", "//div[@class='NumberBoard-value']/text()")
        item_loader.add_xpath("question_follow_num", "//div[@class='NumberBoard-value']/text()")

        question_item = item_loader.load_item()
        question_item["question_create_date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        question_item["question_update_date"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0),
                             meta={"question_item": question_item}, headers=self.headers,
                             callback=self.parse_answer)
        yield question_item

    def parse_answer(self, response):
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        next_url = ans_json["paging"]["next"]

        for answer in ans_json["data"]:
            answer_item = ZhiHuAnswerItem()
            question_item = ZhiHuQuestionItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["answer_url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["answer_author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["answer_content"] = answer["content"] if "content" in answer else None
            answer_item["answer_praise_num"] = answer["voteup_count"]
            answer_item["answer_comments_num"] = answer["comment_count"]
            answer_item["answer_create_date"] = answer["created_time"]
            answer_item["answer_update_date"] = answer["updated_time"]
            # answer_item["answer_crawl_time"] = datetime.datetime.now()
            # answer_item["answer_crawl_updatetime"] = datetime.datetime.now()
            question_item["question_create_date"] = answer["question"]["created"]
            question_item["question_update_date"] = answer["question"]["updated_time"]

            yield answer_item

        if is_end is not True:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)

    def start_requests(self):
        return [scrapy.Request("http://www.zhihu.com/#signin", headers=self.headers, callback=self.login)]

    def login(self, response):
        response_text = response.text
        match_re = re.match('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
        xsrf = ""
        if match_re:
            xsrf = match_re.group(1)

        if xsrf:
            post_data = {
                "_xsrf": xsrf,
                "phone_num": "13770955080",
                "password": "iloveyou1314",
                "captcha": ""
            }
            t = str(int(time.time()*1000))
            captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(t)

            yield scrapy.Request(captcha_url, meta={"post_data": post_data}, headers=self.headers,
                                 callback=self.login_after_captcha)

    def login_after_captcha(self, response):
        with open("captcha.jpg", "wb") as f:
            f.write(response.body)
            f.close()
        # 使用Image方法打开我们下载的验证码图片
        # 如果打开失败就去文件路径下找jpg手动查看
        try:
            im = Image.open("captcha.jpg")
            im.show()
            im.close()
        except:
            print("请到 %s 目录找到captcha.jpg 手动输入" % os.path.abspath("captcha.jpg"))

        captcha = input("输入验证码 : ")

        post_data = response.meta.get("post_data", {})
        post_url = "https://www.zhihu.com/login/phone_num"
        post_data["captcha"] = captcha
        return [scrapy.FormRequest(
            url=post_url,
            formdata=post_data,
            headers=self.headers,
            callback=self.check_login
        )]

    def check_login(self, response):
        text_json = json.loads(response.text)
        if "msg" in text_json and text_json["msg"] == "登录成功":
            print("登录成功")
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)
        else:
            print("登录失败")
