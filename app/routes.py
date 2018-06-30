import urllib
from app import app
from app.models import PatientDetails, OperationRecord, PractitionerDetails
from flask import jsonify, request, url_for

def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

@app.route('/')
def index():
    return "hello, world"

@app.route("/site-map")
def site_map():
    links = []
    output = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)

        if "GET" in rule.methods and has_no_empty_params(rule):
            methods = ','.join(rule.methods)
            url = url_for(rule.endpoint, **options)
            links.append((url, rule.endpoint, methods))
            line = urllib.unquote("{:20s} {}".format(methods, url))
            output.append(line)
    # links is now a list of url, endpoint tuples
    return jsonify(output)


# @app.route('/operations/<int:operation_id>', methods=['GET'])
# def get_operation_record(operation_id):
#     operation_obj = OperationRecord()
#     record = operation_obj.find_one(operation_id)
#     return jsonify(record)
#
# @app.route('/operations', methods=['GET'])
# def get_operation_records():
#     args = request.args
#     if ('page' in args) and ('per_page' in args):
#         page = int(args['page'])
#         per_page = int(args['per_page'])
#     else:
#         return jsonify({'error': 'invalid pagination data'})
#     operation_obj = OperationRecord()
#     operations = operation_obj.find_all(page,per_page,'get_operation_records')
#     return jsonify(operations)
#     return jsonify({'error': 'invalid pagination data'})
#
# @app.route('/operations', methods=['POST'])
# def save_operation_record():
#     details = request.get_json(silent=False)
#     if any(details):
#         patient_obj = OperationRecord()
#         new_operation = patient_obj.save(details['operation_data'])
#         return jsonify(new_operation)
#     else:
#         return jsonify({'error': 'operation data cannot be empty'})
#
# @app.route('/operations/<int:operation_id>', methods=['PATCH'])
# def update_operation_record(operation_id):
#     # update_record()
#     pass
#     # data = request.get_json(silent=False)
#     # if 'id' not in data:
#     #     data["id"] = operation_id
#     # if get_operation_record(patient_id):
#     #     patient_obj = PatientDetails()
#     #     updated_patient = patient_obj.update(data)
#     #     return jsonify(updated_patient)
#
# @app.route('/operations/<int:operation_id>', methods=["DELETE"])
# def delete_operation_record(operation_id):
#     return jsonify({"error": "not allowed"})
