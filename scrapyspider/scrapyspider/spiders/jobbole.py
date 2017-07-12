# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from urllib import parse
from scrapyspider.items import JobboleItem
from scrapyspider.utils.common_use_func import get_md5
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
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse)

    def parse_detail(self, response):
        article_item = JobboleItem()
        front_image_url = response.meta.get("front_image_url", "")
        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first("")
        create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()')\
            .extract_first().strip().replace(" ·", "")
        praise_num = int(response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract_first(""))
        fav_num = response.xpath('//span[contains(@class, "bookmark-btn")]/text()').extract_first("")
        fav_nums_match = re.match(".*?(\d+).*", fav_num)
        if fav_nums_match:
            fav_num = int(fav_nums_match.group(1))
        else:
            fav_num = 0
        comments_num = response.xpath("//a[@href='#article-comment']/span/text()").extract_first("").strip()
        comments_num_match = re.match(".*?(\d+).*", comments_num)
        if comments_num_match:
            comments_num = int(comments_num_match.group(1))
        else:
            comments_num = 0
        content = response.xpath('//div[@class="entry"]').extract_first("")
        tag_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract_first("")
        tag_list = [element for element in tag_list if not element.strip().endswith('评论')]
        tags = "".join(tag_list)

        article_item["url_object_id"] = get_md5(response.url)
        article_item["title"] = title
        try:
            create_date = datetime.datetime.strptime(create_date, "%Y%m%d").date()
        except Exception as e:
            create_date = datetime.datetime.now().date()
        article_item["create_date"] = create_date
        article_item["praise_num"] = praise_num
        article_item["fav_num"] = fav_num
        article_item["comments_num"] = comments_num
        article_item["content"] = content
        article_item["tags"] = tags
        article_item["front_image_url"] = [front_image_url]
        article_item["url"] = response.url

        yield article_item


