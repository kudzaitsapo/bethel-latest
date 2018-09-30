"""
Last Updated: 30-07-2018 01:13 AM (DD-MM-YY HH:MM)
@Module: models.py v1
@Author: Shingai Shamu
@Description: This is a basic database model file to ensure the API is up and
              running until API v0 of the Bethel system is completed.
              This version also includes a database record for the
              Hospital Administrators responsible for managing Doctors on
              the app.
"""
from datetime import datetime
from sqlalchemy import Column
#from sqlalchemy import DateTime, Date, Time
from sqlalchemy import Boolean
from sqlalchemy import Integer
from sqlalchemy import String, Text
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr # see class Base for details
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
#from werkzeug.security import generate_password_hash, check_password_hash

try:
    db_engine = create_engine('postgres://postgres:password@localhost:5432/bethel')
except ImportError:
    db_engine = create_engine('sqlite:///test.sqlite')

# the Newer Stuff is just below this comment:

class Base(object):
    """
    this enables all shared database classes to have premade attributes and behaviour.
    In this case it was to auto generate the __tablename__ attribute ONLY.
    """
    @declared_attr
    def __tablename__(cls):
        """ autogenerates the __tablename__ attribute with the class name
        in lowercase.
        e.g 'class FooBar()' will have an __tablename__ == 'foobar' automatically.
        """
        return cls.__name__.lower()

Base = declarative_base(cls=Base)


class Admin(Base, UserMixin):
    """ The Medical Administrator in charge of managing medical practitioners"""
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String)
    password = Column(String)

    def __repr__(self):
        return "<Admin => {} username={}>".format(self.id, self.username)

    def check_password(self, plain_text):
        return check_password_hash(self.password, plain_text)


# slightly refactored v0 database models
class SurgicalTeam(Base):
    """
    maps medical practitioners to the operations they were
    involved in with a note, if any, of their participataion in the operation.
    """
    id = Column(Integer, primary_key=True)
    practitioner = Column(Integer, ForeignKey('practitionerdetails.id'))
    operation = Column(Integer, ForeignKey('operationrecord.id'))
    note = Column(String(100))


class Prescription(Base):
    """
    details the medical prescription given by a practitoner to
    a patient with a detailed description of the process and drugs used.
    """
    id = Column(Integer, primary_key=True)
    ordered_by = Column(Integer, ForeignKey('practitionerdetails.id'))
    patient_id = Column(Integer, ForeignKey('patientdetails.id'))
    details = Column(Text)

    def __repr__(self):
        return '<Prescription {}>'.format(self.id)


class Referal(Base):
    """
    records patients who have been refered to the hospital by a medical
    practitioner along with any notes, if any.
    """
    id = Column(Integer, primary_key=True)
    referer_id = Column(Integer, ForeignKey('practitionerdetails.id'))
    patient_id = Column(Integer, ForeignKey('patientdetails.id'))
    note = Column(Text)

    def __repr__(self):
        return '<Referal {}>'.format(self.id)


class PractitionerDetails(Base):
    """
    records all the medical practitioners in the hospital along with any details
    about their actions in referring, prescribing medication or surgeries done.
    """
    id = Column(Integer, primary_key=True)
    first_names = Column(String(64))
    surname = Column(String(64), index=True)
    gender = Column(String(1))
    phone = Column(String(20), unique=True)
    password = Column(String(120))
    address = Column(String(64))
    occupation_id = Column(Integer, ForeignKey('occupation.id'))
    referrees = relationship('Referal', lazy='dynamic', backref='referals')
    prescriptions = relationship('Prescription', lazy='dynamic', backref='prescriptions')
    doses = relationship('PremedicationRecord', lazy='dynamic', backref='doses')
    surgeries = relationship('OperationRecord', secondary='surgicalteam',
        lazy='dynamic', backref=backref('surgeries', lazy='dynamic'))

    def __repr__(self):
        return '<Practitioner {}>'.format(self.id)

    def check_password(self, plain_text):
        return check_password_hash(self.password, plain_text)


class Occupation(Base):
    """
    details occupation in the medical field currently done at the hospital and also lists
    practitioners engaged in the practice.
    """
    id = Column(Integer, primary_key=True)
    title = Column(String(20), unique=True)
    practitioners = relationship('PractitionerDetails', backref='qualification', lazy='dynamic')

    def __repr__(self):
        return '<Occupation {}>'.format(self.title)


class Hospital(Base):
    """ record of the hospitals currently on the system """
    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True, unique=True)
    wards = relationship('Ward', backref='hospital', lazy='dynamic')

    def __repr__(self):
        return '<Hospital {}>'.format(self.name)


class Ward(Base):
    """ records all the patient wards in a hospital along with theatres """
    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True)
    hospital_id = Column(Integer, ForeignKey('hospital.id'))
    theaters = relationship('Theater', backref='ward', lazy='dynamic')

    def __repr__(self):
        return '<Ward {}>'.format(self.name)


class Theater(Base):
    """
    records all the operation theatres in a hospital along with the
    operations that have been undertaken within that theatre.
    """
    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True)
    ward_id = Column(Integer, ForeignKey('ward.id'))
    operations = relationship('OperationRecord', backref='theater', lazy='dynamic')

    def __repr__(self):
        return '<Theater {}>'.format(self.name)


class PatientDetails(Base):
    """
    records the details of a patient along with operation history and
    and medication or prescriptions that patient has been on
    """
    id = Column(Integer, primary_key=True)
    national_id = Column(String(30),unique=True, index=True, nullable=False)
    first_names = Column(String(64))
    surname = Column(String(64))
    gender = Column(String(1))
    address = Column(String(64))
    phone = Column(String(20))
    operation_records = relationship('OperationRecord', backref='patient', lazy='dynamic')
    medication = relationship('Prescription', lazy='dynamic', backref='medication')

    def __repr__(self):
        return '<Patient {}>'.format(self.national_id)


class OperationRecord(Base):
    """ record detailing a surgery from pre-op through to post-op """
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patientdetails.id'))
    reference_id = Column(Integer, ForeignKey('referal.id'))
    theater_id = Column(Integer, ForeignKey('theater.id'))
    anaesthetist_id = Column(Integer, ForeignKey('practitionerdetails.id'))
    surgeon_id = Column(Integer, ForeignKey('practitionerdetails.id'))
    date = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    operation = Column(String)
    pre_operative_record_id = Column(Integer, ForeignKey('preoperativerecord.id'))
    operative_record_id = Column(Integer, ForeignKey('operativerecord.id'))
    post_operative_record_id = Column(Integer, ForeignKey('postoperativerecord.id'))
    anaesthetic_id = Column(Integer, ForeignKey('anaesthetic.id'))
    #vitals = relationship('VitalsRecord', backref='operation', lazy='dynamic')
    #surgical_team = relationship('PractitionerDetails', secondary='surgicalteam',lazy='dynamic', backref=backref('surgeries', lazy='subquery'))

    def __repr__(self):
        return '<operation_record {}>'.format(self.id)


class PreOperativeRecord(Base):
    """ record of a surgery before the surgery started. Also known as a pre-op"""
    id = Column(Integer, primary_key=True)
    mass = Column(String)
    temperature = Column(String)
    pulse = Column(String)
    respiration = Column(String)
    respiratory_system = Column(String)
    cardiovascular_system = Column(String)
    urine = Column(String)
    blood_group = Column(String)
    blood_pressure = Column(String)
    haemoglobin = Column(String)
    blood_urea = Column(String)
    drug_therapy = Column(String)
    asa_grade = Column(String)
    mallampati = Column(String)
    laryngoscopy_grade = Column(String)
    creat = Column(String)
    allergies = Column(String)
    attachments = relationship('Attachment', backref='preoperativerecord', lazy='dynamic')
    premedication = relationship('PremedicationRecord', backref='preoperativerecord', lazy='dynamic')

    def __repr__(self):
        return '<preoperative_record {}>'.format(self.id)


class Attachment(Base):
    """ record detailing any images or data relevant to an operation """
    id = Column(Integer, primary_key=True)
    url = Column(String(120))
    file_type = Column(String(6))
    pre_operative_record_id = Column(Integer, ForeignKey('preoperativerecord.id'))

    def __repr__(self):
        return '<Attachments {}>'.format(self.id)


class PremedicationRecord(Base):
    """ record detailing prescriptions administered before the operation """
    id = Column(Integer, primary_key=True)
    prescription_id = Column(Integer, ForeignKey('prescription.id'))
    time_given = Column(String)
    given_by = Column(Integer, ForeignKey('practitionerdetails.id'))
    pre_operative_record_id = Column(Integer, ForeignKey('preoperativerecord.id'))

    def __repr__(self):
        return '<Premedication {}>'.format(self.id)


class Anaesthetic(Base):
    """ record detailing the anasthetics administered and the technique for a surgery """
    id = Column(Integer, primary_key=True)
    start_time = Column(String)
    end_time = Column(String)
    drug = Column(String)
    technique_id = Column(Integer, ForeignKey('technique.id'))

    def __repr__(self):
        return '<Anaesthetic {}>'.format(self.id)


class Drug(Base):
    """ record detailing the drugs used in an anasthetic cocktail"""
    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True, unique=True)

    def __repr__(self):
        return '<Drug {}>'.format(self.name)


class Technique(Base):
    """ record detailing technique used to administer anasthetic to a patient """
    id = Column(Integer, primary_key=True)
    name = Column(String(64), index=True, unique=True)
    description = Column(String(64))

    def __repr__(self):
        return '<Technique {}>'.format(self.name)


class PostOperativeRecord(Base):
    """ record detailing precedures after the operation and if any complications arose from the surgery """
    id = Column(Integer, primary_key=True)
    instructions_to_ward = Column(String)
    iv_therapy = Column(String)
    sedation = Column(String)
    complications = Column(String)
    general = Column(String)
    post_op_ward = Column(String)
    analgesia = Column(String)
    initial_vitals = Column(Integer, ForeignKey('vitalsrecord.id'))



    def __repr__(self):
        return '<PostOperativeRecord {}>'.format(self.id)


class VitalsRecord(Base):
    """ record detailing vital signs taken over the course of the operation """
    id = Column(Integer, primary_key=True)
    heart_rate = Column(String)
    oxygen = Column(String)
    blood_pressure = Column(String)
    time = Column(String)

    def __repr__(self):
        return '<Vitals {}>'.format(self.id)


class OperativeRecord(Base):
    """ record detailing the operation """
    id = Column(Integer, primary_key=True)
    posture = Column(String)
    iv_therapy = Column(String)
    blood_pressure = Column(String)
    pulse_rate = Column(String)
    abnormal_reactions = Column(String)
    induction = Column(String)
    maintenance = Column(String)
    ebl = Column(String)
    monitors = Column(String)



    def __repr__(self):
        return '<OperativeRecord {}>'.format(self.id)


Base.metadata.create_all(db_engine)
Session = sessionmaker(bind=db_engine)
db_session = Session()
