from app.api import bp, helpers, cache
from app.models import Occupation, DAO
from flask import jsonify, request
from flask.views import MethodView

occupation_dao = DAO(Occupation())

@bp.route('/occupations/<int:id>', methods=['GET'])
def get_occupation_details(id):
    path = request.path
    cached = cache.redis.get(path)
    if not cached:
        occupation = occupation_dao.find_one(id)
        cache.set_url_cache(path, occupation)
        return jsonify(occupation)
    else:
        return jsonify(cache.get_url_cache(cached))

@bp.route('/occupations', methods=['GET'])
def get_all_occupations():
    args = request.args
    page, per_page = helpers.paginate(args)
    occupations = occupation_dao.find_all(page,per_page,'api.get_all_occupations')
    return jsonify(occupations)

@bp.route('/occupations', methods=['POST'])
def save_occupation_details():
    details = request.get_json(silent=False)
    new_occupation = occupation_dao.save(details)
    path = new_occupation['_links']['self']
    cache.set_url_cache(path, new_occupation)
    return jsonify(new_occupation)

@bp.route('/occupations/<int:id>', methods=['DELETE'])
def delete_occupation_details(id):
    return "delete occupation"

@bp.route('/occupations/<int:id>', methods=['PATCH'])
def update_occupation_details(id):
    path = request.path
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = id
    updated_occupation = occupation_dao.update(data)
    cache.set_url_cache(path, updated_practitioner)
    return jsonify(updated_occupation)

@bp.route('/occupations/<int:id>/practitioners', methods=['GET'])
def get_occupation_practitioners(id):
    occupation = Occupation.query.get_or_404(id)
    args = request.args
    page, per_page = helpers.paginate(args)
    practitioners = patient_dao.find_relations(occupation.practitioners,page,per_page,'api.get_occupation_practitioners', id=id)
    return jsonify(practitioners)
