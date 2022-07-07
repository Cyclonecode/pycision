from flask import Flask, render_template, request
from cision import CisionService
import gzip
from timeit import default_timer
from math import ceil

app = Flask(__name__)

service = CisionService(options={
    'id': 'A275C0BF733048FFAE9126ACA64DD08F',
    'page_size': 10,
    'items_per_page': 5,
    'language': 'sv',
    'categories': [],
    'keywords': [],
    'regulatory': None,
    'must_have_media': False,
    'sort_order': 'alpha',
    'sort_direction': 'Ascending',
    'date_format': '%Y-%m-%d',
    'query_page': 'page',
    'query_id': 'id',
})

@app.route('/')
def index():
    items = service.get_feed()
    # start = default_timer()
    # full_start = start
    # service.bar(items)
    # end = default_timer()
    # print('foo time', 1000 * (end - full_start), 'ms')
    #
    # start = default_timer()
    # full_start = start
    # service.foo(items)
    # end = default_timer()
    # print('bar time', 1000 * (end - full_start), 'ms')

    page = int(request.args.get(service.query_page, 0))
    max_pages = ceil(len(items) / service.items_per_page)
    if page > max_pages - 1:
        page = max_pages - 1
    if page < 0:
        page = 0
    print('length', len(items))
    start = page * service.items_per_page
    end = service.items_per_page * (page + 1)
    pager = None
    if service.items_per_page:
        pager = render_template('pager.html', options={
            'items_per_page': service.items_per_page,
            'page_size': service.page_size,
            'page_index': service.page_index,
            'page': page,
            'pages': ceil(len(items) / service.items_per_page),
            'query_page': service.query_page,
            'query_id': service.query_id,
        })
    content = render_template('feed.html', items=items if service.items_per_page == 0 else items[start:end], options={
        'mark_items': False,
        'date_format': 'Y-m-d',
        'show_media': True,
        'show_intro': True,
        'show_body': False,
        'show_date': True,
        'show_filters': False,
        'regulatory_text': 'Regulatory',
        'non_regulatory_text': 'Non Regulatory',
        'read_more_text': 'Read more',
        'filter_all_text': 'All',
        'filter_regulatory_text': 'Regulatory',
        'filter_non_regulatory_text': 'Non regulatory',
        'pager': pager
    })
    content = gzip.compress(content.encode('utf8'), 5)
    response = app.make_response(content)
    response.headers['Content-length'] = len(content)
    response.headers['Content-Encoding'] = 'gzip'
    return response


# TODO: add support to add short codes / functions in jinja2 template to render a block
#   https://stackoverflow.com/questions/6036082/call-a-python-function-from-jinja2
#   https://flask.palletsprojects.com/en/2.0.x/api/#flask.Flask.template_global

@app.route('/press/<id>')
def article(id: str) -> dict:
    item = service.get_feed_item(f'{id}')
    return render_template('article.html', item=item)

if __name__ == '__main__':
    app.run('localhost', 4000, debug=True)
