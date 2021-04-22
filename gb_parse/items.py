# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class GbParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class TagParseItem(scrapy.Item):
    _id = scrapy.Field()
    tag_name = scrapy.Field()
    tag_id = scrapy.Field()
    tag_picture_url = scrapy.Field()

class PostParseItem(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    photos = scrapy.Field()
    #_id = scrapy.Field()
    #tag_name = scrapy.Field()
    #post_id = scrapy.Field()
    #post_pic = scrapy.Field()
    #post_url = scrapy.Field()
    #post_owner_id = scrapy.Field()
    #post_all_data = scrapy.Field()
    #parse_data = scrapy.Field()

class Insta(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    photos = scrapy.Field()


class InstaTag(Insta):
    pass

class InstaPost(Insta):
    pass