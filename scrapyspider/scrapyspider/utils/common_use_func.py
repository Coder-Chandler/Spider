import hashlib
import re
import datetime


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
    value = value.strip()
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


def return_value(value):
    return value


def join_str(value):
    # 防止出现“: sequence item 0: expected str instance, bytes found”这一类的错误
    return r"".join(str(i) for i in value)

