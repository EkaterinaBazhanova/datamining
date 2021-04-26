import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from gb_parse.spiders.instagram import InstagramSpider

import pymongo
client = pymongo.MongoClient()

def get_handshake_chain(user_1, user_2):
    if user_1 == user_2:
        return f"Пользователь {user_1} жмет руку сам себе"
    else:
#запускаем паука
        dotenv.load_dotenv(".env")
        crawler_settings = Settings()
        crawler_settings.setmodule("gb_parse.settings")
        crawler_proc = CrawlerProcess(settings=crawler_settings)
        user_accounts = [user_1, user_2]
        crawler_proc.crawl(
                           InstagramSpider,
                           login=os.getenv('USERNAME'),
                           password=os.getenv('ENC_PASSWORD'),
                           queryparams=os.getenv('QUERYPARAMS'),
                           optintoonetap=os.getenv('OPTINTOONETAP'),
                           user_accounts=user_accounts
        )
        crawler_proc.start()
# открываем базу
        db = client.instagram_data_mining
        collection = db.instagram
# подписчики, подписки и рукопожатия user_1
        follows_by_list_user_1 = [friend['user_name'] for friend in collection.find_one({'user_name':user_1}, {'follows_by_list': 1})['follows_by_list']]
        follows_list_user_1 = [friend['user_name'] for friend in collection.find_one({'user_name':user_1}, {'follows_list': 1})['follows_list']]
        handshake_user_1 = list(set(follows_by_list_user_1)&set(follows_list_user_1))
# подписчики, подписки и рукопожатия user_2
        follows_by_list_user_2 = [friend['user_name'] for friend in collection.find_one({'user_name':user_2}, {'follows_by_list': 1})['follows_by_list']]
        follows_list_user_2 = [friend['user_name'] for friend in collection.find_one({'user_name':user_2}, {'follows_list': 1})['follows_list']]
        handshake_user_2 = list(set(follows_by_list_user_2)&set(follows_list_user_2))
# проверяем пустоту списков рукопожатий user_1 и user_2
        if (handshake_user_1 == []) or (handshake_user_2 == []):
            return f'Пользователи {user_1} и {user_2} не имеют цепочки рукопожатий'
        else:
            if (user_1 in handshake_user_2) or (user_2 in handshake_user_1):
                return user_1, user_2
            else:
                common_handshake = list(set(handshake_user_1)&set(handshake_user_2))
                if common_handshake!=[]:
                    return user_1, common_handshake[0], user_2
                else:
                    common_handshake_pairs = [[a,b] for a in handshake_user_1 for b in handshake_user_2]
                    for pair in common_handshake_pairs:
                        return user_1, get_handshake_chain(pair[0], pair[1]), user_2


if __name__ == "__main__":
    user_1 = 'dkbazhanov'
    user_2 = 'ltstripes'
    print(f"Цепочка рукопожатий от пользователя {user_1} к {user_2}: {get_handshake_chain(user_1, user_2)}")


