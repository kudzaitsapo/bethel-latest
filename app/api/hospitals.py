from app.api import bp, helpers
from app.models import Hospital, DAO
from flask import jsonify, request
from flask.views import MethodView

hospital_dao = DAO(Hospital())

@bp.route('/hospitals/<int:hospital_id>', methods=['GET'])
def get_hospital_details(hospital_id):
    hospital = hospital_dao.find_one(hospital_id)
    return jsonify(hospital)

@bp.route('/hospitals', methods=['GET'])
def get_all_hospitals():
    args = request.args
    if not ('page' in args) and not ('per_page' in args):
        return jsonify({'error': 'invalid pagination data'})
    page = int(args['page'])
    per_page = int(args['per_page'])
    hospitals = hospital_dao.find_all(page,per_page,'api.get_all_hospitals')
    return jsonify(hospitals)

@bp.route('/hospitals', methods=['POST'])
def save_hospital_details():
    details = request.get_json(silent=False)
    new_hospital = hospital_dao.save(details)
    return jsonify(new_hospital)

@bp.route('/hospitals/<int:hospital_id>', methods=['DELETE'])
def delete_hospital_details(hospital_id):
    return "delete hospital"

@bp.route('/hospitals/<int:hospital_id>', methods=['PATCH'])
def update_hospital_details(hospital_id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = hospital_id
    updated_hospital = hospital_dao.update(data)
    return jsonify(updated_hospital)
