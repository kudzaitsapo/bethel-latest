from app.api import bp, helpers, cache
from app.models import Prescription, DAO
from flask import jsonify, request
from flask.views import MethodView

prescription_dao = DAO(Prescription())

@bp.route('/prescriptions/<int:id>', methods=['GET'])
def get_prescription_details(id):
    path = request.path
    cached = cache.redis.get(path)
    if not cached:
        prescription = prescription_dao.find_one(id)
        cache.set_url_cache(path, prescription)
        return jsonify(prescription)
    else:
        return jsonify(cache.get_url_cache(cached))

@bp.route('/prescriptions', methods=['GET'])
def get_all_prescriptions():
    args = request.args
    page, per_page = helpers.paginate(args)
    prescriptions = prescription_dao.find_all(page,per_page,'api.get_all_prescriptions')
    return jsonify(prescriptions)

@bp.route('/prescriptions', methods=['POST'])
def save_prescription_details():
    details = request.get_json(silent=False)
    new_prescription = prescription_dao.save(details)
    path = new_prescription['_links']['self']
    cache.set_url_cache(path, new_prescription)
    return jsonify(new_prescription)

@bp.route('/prescriptions/<int:id>', methods=['DELETE'])
def delete_prescription_details(id):
    return "delete prescription"

@bp.route('/prescriptions/<int:id>', methods=['PATCH'])
def update_prescription_details(id):
    path = request.path
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = id
    updated_prescription = prescription_dao.update(data)
    cache.set_url_cache(path, updated_prescription)
    return jsonify(updated_prescription)
