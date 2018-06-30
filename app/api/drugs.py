from app.api import bp, helpers
from app.models import Drug, DAO
from flask import jsonify, request
from flask.views import MethodView

drug_dao = DAO(Drug())

@bp.route('/drugs/<int:drug_id>', methods=['GET'])
def get_drug_details(drug_id):
    drug = drug_dao.find_one(drug_id)
    return jsonify(drug)

@bp.route('/drugs', methods=['GET'])
def get_all_drugs():
    args = request.args
    if not ('page' in args) and not ('per_page' in args):
        return jsonify({'error': 'invalid pagination data'})
    page = int(args['page'])
    per_page = int(args['per_page'])
    drugs = drug_dao.find_all(page,per_page,'api.get_all_drugs')
    return jsonify(drugs)

@bp.route('/drugs', methods=['POST'])
def save_drug_details():
    details = request.get_json(silent=False)
    new_drug = drug_dao.save(details)
    return jsonify(new_drug)

@bp.route('/drugs/<int:drug_id>', methods=['DELETE'])
def delete_drug_details(drug_id):
    return "delete drug"

@bp.route('/drugs/<int:drug_id>', methods=['PATCH'])
def update_drug_details(drug_id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = drug_id
    updated_drug = drug_dao.update(data)
    return jsonify(updated_drug)
