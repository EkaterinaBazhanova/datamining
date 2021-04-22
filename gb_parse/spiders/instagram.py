import scrapy
import json
from urllib.parse import urlencode
import datetime as dt
from gb_parse.items import TagParseItem, PostParseItem

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    _login_url = '/accounts/login/ajax/'
    _tags_path = '/explore/tags/'

    def __init__(self, login, password, queryparams, optintoonetap, tags, *args, **kwargs):
        self.login = login
        self.password = password
        self.queryparams = queryparams
        self.optintoonetap = optintoonetap
        self.tags = tags
        super().__init__(*args, **kwargs)

    #заходим в инстаграм и переходим на страницу tag
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
                for tag in self.tags:
                    yield response.follow(f"{self._tags_path}{tag}/", callback=self.tag_page_parse)

    #заходим на страницу tag, собираем данные о tag и данные с первой страницы
    def tag_page_parse(self, response):
        js_data_tag_page = self.js_data_extract(response)
        tag_name = js_data_tag_page['entry_data']['TagPage'][0]['graphql']['hashtag']['name']
        tag_id = js_data_tag_page['entry_data']['TagPage'][0]['graphql']['hashtag']['id']
        tag_picture_url = js_data_tag_page['entry_data']['TagPage'][0]['graphql']['hashtag']['profile_pic_url']

        yield TagParseItem(
                           tag_name=tag_name,
                           tag_id=tag_id,
                           tag_picture_url=tag_picture_url
        )

        # собираем и сохраняем данные страниы 1
        edges = js_data_tag_page['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']
        for edge in edges:
            yield PostParseItem(date_parse=dt.datetime.utcnow(), data=edge["node"], photos=edge['node']['display_url'])
#            tag_name = js_data_tag_page['entry_data']['TagPage'][0]['graphql']['hashtag']['name']
#            post_id = edge['node']['id']
#            post_pic = edge['node']['display_url']
#            post_url = f"www.instagram.com/p/{edge['node']['shortcode']}"
#            post_owner_id = edge['node']['owner']['id']
#            post_all_data = edge['node']
#            parse_data = datetime.now()
#            yield PostParseItem(
#                                tag_name=tag_name,
#                                post_id=post_id,
#                                post_pic=post_pic,
#                                post_url=post_url,
#                                post_owner_id=post_owner_id,
#                                post_all_data=post_all_data,
#                                parse_data=parse_data
#            )

        #переходим к сбору данных постов страниц >1
        next_page_bool = js_data_tag_page['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page']
        if next_page_bool:
            end_cursor = js_data_tag_page['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
            di = {'tag_name': tag_name, 'first': 12, 'after': end_cursor}
            params = {'query_hash': '9b498c08113f1e09617a1703c22b2f32', 'variables': json.dumps(di)}
            url = 'https://www.instagram.com/graphql/query/?' + urlencode(params)
            yield scrapy.Request(url, callback=self.tag_post_parse, meta={'posts_di': di})

    #собираем информацию о posts со страницы >1 и сохраняем ее, картинки posts загружаем в images
    def tag_post_parse(self, response):
        di = response.meta['posts_di']
        js_data_tag_post = json.loads(response.text)
        edges = js_data_tag_post['data']['hashtag']['edge_hashtag_to_media']['edges']
        for edge in edges:
            yield PostParseItem(date_parse=dt.datetime.utcnow(), data=edge["node"], photos=edge['node']['display_url'])
#            tag_name = js_data_tag_post['data']['hashtag']['name']
#            post_id = edge['node']['id']
#            post_pic = edge['node']['display_url']
#            post_url = f"www.instagram.com/p/{edge['node']['shortcode']}"
#            post_owner_id = edge['node']['owner']['id']
#            post_all_data = edge['node']
#            parse_data = datetime.now()
#            yield PostParseItem(
#                tag_name=tag_name,
#                post_id=post_id,
#                post_pic=post_pic,
#                post_url=post_url,
#                post_owner_id=post_owner_id,
 #               post_all_data=post_all_data,
 #               parse_data=parse_data
  #          )

        next_page_bool = js_data_tag_post['data']['hashtag']['edge_hashtag_to_media']['page_info']['has_next_page']
        if next_page_bool:
            end_cursor = js_data_tag_post['data']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
            di['after'] = end_cursor
            params = {'query_hash': '9b498c08113f1e09617a1703c22b2f32', 'variables': json.dumps(di)}
            url = 'https://www.instagram.com/graphql/query/?' + urlencode(params)
            yield scrapy.Request(url, callback=self.tag_post_parse, meta={'posts_di': di})

    def js_data_extract(self, response):
        script = response.xpath("//body//script[contains(text(),'window._sharedData = ')]").extract_first()
        return json.loads(script.replace('<script type="text/javascript">window._sharedData = ', "")[:-10])