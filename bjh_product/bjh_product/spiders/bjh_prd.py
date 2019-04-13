# -*- coding: utf-8 -*-
import scrapy
import json
import re
import logging
from scrapy import signals
from scrapy.item import Item, Field
from bjh_product.connection import MySQLConnection, RedisConnection
from scrapy.http import Request, FormRequest
from scrapy.utils.project import get_project_settings

settings = get_project_settings()


class UniversalRow(Item):
    # This is a row wrapper. The key is row and the value is a dict
    # The dict wraps key-values of all fields and their values
    row = Field()
    table = Field()
    image_urls = Field()


class BjhPrdSpider(scrapy.Spider):
    # 原始网址: http://bxjg.circ.gov.cn/tabid/6757/Default.aspx
    name = 'bjh_prd'

    # 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&value={uid}&containerid=100505{uid}' # 判别性别和图片数量

    user_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&value={uid}&containerid=100505{uid}'

    follow_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_followers_-_{uid}&page={page}' # max值是10页

    # fan_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&page={page}'
    fan_url = 'https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&since_id={page}' # max值是250页

    pic_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&luicode=10000011&containerid=107803{uid}' # 获取图片数量链接

    start_users = ['1261700994']  # 戚薇 朱亚文 赵宝刚  筷子兄弟 张朝阳 迪丽热巴

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BjhPrdSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)

        return spider

    def __init__(self, params, *args, **kwargs):

        super(BjhPrdSpider, self).__init__(self.name, *args, **kwargs)
        # dispatcher.connect(self.spider_closed, signals.spider_closed)
        paramsjson = json.loads(params)
        self.remote_resource = paramsjson.get('remote_resource', True)

    def spider_opened(self, spider):

        self.redis_conn = RedisConnection(settings['REDIS']).get_conn()

    def spider_closed(self, spider):
        pass

    def start_requests(self):
        for uid in self.start_users:
            yield Request(self.pic_url.format(uid=uid), callback=self.parse_pic_num, meta={'uid': uid})

    def parse_pic_num(self, response):
        """
        解析图片数量信息
        :param response: Response对象
        """
        uid = response.meta.get('uid')
        result = json.loads(response.text)
        if result.get('data').get('cards'):
            try:
                pic_num = int(re.search(r'全部图片\((.*?)\)', str(json.loads(response.body.decode()))).group(1))
                if pic_num > 100:
                    logging.info('图片大于100...')
                    self.insert_redis(settings['NORMAL_TABLE'], uid)  # 执行插入redis 动作 # 插入正常下载池

                else:
                    logging.info('图片小于100...')
                    self.insert_redis(settings['ABNORMAL_TABLE'], uid)  # 执行插入redis 动作 # 插入异常下载池

            except AttributeError:

                logging.info('ID没有图片...')
                self.insert_redis(settings['ABNORMAL_TABLE'], uid)  # 执行插入redis 动作 # 插入异常下载池

            # 关注
            yield Request(self.follow_url.format(uid=uid, page=1), callback=self.parse_follows, meta={'page': 1, 'uid': uid}, dont_filter=True)

            # 粉丝
            yield Request(self.fan_url.format(uid=uid, page=1), callback=self.parse_fans, meta={'page': 1, 'uid': uid}, dont_filter=True)

    def parse_follows(self, response):
        """
        解析用户关注
        :param response: Response对象
        """
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards') and len(result.get('data').get('cards')) and \
                result.get('data').get('cards')[-1].get(
                        'card_group'):
            # 解析用户
            follows = result.get('data').get('cards')[-1].get('card_group')
            for follow in follows:
                if follow.get('user'):
                    uid = follow.get('user').get('id')
                    yield Request(self.pic_url.format(uid=uid), callback=self.parse_pic_num, dont_filter=True, meta={'uid': uid}, priority=9)

            uid = response.meta.get('uid')

            # 下一页关注
            logging.info('获取下一页关注列表...')
            page = response.meta.get('page') + 1
            yield Request(self.follow_url.format(uid=uid, page=page), callback=self.parse_follows, meta={'page': page, 'uid': uid})

    def parse_fans(self, response):
        """
        解析用户粉丝
        :param response: Response对象
        """
        result = json.loads(response.text)
        if result.get('ok') and result.get('data').get('cards') and len(result.get('data').get('cards')) and \
                result.get('data').get('cards')[-1].get(
                    'card_group'):
            # 解析用户
            fans = result.get('data').get('cards')[-1].get('card_group')
            for fan in fans:
                if fan.get('user'):
                    uid = fan.get('user').get('id')
                    yield Request(self.pic_url.format(uid=uid), callback=self.parse_pic_num, dont_filter=True, meta={'uid': uid}, priority=9)

            uid = response.meta.get('uid')

            # 下一页粉丝
            page = response.meta.get('page') + 1
            yield Request(self.fan_url.format(uid=uid, page=page), callback=self.parse_fans, meta={'page': page, 'uid': uid})

    def insert_redis(self, table_name, uid):
        if self.redis_conn.sismember(settings['NORMAL_TABLE'], uid) or self.redis_conn.sismember(settings['ABNORMAL_TABLE'], uid)\
                or self.redis_conn.sismember(settings['NORMAL_DONE'], uid) or self.redis_conn.sismember(settings['NORMAL_ING'], uid):
            logging.warning('数据库已存在...')
        else:
            self.redis_conn.sadd(table_name, uid)
