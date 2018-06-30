from app.api import bp
from app.models import PatientDetails, DAO
from flask import jsonify, request

patient_dao = DAO(PatientDetails())

@bp.route('/patients/<int:patient_id>', methods=['GET'])
def get_patient_details(patient_id):
    patient = patient_dao.find_one(patient_id)
    return jsonify(patient)

@bp.route('/patients', methods=['GET'])
def get_all_patient_details():
    args = request.args
    if not ('page' in args) and not ('per_page' in args):
        return jsonify({'error': 'invalid pagination data'})
    page = int(args['page'])
    per_page = int(args['per_page'])
    patients = patient_dao.find_all(page,per_page,'api.get_all_patient_details')
    return jsonify(patients)

@bp.route('/patients', methods=['POST'])
def save_patient_details():
    details = request.get_json(silent=False)
    new_patient = patient_dao.save(details)
    return jsonify(new_patient)

@bp.route('/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient_details(patient_id):
    # delete a single user
    return "delete patient"


@bp.route('/patients/<int:patient_id>', methods=['PATCH'])
def update_patient_details(patient_id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = patient_id
    updated_patient = patient_dao.update(data)
    return jsonify(updated_patient)
