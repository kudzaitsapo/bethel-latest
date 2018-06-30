from app.api import bp, helpers
from app.models import VitalsRecord, DAO
from flask import jsonify, request
from flask.views import MethodView

vitals_record_dao = DAO(VitalsRecord())

@bp.route('/vitals-records/<int:vitals_record_id>', methods=['GET'])
def get_vitals_record_details(vitals_record_id):
    vitals_record = vitals_record_dao.find_one(vitals_record_id)
    return jsonify(vitals_record)

@bp.route('/vitals-records', methods=['GET'])
def get_all_vitals_records():
    args = request.args
    if not ('page' in args) and not ('per_page' in args):
        return jsonify({'error': 'invalid pagination data'})
    page = int(args['page'])
    per_page = int(args['per_page'])
    vitals_records = vitals_record_dao.find_all(page,per_page,'api.get_all_vitals_records')
    return jsonify(vitals_records)

@bp.route('/vitals-records', methods=['POST'])
def save_vitals_record_details():
    details = request.get_json(silent=False)
    new_vitals_record = vitals_record_dao.save(details)
    return jsonify(new_vitals_record)

@bp.route('/vitals-records/<int:vitals_record_id>', methods=['DELETE'])
def delete_vitals_record_details(vitals_record_id):
    return "delete vitals_record"

@bp.route('/vitals-records/<int:vitals_record_id>', methods=['PATCH'])
def update_vitals_record_details(vitals_record_id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = vitals_record_id
    updated_vitals_record = vitals_record_dao.update(data)
    return jsonify(updated_vitals_record)
