from app.api import bp, helpers, cache
from app.models import Referal, DAO
from flask import jsonify, request
from flask.views import MethodView

referal_dao = DAO(Referal())

@bp.route('/referals/<int:id>', methods=['GET'])
def get_referal_details(id):
    path = request.path
    cached = cache.redis.get(path)
    if not cached:
        referal = referal_dao.find_one(id)
        cache.set_url_cache(path, referal)
        return jsonify(referal)
    else:
        return jsonify(cache.get_url_cache(cached))

@bp.route('/referals', methods=['GET'])
def get_all_referals():
    args = request.args
    page, per_page = helpers.paginate(args)
    referals = referal_dao.find_all(page,per_page,'api.get_all_referals')
    return jsonify(referals)

@bp.route('/referals', methods=['POST'])
def save_referal_details():
    details = request.get_json(silent=False)
    new_referal = referal_dao.save(details)
    path = new_referal['_links']['self']
    cache.set_url_cache(path, new_referal)
    return jsonify(new_referal)

@bp.route('/referals/<int:id>', methods=['DELETE'])
def delete_referal_details(id):
    return "delete referal"

@bp.route('/referals/<int:id>', methods=['PATCH'])
def update_referal_details(id):
    path = request.path
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = id
    updated_referal = referal_dao.update(data)
    cache.set_url_cache(path, updated_referal)
    return jsonify(updated_referal)
