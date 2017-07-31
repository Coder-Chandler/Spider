import hashlib
import re
import datetime
import time
import random
from urllib import parse


def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def date_type(date):
    # 规范化提取到的时间格式
    date = date.strip().replace(" ·", "")
    try:
        create_date = datetime.datetime.strptime(date, "%Y%m%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date


def get_nums(value):
    # 对评论数，点赞数，收藏数进行过滤和判断
    if type(value) == str:
        value = value.strip()
    elif type(value) == list:
        value = "".join(str(i) for i in value)
    elif type(value) == int:
        return value
    elif value is None:
        return 0
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums
# print (get_nums('asdddsad 13dfewf efe'))


def remove_comment_tags(value):
    # 过滤掉掉tag中提取的评论部分
    if "评论" in value:
        return ""
    else:
        return value


def remove_splash(value):
    # 去掉斜线
    return value.replace("/", "")


def publish_time(value):
    time_list = value.split()
    time_value = time_list[0]
    if '天前' in time_value:
        time_value_ = re.match("\d+", time_value)
        time_value = int(time_value_.group())
        today = datetime.datetime.now()
        publish_time_ = datetime.timedelta(days=time_value)
        publish_time = today - publish_time_
        return publish_time.strftime("%Y-%m-%d")
    elif ':' in time_value:
        time_value = str(time.strftime("%Y-%m-%d-"))+time_value
    return time_value


def get_salary_min(value):
    # 获取最低工资并转换成int
    value = value.replace(' ', '')
    if '-' in value:
        value = value.split("-")[0]
        match_re = re.match(".*?(\d+).*", value)
        if match_re:
            value = match_re.group(1)
    elif '以上' in value:
        match_re = re.match(".*?(\d+).*", value)
        if match_re:
            value = match_re.group(1)
    return int(value)*1000


def get_salary_max(value):
    # 获取最高工资并转换成int
    value = value.replace(' ', '')
    if '-' in value:
        value = value.split("-")[1]
        match_re = re.match(".*?(\d+).*", value)
        if match_re:
            value = match_re.group(1)
    elif '以上' in value:
        value = 0
    return int(value)*1000


def get_work_years_min(value):
    # 获取最低工作年限并转换成int
    value = value.replace('/', '').replace(' ', '')
    if '-' in value:
        match_re = re.match(".*?(\d+).*", value)
        if match_re:
            value = match_re.group(1)
    elif '以下' in value:
        value = 0
    elif '不限' in value:
        value = 0
    elif '以上' in value:
        match_re = re.match(".*?(\d+).*", value)
        if match_re:
            value = match_re.group(1)
    elif "应届毕业生" in value:
        value = 0
    return int(value)


def get_work_years_max(value):
    # 获取最高工作年限并转换成int
    value = value.replace('/', '').replace(' ', '')
    if '-' in value:
        match_re = re.match(".*-(\d+).*", value)
        if match_re:
            value = match_re.group(1)
    elif '以下' in value:
        match_re = re.match(".*?(\d+).*", value)
        if match_re:
            value = match_re.group(1)
    elif '不限' in value:
        value = 0
    elif '以上' in value:
        value = 0
    elif "应届毕业生" in value:
        value = 0
    return int(value)


def get_workaddr(value):
    # 利用w3lib.html的remove_tags函数删掉所有html标签后，再用本函数进行最终的地址提取
    addr = value.split("\n")
    addr = [s.strip() for s in addr if s.strip() != '查看地图']
    return "".join(addr)


def return_value(value):
    return value


def join_str(value):
    # 防止出现“: sequence item 0: expected str instance, bytes found”这一类的错误
    if type(value) == int:
        return value
    elif type(value) == str:
        return "".join(str(i) for i in value)
    elif type(value) == list:
        return "".join(str(i) for i in value)


def get_longitude(value):
    match_re = re.match(".*?(\d+.\d+).*", value)
    if match_re:
        nums = float(match_re.group(1))*1.0
    else:
        nums = 0
    return nums
# print(get_longitude('121.12343124,31.1231231232'))


def get_latitude(value):
    match_re = re.match(".*?( \d+.\d+).*", value)
    if match_re:
        nums = float(match_re.group(1))*1.0
    else:
        nums = 0
    return nums


# def random_download_delay():
#     return random.randint(0,5)
# print(random_download_delay())
# print(get_latitude('121.12343124, 31.1231231232, gfdg'))

# s='http://sh.lianjia.com/zufang/guangxin'
# x='http://sh.lianjia.com/zufang/shzr4072292.html'
# match_re = re.match("(.*sh.lianjia.com/zufang/(shz\d*)(.html$))", x)
# print(match_re.group(1))
#
# s=['http://sh.lianjia.com/zufang/sardef/d5','http://sh.lianjia.com/zufang/were','http://sh.lianjia.com/zufang/de234',
#    'http://sh.lianjia.com/zufang/shzr232423.html', 'http://sh.lianjia.com/zufang/shz232423.html']
# #
# #
# def filter_all_urls( value):
#     match_re = re.match("(.*sh.lianjia.com/zufang/(([a-z]{3,30}/d)|(shzr\d+.html)|([a-z]{3,30}$)|d\d+))", value)
#     if match_re:
#         return True
#     else:
#         return False
# all_urls = filter(filter_all_urls, s)
# for i in all_urls:
#     print (i)