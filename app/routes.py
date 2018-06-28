from app import app
from app.models import PatientDetails, OperationRecord, PractitionerDetails

@app.route('/')
def index():
    return "hello, world"

@app.route('/patients/<int:patient_id>', methods=['GET'])
def get_patient_detail(patient_id):
    # find_patient(patient_id)
    pass

@app.route('/patients', methods=['GET'])
def get_all_patient_details():
    patient_obj = PatientDetails()
    # find_all_patients()
    pass

@app.route('/patients', methods=['POST'])
def save_patient_details():
    # save_details()
    pass

@app.route('/patients/<int:pr_id>', methods=['PATCH'])
def update_patient_details(pr_id):
    # update_patient()
    pass

@app.route('/patients/<int:pr_id>', methods=['DELETE'])
def delete_patient_record(pr_id):
    # delete_patient()
    pass

@app.route('/operations/<int:or_id>', methods=['GET'])
def get_operation_record(or_id):
    # get_one_record()
    pass

@app.route('/operations', methods=['GET'])
def get_operation_records():
    # get_all_records()
    pass

@app.route('/operations', methods=['POST'])
def create_operation_record():
    # save_record()
    pass

@app.route('/operations/<int:or_id>', methods=['PATCH'])
def update_operation_record(or_id):
    # update_record()
    pass

@app.route('/operations/<int:or_id>', methods=["DELETE"])
def delete_operation_record(or_id):
    # delete_record()
    pass
