import hashlib
import re
import datetime
import time

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
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


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
        value = value[4] + value[5]
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
    elif value == "应届毕业生":
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
    elif value == "应届毕业生":
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
