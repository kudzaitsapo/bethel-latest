import os
import unittest

from coverage import coverage
basedir = os.getcwd()
cov = coverage(branch=True, omit=['.git/*', 'venv/*', 'models_tests.py', 'requirements.txt'])
cov.start()

from app import app, db
from app.models import *
from datetime import datetime

class DAOCase(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.app = app.test_client()
        db.create_all()
        self.alan = PatientDetails(first_names='alan', national_id='rqwerrr1rq')
        self.chris = PatientDetails(first_names='chris', national_id='rqwerrr2rq')
        self.moris = PatientDetails(first_names='moris', national_id='rqwerrr3rq')
        self.doc = PractitionerDetails(first_names='moris')
        db.session.add_all([self.alan, self.chris, self.moris, self.doc])
        db.session.commit()
        # patient_model = ModelFactory.make_model('PatientDetails')
        self.dao = DAO(PatientDetails())

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_find(self):
        patient1 = self.dao.find_one(1)
        # self.assertError(patient2 = dao.find_patient(5))
        self.assertEqual(patient1['id'], self.alan.id)

    def test_save(self):
        data = {'national_id':'afdsads','first_names':'chris'}
        patient = self.dao.save(data)
        self.assertEqual(patient['id'], 4)

    # def test_save_patient_failure(self):
    #     data = {'first_names':'chris'}
    #     patient = self.dao.save_patient(data)
    #     self.assertEqual(patient['message'], 'oops failed to save patient details.')

    def test_update(self):
        data = {'id':2, 'first_names':'james', 'national_id': 'rqwerrr2rq'}
        patient = self.dao.update(data)
        self.assertEqual(patient['first_names'], 'james')
        self.assertNotEqual(patient['id'], 4)
        self.assertEqual(patient['id'], 2)

    def test_update_patient_failure(self):
        data = {'first_names':'james'}
        patient = self.dao.update(data)
        self.assertEqual(patient['message'], 'Patient ID must be provided.')
        data = {'id':'','first_names':'james'}
        patient = self.dao.update(data)
        self.assertEqual(patient['message'], 'Patient ID cannot be empty.')


class PractitionerDetailsModelCase(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_creation(self):
        p = PractitionerDetails(
            first_names='Chris',
            surname='Moris',
            gender='m',
            phone='0933776882',
            address='Elmore'
        )
        db.session.add(p)
        db.session.commit()
        self.assertTrue(p.id == 1)
        self.assertEqual(p.occupation_id, None)

    def test_occupation(self):
        o1 = Occupation(title='Doctor')
        o2 = Occupation(title='Nurse')
        db.session.add_all([o1, o2])
        db.session.commit()
        p1 = PractitionerDetails(occupation_id=o2.id)
        p2 = PractitionerDetails(occupation_id=o2.id)
        p3 = PractitionerDetails(occupation_id=o1.id)
        db.session.add_all([p1, p2, p3])
        db.session.commit()
        self.assertEqual(p2.occupation_id, 2)
        self.assertEqual(o2.practitioners.count(), 2)

    def test_referals(self):
        patient1 = PatientDetails(first_names='Chris', national_id='rqwerrr1rq')
        patient2 = PatientDetails(first_names='James', national_id='rqwerrr2rq')
        doctor = PractitionerDetails(first_names='Alan')
        db.session.add_all([patient1, doctor, patient2])
        db.session.commit()
        referal1 = Referal(referer_id=doctor.id, patient_id=patient2.id)
        referal2 = Referal(referer_id=doctor.id, patient_id=patient1.id)
        db.session.add_all([referal1, referal2])
        db.session.commit()
        self.assertEqual(referal1.referer_id, 1)
        self.assertEqual(referal1.patient_id, 2)
        self.assertEqual(doctor.referrees.count(), 2)

    def test_surgical_team(self):
        p1 = PractitionerDetails(first_names='Chris')
        p2 = PractitionerDetails(first_names='Moris')
        patient = PatientDetails(first_names='alan', national_id='rqwerrr1rq')
        db.session.add_all([p1, p2, patient])
        db.session.commit()
        op1 = OperationRecord(patient_id=patient.id)
        op2 = OperationRecord(patient_id=patient.id)
        op1.surgical_team.append(p1)
        op1.surgical_team.append(p2)
        op2.surgical_team.append(p1)
        db.session.add_all([op1, op2])
        db.session.commit()
        self.assertEqual(len(p1.surgeries), 2)  # number of surgeries on patien
        # number of 'surgeons' in an operatoin
        self.assertEqual(op1.surgical_team.count(), 2)

    def test_prescription(self):
        p1 = PractitionerDetails(first_names='Chris')
        p2 = PractitionerDetails(first_names='Moris')
        alan = PatientDetails(first_names='alan', national_id='rqwerrr1rq')
        db.session.add_all([p1, p2, alan])
        db.session.commit()
        prescription1 = Prescription(
            ordered_by=p1.id,
            patient_id=alan.id,
            details='some concoction')
        prescription2 = Prescription(
            ordered_by=p2.id,
            patient_id=alan.id,
            details='another one')
        db.session.add_all([prescription1, prescription2])
        db.session.commit()
        self.assertEqual(alan.medication.count(), 2)
        self.assertEqual(p2.prescriptions.count(), 1)

    def test_doses(self):
        p1 = PractitionerDetails(first_names='Chris')
        p2 = PractitionerDetails(first_names='Moris')
        alan = PatientDetails(first_names='alan', national_id='rqwerrr1rq')
        db.session.add_all([p1, p2, alan])
        db.session.commit()
        prescription1 = Prescription(
            ordered_by=p1.id, patient_id=alan.id, details='some concoction')
        prescription2 = Prescription(
            ordered_by=p2.id, patient_id=alan.id, details='another one')
        db.session.add_all([prescription1, prescription2])
        db.session.commit()
        premed1 = PremedicationRecord(
            prescription_id=prescription1.id, given_by=p1.id)
        premed2 = PremedicationRecord(
            prescription_id=prescription2.id, given_by=p1.id)
        db.session.add_all([premed1, premed2])
        db.session.commit()
        self.assertEqual(p1.doses.count(), 2)
        self.assertEqual(p2.doses.count(), 0)


    def todo(self):
        print ('test deletion')


# class PatientDetailsModelCase(unittest.TestCase):
#
#     def setUp(self):
#         app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
#         self.app = app.test_client()
#         db.create_all()
#         self.alan = PatientDetails(first_names='alan', national_id='rqwerrr1rq')
#         self.chris = PatientDetails(first_names='chris', national_id='rqwerrr2rq')
#         self.moris = PatientDetails(first_names='moris', national_id='rqwerrr3rq')
#         db.session.add_all([self.alan, self.chris, self.moris])
#         db.session.commit()
#         self.patient_details_obj = PatientDetails()
#
#     def tearDown(self):
#         db.session.remove()
#         db.drop_all()
#
#     def test_find_patient(self):
#         patient1 = self.patient_details_obj.find_one(self.moris.id)
#         # self.assertError(patient2 = self.patient_details_obj.find_patient(5))
#         self.assertEqual(patient1['id'], 3)
#         # patient404 = self.patient_details_obj.find_one(404)
#         # # print(type(patient404))
#
#     def test_find_all_patients(self):
#         patients = self.patient_details_obj.find_all(1,1,'get_all_patient_details')
#         self.assertNotEqual(patients['_meta']['total_pages'], 4)
#         self.assertEqual(patients['_meta']['total_pages'], 3)
#
#     def test_save_patient(self):
#         data = {'national_id':'afdsads','first_names':'chris'}
#         patient = self.patient_details_obj.save(data)
#         self.assertEqual(patient['id'], 4)
#
#     # def test_save_patient_failure(self):
#     #     data = {'first_names':'chris'}
#     #     patient = self.patient_details_obj.save_patient(data)
#     #     self.assertEqual(patient['message'], 'oops failed to save patient details.')
#
#     def test_update_patient(self):
#         data = {'id':2, 'first_names':'james', 'national_id': 'rqwerrr2rq'}
#         patient = self.patient_details_obj.update(data)
#         self.assertEqual(patient['first_names'], 'james')
#         self.assertNotEqual(patient['id'], 4)
#         self.assertEqual(patient['id'], 2)
#
#     def test_update_patient_failure(self):
#         data = {'first_names':'james'}
#         patient = self.patient_details_obj.update(data)
#         self.assertEqual(patient['message'], 'Patient ID must be provided.')
#         data = {'id':'','first_names':'james'}
#         patient = dao.update(data)
#         self.assertEqual(patient['message'], 'Patient ID cannot be empty.')


class OperationRecordModelCase(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.app = app.test_client()
        db.create_all()
        self.alan = PatientDetails(first_names='alan', national_id='r45354q')
        db.session.add(self.alan)
        db.session.commit()
        self.alan_op1 = OperationRecord(patient_id=self.alan.id)
        self.alan_op2 = OperationRecord(patient_id=self.alan.id)
        self.alan_op3 = OperationRecord(patient_id=self.alan.id)
        db.session.add_all([self.alan_op1, self.alan_op2, self.alan_op3])
        db.session.commit()
        self.operation_record_obj = OperationRecord()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_find_record(self):
        record = self.operation_record_obj.find_one(1)
        self.assertEqual(record['id'], 1)
        # revisit data returned on saving, on finding
        # print('\n\n\n')
        # print(record)
        # print('\n\n\n')

    def test_find_all_records(self):
        records = self.operation_record_obj.find_all(2,1,'get_operation_records')
        self.assertNotEqual(records['_meta']['total_pages'], 4)
        self.assertEqual(records['_meta']['total_pages'], 3)
        # print (records)

    def test_find_all_records_failure(self):
        records = self.operation_record_obj.find_all(4,1,'endpoint')
        self.assertEqual(records['error'], 'page 4 out of bound')

    def test_save_record(self):
        p1 = PractitionerDetails(first_names='Chris')
        p2 = PractitionerDetails(first_names='Moris')
        db.session.add_all([p1, p2])
        anaesthetic_obj = DAO(Anaesthetic())
        anaesthetic = anaesthetic_obj.save({'drug_id': 2})
        self.operation_data = {
                        'theater_id': '32232',
                        'patient_details_data': {'first_names': 'chris', 'national_id': 'r453354q'},
                        'referal_data': {'referer_id': 20, 'patient_id': 232, 'note': 'this guy is sick'},
                        'operative_data': {'skin': 'dark'},
                        'anaesthetic_data': {'drug_id': 1},
                        'pre_operative_data': {
                                'mass': '23',
                                'attachment_data': {'url': 'link_to_file', 'file_type': 'png'},
                                'premedication_data': {
                                        'given_by': 10,
                                        'prescription_data':{'patient_id': 3323, 'details': 'some medicine'}
                                }
                        },
                        'post_operative_data': {'instructions_to_ward': 'some stuff'},
                        'vitals_data':{
                                'readings':[
                                    {'oxygen': 200, 'blood_pressure': 2},
                                    {'oxygen': 300, 'blood_pressure': 8}
                                ]
                        },
                        'surgical_team': [
                                p1,
                                p2,
                                p2
                        ]
        }
        record = self.operation_record_obj.save(self.operation_data)
        self.assertEqual(record['id'], 4)
        self.assertEqual(record['anaesthetic_id'], 2)
        self.assertEqual(self.operation_record_obj.vitals.count(), 2)
        self.assertEqual(self.operation_record_obj.surgical_team.count(), 2)

    def test_update_record(self):
        p1 = PractitionerDetails(first_names='Chris')
        p2 = PractitionerDetails(first_names='Moris')
        p3 = PractitionerDetails(first_names='Moris')
        referal_obj = Referal(id=5)
        pre_operative_record_obj = PreOperativeRecord(id=5)
        operative_record_obj = OperativeRecord(id=5)
        anaesthetic_obj = Anaesthetic(id=5)
        post_operative_record_obj = PostOperativeRecord(id=5)
        attachment_obj = Attachment(id=5)
        premedication_record_obj = PremedicationRecord(id=5)
        prescription_obj = Prescription(id=5)
        vital_obj = VitalsRecord(id=5)
        self.operation_data = {'theater_id': '32232'}
        db.session.add_all(
            [referal_obj, pre_operative_record_obj, operative_record_obj,
            anaesthetic_obj, post_operative_record_obj, attachment_obj,
            premedication_record_obj, prescription_obj, vital_obj, p1, p2, p3]
        )
        db.session.commit()
        self.operation_data = {
                        'id': 2,
                        'patient_details_data': {'id': 1,'first_names': 'john', 'national_id': 'r453354q'},
                        'referal_data': {'id': 5, 'patient_id': self.alan.id, 'note': 'this guy is sick'},
                        'theater_id': '32232',
                        'pre_operative_record_id': 453,
                        'operative_data': {'id': 5,'skin': 'dark'},
                        'post_operative_data': {'id': 5, 'instructions_to_ward': 'some stuff'},
                        'anaesthetic_data': {'id': 5, 'drug_id': 1},
                        'pre_operative_data': {
                                'id': 5,
                                'mass': '23',
                                'attachment_data': {'id': 5, 'url': 'link_to_file', 'file_type': 'png'},
                                'premedication_data': {
                                        'id': 5,
                                        'given_by': 10,
                                        'prescription_data':{'id': 5, 'patient_id': 3323, 'details': 'some medicine'}
                                }
                        },
                        'vitals_data':{
                                'readings':[
                                    {'oxygen': 200, 'blood_pressure': 2},
                                    {'oxygen': 200, 'blood_pressure': 2},
                                    {'id': 5, 'oxygen': 30, 'blood_pressure': 8},
                                    {'id': 5, 'oxygen': 30, 'blood_pressure': 8}
                                ]
                        },
                        'surgical_team': [
                                p1,
                                p3,
                                p2,
                                p1
                        ]
        }
        record = self.operation_record_obj.update(self.operation_data)
        self.assertEqual(record['patient_id'], self.alan.id)
        self.assertEqual(record['reference_id'], 5)
        self.assertEqual(record['pre_operative_record_id'], 5)
        # self.assertEqual(record.vitals.count(), 3)
        # self.assertEqual(record.surgical_team.count(), 3)

    def test_time(self):
        p1 = PractitionerDetails(first_names='Chris')
        p2 = PractitionerDetails(first_names='Moris')
        db.session.add_all([p1, p2])
        anaesthetic_obj = DAO(Anaesthetic())
        anaesthetic = anaesthetic_obj.save({'drug_id': 2})
        self.operation_data = {
                        'theater_id': '32232',
                        'start_time': '14:15',
                        'patient_details_data': {'first_names': 'chris', 'national_id': 'r453354q'},
                        'referal_data': {'referer_id': 20, 'patient_id': 232, 'note': 'this guy is sick'},
                        'operative_data': {'skin': 'dark'},
                        'anaesthetic_data': {'drug_id': 1},
                        'pre_operative_data': {
                                'mass': '23',
                                'attachment_data': {'url': 'link_to_file', 'file_type': 'png'},
                                'premedication_data': {
                                        'given_by': 10,
                                        'prescription_data':{'patient_id': 3323, 'details': 'some medicine'}
                                }
                        },
                        'post_operative_data': {'instructions_to_ward': 'some stuff'},
                        'vitals_data':{
                                'readings':[
                                    {'oxygen': 200, 'blood_pressure': 2},
                                    {'oxygen': 300, 'blood_pressure': 8}
                                ]
                        },
                        'surgical_team': [
                                p1,
                                p2,
                                p2
                        ]
        }
        record = self.operation_record_obj.save(self.operation_data)

if __name__ == '__main__':
    # unittest.main(verbosity=2)
    try:
        unittest.main(verbosity=2)
    except:
        pass
    cov.stop()
    cov.save()
    print("\n\mCoverage Report:\n")
    cov.report()
    print("HTML version: " + os.path.join(basedir, "tmp/coverage/index.html"))
    cov.html_report(directory='tmp/coverage')
    cov.erase()
