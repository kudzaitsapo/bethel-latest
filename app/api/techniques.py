from app.api import bp, helpers
from app.models import Technique, DAO
from flask import jsonify, request
from flask.views import MethodView

technique_dao = DAO(Technique())

@bp.route('/techniques/<int:id>', methods=['GET'])
def get_technique_details(id):
    technique = technique_dao.find_one(id)
    return jsonify(technique)

@bp.route('/techniques', methods=['GET'])
def get_all_techniques():
    args = request.args
    page, per_page = helpers.paginate(args)
    techniques = technique_dao.find_all(page,per_page,'api.get_all_techniques')
    return jsonify(techniques)

@bp.route('/techniques', methods=['POST'])
def save_technique_details():
    details = request.get_json(silent=False)
    new_technique = technique_dao.save(details)
    return jsonify(new_technique)

@bp.route('/techniques/<int:id>', methods=['DELETE'])
def delete_technique_details(id):
    return "delete technique"

@bp.route('/techniques/<int:id>', methods=['PATCH'])
def update_technique_details(id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = id
    updated_technique = technique_dao.update(data)
    return jsonify(updated_technique)

@bp.route('/techniques/<int:id>/anaesthetics', methods=['GET'])
def get_techniques_anaesthetics(id):
    technique = Technique.query.get_or_404(id)
    args = request.args
    page, per_page = helpers.paginate(args)
    anaesthetics = technique_dao.find_relations(technique.anaesthetic_id,page,per_page,'api.get_patient_operations', id=id)
    return jsonify(anaesthetics)
