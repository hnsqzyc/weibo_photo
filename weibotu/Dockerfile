FROM python:3.6
ENV PATH /usr/local/bin:$PATH
RUN pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple \
                 pymysql \
                 redis \
                 scrapy \
                 scrapy-redis
ADD . /code
WORKDIR /code
CMD python main_get_pic.py


