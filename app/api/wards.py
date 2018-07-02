from app.api import bp, helpers
from app.models import Ward, DAO
from flask import jsonify, request
from flask.views import MethodView

ward_dao = DAO(Ward())

@bp.route('/wards/<int:id>', methods=['GET'])
def get_ward_details(id):
    ward = ward_dao.find_one(id)
    return jsonify(ward)

@bp.route('/wards', methods=['GET'])
def get_all_wards():
    args = request.args
    page, per_page = helpers.paginate(args)
    wards = ward_dao.find_all(page,per_page,'api.get_all_wards')
    return jsonify(wards)

@bp.route('/wards', methods=['POST'])
def save_ward_details():
    details = request.get_json(silent=False)
    new_ward = ward_dao.save(details)
    return jsonify(new_ward)

@bp.route('/wards/<int:id>', methods=['DELETE'])
def delete_ward_details(id):
    return "delete ward"

@bp.route('/wards/<int:id>', methods=['PATCH'])
def update_ward_details(id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = id
    updated_ward = ward_dao.update(data)
    return jsonify(updated_ward)

@bp.route('/wards/<int:id>/theaters', methods=['GET'])
def get_ward_theaters(id):
    ward = Ward.query.get_or_404(id)
    args = request.args
    page, per_page = helpers.paginate(args)
    theaters = patient_dao.find_relations(ward.theaters,page,per_page,'api.get_ward_theaters', id=id)
    return jsonify(theaters)
