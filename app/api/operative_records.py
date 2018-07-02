from app.api import bp, helpers
from app.models import OperativeRecord, DAO
from flask import jsonify, request
from flask.views import MethodView

operative_record_dao = DAO(OperativeRecord())

@bp.route('/operative-records/<int:id>', methods=['GET'])
def get_operative_record_details(id):
    operative_record = operative_record_dao.find_one(id)
    return jsonify(operative_record)

@bp.route('/operative-records', methods=['GET'])
def get_all_operative_records():
    args = request.args
    page, per_page = helpers.paginate(args)
    operative_records = operative_record_dao.find_all(page,per_page,'api.get_all_operative_records')
    return jsonify(operative_records)

@bp.route('/operative-records', methods=['POST'])
def save_operative_record_details():
    details = request.get_json(silent=False)
    new_operative_record = operative_record_dao.save(details)
    return jsonify(new_operative_record)

@bp.route('/operative-records/<int:id>', methods=['DELETE'])
def delete_operative_record_details(id):
    return "delete operative_record"

@bp.route('/operative-records/<int:id>', methods=['PATCH'])
def update_operative_record_details(id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = id
    updated_operative_record = operative_record_dao.update(data)
    return jsonify(updated_operative_record)
