from app.api import bp, helpers
from app.models import Hospital, DAO
from flask import jsonify, request
from flask.views import MethodView

hospital_dao = DAO(Hospital())

@bp.route('/hospitals/<int:id>', methods=['GET'])
def get_hospital_details(id):
    hospital = hospital_dao.find_one(id)
    return jsonify(hospital)

@bp.route('/hospitals', methods=['GET'])
def get_all_hospitals():
    args = request.args
    page, per_page = helpers.paginate(args)
    hospitals = hospital_dao.find_all(page,per_page,'api.get_all_hospitals')
    return jsonify(hospitals)

@bp.route('/hospitals', methods=['POST'])
def save_hospital_details():
    details = request.get_json(silent=False)
    new_hospital = hospital_dao.save(details)
    return jsonify(new_hospital)

@bp.route('/hospitals/<int:id>', methods=['DELETE'])
def delete_hospital_details(id):
    return "delete hospital"

@bp.route('/hospitals/<int:id>', methods=['PATCH'])
def update_hospital_details(id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = id
    updated_hospital = hospital_dao.update(data)
    return jsonify(updated_hospital)

@bp.route('/hospitals/<int:id>/wards', methods=['GET'])
def get_hospital_wards(id):
    hospital = Hospital.query.get_or_404(id)
    args = request.args
    page, per_page = helpers.paginate(args)
    wards = hospital_dao.find_relations(hospital.wards,page,per_page,'api.get_hospital_wards', id=id)
    return jsonify(wards)
