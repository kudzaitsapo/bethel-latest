from app.api import bp, helpers
from app.models import Attachment, DAO
from flask import jsonify, request
from flask.views import MethodView

attachments_dao = Attachment()

@bp.route('/attachments/<int:id>', methods=['GET'])
def get_attachments_details(id):
    attachments = attachments_dao.find_one(id)
    return jsonify(attachments)

@bp.route('/attachments', methods=['GET'])
def get_all_attachments():
    args = request.args
    page, per_page = helpers.paginate(args)
    attachmentss = attachments_dao.find_all(page,per_page,'api.get_all_attachments')
    return jsonify(attachmentss)

@bp.route('/attachments', methods=['POST'])
def save_attachments_details():
    details = request.get_json(silent=False)
    new_attachments = attachments_dao.save(details)
    return jsonify(new_attachments)

@bp.route('/attachments/<int:id>', methods=['DELETE'])
def delete_attachments_details(id):
    return "delete attachments"

@bp.route('/attachments/<int:id>', methods=['PATCH'])
def update_attachments_details(id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = id
    updated_attachments = attachments_dao.update(data)
    return jsonify(updated_attachments)
