from pathlib import Path
from urllib.parse import urljoin
import requests
import pymongo
import bs4
from dateutil import parser

class MagnitParse:

    def __init__(self, start_url, db_client):
        self.start_url = start_url
        db = db_client["db_data_mining"]
        self.collection = db["magnit"]

    def _get_response(self, url, *args, **kwargs):
        return requests.get(url, *args, **kwargs)

    def _get_soup(self, url, *args, **kwargs):
        return bs4.BeautifulSoup(self._get_response(url, *args, **kwargs).text, "lxml")

    def run(self):
        for product in self._parse(self.start_url):
            self._save(product)

    @property
    def _template(self):
        return {
            "url": lambda tag: urljoin(self.start_url, tag.attrs.get('href','')),
            "promo_name": lambda tag: tag.find('div', attrs="card-sale__header").text,
            "product_name": lambda tag: tag.find('div', attrs={"class": "card-sale__title"}).text,
            "old_price": lambda tag: float(tag.find('div', attrs="label__price_old").find('span', attrs="label__price-integer").text) + int(tag.find('div', attrs="label__price_old").find('span', attrs="label__price-decimal").text) / 100,
            "new_price": lambda tag: float(tag.find('div', attrs={"class":"label__price_new"}).find('span', attrs={"class":"label__price-integer"}).text) + int(tag.find('div', attrs={"class":"label__price_new"}).find('span', attrs={"class":"label__price-decimal"}).text)/100,
            "image_url": lambda tag: tag.find('img')['data-src'],
            "date_from": lambda tag: parser.parse(tag.find_all('p')[-2].text[2:].split()[0] + mounths_eng[tag.find_all('p')[-2].text[2:].split()[1]] + ' 2021 00:00:00'),
            "date_to": lambda tag: parser.parse(tag.find_all('p')[-1].text[3:].split()[0] + mounths_eng[tag.find_all('p')[-1].text[3:].split()[1]] + ' 2021 23:59:59')

        }

    def _parse(self, url):
        soup = self._get_soup(url)
        catalog_main = soup.find('div', attrs={"class": "сatalogue__main"})
        product_tags = catalog_main.find_all('a', recursive=False)
        for product_tag in product_tags:
            product={}
            for key, func in self._template.items():
                try:
                    product[key] = func(product_tag)
                except AttributeError:
                    product[key] = None
                except ValueError:
                   product[key] = None
            yield product

    def _save(self, data):
        self.collection.insert_one(data)


mounths_eng = {
    "января": ' January',
    "февраля": ' February',
    "марта": ' March',
    "апреля": ' April',
    "мая": ' May',
    "июня": ' June',
    "июля": ' July',
    "августа": ' August',
    "сентября": ' September',
    "октября": ' October',
    "ноября": ' November',
    "декабря": ' December'
}

if __name__ == '__main__':
    url = "https://magnit.ru/promo/?geo=moskva"
    db_client = pymongo.MongoClient()
    Parser = MagnitParse(url, db_client)
    Parser.run()
