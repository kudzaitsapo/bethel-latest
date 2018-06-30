from app.api import bp, helpers
from app.models import Occupation, DAO
from flask import jsonify, request
from flask.views import MethodView

occupation_dao = DAO(Occupation())

@bp.route('/occupations/<int:occupation_id>', methods=['GET'])
def get_occupation_details(occupation_id):
    occupation = occupation_dao.find_one(occupation_id)
    return jsonify(occupation)

@bp.route('/occupations', methods=['GET'])
def get_all_occupations():
    args = request.args
    if not ('page' in args) and not ('per_page' in args):
        return jsonify({'error': 'invalid pagination data'})
    page = int(args['page'])
    per_page = int(args['per_page'])
    occupations = occupation_dao.find_all(page,per_page,'api.get_all_occupations')
    return jsonify(occupations)

@bp.route('/occupations', methods=['POST'])
def save_occupation_details():
    details = request.get_json(silent=False)
    new_occupation = occupation_dao.save(details)
    return jsonify(new_occupation)

@bp.route('/occupations/<int:occupation_id>', methods=['DELETE'])
def delete_occupation_details(occupation_id):
    return "delete occupation"

@bp.route('/occupations/<int:occupation_id>', methods=['PATCH'])
def update_occupation_details(occupation_id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = occupation_id
    updated_occupation = occupation_dao.update(data)
    return jsonify(updated_occupation)
