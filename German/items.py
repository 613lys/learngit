# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GermanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    published_time = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()
    comments = scrapy.Field()
    comments_num=scrapy.Field()
    favourite = scrapy.Field()
    transmit = scrapy.Field()
    description = scrapy.Field()
    pass
