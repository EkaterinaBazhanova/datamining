import scrapy

from gb_parse.avito_loaders import AvitoLoader
from scrapy import Request



class AvitoSpider(scrapy.Spider):
 #   headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
#    headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13'}


    name = 'avito'
    allowed_domains = ['avito.ru']
   # start_urls = ['https://www.avito.ru/krasnodar/kvartiry/prodam-ASgBAgICAUSSA8YQ']
    start_urls = ['https://www.avito.ru/krasnodar/nedvizhimost?cd=1']

    def start_requests(self):
        yield Request(url='https://www.avito.ru/krasnodar/kvartiry/prodam-ASgBAgICAUSSA8YQ?cd=1',
                      meta={'dont_merge_cookies': True})

    _xpath_data_declaration = {
    "title": "//div[@class='title-info-main']/h1[@class='title-info-title']/span[@class='title-info-title-text']/text()",
    "price": "//div[@class='item-price']//span[@class='js-item-price']/@content",
    "address": "//div[@class='item-address']//span[@class='item-address__string']/text()",
    #"flat_parametres": "//div[@class='item-view-block']/div[@class='item-params']/ul[@class='item-params-list']",

   #собрали все li
   "flat_parametres": "//div[@class='item-view-block']/div[@class='item-params']/ul[@class='item-params-list']/li[contains(@class, 'item-params-list-item')]",

   #не пойдет ( "flat_parametres": "//div[@class='item-view-block']/div[@class='item-params']/ul[@class='item-params-list']//text()",
    #"flat_parametres_key": "//span[contains(@class, "item-params-label")]/text()",
    #"flat_parametres_value": "text()",
    "seller_url": "//div[contains(@class, 'item-view-seller-info')]/div[contains(@class, 'seller-info')]/div[contains(@class, 'seller-info-prop')]/div[@class='seller-info-col']/div[@class='seller-info-value']/div[contains(@class, 'seller-info-name')]/a/@href"
    }

    def parse(self, response, *args, **kwargs):
        next_page_num = response.xpath("//div[@class='pagination-root-2oCjZ']/span[@class='pagination-item-1WyVp']/text()").extract_first()
        next_link = f"https://www.avito.ru/krasnodar/kvartiry/prodam-ASgBAgICAUSSA8YQ?cd=1&p={next_page_num}"
        yield response.follow(next_link, callback=self.parse)

        declarations = [
            'https://www.avito.ru'+decl
            for decl in response.xpath("//div[contains(@class,'iva-item-root-G3n7v')]//div[@class='iva-item-titleStep-2bjuh']/a/@href").extract()
        ]
        for link in declarations:
            yield response.follow(link, callback=self.parse_page)

    def parse_page(self, response):
        loader = AvitoLoader(response=response)
        loader.add_value("url", response.url)
        for key, selector in self._xpath_data_declaration.items():
            loader.add_xpath(key, selector)
        print(1)
 #       yield loader.load_item()

