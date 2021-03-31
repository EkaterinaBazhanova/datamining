from pathlib import Path
import json
import requests
#Список категорий
category_list = 'https://5ka.ru/api/v2/categories/'
#cat1 = 'https://5ka.ru/api/v2/special_offers/?store=&records_per_page=12&page=1&categories=&ordering=&price_promo__gte=&price_promo__lte=&search='
#service = 'https://5ka.ru/api/v2/special_offers'

#Делаем запрос
response_category = requests.get(category_list)
data: dict = response_category.json()

for category in data:
    url = f"https://5ka.ru/api/v2/special_offers/?store=&records_per_page=12&page=1&categories={category['parent_group_code']}&"
    category['products'] = []
    while url:
        response_result = requests.get(url)
        data_products: dict = response_result.json()
        url = data_products.get('next')
        category['products'] = data_products['results'] + category['products']
    with open(category['parent_group_name']+".json", 'w', encoding='utf-8') as f:
        json.dump({
            "name": category['parent_group_name'],
            "code": category['parent_group_code'],
            "products": category['products']
        }, f, ensure_ascii=False, indent=4)
