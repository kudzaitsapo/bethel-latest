from app.api import bp, helpers
from app.models import Theater, DAO
from flask import jsonify, request
from flask.views import MethodView

theater_dao = DAO(Theater())

@bp.route('/theaters/<int:id>', methods=['GET'])
def get_theater_details(id):
    theater = theater_dao.find_one(id)
    return jsonify(theater)

@bp.route('/theaters', methods=['GET'])
def get_all_theaters():
    args = request.args
    page, per_page = helpers.paginate(args)
    theaters = theater_dao.find_all(page,per_page,'api.get_all_theaters')
    return jsonify(theaters)

@bp.route('/theaters', methods=['POST'])
def save_theater_details():
    details = request.get_json(silent=False)
    new_theater = theater_dao.save(details)
    return jsonify(new_theater)

@bp.route('/theaters/<int:id>', methods=['DELETE'])
def delete_theater_details(id):
    return "delete theater"

@bp.route('/theaters/<int:id>', methods=['PATCH'])
def update_theater_details(id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = id
    updated_theater = theater_dao.update(data)
    return jsonify(updated_theater)

@bp.route('/theaters/<int:id>/operations', methods=['GET'])
def get_theater_operations(id):
    theater = Theater.query.get_or_404(id)
    args = request.args
    page, per_page = helpers.paginate(args)
    operations = theater_dao.find_relations(theater.operations,page,per_page,'api.get_theater_operations', id=id)
    return jsonify(operations)
