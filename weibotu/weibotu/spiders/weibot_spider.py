# -*- coding: utf-8 -*-
import scrapy
import json
import re
import os
import hashlib
import time
import pymysql
import logging
from scrapy import signals
from scrapy.item import Item, Field
from weibotu.connection import MySQLConnection, RedisConnection
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

    name = 'wbt'

    photo_url = 'https://m.weibo.cn/api/container/getSecond?containerid=107803{uid}_-_photoall&page={page}&count=100&title=%E5%9B%BE%E7%89%87%E5%A2%99&luicode=10000011&lfid=107803{uid}'

    user_url = 'https://m.weibo.cn/api/container/getIndex?uid={uid}&type=uid&value={uid}&containerid=100505{uid}'

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
        # self.data_conn = MySQLConnection(settings['DATA_DB']).get_conn()
        self.redis_conn = RedisConnection(settings['REDIS']).get_conn()

        # self.dbsession = db(self.data_conn)

    def spider_closed(self, spider):
        pass
        # self.data_conn.close()

    def start_requests(self):

        hd = {
            "Host": "m.weibo.cn",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }

        while 1:

            if not self.redis_conn.scard(settings['NORMAL_TABLE']):
                logging.info('资源池空了, 请添加资源...')
                time.sleep(3)

            else:
                uid = self.redis_conn.spop(settings['NORMAL_TABLE']).decode()
                print(self.redis_conn.sadd(settings['NORMAL_ING'], uid))

                meta = {}
                meta['uid'] = uid

                yield Request(self.user_url.format(uid=uid), headers=hd, callback=self.parse_user, meta=meta, priority=9)

    def parse_user(self, response):
        """
        解析用户信息
        :param response: Response对象
        """
        meta = response.request.meta
        uid = meta['uid']
        res_1 = json.loads(response.text)
        if self.verify_sensitive(response):  # 判断是否有敏感词汇
            # 性别
            try:
                gender = re.search(r'"gender":"(.*?)"', response.text).group(1)
                if gender == 'm':
                    meta['gender'] = 1
                elif gender == 'f':
                    meta['gender'] = 2
                else:
                    meta['gender'] = 3

            except:
                meta['gender'] = 3

            screen_name = res_1.get('data').get('userInfo').get('screen_name')

            if screen_name:
                screen_name = str(screen_name) + '_'
            else:
                screen_name = 'None'

            if not os.path.exists(settings['DATA_DIR'] + screen_name + str(uid) + str(meta['gender'])):
                os.mkdir(settings['DATA_DIR'] + screen_name + str(uid) + str(meta['gender']))
            save_location = os.path.join(settings['DATA_DIR'], screen_name + str(uid) + str(meta['gender']))

            try:
                refer_url = re.search(r'containerid.*', self.photo_url.format(uid=uid, page=1)).group()

            except:
                refer_url = 'containerid=1078031266321801_-_photoall&page=1&count=24&title=%E5%9B%BE%E7%89%87%E5%A2%99&luicode=10000011&lfid=1078031266321801'

            header = {
                "Connection": "keep-alive",
                "Accept": "application/json, text/plain, */*",
                "MWeibo-Pwa": "1",
                "X-Requested-With": "XMLHttpRequest",
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
                "Referer": "https://m.weibo.cn/p/second?" + refer_url,
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Cookie": "SUB=_2A25xfKQfDeRhGedJ4lIZ9SnMzTmIHXVSnsxXrDV6PUJbktAKLVP6kW1NUbST3CMVnn4PW0duCoKYtYkaRqudUIGF"
            }

            meta['save_location'] = save_location
            meta['page'] = 1
            meta['uid'] = uid
            meta['header'] = header
            yield Request(url=self.photo_url.format(uid=uid, page=1), headers=header, callback=self.parse_image_url, meta=meta, priority=9)

        else:
            # 此时就认为id含有敏感词, 把uid移入无效池
            logging.warning('含有敏感词, 移入无效池...')
            self.redis_conn.smove(settings['NORMAL_ING'], settings['ABNORMAL_TABLE'], uid)

    def parse_image_url(self, response):
        meta = response.request.meta
        res_js = json.loads(response.text)
        uid = response.meta.get('uid')

        # if not res_js.get('ok') and meta['page'] == 1:
        #     return 备用

        if res_js.get('ok') and res_js.get('data').get('cards') and meta['page'] < 11:

            for picss in res_js['data']['cards']:
                for pic_middles in picss['pics']:
                    pic_url = pic_middles['pic_big']
                    pic_id = pic_middles['pic_id']
                    meta['pic_url'] = pic_url
                    meta['pic_id'] = pic_id
                    yield self.submit_image_request(meta)

            # 下一页
            logging.info('获取下一页图片列表...')
            page = response.meta.get('page') + 1
            meta['page'] = page
            yield Request(self.photo_url.format(uid=uid, page=page), headers=meta['header'], callback=self.parse_image_url, meta=meta, priority=9)

        else:
            # 此时就认为图片已经爬取完成了, 把正在爬取的id 转入 已经爬取完成的id 池
            self.redis_conn.smove(settings['NORMAL_ING'], settings['NORMAL_DONE'], uid)

            # 爬取完成后标记为D
            self.rename_file(meta['save_location'])

    def submit_image_request(self, meta):

        heads = meta['pic_url']
        # head = re.search(r'http://(.*?)/wap360', heads).group(1)
        head = re.search(r'http://(.*?)/large', heads).group(1)
        header = {
            "Host": head,
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36", # 要随机变动
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }

        file_name = os.path.join(meta['save_location'], str(meta['pic_id']) + '.jpg')

        meta['file_name'] = file_name
        print('正在下载:' + file_name)
        return Request(meta['pic_url'], headers=header, callback=self.download_image, meta=meta, priority=10)
        # request.urlretrieve(meta['pic_url'], meta['file_name'])

    def download_image(self, response):
        meta = response.request.meta
        res = response.body
        try:
            with open(meta['file_name'], 'wb') as f:
                f.write(res)
                f.close()
            logging.info('已经下载...')
        except FileNotFoundError:
            print('捕捉到文件名有误...')
            b = re.search(r'\d{11}', meta['file_name']).group()
            filename = re.sub(b, b + '_D', meta['file_name'])
            with open(filename, 'wb') as f:
                f.write(res)
                f.close()
            logging.info('已经下载...')
            
    def rename_file(self, file_name):
        if os.path.exists(file_name):
            try:
                target_file = file_name + '_D'
                os.rename(file_name, target_file)
            except:
                pass

    def verify_sensitive(self, response):

        res_1 = json.loads(response.text)

        screen_name = res_1.get('data').get('userInfo').get('screen_name')
        description = res_1.get('data').get('userInfo').get('description')
        verified_reason = res_1.get('data').get('userInfo').get('verified_reason')
        content = screen_name + description + str(verified_reason)
        print('content:', content)
        minc = ['代购', '化妆', '后援', '粉丝', '客源', '代理', '杂志', '日报', '俱乐部', '有限公司', '电视剧', '客服', '免税店', '直邮', '房屋租售', '新闻', '请加微信',
                '免费资源', '社区', '淘宝店', '打折', '潮鞋范', '现货', '潮鞋', '资讯', '直销', '外汇', '期货', '股票', '旅游', '女装', '服装', '整形', '房产', '娱乐', '潮牌', '新剧',
                '美剧', '日剧', '韩剧', '公司', '维权', '优惠', '淘宝', '美瞳', '粉丝', '激活码', '植发', '资讯', '代理', '考研', '俱乐部', '京东', '珠宝', '后援', '法院','搞笑','交友',
                '代购','批发','时尚','国际','精选','专卖','宠物','国际','交易','中医','积分','大学','消防','美食','医美','养生','经销','影视','理财','政府','美甲','视频','用品','推广',
                '咨询','脑洞','顾问']
        res_li = []
        for mi in minc:
            if mi in content:
                res_li.append(mi)

            else:
                pass
        if res_li:
            return False
        else:
            return True



