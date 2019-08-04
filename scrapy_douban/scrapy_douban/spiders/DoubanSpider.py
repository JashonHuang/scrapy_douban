import scrapy
from ..items import ScrapyDoubanItem
import re
from datetime import datetime
import logging

class DoubanSpider(scrapy.Spider):
    name = 'douban-spider'
    allowed_domains =["douban.com"]
    start_urls = [
        'https://www.douban.com/group/106955/discussion?start=0',
    ]

    def parse_detail(self, response):
        # response.meta返回接收到的meta字典
        item = response.meta['item']
        title_more = response.xpath("//table[@class='infobox']//td[@class='tablecc']/text()").get()
        if title_more is not None:
            item["title"] = title_more.strip()
        content = response.xpath("string(//div[@class='topic-content'])").get()
        if content is None:
            content = ""
        item["content"] = content.strip()
        yield item

    def parse(self, response):
        res_url = response.url
        page_num = int(re.search(r"\?start=(\d+)", res_url).group(1))/25
        scrapy_dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        title_list = response.xpath('//table[@class="olt"]//tr/td[1]/a/text()').getall()
        author_list = response.xpath('//table[@class="olt"]//tr/td[2]/a/text()').getall()
        response_cnt_list = [xps.xpath("text()").get() for xps in response.xpath("//table[@class='olt']//tr/td[3]")][1:]
        response_time_list = [xps.xpath("text()").get() for xps in response.xpath("//table[@class='olt']//tr/td[4]")][1:]
        url_list = response.xpath("//table[@class='olt']//td[@class='title']//@href").getall()

        # print("this len is", len(title_list), len(author_list), len(response_cnt_list), len(response_date_list))
        for i, title in enumerate(title_list):
            item = ScrapyDoubanItem()
            author = author_list[i]
            resp_cnt = response_cnt_list[i]
            resp_time = response_time_list[i]
            detail_url = url_list[i]
            item['title'] = title.strip()
            item['author'] = author
            item['response_count'] = resp_cnt
            item["response_time"] = resp_time
            item["page_num"] = int(page_num)
            item["url"] = detail_url
            item['dt'] = scrapy_dt
            yield scrapy.Request(url=detail_url, callback=self.parse_detail,
                                 meta={'item': item, 'dont_redirect': True,
                                       'handle_httpstatus_list': [301,302]},
                                 dont_filter=True)

        next_page_url = response.css('span.next a::attr(href)').get()
        self.logger.debug("this is the next_page_url : %s" % next_page_url)
        if next_page_url is None:
            fp = open("debug_none.txt", 'w+')
            fp.write(response.text)
            fp.close()
        if next_page_url is not None:
            yield scrapy.Request(next_page_url, self.parse,
                                 meta={
                                       'dont_redirect': True,
                                       'handle_httpstatus_list': [301, 302]},
                                 dont_filter=True)
