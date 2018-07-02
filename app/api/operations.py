from app.api import bp, helpers
from app.models import OperationRecord, PatientDetails, Referal, \
                    PreOperativeRecord, Attachment, PremedicationRecord, \
                    OperationRecord, Anaesthetic, PostOperativeRecord, \
                    VitalsRecord, OperativeRecord, DAO
from flask import jsonify, request, redirect, url_for

operation_dao = DAO(OperationRecord())

@bp.route('/operations/<int:id>', methods=['GET'])
def get_operation_record_details(id):
    operation_dao = OperationRecord()
    record = operation_dao.find_one(id)
    return jsonify(record)

@bp.route('/operations', methods=['GET'])
def get_all_operation_records():
    args = request.args
    page, per_page = helpers.paginate(args)
    operations = operation_dao.find_all(page,per_page,'api.get_all_operation_records')
    return jsonify(operations)
    return jsonify({'error': 'invalid pagination data'})

@bp.route('/operations', methods=['POST'])
def save_operation_record():
    data = request.get_json(silent=False)
    if 'operation_data' in data:
        data = data['operation_data']
        if 'patient_id' not in data:
            patient_dao = DAO(PatientDetails())
            data['patient_id'] = patient_dao.save(data['patient_details_data'])['id']
        if 'reference_id' not in data:
            referal_obj = DAO(Referal())
            data['reference_id'] = referal_obj.save(data['referal_data'])['id']
        if 'pre_operative_record_id' not in data:
            pre_operative_data = data['pre_operative_data']
            pre_operative_record_obj = DAO(PreOperativeRecord())
            data['pre_operative_record_id'] = pre_operative_record_obj.save(pre_operative_data)['id']
            if 'attachment_data' in pre_operative_data:
                attachment_data = pre_operative_data['attachment_data']
                attachment_data['pre_operative_record_id'] = data['pre_operative_record_id']
                attachment_obj = DAO(Attachment())
                file_record = attachment_obj.save_or_update_list(attachment_data,  data['pre_operative_record_id'])
            if 'premedication_data' in data['pre_operative_data']:
                premedication_data = pre_operative_data['premedication_data']
                if 'prescription_data' in premedication_data:
                    prescription_data = premedication_data['prescription_data']
                    prescription_obj = DAO(Prescription())
                    prescription = prescription_obj.save(prescription_data)
                    premedication_data['prescription_id'] = prescription['id']
                premedication_data['pre_operative_record_id'] = data['pre_operative_record_id']
                premedication_record_obj = DAO(PremedicationRecord())
                premedication = premedication_record_obj.save(premedication_data)


        if 'operative_record_id' not in data:
            operative_record_obj = DAO(OperativeRecord())
            data['operative_record_id'] = operative_record_obj.save(data['operative_data'])['id']
        if 'anaesthetic_id' not in data:
            anaesthetic_obj = DAO(Anaesthetic())
            data['anaesthetic_id'] = anaesthetic_obj.save(data['anaesthetic_data'])['id']
        if 'post_operative_record_id' not in data:
            post_operative_record_obj = DAO(PostOperativeRecord())
            data['post_operative_record_id'] = post_operative_record_obj.save(
                data['post_operative_data'])['id']
        new_operation = operation_dao.save(data)
        if 'vitals_data' in data:
            vitals_data = data['vitals_data']
            vital_data['operation_id'] = new_operation['id']
            vitals_record_obj = VitalsRecord()
            vitals = vitals_record_obj.save_or_update_list(vitals_data)
        if 'surgical_team' in data:
            operation_dao.find_one(new_operation['id'])
            surgical_team_data = data['surgical_team']
            operation_dao.add_team(operation_dao.id, surgical_team_data)
            new_operation = operation_dao.to_dict()
        return jsonify(new_operation)
    else:
        return jsonify({'error': 'operation data cannot be empty'})

@bp.route('/operations/<int:id>', methods=['PATCH'])
def update_operation_record(id):
    data = request.get_json(silent=False)
    data = data['operation_data']
    if 'id' not in data:
        return jsonify({'message': 'operation id cannot be empty'})
    if 'patient_details_data' in data:
        patient_details_data = data['patient_details_data']
        if 'id' not in patient_details_data:
            return jsonify({'message': 'patient id cannot be empty'})
        patient_details_obj = DAO(PatientDetails())
        patient_details_obj.update(patient_details_data)
    if 'referal_data' in data:
        referal_obj = DAO(Referal())
        reference_data = data['referal_data']
        if 'id' not in reference_data:
            data['reference_id'] = referal_obj.save(reference_data)['id']
        else:
            referal_obj.update(reference_data)
    if 'pre_operative_data' in data:
        pre_operative_record_obj = DAO(PreOperativeRecord())
        pre_operative_data = data['pre_operative_data']
        if 'id' not in pre_operative_data:
            data['pre_operative_record_id'] = pre_operative_record_obj.save(pre_operative_data)['id']
            if 'attachment_data' in pre_operative_data:
                attachment_data = pre_operative_data['attachment_data']
                attachment_data['pre_operative_record_id'] = pre_operative_data['id']
                attachment_obj = DAO(Attachment())
                if 'id' not in attachment_data:
                    attachment_obj.save_or_update_list(attachment_data)
                else:
                    attachment_obj.save_or_update_list(attachment_data)
            if 'premedication_data' in pre_operative_data:
                premedication_data = pre_operative_data['premedication_data']
                if 'prescription_data' in premedication_data:
                    prescription_data = premedication_data['prescription_data']
                    prescription_dao = DAO(Prescription())
                    if 'id' not in prescription_data:
                        prescription = prescription_dao.save(prescription_data)
                        premedication_data['prescription_id'] = prescription['id']
                    else:
                        prescription_dao.update(prescription_data)
                premedication_data['pre_operative_record_id'] = pre_operative_data['id']
                premedication_record_obj = DAO(PremedicationRecord())
                if 'id' not in premedication_data:
                    premedication_record_obj.save(attachment_data)
                else:
                    attachment_obj.update(attachment_data)
        else:
            pre_operative_record_obj.update(pre_operative_data)
    if 'operative_data' in data:
        operative_record_obj = DAO(OperativeRecord())
        operative_data = data['operative_data']
        if 'id' not in operative_data:
            data['operative_record_id'] = operative_record_obj.save(operative_data)['id']
        else:
            operative_record_obj.update(data['operative_data'])
    if 'post_operative_data' in data:
        post_operative_record_obj = DAO(PostOperativeRecord())
        post_operative_data = data['post_operative_data']
        if 'id' not in post_operative_data:
            data['post_operative_record_id'] = post_operative_record_obj.save(post_operative_data)['id']
        else:
            post_operative_record_obj.update(post_operative_data)
    if 'anaesthetic_data' in data:
        anaesthetic_obj = DAO(Anaesthetic())
        anaesthetic_data = data['anaesthetic_data']
        if 'id' not in anaesthetic_data:
            data['anaesthetic_id'] = anaesthetic_obj.save(anaesthetic_data)['id']
        else:
            anaesthetic_obj.update(anaesthetic_data)
    if 'attachment_data' in data:
        attachment_dao = DAO(Attachment)
    if 'vitals_data' in data:
        vitals_data = data['vitals_data']
        vitals_record_obj = VitalsRecord()
        vitals_record_obj.save(vitals_data, data['id'])
    if 'surgical_team' in data:
        record = OperationRecord.query.get_or_404(data['id'])
        surgical_team_data = data['surgical_team']
        record.add_team(self.id, surgical_team_data)
    updated_record = operation_dao.update(data)
    return jsonify(updated_record)

@bp.route('/operations/<int:id>', methods=["DELETE"])
def delete_operation_record(id):
    return jsonify({"error": "not allowed"})

@bp.route('/operations/<int:id>/vitals', methods=['GET'])
def get_operation_vitals(id):
    operation_dao = DAO(OperationRecord())
    operation = OperationRecord.query.get_or_404(id)
    args = request.args
    page, per_page = helpers.paginate(args)
    vitals = operation_dao.find_relations(operation.vitals,page,per_page,'api.get_operation_vitals', id=id)
    return jsonify(vitals)

@bp.route('/operations/<int:id>/surgical-team', methods=['GET'])
def get_operation_surgical_team(id):
    operation_dao = DAO(OperationRecord())
    operation = OperationRecord.query.get_or_404(id)
    args = request.args
    page, per_page = helpers.paginate(args)
    team = operation_dao.find_relations(operation.surgical_team,page,per_page,'api.get_operation_surgical_team', id=id)
    return jsonify(team)
