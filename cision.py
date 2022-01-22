class CisionService:
    id: int
    page_size: 50
    page_index: 1
    language: None
    types: []
    CISION_FEED_URL = 'https://publish.ne.cision.com/papi/NewsFeed/{id}'
    CISION_RELEASE_URL = 'http://publish.ne.cision.com/papi/Release/'
    DEFAULT_TYPES = ['PRM']

    def __init__(self, options):
        print(options.get('id'))
        print('constructor called', options.get('id'))
        self.id = options.get('id')
        self.page_size = options.get('page_size', 50)
        self.page_index = options.get('page_index', 1)
        self.language = options.get('language', None)
        self.types = options.get('information_type', self.DEFAULT_TYPES)
        print(self.types)

    def getFeed(self):
        params={
                    'PageSize': self.page_size,
                    'PageIndex': self.page_index
                }
        print(params)
        print(self.CISION_FEED_URL.format(id=self.id))
        response = requests.get(self.CISION_FEED_URL.format(id=self.id), params={
            'PageSize': self.page_size,
            'PageIndex': self.page_index
        })
        if response.status_code == 200:
            return json.dumps(self.handleFeedResponse(response.json()))

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
        print (len(items))
        return items
