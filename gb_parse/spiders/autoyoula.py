import scrapy
import pymongo
import urllib

db_client = pymongo.MongoClient()
db = db_client["youla_data_mining"]
collection = db["youla"]

class AutoyoulaSpider(scrapy.Spider):
    name = "autoyoula"
    allowed_domains = ["auto.youla.ru"]
    start_urls = ["https://auto.youla.ru/"]
    _css_selectors = {
        "brands": "div.ColumnItemList_container__5gTrc a.blackLink",
        "pagination": "div.Paginator_block__2XAPy a.Paginator_button__u1e7D",
        "car": "#serp article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu",
    }

    def _get_follow(self, response, selector_css, callback, **kwargs):
        for link_selector in response.css(selector_css):
            yield response.follow(link_selector.attrib.get("href"), callback=callback)

    def parse(self, response, **kwargs):
        yield from self._get_follow(response, self._css_selectors["brands"], self.brand_parse)

    def brand_parse(self, response):
        yield from self._get_follow(response, self._css_selectors["pagination"], self.brand_parse)
        yield from self._get_follow(response, self._css_selectors["car"], self.car_parse)


    def car_parse(self, response):
#        print(1)
        def get_characteristic(response):
            char_list = []
            for i in range(len(response.css("div.AdvertSpecs_row__ljPcX"))):
                try:
                    char_list.append(response.css("div.AdvertSpecs_row__ljPcX")[i].css(".AdvertSpecs_label__2JHnS::text").extract_first() + " " + response.css("div.AdvertSpecs_row__ljPcX")[i].css(".AdvertSpecs_data__xK2Qx::text").extract_first())
                except TypeError:
                    char_list.append(response.css("div.AdvertSpecs_row__ljPcX")[i].css(".AdvertSpecs_label__2JHnS::text").extract_first() + " " + response.css("div.AdvertSpecs_row__ljPcX")[i].css(".AdvertSpecs_data__xK2Qx a.blackLink::text").extract_first())
            return char_list

        def get_saller_url(response):
            index_youlaProfile = urllib.parse.unquote(urllib.parse.unquote(response.css("body script")[8].extract())).split(',').index('"youlaProfile"')
            if urllib.parse.unquote(urllib.parse.unquote(response.css("body script")[8].extract())).split(',')[index_youlaProfile+1]!='null':
                saller_url = f"https://youla.ru/user/{urllib.parse.unquote(urllib.parse.unquote(response.css('body script')[8].extract())).split(',')[index_youlaProfile+3][1:-1]}"
            else:
                saller_url = urllib.parse.unquote(urllib.parse.unquote(response.css("body script")[8].extract())).split(',')[urllib.parse.unquote(urllib.parse.unquote(response.css("body script")[8].extract())).split(',').index('"url"')+1][1:-1]
            return saller_url

        data = {
            "url": response.url,
            "title": response.css(".AdvertCard_advertTitle__1S1Ak::text").extract_first(),
            "photo": [response.css("section.PhotoGallery_thumbnails__3-1Ob button.PhotoGallery_thumbnailItem__UmhLO")[i].attrib.get('style')[21:-1]
                      for i in range(len(response.css("section.PhotoGallery_thumbnails__3-1Ob button.PhotoGallery_thumbnailItem__UmhLO")))],
            "characteristics": get_characteristic(response),
            "description": response.css(".AdvertCard_descriptionInner__KnuRi::text").extract_first(),
            "saller_url": get_saller_url(response)
        }
        collection.insert_one(data)
