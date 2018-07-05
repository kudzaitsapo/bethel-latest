from app.api import bp, helpers, cache
from app.models import PremedicationRecord, DAO
from flask import jsonify, request
from flask.views import MethodView

premedication_record_dao =  DAO(PremedicationRecord())

@bp.route('/premedication-records/<int:id>', methods=['GET'])
def get_premedication_record_details(id):
    path = request.path
    cached = cache.redis.get(path)
    if not cached:
        premedication_record = premedication_record_dao.find_one(id)
        cache.set_url_cache(path, premedication_record)
        return jsonify(premedication_record)
    else:
        return jsonify(cache.get_url_cache(cached))

@bp.route('/premedication-records', methods=['GET'])
def get_all_premedication_records():
    premedication_record_dao = DAO(PremedicationRecord())
    args = request.args
    page, per_page = helpers.paginate(args)
    premedication_records = premedication_record_dao.find_all(page,per_page,'api.get_all_premedication_records')
    return jsonify(premedication_records)

@bp.route('/premedication-records', methods=['POST'])
def save_premedication_record_details():
    details = request.get_json(silent=False)
    new_premedication_record = premedication_record_dao.save(details)
    path = new_premedication_record['_links']['self']
    cache.set_url_cache(path, new_premedication_record)
    return jsonify(new_premedication_record)

@bp.route('/premedication-records/<int:id>', methods=['DELETE'])
def delete_premedication_record_details(id):
    return "delete premedication_record"

@bp.route('/premedication-records/<int:id>', methods=['PATCH'])
def update_premedication_record_details(id):
    path = request.path
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = id
    updated_premedication_record = premedication_record_dao.update(data)
    cache.set_url_cache(path, updated_premedication_record)
    return jsonify(updated_premedication_record)
