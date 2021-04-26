import scrapy
import json
from urllib.parse import urlencode
from urllib.parse import urljoin
import datetime as dt
from gb_parse.items import InstaFollowsItem

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com']
    _login_url = '/accounts/login/ajax/'
    _followers_url = '/followers/'
    api_url = "/graphql/query/"


    def __init__(self, login, password, queryparams, optintoonetap, user_accounts, *args, **kwargs):
        self.login = login
        self.password = password
        self.queryparams = queryparams
        self.optintoonetap = optintoonetap
        self.user_accounts = user_accounts
        super().__init__(*args, **kwargs)

    #заходим в инстаграм и переходим на страницу пользователя
    def parse(self, response):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                response.urljoin(self._login_url),
                method="POST",
                callback=self.parse,
                formdata={
                    'username': self.username,
                    'enc_password': self.password,
                    'queryParams': self.queryparams,
                    'optIntoOneTap': self.optintoonetap,
                },
                headers={'X-CSRFToken': js_data['config']['csrf_token']},
            )
        except AttributeError:
            if response.json()['authenticated']:
                for user in self.user_accounts:
                    yield response.follow(f"{self.start_urls[0]}/{user}", callback=self.user_page_parse)

    #заходим на страницу user и переходим на страницу подписчиков
    def user_page_parse(self, response):
        js_user_data = self.js_data_extract(response)
        query_hash = '5aefa9893005572d237da5068082d8d5'
        id = int(js_user_data['entry_data']['ProfilePage'][0]['graphql']['user']['id'])
        user_name = js_user_data['entry_data']['ProfilePage'][0]['graphql']['user']['username']
        data = {
            "user_id": id,
            "user_name": user_name,
            "followers_list": []
        }

        di = {"id":id,"include_reel":True,"fetch_mutual":True,"first":24}
        params = {'query_hash': query_hash, 'variables': json.dumps(di)}
        url=f"{self.start_urls[0]}{self.api_url}?{urlencode(params)}"
        yield response.follow(
            url,
            callback=self._graphql_followes_by_parse,
            cb_kwargs=data,
            meta={'follows_di': di}
        )

    #собираем подписчиков
    def _graphql_followes_by_parse(self, response, *args, **kwargs):
        followers_data = response.json()
        data = response.cb_kwargs

        #собираем данные о подписчиках
        edges = followers_data['data']['user']['edge_followed_by']['edges']
        for edge in edges:
            user_id = int(edge['node']['id'])
            user_name = edge['node']['username']
            full_name = edge['node']['full_name']
            item = {"user_id": user_id, "user_name": user_name, "full_name": full_name}
            data["followers_list"].append(item)

        #делаем пагинацию
        has_nest_page = followers_data['data']['user']['edge_followed_by']['page_info']['has_next_page']
        if has_nest_page:
            end_cursor = followers_data['data']['user']['edge_followed_by']['page_info']['end_cursor']
            di = response.meta['follows_di']
            di["fetch_mutual"] = False
            di["after"] = end_cursor
            query_hash = '5aefa9893005572d237da5068082d8d5'
            params = {'query_hash': query_hash, 'variables': json.dumps(di)}
            url=f"{self.start_urls[0]}{self.api_url}?{urlencode(params)}"
            yield response.follow(
                url,
                callback=self._graphql_followes_by_parse,
                cb_kwargs=data,
                meta={'follows_di': di}
            )
        else:

            #переходим на страницу подписок
            data['follows_list'] = []
            di = {"id": data['user_id'], "include_reel": True, "fetch_mutual": False, "first": 24}
            query_hash = '3dec7e2c57367ef3da3d987d89f9dbc8'
            params = {'query_hash': query_hash, 'variables': json.dumps(di)}
            url = f"{self.start_urls[0]}{self.api_url}?{urlencode(params)}"
            yield response.follow(
                url,
                callback=self._graphql_followes_parse,
                cb_kwargs=data,
                meta={'follows_di': di}
            )

    #собираем подписки
    def _graphql_followes_parse(self, response, *args, **kwargs):
        follows_data = response.json()
        data = response.cb_kwargs

        #собираем данные о подписках
        edges = follows_data['data']['user']['edge_follow']['edges']
        for edge in edges:
            user_id = int(edge['node']['id'])
            user_name = edge['node']['username']
            full_name = edge['node']['full_name']
            item = {"user_id": user_id, "user_name": user_name, "full_name": full_name}
            data['follows_list'].append(item)

        #делаем пагинацию
        has_next_page = follows_data['data']['user']['edge_follow']['page_info']['has_next_page']
        if has_next_page:
            end_cursor = follows_data['data']['user']['edge_follow']['page_info']['end_cursor']
            di = response.meta['follows_di']
            di["after"] = end_cursor
            query_hash = '3dec7e2c57367ef3da3d987d89f9dbc8'
            params = {'query_hash': query_hash, 'variables': json.dumps(di)}
            url=f"{self.start_urls[0]}{self.api_url}?{urlencode(params)}"
            yield response.follow(
                url,
                callback=self._graphql_followes_parse,
                cb_kwargs=data,
                meta={'follows_di': di}
            )
        else:
            #сохраняем данные в базу
            yield InstaFollowsItem(user_id=data['user_id'], user_name=data['user_name'], follows_by_list=data['followers_list'], follows_list=data['follows_list'] )

# 1. метод получения json запроса
    def js_data_extract(self, response):
        script = response.xpath("//body//script[contains(text(),'window._sharedData = ')]").extract_first()
        return json.loads(script.replace('<script type="text/javascript">window._sharedData = ', "")[:-10])
