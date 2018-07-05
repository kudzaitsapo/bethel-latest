from app.api import bp, helpers, cache
from app.models import VitalsRecord, DAO
from flask import jsonify, request
from flask.views import MethodView

vitals_record_dao = DAO(VitalsRecord())

@bp.route('/vitals-records/<int:id>', methods=['GET'])
def get_vitals_record_details(id):
    path = request.path
    cached = cache.redis.get(path)
    if not cached:
        vitals_record = vitals_record_dao.find_one(id)
        cache.set_url_cache(path, vitals_record)
        return jsonify(vitals_record)
    else:
        return jsonify(cache.get_url_cache(cached))

@bp.route('/vitals-records', methods=['GET'])
def get_all_vitals_records():
    args = request.args
    page, per_page = helpers.paginate(args)
    vitals_records = vitals_record_dao.find_all(page,per_page,'api.get_all_vitals_records')
    return jsonify(vitals_records)

@bp.route('/vitals-records', methods=['POST'])
def save_vitals_record_details():
    details = request.get_json(silent=False)
    new_vitals_record = vitals_record_dao.save_or_update_list(details)
    path = new_vitals_record['_links']['self']
    cache.set_url_cache(path, new_vitals_record)
    return jsonify(new_vitals_record)

@bp.route('/vitals-records/<int:id>', methods=['DELETE'])
def delete_vitals_record_details(id):
    return "delete vitals_record"

@bp.route('/vitals-records/<int:id>', methods=['PATCH'])
def update_vitals_record_details(id):
    path = request.path
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = id
    updated_vitals_record = vitals_record_dao.save_or_update_list(data)
    cache.set_url_cache(path, updated_vitals_record)
    return jsonify(updated_vitals_record)
