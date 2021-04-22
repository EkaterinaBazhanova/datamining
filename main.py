import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gb_parse.spiders.insta import InstagramSpider

if __name__ == "__main__":
    dotenv.load_dotenv(".env")
    crawler_settings = Settings()
    crawler_settings.setmodule("gb_parse.settings")
    crawler_proc = CrawlerProcess(settings=crawler_settings)
    tags = ['programming']
    crawler_proc.crawl(
        InstagramSpider,
        login=os.getenv('USERNAME'),
        password=os.getenv('ENC_PASSWORD'),
        queryparams=os.getenv('QUERYPARAMS'),
        optintoonetap=os.getenv('OPTINTOONETAP'),
        tags=tags
    )
    crawler_proc.start()

