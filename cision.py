import requests
import json

class CisionService:
    id: int
    page_size: 50
    page_index: 1
    items_per_page: 0
    language: None
    types: []
    categories: []
    keywords: []
    regulatory: None
    CISION_FEED_URL = 'https://publish.ne.cision.com/papi/NewsFeed/{id}'
    CISION_RELEASE_URL = 'http://publish.ne.cision.com/papi/Release/'
    DEFAULT_TYPES = ['PRM']

    def __init__(self, options):
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
        print(self.types)

    def getFeed(self):
        params={
                    'PageSize': self.page_size,
                    'PageIndex': self.page_index
                }
        params = {
            'PageSize': self.page_size,
            'PageIndex': self.page_index,
            'DetailLevel': 'detail',
            'Regulatory': None if self.regulatory == None else f'{self.regulatory}'.lower()
        }
        response = requests.get(self.CISION_FEED_URL.format(id=self.id), params={
            k: v for k, v in params.items() if v
        })
        if response.status_code == 200:
            #return json.dumps(self.handleFeedResponse(response.json()))
            return self.handleFeedResponse(response.json())

        return None

    def handleFeedResponse(self, content):
        items = content.get('Releases')
        for item in items[:]:
            if item.get('InformationType') not in self.types:
                print ('removing based on type')
                items.remove(item)
            if self.language and item.get('LanguageCode') != self.language:
                print ('removing basd on language')
                items.remove(item)
            if len(self.categories):
                for category in item.get('Categories', [{ 'Code': None }]):
                  print (category)
                  if category.get('Name').lower() not in self.categories:
                    print ('removing based on category')
                    items.remove(item)
        print (len(items))
        return items
