from app.api import bp, helpers
from app.models import PremedicationRecord, DAO
from flask import jsonify, request
from flask.views import MethodView

premedication_record_dao = DAO(PremedicationRecord())

@bp.route('/premedication-records/<int:premedication_record_id>', methods=['GET'])
def get_premedication_record_details(premedication_record_id):
    premedication_record = premedication_record_dao.find_one(premedication_record_id)
    return jsonify(premedication_record)

@bp.route('/premedication-records', methods=['GET'])
def get_all_premedication_records():
    args = request.args
    if not ('page' in args) and not ('per_page' in args):
        return jsonify({'error': 'invalid pagination data'})
    page = int(args['page'])
    per_page = int(args['per_page'])
    premedication_records = premedication_record_dao.find_all(page,per_page,'api.get_all_premedication_records')
    return jsonify(premedication_records)

@bp.route('/premedication-records', methods=['POST'])
def save_premedication_record_details():
    details = request.get_json(silent=False)
    new_premedication_record = premedication_record_dao.save(details)
    return jsonify(new_premedication_record)

@bp.route('/premedication-records/<int:premedication_record_id>', methods=['DELETE'])
def delete_premedication_record_details(premedication_record_id):
    return "delete premedication_record"

@bp.route('/premedication-records/<int:premedication_record_id>', methods=['PATCH'])
def update_premedication_record_details(premedication_record_id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = premedication_record_id
    updated_premedication_record = premedication_record_dao.update(data)
    return jsonify(updated_premedication_record)
