from app.api import bp

def register_api(view, endpoint, url, pk='id', pk_type='int'):
    view_func = view.as_view(endpoint)
    bp.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['GET',])
    bp.add_url_rule(url, view_func=view_func, methods=['POST',])
    bp.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])

def paginate(args):
    page=1
    per_page=5
    if 'page' in args:
        print("y")
        page = int(args['page'])
    if 'per_page' in args:
        per_page = int(args['per_page'])
    return (page, per_page)
