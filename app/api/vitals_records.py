from app.api import bp, helpers
from app.models import VitalsRecord, DAO
from flask import jsonify, request
from flask.views import MethodView

vitals_record_dao = VitalsRecord() # DAO(VitalsRecord())

@bp.route('/vitals-records/<int:id>', methods=['GET'])
def get_vitals_record_details(id):
    vitals_record_dao = DAO(VitalsRecord())
    vitals_record = vitals_record_dao.find_one(id)
    return jsonify(vitals_record)

@bp.route('/vitals-records', methods=['GET'])
def get_all_vitals_records():
    vitals_record_dao = DAO(VitalsRecord())
    args = request.args
    page, per_page = helpers.paginate(args)
    vitals_records = vitals_record_dao.find_all(page,per_page,'api.get_all_vitals_records')
    return jsonify(vitals_records)

@bp.route('/vitals-records', methods=['POST'])
def save_vitals_record_details():
    details = request.get_json(silent=False)
    new_vitals_record = vitals_record_dao.save(details)
    return jsonify(new_vitals_record)

@bp.route('/vitals-records/<int:id>', methods=['DELETE'])
def delete_vitals_record_details(id):
    return "delete vitals_record"

@bp.route('/vitals-records/<int:id>', methods=['PATCH'])
def update_vitals_record_details(id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = id
    updated_vitals_record = vitals_record_dao.update(data)
    return jsonify(updated_vitals_record)
