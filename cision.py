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
    CISION_FEED_URL = 'https://publish.ne.cision.com/papi/NewsFeed/{id}'
    CISION_RELEASE_URL = 'http://publish.ne.cision.com/papi/Release/{id}'
    DEFAULT_TYPES = ['PRM']

    def __init__(self, options: dict):
        categories = options.get('categories', [])
        for i in range(len(categories)):
            categories[i] = categories[i].lower()
        keywords = options.get('keywords', [])
        for i in range(len(keywords)):
            keywords[i] = keywords[i].lower()
        types = options.get('types', self.DEFAULT_TYPES)
        for i in range(len(types)):
            types[i] = types[i].upper()
        self.id = options.get('id')
        self.page_size = options.get('page_size', 50)
        self.page_index = options.get('page_index', 1)
        self.items_per_page = options.get('items_per_page', 0)
        self.language = options.get('language', None)
        self.types = types
        self.categories = categories
        self.keywords = keywords
        self.regulatory = options.get('regulatory', None)
        self.must_have_media = options.get('must_have_media', False)

    def get_feed(self):
        params = {
            'PageSize': self.page_size,
            'PageIndex': self.page_index,
            'DetailLevel': 'detail',
            'Regulatory': None if self.regulatory == None else f'{self.regulatory}'.lower()
        }
        response = requests.get(self.CISION_FEED_URL.format(id=self.id), params={
            k: v for k, v in params.items() if v
        })
        if response.status_code in [200, 201]:
            return self.handle_feed_response(response.json())

        return None

    def get_feed_item(self, id: str) -> dict:
        """Returns feed item based on its encrypted id.

        Arguments:
        id -- EncryptedId of the release
        """
        response = requests.get(self.CISION_RELEASE_URL.format(id=id)).json()
        return response.get('Release')

    def handle_feed_response(self, content: dict) -> dict:
        items = content.get('Releases')
        for item in items[:]:
            not_found = False
            item['PublishDate'] = datetime.strptime(item.get('PublishDate')[0:item.get('PublishDate').index('T')], '%Y-%m-%d').date()
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

        return items
