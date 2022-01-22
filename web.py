from flask import Flask
import requests
import json
from cision import CisionService

app = Flask(__name__)

service = CisionService(options={
    'id': 'A275C0BF733048FFAE9126ACA64DD08F',
    'page_size': 2,
    'items_per_page': 5,
    'language': 'sv',
    'categories': ['foo', 'bar'],
    'keywords': ['tag1', 'tag2'],
})

@app.route('/')
@app.route('/hello')
def hello():
    # Render the page
    return "Hello Python!"

@app.route('/page/<int:id>')
def page(id):
    return service.getFeed()

if __name__ == '__main__':
    # Run the app server on localhost:4449
    app.run('localhost', 4449, debug=True)

