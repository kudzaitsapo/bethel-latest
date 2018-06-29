import os
import unittest

from app import app, db
from app.models import *
from app.routes import app
from config import Config

class PatentEndPointsCase(unittest.TestCase):

    def setUp(self):
        app.config.from_object(Config)
        db = SQLAlchemy(app)
        self.app = app.test_client()
        # db.create_all()
        self.alan = PatientDetails(first_names='alan', national_id='rqwerrr1rq')
        self.chris = PatientDetails(first_names='chris', national_id='rqwerrr2rq')
        self.moris = PatientDetails(first_names='moris', national_id='rqwerrr3rq')
        db.session.add_all([self.alan, self.chris, self.moris])
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        # db.drop_all()

    def ptest_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_get_patient_details(self):
        response = self.app.get('/patients/1', follow_redirects=True)
        print (response)
        self.assertEqual(response.status_code, 500)

if __name__ == '__main__':
    unittest.main(verbosity=2)
