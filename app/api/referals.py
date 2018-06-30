from app.api import bp, helpers
from app.models import Referal, DAO
from flask import jsonify, request
from flask.views import MethodView

referal_dao = DAO(Referal())

@bp.route('/referals/<int:referal_id>', methods=['GET'])
def get_referal_details(referal_id):
    referal = referal_dao.find_one(referal_id)
    return jsonify(referal)

@bp.route('/referals', methods=['GET'])
def get_all_referals():
    args = request.args
    if not ('page' in args) and not ('per_page' in args):
        return jsonify({'error': 'invalid pagination data'})
    page = int(args['page'])
    per_page = int(args['per_page'])
    referals = referal_dao.find_all(page,per_page,'api.get_all_referals')
    return jsonify(referals)

@bp.route('/referals', methods=['POST'])
def save_referal_details():
    details = request.get_json(silent=False)
    new_referal = referal_dao.save(details)
    return jsonify(new_referal)

@bp.route('/referals/<int:referal_id>', methods=['DELETE'])
def delete_referal_details(referal_id):
    return "delete referal"

@bp.route('/referals/<int:referal_id>', methods=['PATCH'])
def update_referal_details(referal_id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = referal_id
    updated_referal = referal_dao.update(data)
    return jsonify(updated_referal)
