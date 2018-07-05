from app.api import bp, helpers, cache
from app.models import Anaesthetic, DAO
from flask import jsonify, request

anaesthetic_dao = DAO(Anaesthetic())

@bp.route('/anaesthetics/<int:id>', methods=['GET'])
def get_anaesthetic_details(id):
    path = request.path
    cached = cache.redis.get(path)
    if not cached:
        anaesthetic = anaesthetic_dao.find_one(id)
        cache.set_url_cache(path, anaesthetic)
        return jsonify(anaesthetic)
    else:
        return jsonify(cache.get_url_cache(cached))

@bp.route('/anaesthetics', methods=['GET'])
def get_all_anaesthetics():
    args = request.args
    page, per_page = helpers.paginate(args)
    anaesthetics = anaesthetic_dao.find_all(page,per_page,'api.get_all_anaesthetics')
    return jsonify(anaesthetics)

@bp.route('/anaesthetics', methods=['POST'])
def save_anaesthetic_details():
    details = request.get_json(silent=False)
    new_anaesthetic = anaesthetic_dao.save(details)
    path = new_anaesthetic['_links']['self']
    cache.set_url_cache(path, new_anaesthetic)
    return jsonify(new_anaesthetic)

@bp.route('/anaesthetics/<int:id>', methods=['DELETE'])
def delete_anaesthetic_details(id):
    return "delete anaesthetic"

@bp.route('/anaesthetics/<int:id>', methods=['PATCH'])
def update_anaesthetic_details(id):
    path = request.path
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = id
    updated_anaesthetic = anaesthetic_dao.update(data)
    cache.set_url_cache(path, updated_anaesthetic)
    return jsonify(updated_anaesthetic)
