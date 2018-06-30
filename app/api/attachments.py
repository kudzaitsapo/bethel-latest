from app.api import bp, helpers
from app.models import Attachment, DAO
from flask import jsonify, request
from flask.views import MethodView

attachments_dao = DAO(Attachment())

@bp.route('/attachmentss/<int:attachments_id>', methods=['GET'])
def get_attachments_details(attachments_id):
    attachments = attachments_dao.find_one(attachments_id)
    return jsonify(attachments)

@bp.route('/attachmentss', methods=['GET'])
def get_all_attachmentss():
    args = request.args
    if not ('page' in args) and not ('per_page' in args):
        return jsonify({'error': 'invalid pagination data'})
    page = int(args['page'])
    per_page = int(args['per_page'])
    attachmentss = attachments_dao.find_all(page,per_page,'api.get_all_attachmentss')
    return jsonify(attachmentss)

@bp.route('/attachmentss', methods=['POST'])
def save_attachments_details():
    details = request.get_json(silent=False)
    new_attachments = attachments_dao.save(details)
    return jsonify(new_attachments)

@bp.route('/attachmentss/<int:attachments_id>', methods=['DELETE'])
def delete_attachments_details(attachments_id):
    return "delete attachments"

@bp.route('/attachmentss/<int:attachments_id>', methods=['PATCH'])
def update_attachments_details(attachments_id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = attachments_id
    updated_attachments = attachments_dao.update(data)
    return jsonify(updated_attachments)
