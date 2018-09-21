from flask_restless import APIManager
from .models import Hospital, Ward, Theater
from .models import PractitionerDetails, PatientDetails
from .models import PreOperativeRecord, OperativeRecord, PostOperativeRecord
from .models import OperationRecord, VitalsRecord, Anaesthetic, Occupation
from .models import db_session as db

manager = APIManager(session=db)

#personnel management
manager.create_api(PatientDetails, collection_name="patient", methods=['GET','POST','PUT'])
manager.create_api(PractitionerDetails, collection_name="practitioner",
 	methods=['GET','POST','PUT'], 
 	exclude_columns=['password']) #TODO: remove password in endpoint

#hospital data
manager.create_api(Hospital, methods=['GET','POST','PUT'])
manager.create_api(Ward, methods=['GET','POST','PUT'])
manager.create_api(Theater, methods=['GET','POST','PUT'])
manager.create_api(Occupation, collection_name='occupation', methods=['GET', 'POST'])

# operation details
manager.create_api(PreOperativeRecord, collection_name="pre-operative-record", methods=['GET','POST','PUT'])
manager.create_api(OperativeRecord, collection_name="operative-record", methods=['GET','POST','PUT'])
manager.create_api(PostOperativeRecord, collection_name="post-operative-record", methods=['GET','POST','PUT'])
manager.create_api(OperationRecord, collection_name="operation", methods=['GET','POST','PUT'])
manager.create_api(VitalsRecord, collection_name="vitals-records", methods=['GET','POST','PUT'])
manager.create_api(Anaesthetic, collection_name="anaesthetic", methods=['GET', 'POST', 'PUT'])
