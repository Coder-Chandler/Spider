# -*- coding: utf-8 -*-
import scrapy
import re
import json
import time
import os
from PIL import Image


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

    def parse(self, response):
        pass

    def start_requests(self):
        return [scrapy.Request("http://www.zhihu.com/#signin", headers=self.headers, callback=self.login)]

    def login(self, response):
        response_text = response.text
        match_re = re.match('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
        xsrf = ""
        if match_re:
            xsrf = match_re.group(1)

        if xsrf:
            post_url = "https://www.zhihu.com/login/phone_num"
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
            #im.close()
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
                yield scrapy.Request(url,dont_filter=True, headers=self.headers)
        else:
            print("登录失败")
