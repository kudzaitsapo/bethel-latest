from app.api import bp, helpers
from app.models import Anaesthetic, DAO
from flask import jsonify, request

anaesthetic_dao = DAO(Anaesthetic())

@bp.route('/anaesthetics/<int:id>', methods=['GET'])
def get_anaesthetic_details(id):
    anaesthetic = anaesthetic_dao.find_one(id)
    return jsonify(anaesthetic)

@bp.route('/anaesthetics', methods=['GET'])
def get_all_anaesthetics():
    args = request.args
    page, per_page = helpers.paginate(args)
    anaesthetics = anaesthetic_dao.find_all(page,per_page,'api.get_all_anaesthetics')
    return jsonify(anaesthetics)

@bp.route('/anaesthetics', methods=['POST'])
def save_anaesthetic_details():
    details = request.get_json(silent=False)
    new_anaesthetic = anaesthetic_dao.save(details)
    return jsonify(new_anaesthetic)

@bp.route('/anaesthetics/<int:id>', methods=['DELETE'])
def delete_anaesthetic_details(id):
    return "delete anaesthetic"

@bp.route('/anaesthetics/<int:id>', methods=['PATCH'])
def update_anaesthetic_details(id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = id
    updated_anaesthetic = anaesthetic_dao.update(data)
    return jsonify(updated_anaesthetic)
