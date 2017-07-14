# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader
from scrapyspider.utils.common_use_func import date_type, get_nums, remove_comment_tags, \
     return_value, join_str


class ScrapyspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class JobboleItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()


class JobboleItem(scrapy.Item):
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(date_type)
    )
    praise_num = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_num = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comments_num = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    content = scrapy.Field()
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(",")
    )
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into  jobbole(title, url, url_object_id, praise_num, fav_num, comments_num, tags, 
            front_image_url, front_image_path, create_date, content)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE title=VALUES(title),url=VALUES(url),
            url_object_id=VALUES(url_object_id),praise_num=VALUES(praise_num),fav_num=VALUES(fav_num),
            comments_num=VALUES(comments_num),tags=VALUES(tags),front_image_url=VALUES(front_image_url),
            front_image_path=VALUES(front_image_path),create_date=VALUES(create_date),content=VALUES(content)
        """
        article_image_url = ""
        if self["front_image_url"]:
            article_image_url = self["front_image_url"][0]
        params = (self["title"], self["url"], self["url_object_id"], self["praise_num"], self["fav_num"],
                  self["comments_num"], self["tags"], article_image_url, self["front_image_path"],
                  self["create_date"], self["content"])
        return insert_sql, params
