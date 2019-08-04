# -*- coding: utf-8 -*-
import pymongo
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class ScrapyDoubanPipeline(object):

    def __init__(self, host='localhost', port=27017):
        self.host = host
        self.port = port

    def open_spider(self, spider):
        self.conn = pymongo.MongoClient(self.host, self.port)
        self.db = self.conn.db_huangsy
        self.collection = self.db.douban_sz_rent_group_v0

    def process_item(self, item, spider):
        dict_item = dict(item)
        self.collection.replace_one(dict_item, dict_item,True)
        return item

    def close_spider(self, spider):
        self.conn.close()
