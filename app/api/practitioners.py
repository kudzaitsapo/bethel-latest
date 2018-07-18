from app.api import bp, helpers, cache
from app.models import PractitionerDetails, DAO
from flask import jsonify, request
from flask.views import MethodView

practitioner_dao = DAO(PractitionerDetails())

@bp.route('/practitioners/<int:id>', methods=['GET'])
def get_practitioner_details(id):
    path = request.path
    cached = cache.redis.get(path)
    if not cached:
        practitioner = practitioner_dao.find_one(id)
        cache.set_url_cache(path, practitioner)
        return jsonify(practitioner)
    else:
        return jsonify(cache.get_url_cache(cached))

@bp.route('/practitioners', methods=['GET'])
def get_all_practitioners():
    args = request.args
    page, per_page = helpers.paginate(args)
    practitioners = practitioner_dao.find_all(page,per_page,'api.get_all_practitioners')
    return jsonify(practitioners)

@bp.route('/practitioners', methods=['POST'])
def save_practitioner_details():
    details = request.get_json(silent=False)
    new_practitioner = practitioner_dao.save(details)
    path = new_practitioner['_links']['self']
    cache.set_url_cache(path, new_practitioner)
    return jsonify(new_practitioner)

@bp.route('/practitioners/<int:id>', methods=['DELETE'])
def delete_practitioner_details(id):
    return "delete practitioner"

@bp.route('/practitioners/<int:id>', methods=['PATCH'])
def update_practitioner_details(id):
    path = request.path
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = id
    updated_practitioner = practitioner_dao.update(data)
    cache.set_url_cache(path, updated_practitioner)
    return jsonify(updated_practitioner)

@bp.route('/practitioners/<int:id>/patients', methods=['GET'])
def get_practitioner_referrees(id):
    # path = request.path
    # cached = redis.get(path)
    # if not cached:
    practitioner = PractitionerDetails.query.get_or_404(id)
    args = request.args
    page, per_page = helpers.paginate(args)
    referrees = practitioner_dao.find_relations(practitioner.referrees,page,per_page,'api.get_practitioner_referrees',id=id)
    return jsonify(referrees)

@bp.route('/practitioners/<int:id>/prescriptions', methods=['GET'])
def get_practitioner_prescriptions(id):
    practitioner = PractitionerDetails.query.get_or_404(id)
    args = request.args
    page, per_page = helpers.paginate(args)
    prescriptions = practitioner_dao.find_relations(practitioner.prescriptions,page,per_page,'api.get_practitioner_prescriptions', id=id)
    return jsonify(prescriptions)

@bp.route('/practitioners/<int:id>/operations', methods=['GET'])
def get_practitioner_operations(id):
    practitioner = PractitionerDetails.query.get_or_404(id)
    args = request.args
    page, per_page = helpers.paginate(args)
    operations = practitioner_dao.find_relations(practitioner.surguries,page,per_page,'api.get_practitioner_operations', id=id)
    return jsonify(operations)

@bp.route('/practitioners/<int:id>/doses', methods=['GET'])
def get_practitioner_doses(id):
    practitioner = PractitionerDetails.query.get_or_404(id)
    args = request.args
    page, per_page = helpers.paginate(args)
    doses = practitioner_dao.find_relations(practitioner.doses,page,per_page,'api.get_practitioner_doses', id=id)
    return jsonify(dosess)
