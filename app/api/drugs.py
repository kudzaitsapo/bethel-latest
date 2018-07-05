from app.api import bp, helpers, cache
from app.models import Drug, DAO
from flask import jsonify, request
from flask.views import MethodView

drug_dao = DAO(Drug())

@bp.route('/drugs/<int:id>', methods=['GET'])
def get_drug_details(id):
    path = request.path
    cached = cache.redis.get(path)
    if not cached:
        drug = drug_dao.find_one(id)
        cache.set_url_cache(path, drug)
        return jsonify(drug)
    else:
        return jsonify(cache.get_url_cache(cached))

@bp.route('/drugs', methods=['GET'])
def get_all_drugs():
    args = request.args
    page, per_page = helpers.paginate(args)
    drugs = drug_dao.find_all(page,per_page,'api.get_all_drugs')
    return jsonify(drugs)

@bp.route('/drugs', methods=['POST'])
def save_drug_details():
    details = request.get_json(silent=False)
    new_drug = drug_dao.save(details)
    path = new_drug['_links']['self']
    cache.set_url_cache(path, new_drug)
    return jsonify(new_drug)

@bp.route('/drugs/<int:id>', methods=['DELETE'])
def delete_drug_details(id):
    return "delete drug"

@bp.route('/drugs/<int:id>', methods=['PATCH'])
def update_drug_details(id):
    path = request.path
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = id
    updated_drug = drug_dao.update(data)
    cache.set_url_cache(path, updated_drug)
    return jsonify(updated_drug)

@bp.route('/drugs/<int:id>/anaesthetics', methods=['GET'])
def get_drugs_anaesthetics(id):
    drug = Drug.query.get_or_404(id)
    args = request.args
    page, per_page = helpers.paginate(args)
    anaesthetics = drug_dao.find_relations(drug.anaesthetics,page,per_page,'api.get_drugs_anaesthetics', id=id)
    return jsonify(anaesthetics)
