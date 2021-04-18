from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst, Join
from scrapy import Selector

def get_price(price):
    result = float(price)
    return result

#def get_params_in(item: str) -> list:
#    selector = Selector(text=item)
#    data = {
#            "name": selector.xpath('.//span[contains(@class, "item-params-label")]/text()').extract_first().replace(": ", ""),
#            "value": selector.xpath("./text()[last()] | ./a/text()").extract_first()
#        }
#    return data

#def get_params_out(list) -> dict:
#    params = {dict['name']:dict['value'] for dict in list}
 #   return params

def get_params(item: str) -> list:
    sel = Selector(text=item)
    data = {
        sel.xpath('.//span[contains(@class, "item-params-label")]/text()').extract_first().replace(": ", ""):
        sel.xpath("./text()[last()] | ./a/text()").extract_first()
        }
    return data

def get_address(text):
    address = text.replace("\n ", "")
    return address

def get_seller_url(text):
    url = f"https://www.avito.ru{text}"
    url = url.replace('https://www.avito.ruhttps://www.avito.ru', 'https://www.avito.ru')
    return url

class AvitoLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_out = TakeFirst()
    price_in = MapCompose(get_price)
    price_out = TakeFirst()
    address_in = MapCompose(get_address)
    address_out = TakeFirst()
    flat_parametres_in = MapCompose(get_params)
#flat_parametres_in = MapCompose(get_params_in)
  #  flat_parametres_out = MapCompose(get_params_out)
    seller_url_in = MapCompose(get_seller_url)
    seller_url_out = TakeFirst()
