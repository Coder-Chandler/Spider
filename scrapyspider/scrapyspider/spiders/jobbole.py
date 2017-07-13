# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
from scrapyspider.items import JobboleItem
from scrapyspider.utils.common_use_func import get_md5
from scrapyspider.items import JobboleItemLoader
import datetime


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1.获取文章列表中的文章url交给scrapy下载后并解析函数解析
        2.获取下一页的url交给scrapy下载
        """

        # 获取文章列表中的文章url交给scrapy下载后并解析函数解析
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            front_image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": front_image_url},
                          callback=self.parse_detail)

        # 提取下一页，交给scrapy下载
        next_urls = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_urls:
            yield Request(url=parse.urljoin(response.url, next_urls), callback=self.parse)

    def parse_detail(self, response):
        article_item = JobboleItem()
        front_image_url = response.meta.get("front_image_url", "")
        item_loader = JobboleItemLoader(item=JobboleItem(), response=response)
        item_loader.add_xpath("title", '//div[@class="entry-header"]/h1/text()')
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_xpath("create_date", '//p[@class="entry-meta-hide-on-mobile"]/text()')
        item_loader.add_xpath("praise_num", '//span[contains(@class,"vote-post-up")]/h10/text()')
        item_loader.add_xpath("fav_num", '//span[contains(@class, "bookmark-btn")]/text()')
        item_loader.add_xpath("comments_num", "//a[@href='#article-comment']/span/text()")
        item_loader.add_xpath("tags", '//p[@class="entry-meta-hide-on-mobile"]/a/text()')
        item_loader.add_xpath("content", '//div[@class="entry"]')

        article_item = item_loader.load_item()
        yield article_item


