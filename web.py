from flask import Flask, render_template
import requests
import json
from cision import CisionService
# from Jinja2 import Template

app = Flask(__name__)

service = CisionService(options={
    'id': 'A275C0BF733048FFAE9126ACA64DD08F',
    'page_size': 2,
    'items_per_page': 5,
    'language': 'sv',
    'categories': ['Regular pressreleases', 'BAR'],
    'keywords': ['tag1', 'TAG2'],
    'regulatory': False,
})

@app.route('/')
def index():
    items = service.getFeed()
    items = items if service.items_per_page == 0 else items[0:service.items_per_page]
    print(len(items))
    print(service.items_per_page)
    return render_template('feed.html', items=items)

if __name__ == '__main__':
    # Run the app server on localhost:4449
    app.run('localhost', 4449, debug=True)

