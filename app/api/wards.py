from app.api import bp, helpers, cache
from app.models import Ward, DAO
from flask import jsonify, request

ward_dao = DAO(Ward())

@bp.route('/wards/<int:id>', methods=['GET'])
def get_ward_details(id):
    path = request.path
    cached = cache.redis.get(path)
    if not cached:
        ward = ward_dao.find_one(id)
        cache.set_url_cache(path, ward)
        return jsonify(ward)
    else:
        return jsonify(cache.get_url_cache(cached))

@bp.route('/wards', methods=['GET'])
def get_all_wards():
    args = request.args
    page, per_page = helpers.paginate(args)
    wards = ward_dao.find_all(page,per_page,'api.get_all_wards')
    return jsonify(wards)

@bp.route('/wards', methods=['POST'])
def save_ward_details():
    details = request.get_json(silent=False)
    new_ward = ward_dao.save(details)
    path = new_ward['_links']['self']
    cache.set_url_cache(path, new_ward)
    return jsonify(new_ward)

@bp.route('/wards/<int:id>', methods=['DELETE'])
def delete_ward_details(id):
    return "delete ward"

@bp.route('/wards/<int:id>', methods=['PATCH'])
def update_ward_details(id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = id
    updated_ward = ward_dao.update(data)
    cache.set_url_cache(path, updated_ward)
    return jsonify(updated_ward)

@bp.route('/wards/<int:id>/theaters', methods=['GET'])
def get_ward_theaters(id):
    ward = Ward.query.get_or_404(id)
    args = request.args
    page, per_page = helpers.paginate(args)
    theaters = patient_dao.find_relations(ward.theaters,page,per_page,'api.get_ward_theaters', id=id)
    return jsonify(theaters)
