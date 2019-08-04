# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals, Request
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware

from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
import random
import pymongo
from fake_useragent import UserAgent
from scrapy.exceptions import CloseSpider
from .settings import  CUSTOM_USER_AGENT
import time
import logging
from datetime import datetime

class DownloadDelayMiddleware(object):
    def __init__(self, delay):
        self.delay = delay

    @classmethod
    # 延时多少个100ms, 1s-5s
    def from_crawler(cls, crawler):
        delay = crawler.spider.settings.get("RANDOM_DELAY", 40)
        if not isinstance(delay, int):
            raise ValueError("RANDOM_DELAY need a int")
        return cls(delay)

    def process_request(self, request, spider):
        delay = random.randint(0, self.delay)
        s_delay = (1000 + 100.0*delay)/1000
        request.meta["download_slot"] = s_delay
        logging.debug("### random delay: %.2f s ###" % s_delay)
        # time.sleep(s_delay)



class MyUserAgentMiddleware(UserAgentMiddleware):
    '''
    设置User-Agent
    '''

    def __init__(self, user_agent):
        self.ua = UserAgent()
        self.user_agent = user_agent

    @classmethod
    def from_crawler(cls, crawler):

        return cls(
            user_agent=crawler.settings.get('CUSTOM_USER_AGENT')
        )

    def process_request(self, request, spider):
        # agent = random.choice(self.user_agent)
        agent = self.ua.random
        request.headers['User-Agent'] = agent


class MyProxyMiddleWare(HttpProxyMiddleware):

    def __init__(self, ip=''):
        self.ip = ip
        self.proxy = ''
        self.invalidate_proxy=list()

    def process_request(self, request, spider):
        '''对request对象加上proxy'''
        print(request.url)
        proxy = self.get_random_proxy()
        # self.proxy = proxy
        print(" Request this request ip is:" + proxy)
        request.meta['proxy'] = proxy
        # request.meta["origin_url"] = request.url
        request.meta["download_timeout"] = 10

    def process_exception(self, request, exception, spider):
        # proxy = ""
        # while proxy == self.proxy:
        #     if len(self.validate_proxy) != 0:
        #         proxy = random.choice(self.validate_proxy)
        #     else:
        proxy = request.meta.get('proxy', False)
        print("ConnectErr this request is ", proxy)
        self.invalidate_proxy.append(proxy)
        print("exception ,retry")
        proxy = self.get_random_proxy()
        # request['url'] = request.meta.get('origin_url', "")
        request.meta['proxy'] = proxy
        return request

    def process_response(self, request, response, spider):
        '''对返回的response处理'''
        # 如果返回的response状态不是200，重新生成当前request对象
        if response.status != 200:
            proxy = request.meta.get('proxy', False)
            self.invalidate_proxy.append(proxy)
            # print("response status:", response.status)
            url = response.url
            if "检测到有异常请求从你的 IP 发出" in response.text:
                print("被检测到异常IP")
            print("C this response ip is: %s with status %d in %s" %(proxy, response.status, url))
            # # 对当前reque加上代理
            proxy =self.get_random_proxy()
            request.meta['proxy'] = proxy
            # url = request.meta.get('origin_url', url)
            # request.meta['download_timeout'] = 1200
            return request
            # return request
        # else:
        elif len(response.text) < 1000:
            proxy = request.meta.get('proxy', False)
            self.invalidate_proxy.append(proxy)
        # 可能返回ip被限制
        # https://sec.douban.com/a?c=b7fde2&d=Win32|Mozilla/5.0%20(Windows%20NT%2010.0;%20Win64;%20x64)%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/74.0.3729.169%20Safari/537.36|Google%20Inc.&r=https%3A%2F%2Fwww.douban.com%2Fgroup%2F106955%
        # 2Fdiscussion%3Fstart%3D8100&k=hivCr3rGoFvYUmEDOgS9OIAwFxhfS1JPS%2BBJMXmcUXI
            print("Restricted IP")
            proxy = self.get_random_proxy()
            request.meta['proxy'] = proxy
            return request
        else:

            return response

    def get_random_proxy(self):
        '''随机从文件中读取proxy'''
        mongo_client = pymongo.MongoClient("localhost", 27017)
        db = mongo_client.db_huangsy
        my_collection = db.ip_proxies
        # 获取当前爬取的proxy
        #dt = datetime.now().strftime("%Y-%m-%d")
        dt = "2019-06-14"
        query = {"dt": dt, 'http_type':'https'}
        res_list = my_collection.find(query)
        proxies = []
        for ip_res in res_list:
            proxy = ip_res['http_type'] + '://' + ip_res['ip'] + ':' + ip_res['port']
            #proxy = ip_res['ip'] + ':' + ip_res['port']
            proxies.append(proxy)
        proxies = list(set(proxies) - set(self.invalidate_proxy))
        if len(proxies) == 0:
            raise CloseSpider("all the ips are dead!")
        proxy = random.choice(proxies).strip()
        return proxy


class ScrapyDoubanSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ScrapyDoubanDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
