from app.api import bp
from app.models import OperationRecord, DAO
from flask import jsonify, request

operation_dao = DAO(OperationRecord())

@bp.route('/operations/<int:operation_id>', methods=['GET'])
def get_operation_record(operation_id):
    operation_dao = OperationRecord()
    record = operation_dao.find_one(operation_id)
    return jsonify(record)

@bp.route('/operations', methods=['GET'])
def get_operation_records():
    args = request.args
    if ('page' in args) and ('per_page' in args):
        page = int(args['page'])
        per_page = int(args['per_page'])
    else:
        return jsonify({'error': 'invalid pagination data'})
    operation_dao = OperationRecord()
    operations = operation_dao.find_all(page,per_page,'get_operation_records')
    return jsonify(operations)
    return jsonify({'error': 'invalid pagination data'})

@bp.route('/operations', methods=['POST'])
def save_operation_record():
    details = request.get_json(silent=False)
    if any(details):
        patient_obj = OperationRecord()
        new_operation = patient_obj.save(details['operation_data'])
        return jsonify(new_operation)
    else:
        return jsonify({'error': 'operation data cannot be empty'})

@bp.route('/operations/<int:operation_id>', methods=['PATCH'])
def update_operation_record(operation_id):
    # update_record()
    pass
    # data = request.get_json(silent=False)
    # if 'id' not in data:
    #     data["id"] = operation_id
    # if get_operation_record(patient_id):
    #     patient_obj = PatientDetails()
    #     updated_patient = patient_obj.update(data)
    #     return jsonify(updated_patient)

@bp.route('/operations/<int:operation_id>', methods=["DELETE"])
def delete_operation_record(operation_id):
    return jsonify({"error": "not allowed"})
