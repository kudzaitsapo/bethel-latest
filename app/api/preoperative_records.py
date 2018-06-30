from app.api import bp, helpers
from app.models import PreOperativeRecord, DAO
from flask import jsonify, request
from flask.views import MethodView

preoperative_record_dao = DAO(PreOperativeRecord())

@bp.route('/preoperative_records/<int:preoperative_record_id>', methods=['GET'])
def get_preoperative_record_details(preoperative_record_id):
    preoperative_record = preoperative_record_dao.find_one(preoperative_record_id)
    return jsonify(preoperative_record)

@bp.route('/preoperative_records', methods=['GET'])
def get_all_preoperative_records():
    args = request.args
    if not ('page' in args) and not ('per_page' in args):
        return jsonify({'error': 'invalid pagination data'})
    page = int(args['page'])
    per_page = int(args['per_page'])
    preoperative_records = preoperative_record_dao.find_all(page,per_page,'api.get_all_preoperative_records')
    return jsonify(preoperative_records)

@bp.route('/preoperative_records', methods=['POST'])
def save_preoperative_record_details():
    details = request.get_json(silent=False)
    new_preoperative_record = preoperative_record_dao.save(details)
    return jsonify(new_preoperative_record)

@bp.route('/preoperative_records/<int:preoperative_record_id>', methods=['DELETE'])
def delete_preoperative_record_details(preoperative_record_id):
    return "delete preoperative_record"

@bp.route('/preoperative_records/<int:preoperative_record_id>', methods=['PATCH'])
def update_preoperative_record_details(preoperative_record_id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = preoperative_record_id
    updated_preoperative_record = preoperative_record_dao.update(data)
    return jsonify(updated_preoperative_record)
