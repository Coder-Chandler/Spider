# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader
import datetime
import re


class ScrapyspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class JobboleItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()


def date_type(date):
    date = date.strip().replace(" ·", "")
    try:
        create_date = datetime.datetime.strptime(date, "%Y%m%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date


def get_nums(value):
    value = value.strip()
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


def remove_comment_tags(value):
    # 去掉tag中提取的评论
    if "评论" in value:
        return ""
    else:
        return value


def return_value(value):
    return value


def join_str(value):
    return r"".join(str(i) for i in value)


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
            article_image_url = join_str(self["front_image_url"][0])
        params = (self["title"], self["url"], self["url_object_id"], self["praise_num"], self["fav_num"],
                  self["comments_num"], self["tags"], article_image_url, self["front_image_path"],
                  self["create_date"], self["content"])
        return insert_sql, params
