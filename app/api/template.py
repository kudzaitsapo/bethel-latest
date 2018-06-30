from app.api import bp, helpers
from app.models import record, DAO
from flask import jsonify, request
from flask.views import MethodView

record_dao = DAO(record())

@bp.route('/records/<int:record_id>', methods=['GET'])
def get_record_details(record_id):
    record = record_dao.find_one(record_id)
    return jsonify(record)

@bp.route('/records', methods=['GET'])
def get_all_records():
    args = request.args
    if not ('page' in args) and not ('per_page' in args):
        return jsonify({'error': 'invalid pagination data'})
    page = int(args['page'])
    per_page = int(args['per_page'])
    records = record_dao.find_all(page,per_page,'api.get_all_records')
    return jsonify(records)

@bp.route('/records', methods=['POST'])
def save_record_details():
    details = request.get_json(silent=False)
    new_record = record_dao.save(details)
    return jsonify(new_record)

@bp.route('/records/<int:record_id>', methods=['DELETE'])
def delete_record_details(record_id):
    return "delete record"

@bp.route('/records/<int:record_id>', methods=['PATCH'])
def update_record_details(record_id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = record_id
    updated_record = record_dao.update(data)
    return jsonify(updated_record)
