# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyDoubanItem(scrapy.Item):
    title = scrapy.Field()
    page_num = scrapy.Field()
    author = scrapy.Field()
    response_count = scrapy.Field()
    response_time = scrapy.Field()
    url = scrapy.Field()
    content = scrapy.Field()
    dt = scrapy.Field()

    # define the fields for your item here like:
    # name = scrapy.Field()

