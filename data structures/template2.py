from app.api import bp, helpers
from app.models import record, DAO
from flask import jsonify, request
from flask.views import MethodView

record_dao = DAO(record())

@bp.route('/records/<int:id>', methods=['GET'])
def get_record_details(id):
    record = record_dao.find_one(id)
    return jsonify(record)

@bp.route('/records', methods=['GET'])
def get_all_records():
    args = request.args
    page, per_page = helpers.paginate(args)
    records = record_dao.find_all(page,per_page,'api.get_all_records')
    return jsonify(records)

@bp.route('/records', methods=['POST'])
def save_record_details():
    details = request.get_json(silent=False)
    new_record = record_dao.save(details)
    return jsonify(new_record)

@bp.route('/records/<int:id>', methods=['DELETE'])
def delete_record_details(id):
    return "delete record"

@bp.route('/records/<int:id>', methods=['PATCH'])
def update_record_details(id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = id
    updated_record = record_dao.update(data)
    return jsonify(updated_record)

# relationship
@bp.route('/records/<int:id>/relationship', methods=['GET'])
def get_records_relationship(id):
    record = Record.query.get_or_404(id)
    args = request.args
    page, per_page = helpers.paginate(args)
    result = record_dao.find_relations(record.relationship,page,per_page,'api.get_records_relationship', id=id)
    return jsonify(result)
