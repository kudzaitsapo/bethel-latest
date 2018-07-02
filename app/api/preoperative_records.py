from app.api import bp, helpers
from app.models import PreOperativeRecord, DAO
from flask import jsonify, request
from flask.views import MethodView

preoperative_record_dao = DAO(PreOperativeRecord())

@bp.route('/preoperative-records/<int:id>', methods=['GET'])
def get_preoperative_record_details(id):
    preoperative_record = preoperative_record_dao.find_one(id)
    return jsonify(preoperative_record)

@bp.route('/preoperative-records', methods=['GET'])
def get_all_preoperative_records():
    args = request.args
    page, per_page = helpers.paginate(args)
    preoperative_records = preoperative_record_dao.find_all(page,per_page,'api.get_all_preoperative_records')
    return jsonify(preoperative_records)

@bp.route('/preoperative-records', methods=['POST'])
def save_preoperative_record_details():
    details = request.get_json(silent=False)
    new_preoperative_record = preoperative_record_dao.save(details)
    return jsonify(new_preoperative_record)

@bp.route('/preoperative-records/<int:id>', methods=['DELETE'])
def delete_preoperative_record_details(id):
    return "delete preoperative_record"

@bp.route('/preoperative-records/<int:id>', methods=['PATCH'])
def update_preoperative_record_details(id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = id
    updated_preoperative_record = preoperative_record_dao.update(data)
    return jsonify(updated_preoperative_record)

@bp.route('/preoperative-records/<int:id>/attachments', methods=['GET'])
def get_preoperative_records_attachments(id):
    pre_operative_record = PreOperativeRecord.query.get_or_404(id)
    args = request.args
    page, per_page = helpers.paginate(args)
    attachments = preoperative_record_dao.find_relations(pre_operative_record.attachments,page,per_page,'api.get_preoperative_records_attachments', id=id)
    return jsonify(attachments)

@bp.route('/preoperative-records/<int:id>/premedication', methods=['GET'])
def get_preoperative_records_premedication(id):
    pre_operative_record = PreOperativeRecord.query.get_or_404(id)
    args = request.args
    page, per_page = helpers.paginate(args)
    premedication = preoperative_record_dao.find_relations(pre_operative_record.premedication,page,per_page,'api.get_preoperative_records_premedication', id=id)
    return jsonify(premedication)
