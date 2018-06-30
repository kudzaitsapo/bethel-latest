from app.api import bp, helpers
from app.models import Prescription, DAO
from flask import jsonify, request
from flask.views import MethodView

prescription_dao = DAO(Prescription())

@bp.route('/prescriptions/<int:prescription_id>', methods=['GET'])
def get_prescription_details(prescription_id):
    prescription = prescription_dao.find_one(prescription_id)
    return jsonify(prescription)

@bp.route('/prescriptions', methods=['GET'])
def get_all_prescriptions():
    args = request.args
    if not ('page' in args) and not ('per_page' in args):
        return jsonify({'error': 'invalid pagination data'})
    page = int(args['page'])
    per_page = int(args['per_page'])
    prescriptions = prescription_dao.find_all(page,per_page,'api.get_all_prescriptions')
    return jsonify(prescriptions)

@bp.route('/prescriptions', methods=['POST'])
def save_prescription_details():
    details = request.get_json(silent=False)
    new_prescription = prescription_dao.save(details)
    return jsonify(new_prescription)

@bp.route('/prescriptions/<int:prescription_id>', methods=['DELETE'])
def delete_prescription_details(prescription_id):
    return "delete prescription"

@bp.route('/prescriptions/<int:prescription_id>', methods=['PATCH'])
def update_prescription_details(prescription_id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = prescription_id
    updated_prescription = prescription_dao.update(data)
    return jsonify(updated_prescription)
