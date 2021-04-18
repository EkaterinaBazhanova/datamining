# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.http import Request
from scrapy.pipelines.images import ImagesPipeline
import pymongo


class GbParsePipeline:
    def process_item(self, item, spider):
        return item


class GbParseMongoPipeline:
    def __init__(self):
        client = pymongo.MongoClient()
#        self.db = client["hhru_data_mining"]
        self.db = client["avito_data_mining"]

    def process_item(self, item, spider):
        self.db[spider.name].insert_one(item)
        return item

class GbImageDownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for url in item.get('photo', []):
            yield Request(url)

    def item_completed(self, results, item, info):
        if 'photo' in item:
            item['photo'] = [itm[1] for itm in results]
        return item