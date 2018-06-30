from app.api import bp, helpers
from app.models import OperativeRecord, DAO
from flask import jsonify, request
from flask.views import MethodView

operative_record_dao = DAO(OperativeRecord())

@bp.route('/operative-records/<int:operative_record_id>', methods=['GET'])
def get_operative_record_details(operative_record_id):
    operative_record = operative_record_dao.find_one(operative_record_id)
    return jsonify(operative_record)

@bp.route('/operative-records', methods=['GET'])
def get_all_operative_records():
    args = request.args
    if not ('page' in args) and not ('per_page' in args):
        return jsonify({'error': 'invalid pagination data'})
    page = int(args['page'])
    per_page = int(args['per_page'])
    operative_records = operative_record_dao.find_all(page,per_page,'api.get_all_operative_records')
    return jsonify(operative_records)

@bp.route('/operative-records', methods=['POST'])
def save_operative_record_details():
    details = request.get_json(silent=False)
    new_operative_record = operative_record_dao.save(details)
    return jsonify(new_operative_record)

@bp.route('/operative-records/<int:operative_record_id>', methods=['DELETE'])
def delete_operative_record_details(operative_record_id):
    return "delete operative_record"

@bp.route('/operative-records/<int:operative_record_id>', methods=['PATCH'])
def update_operative_record_details(operative_record_id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = operative_record_id
    updated_operative_record = operative_record_dao.update(data)
    return jsonify(updated_operative_record)
