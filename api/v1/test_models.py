from models import Admin
from models import Hospital, Ward, Theater
from models import PractitionerDetails, PatientDetails
from models import PreOperativeRecord, OperativeRecord, PostOperativeRecord
from models import OperationRecord
from models import db_session as db


# creating models for use
admin = Admin(username="admin", email="admin@admin.com", password="admin123")
parirenyatwa = Hospital(name="parirenyatwa")
bc1 = Ward(name="BC1", hospital_id=parirenyatwa.id)
theatre_a = Theater(name="TA", ward_id=bc1.id)

if __name__ == '__main__':
	db.add_all([admin, parirenyatwa, bc1, theatre_a])
	db.commit()
