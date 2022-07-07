import requests
from requests import Response
from functools import lru_cache
from datetime import datetime

# TODO: Handle constants
class ImmutableDict(dict):
    def __setitem__(self, key, value):
        raise TypeError("%r object does not support item assignment" % type(self).__name__)

    def __delitem__(self, key):
        raise TypeError("%r object does not support item deletion" % type(self).__name__)

    def __getattribute__(self, attribute):
        if attribute in ('clear', 'update', 'pop', 'popitem', 'setdefault'):
            raise AttributeError("%r object has no attribute %r" % (type(self).__name__, attribute))
        return dict.__getattribute__(self, attribute)

    def __hash__(self):
        return hash(tuple(sorted(self.iteritems())))

    def fromkeys(self, S, v):
        return type(self)(dict(self).fromkeys(S, v))


class ImmutableStr(str):
    def __setitem__(self, key, value):
        raise TypeError("%r object STRING __setitem__ does not support item assignment" % type(self).__name__)

    def __set__(self, key, value):
        raise TypeError("%r object STRING __set__ does not support item assignment" % type(self).__name__)

    def __delitem__(self, key):
        raise TypeError("%r object does not support item deletion" % type(self).__name__)


class ImmutableInt(int):
    def __setitem__(self, key, value):
        raise TypeError("%r object INT __setitem__ does not support item assignment" % type(self).__name__)

    def __set__(self, key, value):
        raise TypeError("%r object INT __set__ does not support item assignment" % type(self).__name__)

    def __delitem__(self, key):
        raise TypeError("%r object INT does not support item deletion" % type(self).__name__)


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
    DEFAULT_TYPES = ('PRM',)
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

    @lru_cache
    def get_feed(self) -> list:
        params = {
            'PageSize': self.page_size,
            'PageIndex': self.page_index,
            'DetailLevel': 'detail',
            'Regulatory': None if self.regulatory == None else f'{self.regulatory}'.lower()
        }
        response = self.__fetch(self.CISION_FEED_URL.format(id=self.id), params={
            k: v for k, v in params.items() if v
        })
        return self.__handle_feed_response(response.json()) if response.status_code in [200, 201] else []

    @lru_cache
    def get_feed_item(self, id: str) -> dict:
        """Returns feed item based on its encrypted id.

        Arguments:
        id -- EncryptedId of the release
        """
        response = self.__fetch(self.CISION_RELEASE_URL.format(id=id))
        return response.json().get('Release') if response.status_code in [200, 201] else []

    @staticmethod
    def __transform_items(items: list) -> list:
        return [{
            'EncryptedId': it.get('EncryptedId'),
            'Title': it.get('Title'),
            'Intro': it.get('Intro'),
            'Body': it.get('Body'),
            'Images': it.get('Images'),
            'PublishDate': datetime.strptime(it.get('PublishDate')[0:it.get('PublishDate').index('T')], '%Y-%m-%d').date(),
            'Files': it.get('Files'),
        } for it in items]

    @staticmethod
    def __fetch(url: str, params: dict = {}) -> Response:
        return requests.get(url, params, headers={
            b'User-Agent': 'cisionpy/{0}'.format(CisionService.VERSION),
            b'Accept-Encoding': 'gzip, deflate',
            b'Accept': 'application/json'
        })

    def __handle_feed_response(self, content: dict) -> dict:
        items = content.get('Releases')
        for item in items[:]:
            if self.must_have_media and not len(item.get('Images')):
                print('removing based on media')
                items.remove(item)
                continue
            if item.get('InformationType') not in self.types:
                print('removing based on type', item.get('InformationType'))
                items.remove(item)
                continue
            if self.language and item.get('LanguageCode') != self.language:
                print('removing basd on language')
                items.remove(item)
                continue
            if len(self.categories) and not bool([c for c in item.get('Categories') if c.get('Name').lower() in self.categories]):
                print('removing based on category')
                items.remove(item)
                continue
            if len(self.keywords) and not bool([k for k in item.get('Keywords') if k.lower() in self.keywords]):
                print('removing based on keyword')
                items.remove(item)
                continue
        return self.__transform_items(items=items)
