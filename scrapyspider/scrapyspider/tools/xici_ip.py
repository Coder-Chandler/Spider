import requests
from scrapy.selector import Selector
import MySQLdb

conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="root", db="spider", charset="utf8")
cursor = conn.cursor()


def crawl_ips():
    # 爬取西刺免费代理ip
    headers = {'User-Agent': "Mozilla/5.0 (compatible; MSIE 10.0; Macintosh; Intel Mac OS X 10_7_3; Trident/6.0)"}
    for i in range(1, 1000):
        re = requests.get("http://www.xicidaili.com/nn/{0}".format(i), headers=headers)
        # print(re.text)
        selector = Selector(text=re.text)
        all_trs = selector.css("#ip_list tr")

        ip_list = []
        for tr in all_trs[1:]:
            speed_str = tr.css(".bar::attr(title)").extract()[0]
            speed = 0.0
            if speed_str:
                speed = float(speed_str.split("秒")[0])
                # print(speed)
            all_texts = tr.css("td::text").extract()
            # print(all_texts)

            ip = all_texts[0]
            port = all_texts[1]
            proxy_type = all_texts[5]

            ip_list.append((ip, port, proxy_type, speed))

            for ip_info in ip_list:
                print(ip_info)
                cursor.execute(
                    "insert into proxy_ip(ip, port, proxy_type, speed) VALUES('{0}', '{1}', 'HTTPS', {2}) "
                    "ON DUPLICATE KEY UPDATE ip = VALUES(ip)".format(
                        ip_info[0], ip_info[1], ip_info[3])
                )

                conn.commit()


class GetIP(object):

    def delete_ip(self, ip):
        # delete the invalid ip from mysql
        delete_sql = """
            delete from proxy_ip where ip ='{0}'
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self, ip, port):
        # judge whether the ip can be used
        http_url = "https://www.lagou.com/jobs/list_?px=new&city=%E4%B8%8A%E6%B5%B7#filterBox"
        proxy_url = "http://{0}:{1}".format(ip, port)
        try:
            proxy_dict = {
                "http": proxy_url
            }
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            print("Invalid ip and port")
            self.delete_ip(ip)
            print("it was deleted")
            return False
        else:
            code = response.status_code
            if 200 <= code < 300:
                print("Effective ip")
                print(proxy_url)
                return True
            else:
                print("Invalid ip and port")
                self.delete_ip(ip)
                print("it was deleted")
                return False

    def get_random_ip(self):
        random_sql = """
            SELECT ip, port FROM proxy_ip
            ORDER BY RAND()
            LIMIT 1
        """
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]

            judge_re = self.judge_ip(ip, port)
            if judge_re:
                print("http://{0}:{1}".format(ip, port))
                return "http://{0}:{1}".format(ip, port)
            else:
                return self.get_random_ip()


if __name__ == "__main__":
    # crawl_ips()
    # for i in range(1,10000):
    get_ip = GetIP()
    get_ip.get_random_ip()