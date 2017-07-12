# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class JobboleItem(scrapy.Item):
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    title = scrapy.Field()
    create_date = scrapy.Field()
    praise_num = scrapy.Field()
    fav_num = scrapy.Field()
    comments_num = scrapy.Field()
    content = scrapy.Field()
    tags = scrapy.Field()
    front_image_url = scrapy.Field()
    front_image_path = scrapy.Field()