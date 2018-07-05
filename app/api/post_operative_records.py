from app.api import bp, helpers, cache
from app.models import PostOperativeRecord, DAO
from flask import jsonify, request
from flask.views import MethodView

post_operative_record_dao = DAO(PostOperativeRecord())

@bp.route('/post-operative-records/<int:id>', methods=['GET'])
def get_post_operative_record_details(id):
    path = request.path
    cached = cache.redis.get(path)
    if not cached:
        post_operative_record = post_operative_record_dao.find_one(id)
        cache.set_url_cache(path, post_operative_record)
        return jsonify(post_operative_record)
    else:
        return jsonify(cache.get_url_cache(cached))

@bp.route('/post-operative-records', methods=['GET'])
def get_all_post_operative_records():
    args = request.args
    page, per_page = helpers.paginate(args)
    post_operative_records = post_operative_record_dao.find_all(page,per_page,'api.get_all_post_operative_records')
    return jsonify(post_operative_records)

@bp.route('/post-operative-records', methods=['POST'])
def save_post_operative_record_details():
    details = request.get_json(silent=False)
    new_post_operative_record = post_operative_record_dao.save(details)
    path = new_post_operative_record['_links']['self']
    cache.set_url_cache(path, new_post_operative_record)
    return jsonify(new_post_operative_record)

@bp.route('/post-operative-records/<int:id>', methods=['DELETE'])
def delete_post_operative_record_details(id):
    return "delete post_operative_record"

@bp.route('/post-operative-records/<int:id>', methods=['PATCH'])
def update_post_operative_record_details(id):
    path = request.path
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = id
    updated_post_operative_record = post_operative_record_dao.update(data)
    cache.set_url_cache(path, updated_post_operative_record)
    return jsonify(updated_post_operative_record)
