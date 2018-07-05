from app.api import bp, helpers, cache
from app.models import PatientDetails, DAO
from flask import jsonify, request

patient_dao = DAO(PatientDetails())

@bp.route('/patients/<int:id>', methods=['GET'])
def get_patient_details(id):
    path = request.path
    cached = cache.redis.get(path)
    if not cached:
        patient = patient_dao.find_one(id)
        cache.set_url_cache(path, patient)
        return jsonify(patient)
    else:
        return jsonify(cache.get_url_cache(cached))

@bp.route('/patients', methods=['GET'])
def get_all_patient_details():
    args = request.args
    page, per_page = helpers.paginate(args)
    patients = patient_dao.find_all(page,per_page,'api.get_all_patient_details')
    return jsonify(patients)

@bp.route('/patients', methods=['POST'])
def save_patient_details():
    details = request.get_json(silent=False)
    new_patient = patient_dao.save(details)
    path = new_patient['_links']['self']
    cache.set_url_cache(path, new_patient)
    return jsonify(new_patient)

@bp.route('/patients/<int:id>', methods=['DELETE'])
def delete_patient_details(id):
    # delete a single user
    return "delete patient"

@bp.route('/patients/<int:id>', methods=['PATCH'])
def update_patient_details(id):
    path = request.path
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = id
    updated_patient = patient_dao.update(data)
    cache.set_url_cache(path, updated_patient)
    return jsonify(updated_patient)

@bp.route('/patients/<int:id>/operations', methods=['GET'])
def get_patient_operations(id):
    patient = PatientDetails.query.get_or_404(id)
    args = request.args
    page, per_page = helpers.paginate(args)
    operations = patient_dao.find_relations(patient.operation_records,page,per_page,'api.get_patient_operations', id=id)
    return jsonify(operations)

@bp.route('/patients/<int:id>/prescriptions', methods=['GET'])
def get_patient_prescriptions(id):
    patient = PatientDetails.query.get_or_404(id)
    args = request.args
    page, per_page = helpers.paginate(args)
    operations = patient_dao.find_relations(patient.medication,page,per_page,'api.get_patient_prescriptions', id=id)
    return jsonify(operations)
