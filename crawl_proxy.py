
import requests
import re
from lxml import etree
from fake_useragent import UserAgent
import time
import json
import pymongo
from datetime import datetime


class Proxies:
    def __init__(self):
        self.http_type_list = []
        self.proxy_list = []
        self.ua = UserAgent()
        self.headers  = {
         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36 ",
         "Accept-Encoding": "gzip, deflate, sdch",
        }
    # 爬取西刺代理的国内高匿代理
    def get_proxy_nn(self):
        url_base = "http://www.xicidaili.com/nn"
        proxy_list = []
        for i in range(20):
            if i == 0:
                url = url_base
            else:
                url = url_base + "/" + str(i)
                self.headers['User-Agent'] = self.ua.random
                res = requests.get(url, headers=self.headers)
#                 print(res.status_code)
                if res.status_code != 200:
                    print(res.status_code)
                ehtml = etree.HTML(res.text, etree.HTMLParser())
                ip_list = ehtml.xpath("//tr/td[2]/text()")
                port_list = ehtml.xpath("//tr/td[3]/text()")
                speed_list = [speed_str.replace("秒", "") for speed_str in ehtml.xpath("//tr/td[7]/div/@title")]
                expectancy_list = ehtml.xpath("//tr/td[9]/text()")
                http_type_list = ehtml.xpath("//tr/td[6]/text()")
                for ip, port, speed, expectancy, http_type in zip(ip_list, port_list, speed_list, expectancy_list, http_type_list):
                    is_day = "天" in expectancy
#                     print(http_type)
                    if float(speed) <= 1.0 and is_day and http_type.lower()=='https':
                        proxy = ip + ":" + port
                        proxy_list.append({http_type.lower(): proxy})
        return proxy_list
    # 验证代理是否能用
    def verify_proxy(self, proxy_list):
        self.html_list = list()
        ua = UserAgent()
        for proxy in proxy_list:
            try:
                user_agent  = ua.random
                self.headers["User-Agent"] = user_agent
                req = requests.get("https://www.douban.com/group/106955/discussion?start=0", proxies=proxy, headers=self.headers, timeout=1)
                if req.status_code == 200:
                    self.html_list.append(req.text)
                    print('success %s' % proxy)
                if proxy not in self.proxy_list:
                    self.proxy_list.append(proxy)
            except:
                 continue
    # 保存到proxies.txt里
    def get_proxy(self):
        return self.proxy_list

# def crawl_proxy():
#     print("this is crawl proxy_process")

def crawl_proxy():
    i = 0
    imax = 200 #循环次数
    while True:
        i += 1
        # url填写从西瓜获得的获取ip的api
        url = "http://api3.xiguadaili.com/ip/?tid=558941847755113&num=1000&protocol=https&sortby=time&format=json"
        headers = {
            "User-Agent": "",
            "Accept-Encoding": "gzip, deflate, sdch",
        }
        ua = UserAgent()
        headers["User-Agent"] = ua.random
        res = requests.get(url, headers=headers)
        try:
            res_js = json.loads(res.text, encoding="utf8")
            proxies = [data['host'] + ':' + str(data['port']) for data in res_js]
        except:
            print("except")
            time.sleep(300)
            continue
        proxies = list(set(proxies))
        results = [{'https': ip} for ip in proxies]
        p = Proxies()
        # results = p.get_proxy_nn()
        print("爬取到的代理数量", len(results))
        p.verify_proxy(results)
        mongo_client = pymongo.MongoClient("localhost", 27017)
        db = mongo_client.db_huangsy
        my_collection = db.ip_proxies
        # 将ip与port 写进mongodb
        dt = datetime.now().strftime("%Y-%m-%d")
        for proxy in p.proxy_list:
            proxy_format = dict()
            proxy_format["http_type"] = list(proxy.keys())[0]
            proxy_format["ip"] = re.match("(.+)?\:\d+", list(proxy.values())[0]).group(1)
            proxy_format["port"] = re.match(".+?\:(\d+)", list(proxy.values())[0]).group(1)
            proxy_format["dt"] = dt
            my_collection.replace_one(proxy_format, proxy_format, True)
        # 休眠5分钟再取
        time.sleep(300)
        if i > imax:
            break


if __name__ == "__main__":
    crawl_proxy()




