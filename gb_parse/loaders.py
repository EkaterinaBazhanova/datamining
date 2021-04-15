import re
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst, Join

def get_employer_activity(text):
    list = text.split(", ")
    return list

def clear_list_of_text(text):
    if text == " ":
        text = None
    return text

class HhruLoader(ItemLoader):
    default_item_class = dict
    vacancy_title_out = TakeFirst()
    salary_out = Join()
    description_out = Join()
    company_url_out = TakeFirst()
    employer_name_in = MapCompose(clear_list_of_text)
    employer_name_out = Join()
    employer_url_out = TakeFirst()
    employer_description_in = MapCompose(clear_list_of_text)
    employer_description_out = Join()
    employer_activity_in = MapCompose(get_employer_activity)
