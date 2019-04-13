# -*- coding: utf-8 -*-

# Scrapy settings for bjh_product project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'weibotu'

SPIDER_MODULES = ['weibotu.spiders']
NEWSPIDER_MODULE = 'weibotu.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'bjh_product (+http://www.yourdomain.com)'

PRODUCT_NAME = 'bjh_test'
PRODUCT_TEMP_NAME = 'bjh_test_t'

BXS_RESOURCE_POOL = 'bxs_resource'  # LIST
INVALID_BXS_RESOURCE_POOL = 'invalid_bxs_resour' # LIST

BXS_RESOURCE_POOL_PR = 'https_proxy'
INVALID_BXS_RESOURCE_POOL_PR = 'invalid_https_proxy'
BXS_RESOURCE_POOL_UA = 'mobile_ua'
BXS_RESOURCE_POOL_CK = 'weibo_cookies'
INVALID_BXS_RESOURCE_POOL_CK = 'invalid_weibo_cookies'

NORMAL_TABLE = 'normal_1'
ABNORMAL_TABLE = 'abnormal_1'

NORMAL_ING = 'normal_ing_1'
NORMAL_DONE = 'normal_done_1'

ID_TABLE = 'normal_ids'


# DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'
# SCHEDULER = 'scrapy_redis.scheduler.Scheduler'
#
# SCHEDULER_PERSIST = True
#
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderPriorityQueue'
#
# REDIS_HOST = "47.105.103.8"
# REDIS_PORT = 56789
# REDIS_PARAMS = {
# 'password': '12345678'
# }




# Obey robots.txt rules
ROBOTSTXT_OBEY = False
DOWNLOAD_TIMEOUT = 60 # 由于是请求图片， 所以时间太短就会删除ip

# LOG_LEVEL = 'INFO' # default is DEBUG
# LOG_FILE='crawl_bjh.log'

# DATA_DB = {
# 'host' : '120.92.79.194',
#   'user': 'crawler',
#   'password': 'Crawlgag@#fag122',
#   'dbname': 'crawler',
#   'port': 3306
# }

DATA_DB = {
'host' : '47.105.103.8',
  'user': 'root',
  'password': 'Mysql@1234',
  'dbname': 'ali_crawler',
  'port': 3306
}

REDIS = {
    'url': None,
    'host': '172.181.217.58',
    'port': 6379,
    }

# REDIS = {
#     'url': None,
#      # 'host': 'localhost',
#     'host': '47.105.103.8',
#     'port': 56789,
#     'password': '12345678'
#     }

# REDIS = {
#     'url': None,
# #     'host': 'localhost',
#     'host': '120.92.105.253',
#     'port': 56789,
#     'password': '12345678@redis.com'
#     }

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 10

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.1
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False
# DATA_DIR = r'C:\Users\Administrator\Desktop\tk_pic\\'
# DATA_DIR = r'C:\Users\Administrator\Desktop\weibo\\'
DATA_DIR = r'/mnt/zhangyanchao/'
# REDIRECT_ENABLED = False
# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#     "Host": "m.weibo.cn",
#     "Connection": "keep-alive",
#     "Accept": "application/json, text/plain, */*",
#     "MWeibo-Pwa": "1",
#     "X-Requested-With": "XMLHttpRequest",
#     "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
#     # "Referer": "https://m.weibo.cn/p/second?containerid=1078035187664653_-_photoall&page=1&count=24&title=%E5%9B%BE%E7%89%87%E5%A2%99&luicode=10000011&lfid=1078035187664653",
#     "Accept-Encoding": "gzip, deflate, br",
#     "Accept-Language": "zh-CN,zh;q=0.9",
#     "Cookie": "SUB=_2A25xfKQfDeRhGedJ4lIZ9SnMzTmIHXVSnsxXrDV6PUJbktAKLVP6kW1NUbST3CMVnn4PW0duCoKYtYkaRqudUIGF",
#     "Accept-Lan": "zh-CN",
# }

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    # 'bjh_product.middlewares.BjhProductSpiderMiddleware': 543,
#    'bjh_product.middlewares.BjhProductSpiderMiddleware': 400,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'bjh_product.middlewares.BjhProductDownloaderMiddleware': 543,
# }
# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    # 'weibotu.pipelines.WeiBoTuPipeline': 300,
#     'scrapy_redis.pipelines.RedisPipeline': 900
# }

DOWNLOADER_MIDDLEWARES = {
    # 'bjh_product.middlewares.ResourceMiddleware' : 390,
    # 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware' : 400,
    'weibotu.middlewares.UserAgentMiddleware': 401,
    'weibotu.middlewares.CookiesMiddleware': 402,
    'weibotu.middlewares.ProxyMiddleware': 450,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
}
# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}
HANDLE_HTTPSTATUS_CODES = [404, 406]
RETRY_HTTP_CODES = [500, 502] # default is  [500, 502, 503, 504, 408]
HANDLE_PROXY_ERROR_CODES = [400, 401, 403, 407, 408, 503, 504]


# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
