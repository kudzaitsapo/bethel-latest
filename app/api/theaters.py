from app.api import bp, helpers
from app.models import Theater, DAO
from flask import jsonify, request
from flask.views import MethodView

theater_dao = DAO(Theater())

@bp.route('/theaters/<int:theater_id>', methods=['GET'])
def get_theater_details(theater_id):
    theater = theater_dao.find_one(theater_id)
    return jsonify(theater)

@bp.route('/theaters', methods=['GET'])
def get_all_theaters():
    args = request.args
    if not ('page' in args) and not ('per_page' in args):
        return jsonify({'error': 'invalid pagination data'})
    page = int(args['page'])
    per_page = int(args['per_page'])
    theaters = theater_dao.find_all(page,per_page,'api.get_all_theaters')
    return jsonify(theaters)

@bp.route('/theaters', methods=['POST'])
def save_theater_details():
    details = request.get_json(silent=False)
    new_theater = theater_dao.save(details)
    return jsonify(new_theater)

@bp.route('/theaters/<int:theater_id>', methods=['DELETE'])
def delete_theater_details(theater_id):
    return "delete theater"

@bp.route('/theaters/<int:theater_id>', methods=['PATCH'])
def update_theater_details(theater_id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = theater_id
    updated_theater = theater_dao.update(data)
    return jsonify(updated_theater)
