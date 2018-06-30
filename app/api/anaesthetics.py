from app.api import bp
from app.models import Anaesthetic, DAO
from flask import jsonify, request

anaesthetic_dao = DAO(Anaesthetic())

@bp.route('/anaesthetics/<int:anaesthetic_id>', methods=['GET'])
def get_anaesthetic_details(anaesthetic_id):
    anaesthetic = anaesthetic_dao.find_one(anaesthetic_id)
    return jsonify(anaesthetic)

@bp.route('/anaesthetics', methods=['GET'])
def get_all_anaesthetics():
    args = request.args
    if not ('page' in args) and not ('per_page' in args):
        return jsonify({'error': 'invalid pagination data'})
    page = int(args['page'])
    per_page = int(args['per_page'])
    anaesthetics = anaesthetic_dao.find_all(page,per_page,'api.get_all_anaesthetics')
    return jsonify(anaesthetics)

@bp.route('/anaesthetics', methods=['POST'])
def save_anaesthetic_details():
    details = request.get_json(silent=False)
    new_anaesthetic = anaesthetic_dao.save(details)
    return jsonify(new_anaesthetic)

@bp.route('/anaesthetics/<int:anaesthetic_id>', methods=['DELETE'])
def delete_anaesthetic_details(anaesthetic_id):
    return "delete anaesthetic"

@bp.route('/anaesthetics/<int:anaesthetic_id>', methods=['PATCH'])
def update_anaesthetic_details(anaesthetic_id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = anaesthetic_id
    updated_anaesthetic = anaesthetic_dao.update(data)
    return jsonify(updated_anaesthetic)
