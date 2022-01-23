import requests
from datetime import datetime


class CisionService:
    id: int
    page_size: int = 50
    page_index: int = 1
    items_per_page: int = 0
    language: str = None
    types: list = []
    categories: list = []
    keywords: list = []
    regulatory: bool = None
    must_have_media: bool = False
    query_page: str = 'cb_page'
    query_id: str = 'cb_id'

    CISION_FEED_URL = 'https://publish.ne.cision.com/papi/NewsFeed/{id}'
    CISION_RELEASE_URL = 'http://publish.ne.cision.com/papi/Release/{id}'
    DEFAULT_TYPES = ['PRM']
    DEFAULT_PAGE_SIZE = 50
    DEFAULT_PAGE_INDEX = 1
    DEFAULT_ITEMS_PER_PAGE = 0
    VERSION = '1.0.0'

    def __init__(self, options: dict):
        categories = [c.lower() for c in options.get('categories', [])]
        keywords = [k.lower() for k in options.get('keywords', [])]
        types = [t.upper() for t in options.get('types', self.DEFAULT_TYPES)]
        self.id = options.get('id')
        self.page_size = options.get('page_size', self.DEFAULT_PAGE_SIZE)
        self.page_index = options.get('page_index', self.DEFAULT_PAGE_INDEX)
        self.items_per_page = options.get('items_per_page', self.DEFAULT_ITEMS_PER_PAGE)
        self.language = options.get('language', None)
        self.types = types
        self.categories = categories
        self.keywords = keywords
        self.regulatory = options.get('regulatory', None)
        self.must_have_media = options.get('must_have_media', False)
        self.query_page = options.get('query_page', 'cb_page')
        self.query_id = options.get('query_id', 'cb_id')

    def get_feed(self) -> list:
        params = {
            'PageSize': self.page_size,
            'PageIndex': self.page_index,
            'DetailLevel': 'detail',
            'Regulatory': None if self.regulatory == None else f'{self.regulatory}'.lower()
        }
        response = requests.get(self.CISION_FEED_URL.format(id=self.id), params={
            k: v for k, v in params.items() if v
        }, headers={
            b'User-Agent': 'cisionpy/{0}'.format(self.VERSION),
            b'Accept-Encoding': 'gzip, deflate',
            b'Accept': 'application/json'
        })
        if response.status_code in [200, 201]:
            return self.__handle_feed_response(response.json())

        return []

    def get_feed_item(self, id: str) -> dict or None:
        """Returns feed item based on its encrypted id.

        Arguments:
        id -- EncryptedId of the release
        """
        response = requests.get(self.CISION_RELEASE_URL.format(id=id)).json()
        return response.get('Release')

    @staticmethod
    def __transform_items(items: list) -> list:
        result = map(lambda it: {
            'EncryptedId': it.get('EncryptedId'),
            'Title': it.get('Title'),
            'Intro': it.get('Intro'),
            'Body': it.get('Body'),
            'Images': it.get('Images'),
            'PublishDate': it.get('PublishDate'),
        }, items)
        return list(result)

    def __handle_feed_response(self, content: dict) -> dict:
        items = content.get('Releases')
        for item in items[:]:
            not_found = False
            item['PublishDate'] = datetime.strptime(item.get('PublishDate')[0:item.get('PublishDate').index('T')],
                                                    '%Y-%m-%d').date()
            if self.must_have_media and not len(item.get('Images', [])):
                print('removing based on media')
                items.remove(item)
                continue
            if item.get('InformationType') not in self.types:
                print('removing based on type')
                items.remove(item)
                continue
            if self.language and item.get('LanguageCode') != self.language:
                print('removing basd on language')
                items.remove(item)
                continue
            if len(self.categories):
                if not len(item.get('Categories', [])):
                    items.remove(item)
                    continue
                for category in item.get('Categories', [{'Code': None}]):
                    if category.get('Name').lower() not in self.categories:
                        print('removing based on category')
                        not_found = True
                        break
                if not_found:
                    items.remove(item)
                    continue
            if len(self.keywords):
                print(item.get('Keywords'))
                if not len(item.get('Keywords', [])):
                    items.remove(item)
                    continue
                for keyword in item.get('Keywords', []):
                    print('keyword', keyword)
                    if keyword.lower() not in self.keywords:
                        print('removing based on keyword => ', item.get('Title'))
                        items.remove(item)
                        break
        return self.__transform_items(items=items)
