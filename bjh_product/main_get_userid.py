import scrapy.cmdline


def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', 'bjh_prd', '-a', 'params='+'{"remote_resource": true}'])
    # ['scrapy', 'crawl', 'jihuashu', '-a', 'params='+'{"remote_resource": true, "interest_flag": true}']


if __name__ == '__main__':
    main()