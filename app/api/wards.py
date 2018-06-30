from app.api import bp, helpers
from app.models import Ward, DAO
from flask import jsonify, request
from flask.views import MethodView

ward_dao = DAO(Ward())

@bp.route('/wards/<int:ward_id>', methods=['GET'])
def get_ward_details(ward_id):
    ward = ward_dao.find_one(ward_id)
    return jsonify(ward)

@bp.route('/wards', methods=['GET'])
def get_all_wards():
    args = request.args
    if not ('page' in args) and not ('per_page' in args):
        return jsonify({'error': 'invalid pagination data'})
    page = int(args['page'])
    per_page = int(args['per_page'])
    wards = ward_dao.find_all(page,per_page,'api.get_all_wards')
    return jsonify(wards)

@bp.route('/wards', methods=['POST'])
def save_ward_details():
    details = request.get_json(silent=False)
    new_ward = ward_dao.save(details)
    return jsonify(new_ward)

@bp.route('/wards/<int:ward_id>', methods=['DELETE'])
def delete_ward_details(ward_id):
    return "delete ward"

@bp.route('/wards/<int:ward_id>', methods=['PATCH'])
def update_ward_details(ward_id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = ward_id
    updated_ward = ward_dao.update(data)
    return jsonify(updated_ward)
