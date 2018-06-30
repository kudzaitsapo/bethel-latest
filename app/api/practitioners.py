from app.api import bp, helpers
from app.models import PractitionerDetails, DAO
from flask import jsonify, request
from flask.views import MethodView

practitioner_dao = DAO(PractitionerDetails())

@bp.route('/practitioners/<int:practitioner_id>', methods=['GET'])
def get_practitioner_details(practitioner_id):
    practitioner = practitioner_dao.find_one(practitioner_id)
    return jsonify(practitioner)

@bp.route('/practitioners', methods=['GET'])
def get_all_practitioners():
    args = request.args
    if not ('page' in args) and not ('per_page' in args):
        return jsonify({'error': 'invalid pagination data'})
    page = int(args['page'])
    per_page = int(args['per_page'])
    practitioners = practitioner_dao.find_all(page,per_page,'api.get_all_practitioners')
    return jsonify(practitioners)

@bp.route('/practitioners', methods=['POST'])
def save_practitioner_details():
    details = request.get_json(silent=False)
    new_practitioner = practitioner_dao.save(details)
    return jsonify(new_practitioner)

@bp.route('/practitioners/<int:practitioner_id>', methods=['DELETE'])
def delete_practitioner_details(practitioner_id):
    return "delete practitioner"

@bp.route('/practitioners/<int:practitioner_id>', methods=['PATCH'])
def update_practitioner_details(practitioner_id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = practitioner_id
    updated_practitioner = practitioner_dao.update(data)
    return jsonify(updated_practitioner)
