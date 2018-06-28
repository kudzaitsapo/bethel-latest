from app import db
from flask import url_for


class PaginateAPI(object):

    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            # '_links': {
            #     'self': url_for(endpoint, page=page, per_page=per_page,
            #                     **kwargs),
            #     'next': url_for(endpoint, page=page + 1, per_page=per_page,
            #                     **kwargs) if resources.has_next else None,
            #     'prev': url_for(endpoint, page=page - 1, per_page=per_page,
            #                     **kwargs) if resources.has_prev else None
            # }
        }
        if len(data['items']) == 0:
            return {'error': 'page {} out of bound'.format(page)}
        return data

'''
    __TODO_
    ** add __deletion__ funtionality
'''

surgical_team = db.Table('surgical_team',
                         db.Column('practioner_id', db.Integer,
                                   db.ForeignKey('practitioner_details.id'),
                                   primary_key=True),
                         db.Column('operation_id', db.Integer,
                                   db.ForeignKey('operation_record.id'),
                                   primary_key=True)
                         )


class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ordered_by = db.Column(
        db.Integer, db.ForeignKey('practitioner_details.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_details.id'))
    details = db.Column(db.Text)

    def __repr__(self):
        return '<Prescription {}>'.format(self.id)

    def save(self, data):
        self = self.from_dict(data)
        db.session.add(self)
        db.session.commit()
        return self.to_dict()

    def update(self, data):
        if 'id' in data:
            self = self.query.get_or_404(data['id'])
            self = self.from_dict(data)
            db.session.commit()
        else:
            return {'error': 'id connot be null'}
        return self.to_dict()

    def to_dict(self):
        data = {
            'id': self.id,
            'ordered_by': self.ordered_by,
            'patient_id': self.patient_id,
            'details': self.details
        }
        return data

    def from_dict(self, data):
        for field in ['ordered_by', 'patient_id', 'details']:
            if field in data:
                setattr(self, field, data[field])
        return self


class Referal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    referer_id = db.Column(
        db.Integer, db.ForeignKey('practitioner_details.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_details.id'))
    note = db.Column(db.Text)

    def save(self, data):
        self = self.from_dict(data)
        db.session.add(self)
        db.session.commit()
        return self.to_dict()

    def update(self, data):
        if 'id' in data:
            self = self.query.get_or_404(data['id'])
            self = self.from_dict(data)
            db.session.commit()
        else:
            return {'error': 'id connot be null'}
        return self.to_dict()

    def to_dict(self):
        data = {
            'id': self.id,
            'referer_id': self.referer_id,
            'patient_id': self.patient_id,
            'note': self.note
        }
        return data

    def from_dict(self, data):
        for field in ['referer_id', 'patient_id', 'note']:
            if field in data:
                setattr(self, field, data[field])
        return self


class PractitionerDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_names = db.Column(db.String(64))
    surname = db.Column(db.String(64), index=True)
    gender = db.Column(db.String(1))
    phone = db.Column(db.String(20), unique=True)
    address = db.Column(db.String(64))
    occupation_id = db.Column(db.Integer, db.ForeignKey('occupation.id'))
    referrees = db.relationship('Referal', lazy='dynamic', backref='referals')
    prescriptions = db.relationship(
        'Prescription', lazy='dynamic', backref='prescriptions')
    doses = db.relation('PremedicationRecord', lazy='dynamic', backref='doses')

    def __repr__(self):
        return '<Practitioner {}>'.format(self.id)

    def to_dict(self):
        data = {
            'id': self.id,
            'first_names': self.first_names,
            'surname': self.surname,
            'gender': self.gender,
            # 'occupatoin': self.occupatoin,
            'phone': self.phone,
            'address': self.address,
            '_links': {
                'self': url_for('app.get_practioner', id=self.id)
            }
        }
        return data

    def from_dict(self, data):
        for field in ['first_names', 'surname', 'gender', 'phone', 'address']:
            if field in data:
                setattr(self, field, data[field])
            return self

    def refere(self, patient_details):
        self.referals.append(patient_details)


class Occupation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), unique=True)
    practioners = db.relationship(
        'PractitionerDetails', backref='qualification', lazy='dynamic')

    def __repr__(self):
        return '<Occupation {}>'.format(self.tittle)

    def to_dict(self):
        data = {
            'id': self.id,
            'title': self.title,
            '_links': {
                'self': url_for('app.get_occupation', id=self.id)
            }
        }

    def from_dict(self, data):
        if 'title' in data:
            setattr(self, title, data['title'])


class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    wards = db.relationship('Ward', backref='hospital', lazy='dynamic')

    def __repr__(self):
        return '<Hospital {}>'.format(self.name)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            '_links': {
                'self': url_for('app.get_hospital', id=self.id)
            }
        }

    def from_dict(self, data):
        if 'name' in data:
            setattr(self, name, data['name'])


class Ward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'))
    theaters = db.relationship('Theater', backref='ward', lazy='dynamic')

    def __repr__(slef):
        return '<Ward {}>'.format(self.name)

    def to_dict(self):
        data = {
            'id': self.id,
            'title': self.name,
            '_links': {
                'self': url_for('app.get_ward', id=self.id)
            }
        }

    def from_dict(self, data):
        if 'title' in data:
            setattr(self, name, data['name'])


class Theater(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    ward_id = db.Column(db.Integer, db.ForeignKey('ward.id'))
    operations = db.relationship(
        'OperationRecord', backref='Theater', lazy='dynamic')

    def __repr__(self):
        return '<Theater {}>'.format(self.name)

    def to_dict(self):
        data = {
            'id': self.id,
            'title': self.name,
            '_links': {
                'self': url_for('app.get_theater', id=self.id)
            }
        }

    def from_dict(self, data):
        if 'title' in data:
            setattr(self, name, data['name'])


class PatientDetails(PaginateAPI, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    national_id = db.Column(db.String(30),
                            unique=True, index=True, nullable=False)
    first_names = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    gender = db.Column(db.String(1))
    address = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    operation_records = db.relationship(
        'OperationRecord', backref='patient', lazy='dynamic')
    medication = db.relationship(
        'Prescription', lazy='dynamic', backref='medication')

    def __repr__(self):
        return '<Patient {}>'.format(self.national_id)

    def find_one(self, patient_id):
        return self.query.get_or_404(patient_id).to_dict()

    def find_all(self, page, per_page, endpoint, **kwargs):
        return self.to_collection_dict(self.query, page, per_page, endpoint, **kwargs)

    def save(self, data):
        # try:
        if data['national_id'] is not None:
            self = self.from_dict(data)
            db.session.add(self)
            db.session.commit()
            return self.to_dict()
        # except: # add exception to error
        #     return {'message': 'oops failed to save patient details.'}

    def update(self, data):
        # try:
        if 'id' in data:
            if data['id'] is not '':
                self = self.query.get_or_404(data['id'])
                self = self.from_dict(data)
                db.session.commit()
            else:
                return {'message': 'Patient ID cannot be empty.'}
            return self.to_dict()
        else:
            return {'message': 'Patient ID must be provided.'}
        # except:# add exception to error
        #     return {'message': 'Oops failed to update patient details.'}

    def delete(self, data):
        return {'error': 'Prohibited!'}

    def to_dict(self):
        # 'national_id' if 'national_id' in kwargs: self.national_id
        data = {
            'id': self.id,
            'national_id': self.national_id,
            'first_names': self.first_names,
            'surname': self.surname,
            'gender': self.gender,
            'address': self.address,
            'phone': self.phone,
            '_links': {
                # 'self': url_for('app.get_patient_record', id=self.id)
                # 'operatoin_records': url_for('app.get_operation_records', patient_id=self.id),
                # 'medication': url_for('app.get_medications', patient_id=self.id)
            }
        }
        return data

    def from_dict(self, data):
        for field in [
            'national_id', 'first_names',
            'surname', 'gender', 'phone', 'address'
        ]:
            if field in data:
                setattr(self, field, data[field])
        return self


class OperationRecord(PaginateAPI, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_details.id'))
    reference_id = db.Column(db.Integer, db.ForeignKey('referal.id'))
    theater_id = db.Column(db.Integer, db.ForeignKey('theater.id'))
    date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    pre_operative_record_id = db.Column(
        db.Integer, db.ForeignKey('pre_operative_record.id'))
    operative_record_id = db.Column(
        db.Integer, db.ForeignKey('operative_record.id'))
    post_operative_record_id = db.Column(
        db.Integer, db.ForeignKey('post_operative_record.id'))
    anaesthetic_id = db.Column(db.Integer, db.ForeignKey('anaesthetic.id'))
    vitals = db.relationship(
        'VitalsRecord', backref='operation', lazy='dynamic')
    surgical_team = db.relationship(
        'PractitionerDetails', secondary=surgical_team,
        lazy='dynamic', backref=db.backref('surgeries', lazy='subquery'))

    def __repr__(self):
        return '<operation_record {}>'.format(self.id)

    def add_team(self, operation_id, team):
        for practioner in team:
            if not (practioner in self.surgical_team):
                self.surgical_team.append(practioner)
            else:
                pass

    def find_one(self, operation_record_id):
        return self.query.get_or_404(operation_record_id).to_dict()

    def find_all(self, page, per_page, endpoint, **kwargs):
        return self.to_collection_dict(self.query, page, per_page, endpoint, **kwargs)

    def save(self, data):

        if 'patient_id' not in data:
            patient_details_obj = PatientDetails()
            patient = patient_details_obj.save(
                data['patient_details_data'])
            data['patient_id'] = patient['id']

        if 'reference_id' not in data:
            referal_obj = Referal()
            reference = referal_obj.save(data['referal_data'])
            data['reference_id'] = reference['id']

        if 'pre_operative_record_id' not in data:
            pre_operative_record_obj = PreOperativeRecord()
            record = pre_operative_record_obj.save(data['pre_operative_data'])
            data['pre_operative_record_id'] = record['id']

            if 'attachment_data' in data['pre_operative_data']:
                attachment_data = data['pre_operative_data']['attachment_data']
                attachment_data['pre_operative_record_id'] = record['id']
                attachment_obj = Attachment()
                file_record = attachment_obj.save(attachment_data)

            if 'premedication_data' in data['pre_operative_data']:
                premedication_data = data[
                    'pre_operative_data']['premedication_data']
                premedication_data['pre_operative_record_id'] = record['id']
                premedication_record_obj = PremedicationRecord()
                premedication = premedication_record_obj.save(
                    premedication_data)

        if 'operative_record_id' not in data:
            operative_record_obj = OperativeRecord()
            record = operative_record_obj.save(data['operative_data'])
            data['operative_record_id'] = record['id']

        if 'anaesthetic_id' not in data:
            anaesthetic_obj = Anaesthetic()
            anaesthetic = anaesthetic_obj.save(data['anaesthetic_data'])
            data['anaesthetic_id'] = anaesthetic['id']

        if 'post_operative_record_id' not in data:
            post_operative_record_obj = PostOperativeRecord()
            record = post_operative_record_obj.save(
                data['post_operative_data'])
            data['post_operative_record_id'] = record['id']
        # try:
        self = self.from_dict(data)
        db.session.add(self)
        db.session.commit()
        vitals_data = data['vitals_data']
        vitals_data['operation_record_id'] = self.id
        vitals_record_obj = VitalsRecord()
        vitals = vitals_record_obj.save(vitals_data)
        surgical_team_data = data['surgical_team']
        self.add_team(self.id, surgical_team_data)
        return self.to_dict()
        # except: # add exception to error
        #     return {'message': 'oops failed to save operation record'}

    def update(self, data):
        if 'id' in data:
            if 'patient_details_data' in data:
                patient_details_obj = PatientDetails()
                patient_details_obj.update(
                    data['patient_details_data'])
            if 'referal_data' in data:
                referal_obj = Referal()
                reference = referal_obj.update(
                    data['referal_data'])
                data['reference_id'] = reference['id']
            if 'pre_operative_data' in data:
                pre_operative_record_obj = PreOperativeRecord()
                record = pre_operative_record_obj.update(
                    data['pre_operative_data'])
                data['pre_operative_record_id'] = record['id']
            if 'operative_data' in data:
                operative_record_obj = OperativeRecord()
                record = operative_record_obj.update(
                    data['operative_data'])
                data['operative_record_id'] = record['id']
            if 'post_operative_data' in data:
                post_operative_record_obj = PostOperativeRecord()
                record = post_operative_record_obj.update(
                    data['post_operative_data'])
                data['post_operative_record_id'] = record['id']
            if 'anaesthetic_data' in data:
                anaesthetic_obj = Anaesthetic()
                anaesthetic = anaesthetic_obj.update(
                    data['anaesthetic_data'])
                data['anaesthetic_id'] = anaesthetic['id']
            if 'vitals_data' in data:
                vitals_data = data['vitals_data']
                vitals_data['operation_record_id'] = data['id']
                vitals_record_obj = VitalsRecord()
                vitals = vitals_record_obj.save(
                    vitals_data)
            self = self.query.get_or_404(data['id'])
            self = self.from_dict(data)
            db.session.commit()
            if 'surgical_team' in data:
                surgical_team_data = data['surgical_team']
                self.add_team(self.id, surgical_team_data)
            return self.to_dict()
        else:
            return {'error': 'id cannot be empty'}

    def delete_record(self):
        return {'error': 'Prohibited!'}

    def to_dict(self):
        pd = PatientDetails()
        data = {
            'id': self.id,
            'patient_id': self.patient_id,
            'reference_id': self.reference_id,
            'theater_id': self.theater_id,
            'date': self.date,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'pre_operative_record_id': self.pre_operative_record_id,
            'operative_record_id': self.operative_record_id,
            'post_operative_record_id': self.post_operative_record_id,
            'anaesthetic_id': self.anaesthetic_id,
            '_links': {
                # 'self': url_for('app.get_operation_record', id=self.id)
            }
        }
        return data

    def from_dict(self, data):
        for field in [
            'patient_id', 'reference_id', 'theater_id', 'date',
            'start_time', 'end_time', 'pre_operative_record_id',
            'operative_record_id', 'post_operative_record_id',
            'anaesthetic_id'
        ]:
            if field in data:
                setattr(self, field, data[field])
        return self


class PreOperativeRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mass = db.Column(db.Float)
    temperature = db.Column(db.Float)
    pulse = db.Column(db.String)
    respiration = db.Column(db.String)
    respiratory_system = db.Column(db.String)
    cadiovascular_system = db.Column(db.String)
    urine = db.Column(db.String)
    blood_group = db.Column(db.String)
    blood_pressure = db.Column(db.String)
    haemoglobin = db.Column(db.String)
    blood_urea = db.Column(db.String)
    drug_therapy = db.Column(db.String)
    attachments = db.relationship(
        'Attachment', backref='preoperative_record', lazy='dynamic')
    premedication = db.relationship(
        'PremedicationRecord', backref='preoperative_record', lazy='dynamic')

    def __repr__(self):
        return '<preoperative_record {}>'.format(self.id)

    def save(self, data):
        # try:
        self = self.from_dict(data)
        db.session.add(self)
        db.session.commit()
        return self.to_dict()
        # except: # add exception to error
        #     return {'message': 'oops failed to save referal record'}

    def update(self, data):
        if 'id' in data:
            if 'attachment_data' in data:
                attachment_obj = Attachment()
                attachment = attachment_obj.update(
                    data['attachment_data'])
            if 'premedication_data' in data:
                premedication_record_obj = PremedicationRecord()
                record = premedication_record_obj.update(
                    data['premedication_data'])
            self = self.query.get_or_404(data['id'])
            self = self.from_dict(data)
            db.session.commit()
        else:
            return {'error': 'id connot be null'}
        return self.to_dict()

    def to_dict(self):
        data = {
            'id': self.id,
            'mass': self.mass,
            'temperature': self.temperature,
            'pulse': self.pulse,
            'respiration': self.respiration,
            'respiratory_system': self.respiratory_system,
            'cadiovascular_system': self.cadiovascular_system,
            'urine': self.urine,
            'blood_group': self.blood_group,
            'blood_pressure': self.blood_pressure,
            'haemoglobin': self.haemoglobin,
            'blood_urea': self.blood_urea,
            'blood_pressure': self.blood_pressure,
            'drug_therapy': self.drug_therapy,
            '_links': {
                # 'self': url_for('app.get_operation_record', id=self.id)
            }
        }
        return data

    def from_dict(self, data):
        for field in [
            'mass', 'temperature', 'pulse', 'respiration',
            'respiratory_system', 'cadiovascular_system',
            'urine', 'blood_group', 'blood_pressure',
            'haemoglobin', 'blood_urea', 'blood_pressure',
            'drug_therapy'
        ]:
            if field in data:
                setattr(self, field, data[field])
        return self


class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(120))
    file_type = db.Column(db.String(6))
    pre_operative_record_id = db.Column(
        db.Integer, db.ForeignKey('pre_operative_record.id'))

    def __repr__(self):
        return '<Attachments {}>'.format(self.id)

    def save(self, data):
        self = self.from_dict(data)
        db.session.add(self)
        db.session.commit()
        return self.to_dict()

    def update(self, data):
        if 'id' in data:
            self = self.query.get_or_404(data['id'])
            self = self.from_dict(data)
            db.session.commit()
        else:
            return {'error': 'id connot be null'}
        return self.to_dict()

    def to_dict(self):
        data = {
            'id': self.id,
            'url': self.url,
            'file_type': self.file_type,
            'pre_operative_record_id': self.pre_operative_record_id
            # '_links': {
            #     # 'self': url_for('app.get_operation_record', id=self.id)
            # }
        }
        return data

    def from_dict(self, data):
        for field in ['url', 'file_type', 'pre_operative_record_id']:
            if field in data:
                setattr(self, field, data[field])
        return self


class PremedicationRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescription.id'))
    time_given = db.Column(db.Time)
    given_by = db.Column(db.Integer, db.ForeignKey('practitioner_details.id'))
    pre_operative_record_id = db.Column(
        db.Integer, db.ForeignKey('pre_operative_record.id'))

    def __repr__(self):
        return '<Premedication {}>'.format(self.id)

    def save(self, data):
        # Save prescription
        if 'prescription_data' in data:
            prescription_data = data['prescription_data']
            prescription_obj = Prescription()
            prescription = prescription_obj.save(prescription_data)
            data['prescription_id'] = prescription['id']
        self = self.from_dict(data)
        db.session.add(self)
        db.session.commit()
        return self.to_dict()

    def update(self, data):
        if 'id' in data:
            if 'prescription_data' in data:
                prescription_obj = Prescription()
                prescription = prescription_obj.update(data['prescription_data'])
                data['prescription_id'] = prescription['id']
            self = self.query.get_or_404(data['id'])
            self = self.from_dict(data)
            db.session.commit()
        else:
            return {'error': 'id connot be null'}
        return self.to_dict()

    def to_dict(self):
        data = {
            'id': self.id,
            'prescription_id': self.prescription_id,
            'time_given': self.time_given,
            'given_by': self.given_by,
            'pre_operative_record_id': self.pre_operative_record_id
            # '_links': {
            #     # 'self': url_for('app.get_operation_record', id=self.id)
            # }
        }
        return data

    def from_dict(self, data):
        for field in ['prescription_id', 'time_given', 'given_by', 'pre_operative_record_id']:
            if field in data:
                setattr(self, field, data[field])
        return self


class Anaesthetic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    drug_id = db.Column(db.Integer, db.ForeignKey('drug.id'))
    technique_id = db.Column(db.Integer, db.ForeignKey('technique.id'))

    def __repr__(self):
        return '<Anaesthetic {}>'.format(self.id)

    def save(self, data):
        # try:
        self = self.from_dict(data)
        db.session.add(self)
        db.session.commit()
        return self.to_dict()
        # except: # add exception to error
        #     return {'message': 'oops failed to save referal record'}

    def update(self, data):
        if 'id' in data:
            self = self.query.get_or_404(data['id'])
            self = self.from_dict(data)
            db.session.commit()
        else:
            return {'error': 'id connot be null'}
        return self.to_dict()

    def to_dict(self):
        data = {
            'id': self.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'drug_id': self.drug_id,
            'technique_id': self.technique_id,
            # '_links': {
            #     # 'self': url_for('app.get_operation_record', id=self.id)
            # }
        }
        return data

    def from_dict(self, data):
        for field in ['start_time', 'end_time', 'end_time', 'technique_id']:
            if field in data:
                setattr(self, field, data[field])
        return self


class Drug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    anaesthetics = db.relationship(
        'Anaesthetic', backref='drug', lazy='dynamic')

    def __repr__(self):
        return '<Drug {}>'.format(self.name)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.anaesthetist,
            '_links': {
                # 'self': url_for('app.get_operation_record', id=self.id)
            }
        }

    def from_dict(self, data):
        if 'name' in data:
            setattr(self, name, data['name'])


class Technique(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(64))
    anaesthetic_id = db.relationship(
        'Anaesthetic', backref='technique', lazy='dynamic')

    def __repr__(self):
        return '<Technique {}>'.format(self.name)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            '_links': {
                # 'self': url_for('app.get_operation_record', id=self.id)
            }
        }

    def from_dict(self, data):
        for field in ['name', 'description']:
            if field in data:
                setattr(self, field, data[field])


class PostOperativeRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instructions_to_ward = db.Column(db.String)
    iv_therapy = db.Column(db.String)
    sedation = db.Column(db.String)
    complications = db.Column(db.String)

    def __repr__(self):
        return '<PostOperativeRecord {}>'.format(self.id)

    def save(self, data):
        # try:
        self = self.from_dict(data)
        db.session.add(self)
        db.session.commit()
        return self.to_dict()
        # except: # add exception to error
        #     return {'message': 'oops failed to save referal record'}

    def update(self, data):
        if 'id' in data:
            self = self.query.get_or_404(data['id'])
            self = self.from_dict(data)
            db.session.commit()
        else:
            return {'error': 'id connot be null'}
        return self.to_dict()

    def to_dict(self):
        data = {
            'id': self.id,
            'instructions_to_ward': self.instructions_to_ward,
            'iv_therapy': self.iv_therapy,
            'sedation': self.sedation,
            'complications': self.complications,
            # '_links': {
            #     # 'self': url_for('app.get_operation_record', id=self.id)
            # }
        }
        return data

    def from_dict(self, data):
        for field in [
            'instructions_to_ward', 'iv_therapy', 'sedation',
            'complications'
        ]:
            if field in data:
                setattr(self, field, data[field])
        return self


class VitalsRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    heart_rate = db.Column(db.String)
    oxygen = db.Column(db.String)
    blood_pressure = db.Column(db.String)
    time = db.Column(db.Time)
    operation_record_id = db.Column(db.Integer, db.ForeignKey('operation_record.id'))

    def __repr__(self):
        return '<Vitals {}>'.format(self.id)

    def save(self, data):
        saved = []
        for reading in data['readings']:
            reading['operation_record_id'] = data['operation_record_id']
            if 'id' not in reading:
                vital_reading = self.commit(reading)
                saved.append(vital_reading)
            else:
                vital_reading = self.update(reading)
                saved.append(vital_reading)
        # print(saved)
        return saved

    def commit(self, data):
        vital_obj = VitalsRecord()
        vital_obj = vital_obj.from_dict(data)
        db.session.add(vital_obj)
        db.session.commit()
        return vital_obj.to_dict()

    def update(self, data):
        vital_obj = VitalsRecord()
        vital_obj = vital_obj.query.get_or_404(data['id'])
        vital_obj = vital_obj.from_dict(data)
        db.session.commit()
        return vital_obj.to_dict()

    def to_dict(self):
        data = {
            'id': self.id,
            'heart_rate': self.heart_rate,
            'oxygen': self.oxygen,
            'blood_pressure': self.blood_pressure,
            'time': self.time,
            'operation_record_id': self.operation_record_id
            # '_links': {
            #     # 'self': url_for('app.get_operation_record', id=self.id)
            # }
        }
        return data

    def from_dict(self, data):
        for field in [
            'heart_rate', 'oxygen', 'time',
            'blood_pressure', 'operation_record_id'
        ]:
            if field in data:
                setattr(self, field, data[field])
        return self


class OperativeRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    posture = db.Column(db.String)
    iv_therapy = db.Column(db.String)
    skin = db.Column(db.String)
    color = db.Column(db.String)
    reflexes = db.Column(db.String)
    blood_pressure = db.Column(db.String)
    pulse_rate = db.Column(db.String)
    abnormal_reactions = db.Column(db.String)

    def __repr__(self):
        return '<OperativeRecord {}>'.format(self.id)

    def save(self, data):
        # try:
        self = self.from_dict(data)
        db.session.add(self)
        db.session.commit()
        return self.to_dict()
        # except: # add exception to error
        #     return {'message': 'oops failed to save referal record'}

    def update(self, data):
        if 'id' in data:
            self = self.query.get_or_404(data['id'])
            self = self.from_dict(data)
            db.session.commit()
        else:
            return {'error': 'id connot be null'}
        return self.to_dict()

    def to_dict(self):
        data = {
            'id': self.id,
            'anaesthetic': self.anaesthetic,
            'posture': self.posture,
            'iv_therapy': self.iv_therapy,
            'skin': self.skin,
            'color': self.color,
            'reflexes': self.reflexes,
            'blood_pressure': self.blood_pressure,
            'pulse_rate': self.pulse_rate,
            'abnormal_reactions': self.abnormal_reactions
            # '_links': {
            #     # 'self': url_for('app.get_operation_record', id=self.id)
            # }
        }
        return data

    def from_dict(self, data):
        for field in [
            'anaesthetic', 'posture', 'iv_therapy',
            'skin', 'color', 'reflexes', 'blood_pressure',
            'pulse_rate', 'abnormal_reactions'
        ]:
            if field in data:
                setattr(self, field, data[field])
        return self
