from app.api import bp, helpers
from app.models import PostOperativeRecord, DAO
from flask import jsonify, request
from flask.views import MethodView

post_operative_record_dao = DAO(PostOperativeRecord())

@bp.route('/post_operative_records/<int:post_operative_record_id>', methods=['GET'])
def get_post_operative_record_details(post_operative_record_id):
    post_operative_record = post_operative_record_dao.find_one(post_operative_record_id)
    return jsonify(post_operative_record)

@bp.route('/post_operative_records', methods=['GET'])
def get_all_post_operative_records():
    args = request.args
    if not ('page' in args) and not ('per_page' in args):
        return jsonify({'error': 'invalid pagination data'})
    page = int(args['page'])
    per_page = int(args['per_page'])
    post_operative_records = post_operative_record_dao.find_all(page,per_page,'api.get_all_post_operative_records')
    return jsonify(post_operative_records)

@bp.route('/post_operative_records', methods=['POST'])
def save_post_operative_record_details():
    details = request.get_json(silent=False)
    new_post_operative_record = post_operative_record_dao.save(details)
    return jsonify(new_post_operative_record)

@bp.route('/post_operative_records/<int:post_operative_record_id>', methods=['DELETE'])
def delete_post_operative_record_details(post_operative_record_id):
    return "delete post_operative_record"

@bp.route('/post_operative_records/<int:post_operative_record_id>', methods=['PATCH'])
def update_post_operative_record_details(post_operative_record_id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = post_operative_record_id
    updated_post_operative_record = post_operative_record_dao.update(data)
    return jsonify(updated_post_operative_record)
