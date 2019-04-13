# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import hashlib
import logging
import json
from weibotu.mysql import db
from urllib.parse import urlparse
from os.path import basename, dirname, join
from scrapy.http import Request
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from scrapy.pipelines.files import FilesPipeline


class WeiBoTuPipeline(object):
    def process_item(self, item, spider):

        self.conn = spider.data_conn
        self.dbsession = db(self.conn)

        try:
            with self.conn:
                self.conn.ping(reconnect=True)
                self.dbsession.Insert(item['table'], item['row'])
        except pymysql.Warning as w:
            logging.warning("Insert Warning:%s" % str(w))

        except pymysql.Error as e:
            logging.error("Insert Error:%s" % str(e))

        return item