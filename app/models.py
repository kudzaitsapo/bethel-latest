from app import db
from app.search import add_to_index, remove_form_index, query_index
from flask import url_for, abort
from dateutil import parser
from datetime import datetime

class DAO(object):

    def __init__(self, object):
        self.model = object

    def find_one(self, id):
        return self.model.query.get_or_404(id).to_dict()

    def find_all(self, page, per_page, endpoint, **kwargs):
        return self.model.to_collection_dict(self.model.query, page, per_page, endpoint, **kwargs)

    def find_relations(self, query, page, per_page, endpoint, **kwargs):
        return self.model.to_collection_dict(query, page, per_page, endpoint, **kwargs)

    def save(self, data):
        try:
            self.model = self.model.from_dict(data)
            db.session.add(self.model)
            db.session.commit()
            return self.model.to_dict()
        except:
            db.session.rollback()
            abort(400)


    def save_or_update_list(self, data):
        saved = []
        try:
            for item in data['items']:
                if 'id' not in reading:
                    new_item = self.model.commit(item)
                    saved.append(new_item)
                else:
                    item = self.model.update(item)
                    saved.append(item)
            return saved
        except:
            db.session.rollback()
            abort(400)


    def commit(self, data):
        model_obj = self.model.from_dict(data)
        db.session.add(model_obj)
        db.session.commit()
        return model_obj.to_dict()

    def update_list(self, data):
        model_obj = self.model.query.get_or_404(data['id'])
        model_obj = model_obj.from_dict(data)
        db.session.commit()
        return model_obj.to_dict()

    def update(self, data):
        try:
            if data['id'] is not '':
                print(data['id'])
                self.model = self.model.query.get_or_404(data['id'])
                print(data['id'])
                self.model = self.model.from_dict(data)
                db.session.commit()
                return self.model.to_dict()
            else:
                db.session.rollback()
                return {'message': 'ID cannot be empty.'}
        except:
            db.session.rollback()
            abort(400)

    def delete(self, data):
        abort(400)


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filer(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(sessiom.dirty),
            'delete': list(session.delete)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_form_index(obj.__tablename__, obj)
        session_changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

# db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
# db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


class PaginateAPI(object):

    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        if resources.total == 0:
            abort(404)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        if len(data['items']) == 0:
            return {'error': 'page {} out of bound'.format(page)}
        return data


surgical_team = db.Table('surgical_team',
                         db.Column('practitioner_id', db.Integer,
                                   db.ForeignKey('practitioner_details.id'),
                                   primary_key=True),
                         db.Column('operation_id', db.Integer,
                                   db.ForeignKey('operation_record.id'),
                                   primary_key=True)
                         )


class Prescription(PaginateAPI, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ordered_by = db.Column(
        db.Integer, db.ForeignKey('practitioner_details.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_details.id'))
    details = db.Column(db.Text)

    def __repr__(self):
        return '<Prescription {}>'.format(self.id)

    def to_dict(self, load_links=True):
        data = {
            'id': self.id,
            'ordered_by': PractitionerDetails.query.get(self.ordered_by).to_dict(load_links=False),
            'patient_id': PatientDetails.query.get(self.patient_id).to_dict(load_links=False),
            'details': self.details
        }
        if load_links:
            data['_links'] = {
                'self': url_for('api.get_prescription_details', id=self.id),
                'ordered_by': url_for('api.get_practitioner_details', id=self.ordered_by),
                'patient': url_for('api.get_patient_details', id=self.patient_id)
            }
        return data

    def from_dict(self, data):
        for field in ['ordered_by', 'patient_id', 'details']:
            if field in data:
                setattr(self, field, data[field])
        return self


class Referal(PaginateAPI, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    referer_id = db.Column(
        db.Integer, db.ForeignKey('practitioner_details.id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_details.id'))
    note = db.Column(db.Text)

    def __repr__(self):
        return '<Referal {}>'.format(self.id)

    def to_dict(self, load_links=True):
        data = {
            'id': self.id,
            # 'referer_id': PractitionerDetails.query.get(self.referer_id).to_dict(load_links=False),
            # 'patient_id': PatientDetails.query.get(self.patient_id).to_dict(load_links=False),
            'note': self.note
        }
        if load_links:
            data['_links'] = {
                'self': url_for('api.get_referal_details', id=self.id)
                # 'referred_by': url_for('api.get_practitioner_details', id=self.referer_id),
                # 'patient':url_for('api.get_patient_details', id=self.patient_id)
            }
        return data

    def from_dict(self, data):
        for field in ['referer_id', 'patient_id', 'note']:
            if field in data:
                setattr(self, field, data[field])
        return self


class PractitionerDetails(PaginateAPI, db.Model):
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
    surguries = db.relationship(
        'OperationRecord', secondary=surgical_team,
        lazy='dynamic', backref=db.backref('surgeries', lazy='dynamic'))

    def __repr__(self):
        return '<Practitioner {}>'.format(self.id)

    def to_dict(self, load_links=True):
        data = {
            'id': self.id,
            'first_names': self.first_names,
            'surname': self.surname,
            'gender': self.gender,
            'occupation': Occupation.query.get(self.occupation_id).to_dict(load_links=False) if self.occupation_id else None,
            'phone': self.phone,
            'address': self.address,
            'patients_dosed': self.doses.count(),
            'no_operations': self.surguries.count()
        }
        if load_links:
            data['_links'] = {
                'self': url_for('api.get_practitioner_details', id=self.id),
                'occupation': url_for('api.get_occupation_details', id=self.occupation_id) if self.occupation_id else None,
                'referrees': url_for('api.get_practitioner_referrees',  id=self.id),
                'prescriptions': url_for('api.get_practitioner_prescriptions', id=self.id),
                'surgeries': url_for('api.get_practitioner_operations', id=self.id),
                'patients_dosed': url_for('api.get_practitioner_doses', id=self.id) if (self.doses.count() > 0) else None,
                'operations_perfomed': url_for('api.get_practitioner_operations',id=self.id) if (self.surguries.count() > 0) else None
            }
        return data

    def from_dict(self, data):
        for field in ['first_names', 'surname', 'gender', 'phone', 'address']:
            if field in data:
                setattr(self, field, data[field])
            return self


class Occupation(PaginateAPI, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), unique=True)
    practitioners = db.relationship(
        'PractitionerDetails', backref='qualification', lazy='dynamic')

    def __repr__(self):
        return '<Occupation {}>'.format(self.tittle)

    def to_dict(self, load_links=True):
        data = {
            'id': self.id,
            'title': self.title
        }
        if load_links:
            data['_links'] = {
                'self': url_for('api.get_occupation_details', id=self.id),
                'practitioners': url_for('api.get_occupation_practitioners', id=self.id) if (self.practitioners.count() > 0) else None
            }
        return data

    def from_dict(self, data):
        if 'title' in data:
            setattr(self, title, data['title'])
        return self


class Hospital(PaginateAPI, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    wards = db.relationship('Ward', backref='hospital', lazy='dynamic')

    def __repr__(self):
        return '<Hospital {}>'.format(self.name)

    def to_dict(self, load_links=True):
        data = {
            'id': self.id,
            'name': self.name
        }
        if load_links:
            data['_links'] = {
                'self': url_for('api.get_hospital_details', id=self.id),
                'wards': url_for('api.get_hospital_wards', id=self.id) if (self.wards.count() > 0) else None
            }
        return data

    def from_dict(self, data):
        if 'name' in data:
            setattr(self, name, data['name'])
        return self


class Ward(PaginateAPI, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital.id'), nullable=False)
    theaters = db.relationship('Theater', backref='ward', lazy='dynamic')

    def __repr__(slef):
        return '<Ward {}>'.format(self.name)

    def to_dict(self, load_links=True):
        data = {
            'id': self.id,
            'title': self.name,
            'hospital': hospital.query.get(self.hospital_id).to_dict(load_links=False)
        }
        if load_links:
            data['_links'] = {
                'self': url_for('api.get_ward_details', id=self.id),
                'hospital': url_for('api.get_hospital_details', id=self.hospital_id),
                'theaters': url_for('api.get_ward_theaters', id=self.id) if (self.theaters.count() > 0) else None
            }
        return data

    def from_dict(self, data):
        if 'title' in data:
            setattr(self, name, data['name'])
        return self


class Theater(PaginateAPI, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    ward_id = db.Column(db.Integer, db.ForeignKey('ward.id'), nullable=False)
    operations = db.relationship(
        'OperationRecord', backref='Theater', lazy='dynamic')

    def __repr__(self):
        return '<Theater {}>'.format(self.name)

    def to_dict(self, load_links=True):
        data = {
            'id': self.id,
            'title': self.name,
            'ward': Ward.query.get(self.ward_id).to_dict(load_links=False)
        }
        if load_links:
            data['_links'] = {
                'self': url_for('api.get_theater_details', id=self.id),
                'ward': url_for('api.get_ward_details', id=self.ward_id),
                'operations': url_for('api.get_theater_operations', id=self.id) if (self.operations.count() > 0) else None
            }
        return data

    def from_dict(self, data):
        if 'title' in data:
            setattr(self, name, data['name'])
        return self


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

    def to_dict(self, load_links=True):
        data = {
            'id': self.id,
            'national_id': self.national_id,
            'first_names': self.first_names,
            'surname': self.surname,
            'gender': self.gender,
            'address': self.address,
            'phone': self.phone,
            'operations': self.operation_records.count(),
            'prescriptions': self.medication.count()
        }
        if load_links:
            data['_links'] = {
                'self': url_for('api.get_patient_details', id=self.id),
                'operation_records': url_for('api.get_patient_operations', id=self.id) if (self.operation_records.count() > 0) else None,
                'prescriptions': url_for('api.get_patient_prescriptions', id=self.id) if (self.medication.count() > 0) else None
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


class OperationRecord(SearchableMixin, PaginateAPI, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient_details.id'), nullable=False)
    reference_id = db.Column(db.Integer, db.ForeignKey('referal.id'), nullable=False)
    theater_id = db.Column(db.Integer, db.ForeignKey('theater.id'), nullable=False)
    name = db.Column(db.String(100))
    date = db.Column(db.Date)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    pre_operative_record_id = db.Column(
        db.Integer, db.ForeignKey('pre_operative_record.id'), nullable=False)
    operative_record_id = db.Column(
        db.Integer, db.ForeignKey('operative_record.id'), nullable=False)
    post_operative_record_id = db.Column(
        db.Integer, db.ForeignKey('post_operative_record.id'), nullable=False)
    anaesthetic_id = db.Column(db.Integer, db.ForeignKey('anaesthetic.id'), default=None)
    vitals = db.relationship(
        'VitalsRecord', backref='operation', lazy='dynamic')
    surgical_team = db.relationship(
        'PractitionerDetails', secondary=surgical_team,
        lazy='dynamic', backref=db.backref('surgeries', lazy='subquery'))

    def __repr__(self):
        return '<operation_record {}>'.format(self.id)

    def add_team(self, operation_id, team):
        for practitioner in team:
            if not (practitioner in self.surgical_team):
                self.surgical_team.append(practitioner)
            else:
                pass

    def find_one(self, operation_record_id):
        return self.query.get_or_404(operation_record_id).to_dict()

    def find_all(self, page, per_page, endpoint, **kwargs):
        return self.to_collection_dict(self.query, page, per_page, endpoint, **kwargs)

    def delete_record(self):
        return {'error': 'Prohibited!'}

    def to_dict(self, load_links=True):
        # print(self.patient_id)
        data = {
            'id': self.id,
            'patient': PatientDetails.query.get(self.patient_id).to_dict(load_links=False),
            'referal': Referal.query.get(self.reference_id).to_dict(load_links=False),
            # 'theater_id': Theater.query.get(self.theater_id).to_dict(load_links=False),
            'name': self.name,
            'date': self.date,
            'start_time': str(self.start_time),
            'end_time': str(self.end_time),
            'pre_operative_record': PreOperativeRecord.query.get(self.pre_operative_record_id).to_dict(load_links=False),
            'operative_record': OperativeRecord.query.get(self.operative_record_id).to_dict(load_links=False),
            'post_operative_record': PostOperativeRecord.query.get(self.post_operative_record_id).to_dict(load_links=False) ,
            'anaesthetic': Anaesthetic.query.get(self.anaesthetic_id).to_dict(load_links=False)
        }
        if load_links:
            data['_links'] = {
                'self': url_for('api.get_operation_record_details', id=self.id),
                'vitals': url_for('api.get_operation_vitals', id=self.id),
                'surgical_team': url_for('api.get_operation_surgical_team', id=self.id),
                'theater': url_for('api.get_theater_details', id=self.theater_id),
                'patient': url_for('api.get_patient_details', id=self.patient_id),
                'anaesthetic': url_for('api.get_anaesthetic_details', id=self.anaesthetic_id),
                'operative_record': url_for('api.get_operative_record_details', id=self.operative_record_id),
                'post_operative_record': url_for('api.get_post_operative_record_details', id=self.post_operative_record_id),
                'pre_operative_record': url_for('api.get_preoperative_record_details', id=self.pre_operative_record_id),
                'reference': url_for('api.get_referal_details', id=self.reference_id)
            }
        return data

    def from_dict(self, data):
        for field in [
            'patient_id', 'reference_id', 'theater_id', 'date', 'name',
            'start_time', 'end_time', 'pre_operative_record_id',
            'operative_record_id', 'post_operative_record_id',
            'anaesthetic_id'
        ]:
            if field in data:
                if (field is 'start_time') or (field is 'end_time'):
                    date = parser.parse(data[field])
                    time = datetime.time(date)
                    setattr(self, field, time)
                elif (field is 'date'):
                    date = parser.parse(data[field])
                    setattr(self, field, date)
                else:
                    setattr(self, field, data[field])
        return self


class PreOperativeRecord(PaginateAPI, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mass = db.Column(db.String)
    temperature = db.Column(db.String)
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

    def to_dict(self, load_links=True):
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
            'drug_therapy': self.drug_therapy
        }
        if load_links:
            data['_links'] = {
                'self': url_for('api.get_preoperative_record_details', id=self.id),
                'attachments': url_for('api.get_preoperative_records_attachments', id=self.id),
                'premedication': url_for('api.get_preoperative_records_premedication', id=self.id),
                'operation': url_for('api.get_operation_record_details',id=OperationRecord.query.filter_by(pre_operative_record_id=self.id).first().id)
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


class Attachment(PaginateAPI, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(120))
    file_type = db.Column(db.String(6))
    pre_operative_record_id = db.Column(
        db.Integer, db.ForeignKey('pre_operative_record.id'))

    def __repr__(self):
        return '<Attachments {}>'.format(self.id)

    def to_dict(self, load_links=True):
        data = {
            'id': self.id,
            'url': self.url,
            'file_type': self.file_type
        }
        if load_links:
            data['_links'] = {
                'self': url_for('api.get_attachments_details', id=self.id),
                'pre_operative_record': url_for('api.get_preoperative_record_details', id=self.pre_operative_record_id)
            }
        return data

    def from_dict(self, data):
        for field in ['url', 'file_type', 'pre_operative_record_id']:
            if field in data:
                setattr(self, field, data[field])
        return self


class PremedicationRecord(PaginateAPI, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('prescription.id'))
    time_given = db.Column(db.Time)
    given_by = db.Column(db.Integer, db.ForeignKey('practitioner_details.id'))
    pre_operative_record_id = db.Column(
        db.Integer, db.ForeignKey('pre_operative_record.id'))

    def __repr__(self):
        return '<Premedication {}>'.format(self.id)

    def to_dict(self, load_links=True):
        data = {
            'id': self.id,
            'prescription': Prescription.query.get(self.prescription_id).to_dict(load_links=False) if self.prescription_id else None,
            'time_given': str(self.time_given),
            'given_by': self.given_by
        }
        if load_links:
            data['_links'] = {
                'self': url_for('api.get_premedication_record_details', id=self.id),
                'pre_operative_record': url_for('api.get_preoperative_record_details', id=self.pre_operative_record_id),
                'prescription': url_for('api.get_prescription_details', id=self.prescription_id) if self.prescription_id else None
            }
        return data

    def from_dict(self, data):
        for field in ['prescription_id', 'time_given', 'given_by', 'pre_operative_record_id']:
            if field in data:
                if field is 'time_given':
                    date = parser.parse(data[field])
                    time = datetime.time(date)
                    setattr(self, field, time)
                else:
                    setattr(self, field, data[field])
        return self


class Anaesthetic(PaginateAPI, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    drug_id = db.Column(db.Integer, db.ForeignKey('drug.id'))
    technique_id = db.Column(db.Integer, db.ForeignKey('technique.id'))

    def __repr__(self):
        return '<Anaesthetic {}>'.format(self.id)

    def to_dict(self, load_links=True):
        data = {
            'id': self.id,
            'start_time': str(self.start_time),
            'end_time': str(self.end_time),
            # 'drug': Drug.query.get(self.drug_id).to_dict(load_links=False),
            # 'technique': Technique.query.get(self.technique_id).to_dict(load_links=False),
            'operation': url_for('api.get_operation_record_details',id=OperationRecord.query.filter_by(anaesthetic_id=self.id).first().id)
        }
        if load_links:
            data['_links'] = {
                'self': url_for('api.get_anaesthetic_details', id=self.id)
                # 'drug' : url_for('api.get_drug_details', id=self.drug_id),
                # 'technique': url_for('api.get_technique_details', id=self.technique_id)
            }
        return data

    def from_dict(self, data):
        for field in ['start_time', 'end_time', 'drug_id', 'technique_id']:
            if field in data:
                if (field is 'start_time') or (field is 'end_time'):
                    date = parser.parse(data[field])
                    time = datetime.time(date)
                    setattr(self, field, time)
                else:
                    setattr(self, field, data[field])
        return self


class Drug(PaginateAPI, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    anaesthetics = db.relationship(
        'Anaesthetic', backref='drug', lazy='dynamic')

    def __repr__(self):
        return '<Drug {}>'.format(self.name)

    def to_dict(self, load_links=True):
        data = {
            'id': self.id,
            'name': self.name,
            'anaesthetics': self.anaesthetics.count()
        }
        if load_links:
            data['_links'] =  {
                'self': url_for('api.get_drug_details', id=self.id),
                'anaesthetics': url_for('api.get_drugs_anaesthetics', id=self.id) if (self.anaesthetics.count() > 0) else None
            }

    def from_dict(self, data):
        if 'name' in data:
            setattr(self, name, data['name'])
        return self


class Technique(PaginateAPI, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    description = db.Column(db.String(64))
    anaesthetic_id = db.relationship(
        'Anaesthetic', backref='technique', lazy='dynamic')

    def __repr__(self):
        return '<Technique {}>'.format(self.name)

    def to_dict(self, load_links=True):
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }
        if load_links:
            data['_links'] = {
                'self': url_for('api.get_technique_details', id=self.id),
                'anaesthetics': url_for('api.get_techniques_anaesthetics', id=self.id) if (self.anaesthetic_id.count() > 0) else None
            }
        return data

    def from_dict(self, data):
        for field in ['name', 'description']:
            if field in data:
                setattr(self, field, data[field])
        return self


class PostOperativeRecord(PaginateAPI, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instructions_to_ward = db.Column(db.String)
    iv_therapy = db.Column(db.String)
    sedation = db.Column(db.String)
    complications = db.Column(db.String)

    def __repr__(self):
        return '<PostOperativeRecord {}>'.format(self.id)

    def to_dict(self, load_links=True):
        data = {
            'id': self.id,
            'instructions_to_ward': self.instructions_to_ward,
            'iv_therapy': self.iv_therapy,
            'sedation': self.sedation,
            'complications': self.complications
        }
        if load_links:
            data['_links'] = {
                'self': url_for('api.get_post_operative_record_details', id=self.id),
                'operation': url_for('api.get_operation_record_details',id=OperationRecord.query.filter_by(post_operative_record_id=self.id).first().id)
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


class VitalsRecord(PaginateAPI, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    heart_rate = db.Column(db.String)
    oxygen = db.Column(db.String)
    blood_pressure = db.Column(db.String)
    time = db.Column(db.Time)
    operation_record_id = db.Column(db.Integer, db.ForeignKey('operation_record.id'))

    def __repr__(self):
        return '<Vitals {}>'.format(self.id)

    def to_dict(self, load_links=True):
        data = {
            'id': self.id,
            'heart_rate': self.heart_rate,
            'oxygen': self.oxygen,
            'blood_pressure': self.blood_pressure,
            'time': str(self.time),
            'operation_record_id': self.operation_record_id
        }
        if load_links:
            data['_links'] = {
                'self': url_for('api.get_vitals_record_details', id=self.id),
                'operation': url_for('api.get_operation_record_details', id=self.operation_record_id)
            }
        return data

    def from_dict(self, data):
        for field in [
            'heart_rate', 'oxygen', 'time',
            'blood_pressure', 'operation_record_id'
        ]:
            if field in data:
                if field is 'time':
                    date = parser.parse(data[field])
                    time = datetime.time(date)
                    setattr(self, field, time)
                else:
                    setattr(self, field, data[field])
        return self


class OperativeRecord(PaginateAPI, db.Model):
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

    def to_dict(self, load_links=True):
        data = {
            'id': self.id,
            'posture': self.posture,
            'iv_therapy': self.iv_therapy,
            'skin': self.skin,
            'color': self.color,
            'reflexes': self.reflexes,
            'blood_pressure': self.blood_pressure,
            'pulse_rate': self.pulse_rate,
            'abnormal_reactions': self.abnormal_reactions
        }
        if load_links:
            data['_links'] = {
                'self': url_for('api.get_operative_record_details', id=self.id),
                'operation': url_for('api.get_operation_record_details',id=OperationRecord.query.filter_by(operative_record_id=self.id).first().id)
            }
        return data

    def from_dict(self, data):
        for field in [
            'posture', 'iv_therapy',
            'skin', 'color', 'reflexes', 'blood_pressure',
            'pulse_rate', 'abnormal_reactions'
        ]:
            if field in data:
                setattr(self, field, data[field])
        return self
