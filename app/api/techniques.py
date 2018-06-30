from app.api import bp, helpers
from app.models import Technique, DAO
from flask import jsonify, request
from flask.views import MethodView

technique_dao = DAO(Technique())

@bp.route('/techniques/<int:technique_id>', methods=['GET'])
def get_technique_details(technique_id):
    technique = technique_dao.find_one(technique_id)
    return jsonify(technique)

@bp.route('/techniques', methods=['GET'])
def get_all_techniques():
    args = request.args
    if not ('page' in args) and not ('per_page' in args):
        return jsonify({'error': 'invalid pagination data'})
    page = int(args['page'])
    per_page = int(args['per_page'])
    techniques = technique_dao.find_all(page,per_page,'api.get_all_techniques')
    return jsonify(techniques)

@bp.route('/techniques', methods=['POST'])
def save_technique_details():
    details = request.get_json(silent=False)
    new_technique = technique_dao.save(details)
    return jsonify(new_technique)

@bp.route('/techniques/<int:technique_id>', methods=['DELETE'])
def delete_technique_details(technique_id):
    return "delete technique"

@bp.route('/techniques/<int:technique_id>', methods=['PATCH'])
def update_technique_details(technique_id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = technique_id
    updated_technique = technique_dao.update(data)
    return jsonify(updated_technique)
