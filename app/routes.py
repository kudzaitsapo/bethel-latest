from app import app
from app.models import PatientDetails, OperationRecord, PractitionerDetails
from flask import jsonify, request

@app.route('/')
def index():
    return "hello, world"

@app.route('/patients/<int:patient_id>', methods=['GET'])
def get_patient_details(patient_id):
    patient_obj = PatientDetails()
    patient = patient_obj.find_one(patient_id)
    return jsonify(patient)

@app.route('/patients', methods=['GET'])
def get_all_patient_details():
    args = request.args
    if ('page' in args) and ('per_page' in args):
        page = int(args['page'])
        per_page = int(args['per_page'])
    else:
        return jsonify({'error': 'invalid pagination data'})
    patient_obj = PatientDetails()
    patients = patient_obj.find_all(page,per_page,'get_all_patient_details')
    return jsonify(patients)

@app.route('/patients', methods=['POST'])
def save_patient_details():
    details = request.get_json(silent=False)
    patient_obj = PatientDetails()
    new_patient = patient_obj.save(details)
    return jsonify(new_patient)

@app.route('/patients/<int:patient_id>', methods=['PATCH'])
def update_patient_details(patient_id):
    data = request.get_json(silent=False)
    if 'id' not in data:
        data["id"] = patient_id
    if get_patient_details(patient_id):
        patient_obj = PatientDetails()
        updated_patient = patient_obj.update(data)
        return jsonify(updated_patient)

@app.route('/patients/<int:pr_id>', methods=['DELETE'])
def delete_patient_record(pr_id):
    return jsonify({"error": "not allowed"})


@app.route('/operations/<int:operation_id>', methods=['GET'])
def get_operation_record(operation_id):
    operation_obj = OperationRecord()
    record = operation_obj.find_one(operation_id)
    return jsonify(record)

@app.route('/operations', methods=['GET'])
def get_operation_records():
    args = request.args
    if ('page' in args) and ('per_page' in args):
        page = int(args['page'])
        per_page = int(args['per_page'])
    else:
        return jsonify({'error': 'invalid pagination data'})
    operation_obj = OperationRecord()
    operations = operation_obj.find_all(page,per_page,'get_operation_records')
    return jsonify(operations)
    return jsonify({'error': 'invalid pagination data'})

@app.route('/operations', methods=['POST'])
def save_operation_record():
    details = request.get_json(silent=False)
    if any(details):
        patient_obj = OperationRecord()
        new_operation = patient_obj.save(details['operation_data'])
        return jsonify(new_operation)
    else:
        return jsonify({'error': 'operation data cannot be empty'})

@app.route('/operations/<int:operation_id>', methods=['PATCH'])
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

@app.route('/operations/<int:operation_id>', methods=["DELETE"])
def delete_operation_record(operation_id):
    return jsonify({"error": "not allowed"})
