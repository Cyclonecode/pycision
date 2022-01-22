from flask import Flask, render_template
from cision import CisionService

app = Flask(__name__)

service = CisionService(options={
    'id': 'A275C0BF733048FFAE9126ACA64DD08F',
    'page_size': 10,
    'items_per_page': 5,
    'language': 'sv',
    'categories': ['foo', 'bar', 'BAZ'],
    'keywords': [],
    'regulatory': None,
    'must_have_media': False,
    'sort_order': 'alpha',
    'sort_direction': 'Ascending',
    'date_format': '%Y-%m-%d',
})


@app.route('/')
def index():
    items = service.get_feed()
    print(len(items))
    items = items if service.items_per_page == 0 else items[0:service.items_per_page]
    return render_template('feed.html', items=items, options={
        'mark_items': False,
        'date_format': 'Y-m-d',
        'show_media': False,
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
        'pager': render_template('pager.html', items=items, options={
            'items_per_page': service.items_per_page,
            'page_size': service.page_size,
            'page_index': service.page_index,
        })
    })

@app.route('/press/<id>')
def article(id: str) -> dict:
    item = service.get_feed_item(f'{id}')
    return render_template('article.html', item=item)


if __name__ == '__main__':
    app.run('localhost', 4000, debug=True)
