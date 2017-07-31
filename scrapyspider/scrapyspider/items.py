# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader
from w3lib.html import remove_tags
from scrapyspider.utils.common_use_func import date_type, get_nums, remove_comment_tags, \
     return_value, join_str, remove_splash, publish_time, get_salary_min, get_salary_max, \
     get_work_years_min, get_work_years_max, get_workaddr, get_longitude, get_latitude


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


class ZhiHuQuestionItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    question_topics = scrapy.Field(
        output_processor=Join(",")
    )
    question_url = scrapy.Field(
        output_processor=Join(",")
    )
    question_title = scrapy.Field(
        output_processor=Join(",")
    )
    question_content = scrapy.Field(
        output_processor=Join(",")
    )
    question_create_date = scrapy.Field()
    question_update_date = scrapy.Field()
    question_answer_num = scrapy.Field(
        input_processor=MapCompose(join_str)
    )
    question_comments_num = scrapy.Field(
        input_processor=MapCompose(join_str)
    )
    question_watch_user_num = scrapy.Field()
    question_follow_num = scrapy.Field()
    question_crawl_time = scrapy.Field()
    question_crawl_updatetime = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into zhihu_question(zhihu_id, question_topics, question_url, question_title,
                                       question_content, question_create_date, question_update_date,
                                       question_answer_num, question_comments_num, question_watch_user_num,
                                       question_follow_num, question_crawl_time, question_crawl_updatetime)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE 
            zhihu_id=VALUES(zhihu_id), question_topics=VALUES(question_topics), question_url=VALUES(question_url),
            question_title=VALUES(question_title), question_content=VALUES(question_content),
            question_create_date=VALUES(question_create_date), question_update_date=VALUES(question_update_date),
            question_answer_num=VALUES(question_answer_num), question_comments_num=VALUES(question_comments_num),
            question_watch_user_num=VALUES(question_watch_user_num), question_follow_num=VALUES(question_follow_num),
            question_crawl_updatetime=VALUES(question_crawl_updatetime)
        """
        zhihu_id = self["zhihu_id"][0]
        question_topics = self["question_topics"]
        question_url = self["question_url"]
        question_title = self["question_title"]
        question_content = self.get("question_content", "")
        question_create_date = self["question_create_date"]
        question_update_date = self["question_update_date"]
        question_answer_num = get_nums(self["question_answer_num"])
        question_comments_num = get_nums(self["question_comments_num"])
        if len(self["question_watch_user_num"]) == 2:
            question_follow_num = get_nums(self["question_watch_user_num"][0])
            question_watch_user_num = get_nums(self["question_follow_num"][1])
        else:
            question_follow_num = 0
            question_watch_user_num = 0
        question_crawl_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        question_crawl_updatetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        params = (zhihu_id, question_topics, question_url, question_title, question_content,
                  question_create_date, question_update_date, question_answer_num, question_comments_num,
                  question_watch_user_num, question_follow_num, question_crawl_time, question_crawl_updatetime)
        return insert_sql, params


class ZhiHuAnswerItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    answer_url = scrapy.Field()
    question_id = scrapy.Field()
    answer_author_id = scrapy.Field()
    answer_content = scrapy.Field()
    answer_praise_num = scrapy.Field()
    answer_comments_num = scrapy.Field()
    answer_create_date = scrapy.Field()
    answer_update_date = scrapy.Field()
    crawl_time = scrapy.Field()
    answer_crawl_updatetime = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into zhihu_answer(zhihu_id, answer_url, question_id, answer_author_id, answer_content,
                                    answer_praise_num, answer_comments_num, answer_create_date,
                                    answer_update_date, answer_crawl_time, answer_crawl_updatetime)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE 
            zhihu_id=VALUES(zhihu_id), answer_url=VALUES(answer_url), question_id=VALUES(question_id),
            answer_author_id=VALUES(answer_author_id), answer_content=VALUES(answer_content),
            answer_praise_num=VALUES(answer_praise_num), answer_comments_num=VALUES(answer_comments_num),
            answer_create_date=VALUES(answer_create_date), answer_update_date=VALUES(answer_update_date),
            answer_crawl_updatetime=VALUES(answer_crawl_updatetime)
        """
        zhihu_id = self["zhihu_id"]
        answer_url = self["answer_url"]
        question_id = self["question_id"]
        answer_author_id = self["answer_author_id"]
        answer_content = self["answer_content"]
        answer_praise_num = self["answer_praise_num"]
        answer_comments_num = self["answer_comments_num"]
        answer_create_date = datetime.datetime.fromtimestamp(self["answer_create_date"]).strftime("%Y-%m-%d %H:%M:%S")
        answer_update_date = datetime.datetime.fromtimestamp(self["answer_update_date"]).strftime("%Y-%m-%d %H:%M:%S")
        answer_crawl_time = datetime.datetime.now()
        answer_crawl_updatetime = datetime.datetime.now()
        params = (zhihu_id, answer_url, question_id, answer_author_id, answer_content, answer_praise_num,
                  answer_comments_num, answer_create_date, answer_update_date, answer_crawl_time,
                  answer_crawl_updatetime)

        return insert_sql, params


class LaGouItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()


class LaGouJobItem(scrapy.Item):
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    title = scrapy.Field()
    salary_min = scrapy.Field(
        input_processor=MapCompose(get_salary_min)
    )
    salary_max = scrapy.Field(
        input_processor=MapCompose(get_salary_max)
    )
    company_name = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    work_years_min = scrapy.Field(
        input_processor=MapCompose(get_work_years_min)
    )
    work_years_max = scrapy.Field(
        input_processor=MapCompose(get_work_years_max)
    )
    education_degree = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field(
        input_processor=MapCompose(publish_time)
    )
    tags = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, get_workaddr)
    )
    company_url = scrapy.Field()
    crwal_time = scrapy.Field()
    crwal_update_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into lagou_job(url, url_object_id, title, salary_min, salary_max,
                                    company_name, job_city, work_years_min, work_years_max,
                                    education_degree, job_type, publish_time, tags, job_advantage,
                                    job_desc, job_addr, company_url, crwal_time, crwal_update_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            ON DUPLICATE KEY UPDATE url=VALUES(url), url_object_id=VALUES(url_object_id), 
            title=VALUES(title), salary_min=VALUES(salary_min), salary_max=VALUES(salary_max), 
            company_name=VALUES(company_name), job_city=VALUES(job_city), work_years_min=VALUES(work_years_min), 
            work_years_max=VALUES(work_years_max), education_degree=VALUES(education_degree),
            job_type=VALUES(job_type), publish_time=VALUES(publish_time), tags=VALUES(tags),
            job_advantage=VALUES(job_advantage), job_desc=VALUES(job_desc), job_addr=VALUES(job_addr),
            company_url=VALUES(company_url), crwal_update_time=VALUES(crwal_update_time)
        """
        url = self["url"]
        url_object_id = self["url_object_id"]
        title = self["title"]
        salary_min = self["salary_min"]
        salary_max = self["salary_max"]
        company_name = self["company_name"]
        job_city = self["job_city"]
        work_years_min = self["work_years_min"]
        work_years_max = self["work_years_max"]
        education_degree = self["education_degree"]
        job_type = self["job_type"]
        publish_time = self["publish_time"]
        tags = self["tags"]
        job_advantage = self["job_advantage"]
        job_desc = self["job_desc"]
        job_addr = self["job_addr"]
        company_url = self["company_url"]
        crwal_time = self["crwal_time"]
        crwal_update_time = self["crwal_update_time"]

        params = (url, url_object_id, title, salary_min, salary_max, company_name, job_city,
                  work_years_min, work_years_max, education_degree, job_type,
                  publish_time, tags, job_advantage, job_desc, job_addr, company_url,
                  crwal_time, crwal_update_time)

        return insert_sql, params


class LianJiaItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()


class LianJiaItem(scrapy.Item):
    url = scrapy.Field()
    lianjia_id = scrapy.Field()
    residential_district_name = scrapy.Field()
    residential_district_url = scrapy.Field()
    title = scrapy.Field()
    region = scrapy.Field()
    region_detail = scrapy.Field()
    address = scrapy.Field()
    house_area = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    room_count = scrapy.Field()
    face_direction = scrapy.Field()
    rent_price = scrapy.Field()
    floor = scrapy.Field()
    publish_time = scrapy.Field()
    total_watch_count = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    crwal_time = scrapy.Field()
    crwal_update_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into lianjia_copy(url, lianjia_id, residential_district_name, 
                                residential_district_url, title, region, region_detail,
                                address, house_area, room_count, face_direction, 
                                rent_price, floor, publish_time, total_watch_count, 
                                crwal_time, crwal_update_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            ON DUPLICATE KEY UPDATE url=VALUES(url), lianjia_id=VALUES(lianjia_id), 
            house_area=VALUES(house_area), room_count=VALUES(room_count), face_direction=VALUES(face_direction), 
            rent_price=VALUES(rent_price), floor=VALUES(floor), total_watch_count=VALUES(total_watch_count), 
            crwal_update_time=VALUES(crwal_update_time)
        """
        url = self["url"][0]
        lianjia_id = self["lianjia_id"][0]
        residential_district_name = ""
        if 'shzr' in url:
            residential_district_name = self["residential_district_name"][0]+'(自如租房)'
        if 'shz' in url:
            residential_district_name = self["residential_district_name"][0]
        residential_district_url = self["residential_district_url"]
        title = self["title"][0]
        region = self["region"][0]
        region_detail = self["region"][1]
        address = self["address"][0]
        house_area = float(self["house_area"][0])*1.0
        room_count = int(self["room_count"][0][0])
        face_direction = "".join(self["face_direction"]).strip()
        rent_price = int("".join(self["rent_price"]))
        floor = self["floor"][0]
        publish_time = self["publish_time"][0]
        try:
            total_watch_count = self["total_watch_count"][0]
        except KeyError:
            total_watch_count = 0
        crwal_time = datetime.datetime.now()
        crwal_update_time = datetime.datetime.now()

        params = (url, lianjia_id, residential_district_name,
                  residential_district_url, title, region, region_detail, address, house_area,
                  room_count, face_direction, rent_price, floor, publish_time, total_watch_count,
                  crwal_time, crwal_update_time)

        return insert_sql, params


class LianJia_latitude_longitude(scrapy.Item):
    residential_district_name = scrapy.Field()
    residential_district_url = scrapy.Field()
    lianjia_id = scrapy.Field()
    longitude = scrapy.Field(
        input_processor=MapCompose(get_longitude)
    )
    latitude = scrapy.Field(
        input_processor=MapCompose(get_latitude)
    )
    crwal_time = scrapy.Field()
    crwal_update_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
                insert into LianJia_latitude_longitude_copy(lianjia_id, residential_district_name, 
                                                       residential_district_url, longitude, latitude, 
                                                       crwal_time, crwal_update_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s) 
                ON DUPLICATE KEY UPDATE residential_district_name=VALUES(residential_district_name),
                residential_district_url=VALUES(residential_district_url), lianjia_id=VALUES(lianjia_id),
                longitude=VALUES(longitude), latitude=VALUES(latitude), crwal_update_time=VALUES(crwal_update_time)
            """
        residential_district_name = self["residential_district_name"]
        residential_district_url = self["residential_district_url"]
        lianjia_id = self["lianjia_id"]
        longitude = self["longitude"][0]
        latitude = self["latitude"][0]
        crwal_time = datetime.datetime.now()
        crwal_update_time = datetime.datetime.now()

        params = (lianjia_id, residential_district_name, residential_district_url,
                  longitude, latitude, crwal_time, crwal_update_time)

        return insert_sql, params