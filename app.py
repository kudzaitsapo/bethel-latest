from flask import Flask, redirect, request, render_template, url_for, abort, flash, jsonify
from flask_login import LoginManager, login_required, login_user, logout_user
from flask_cors import CORS
from sqlalchemy import and_
from werkzeug.security import generate_password_hash
from api.v1 import manager
import api.v1.models as db
import requests

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = "abcdefg"
manager.init_app(app)
#login_api.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
	return db.db_session.query(db.Admin).get(int(userid))


# redirect to login page if not logged in
@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

# somewhere to login
@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		try:
			user = db.db_session.query(db.Admin).filter(db.Admin.email == email).first()
			if user.check_password(password):
				login_user(user)
				return redirect(request.args.get("next") or url_for('index'))
			else:
				flash('Incorrect login credentials!!')
				return render_template('login.html')
		except Exception as e:
			flash('An internal error has occurred!')
			return render_template('login.html')
		
	else:
		return render_template('login.html')

@app.route('/register-admin')
def register_admin():
	admins = db.db_session.query(db.Admin).count()
	if admins == 0:
		try:
			administrator = db.Admin(username='Administrator', email='admin@bethel.app', password=generate_password_hash('secret_password'))
			db.db_session.add(administrator)
			db.db_session.commit()
			message = 'The administrator has been registered. The email is admin@bethel.app, the password is secret_password'
			message += '. Click <a href="' + url_for('login') + '">here</a> to login'
		except Exception as e:
			message = str(e)

		return message
	else:
		message = 'An administrator has already been added! Please click the following link to login! <a href="' + url_for('login') + '">login</a>'
		return 'There are ' + str(admins) + ' administrators'

# somewhere to logout
@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))

# handle login failed
@app.errorhandler(401)
def page_not_found(e):
	flash("ERROR: failed to Login ")
	return redirect(url_for('index'))


def get_record_data(something):
	
	return True

@app.route('/')
@app.route('/home')
@login_required
def index():
	practitioners_list = db.db_session.query(db.PractitionerDetails).all()

	occupations = db.db_session.query(db.Occupation).all()
	return render_template('index.html', practitioners=practitioners_list, occupations=occupations)

@app.route('/sw.js')
def service_worker():
	return app.send_static_file('sw.js')

@app.route('/profile')
@login_required
def profile():
	return render_template('profile.html')

@app.route('/records')
@login_required
def display_records_list():
	practitioners_list = db.db_session.query(db.PractitionerDetails).all()

	occupations = db.db_session.query(db.Occupation).all()
	return render_template('list_records.html', practitioners=practitioners_list, occupations=occupations)

@app.route('/records/<int:record_id>')
@login_required
def display_record(record_id):
	patient_data = get_record_data(record_id)
	return render_template('view_record.html', data=patient_data)

@app.route('/records/new')
@login_required
def new_record():
	occupations = db.db_session.query(db.Occupation).all()

	choices = []
	gender_options = [{'key': 'male', 'value': 'm'}, {'key': 'female', 'value': 'f'}]

	for occupation in occupations:
		choices.append({
			'key':occupation.title, 'value': occupation.id
			})
	return render_template('new_record.html', choices=choices, gender_options=gender_options)

@app.route('/records/submit-new-record', methods=['GET', 'POST'])
def submit_new_record():
	if request.method == 'POST':
		firstnames = request.form.get('firstnames', '')
		surname = request.form.get('surname', '')
		gender = request.form.get('gender', '')
		occupation = request.form.get('occupation', '')
		phone = request.form.get('phone', '')
		address = request.form.get('address', '')

		try:
			practitioner = db.PractitionerDetails(first_names=firstnames, surname=surname, gender=gender, phone=phone,
			 password=generate_password_hash(surname), address=address, occupation_id=occupation)
			db.db_session.add(practitioner)
			db.db_session.commit()
			flash('Successfully added practitioner. Default password is their surname.')
		except Exception as e:
			print(str(e))
			flash('Application error!')

		#db.db_session.rollback()

	return render_template('new_record.html')

@app.route('/records/add-occupation', methods=['GET', 'POST'])
def add_occupation():
	if request.method == 'POST':
		try:
			occupation = db.Occupation(title=request.form.get('occupation', ''))
			db.db_session.add(occupation)
			db.db_session.commit()
			flash('Submitted without errors')
		except:
			flash('Application error!')
	return render_template('add_occupation.html')

@app.route('/hospital/details')
@login_required
def hospital_details():
	raw_hospital_wards = db.db_session.query(db.Ward).all()
	raw_theaters = db.db_session.query(db.Theater).all()

	ward_count = db.db_session.query(db.Ward).count()
	theater_count = db.db_session.query(db.Theater).count()

	wards = raw_hospital_wards
	ward_choices = []
	theaters = []

	for theater in raw_theaters:
		if theater.ward_id is not None:
			ward = db.db_session.query(db.Ward).get(int(theater.ward_id))
			theaters.append({
				'id': theater.id,
				'name': theater.name,
				'ward': ward.name
				})
		else:
			theaters.append({
				'id': theater.id,
				'name': theater.name,
				'ward': ''
				})

	for ward in raw_hospital_wards:
		ward_choices.append({
			'key': ward.name,
			'value': ward.id
			})
	return render_template('hospital_details.html', ward_choices=ward_choices, 
		wards=wards, theaters=theaters, theater_count=theater_count, ward_count=ward_count)

@app.route('/hospital/submit-details', methods=['GET', 'POST'])
@login_required
def submit_details():
	if request.method == 'POST':
		record_type = request.form.get('record', '')
		message = ""
		_class = "alert alert-danger"
		html_message = ""

		if record_type == 'ward':
			ward_name = request.form.get('Ward_Name', '')
			db_ward_count = db.db_session.query(db.Ward).filter(db.Ward.name == ward_name).count()
			if db_ward_count == 0:
				try:
					db_ward = db.Ward(name=ward_name)
					db.db_session.add(db_ward)
					db.db_session.commit()
					message = "Successfully saved the ward"
					_class = "alert alert-success"
				except Exception as e:
					message = "Could not save the ward"

			
		elif record_type == 'theater':
			ward = request.form.get('ward', '')
			theater_name = request.form.get('Theatre_Name', '')

			theater_count = db.db_session.query(db.Theater).filter(and_(db.Theater.name == theater_name, 
				db.Theater.ward_id == ward)).count()
			if theater_count == 0:
				try:
					new_theater = db.Theater(name=theater_name, ward_id=ward)
					db.db_session.add(new_theater)
					db.db_session.commit()
					message = "Successfully saved the theater"
					_class = "alert alert-success"
				except Exception as e:
					message = "Could not save the theater!"

		html_message = "<p class='" + _class + "'>" + message + "</p>"

		flash(html_message)
	return render_template('hospital_details.html')


@app.route('/hospital/ward')
@login_required
def hospital_ward():
	return render_template('hospital_details.html')

@app.route('/operations')
@login_required
def view_operations():
	operations = db.db_session.query(db.OperationRecord).join(db.PatientDetails, 
		db.OperationRecord.patient_id == db.PatientDetails.id).all()
	return render_template('view_operations.html', operations=operations)

@app.route('/operations/<int:id>')
@login_required
def view_operation(id):
	operation_data = db.db_session.query(db.OperationRecord).filter(db.OperationRecord.id == id).first()
	patient = db.db_session.query(db.PatientDetails).filter(db.PatientDetails.id == operation_data.patient_id).first()
	anaesthetist = db.db_session.query(db.PractitionerDetails).filter(db.PractitionerDetails.id == operation_data.anaesthetist_id).first()
	surgeon = db.db_session.query(db.PractitionerDetails).filter(db.PractitionerDetails.id == operation_data.surgeon_id).first()
	preoperative_record = db.db_session.query(db.PreOperativeRecord).filter(db.PreOperativeRecord.id == operation_data.pre_operative_record_id).first()
	operative_record = db.db_session.query(db.OperativeRecord).filter(db.OperativeRecord.id == operation_data.operative_record_id).first()
	postoperative_record = db.db_session.query(db.PostOperativeRecord).filter(db.PostOperativeRecord.id == operation_data.post_operative_record_id).first()
	vitals_record = db.db_session.query(db.VitalsRecord).filter(db.VitalsRecord.operation_record_id == operation_data.id).all()

	return render_template('view_operation.html', operation = {
		'operation': operation_data, 'patient': patient, 'anaesthetist': anaesthetist, 'surgeon': surgeon,
		'preop_record': preoperative_record, 'op_record': operative_record, 'postop_record': postoperative_record,
		'vitals': vitals_record
		})

@app.route('/patients')
@login_required
def view_patients():
	patients = db.db_session.query(db.PatientDetails).all()
	return render_template('view_patients.html', patients=patients)

@app.route('/api/login', methods=['POST'])
def check_api_login():
	phonenumber = request.json.get('phone_number', '')
	password = request.json.get('password', '')
	try:
		if phonenumber != '' and password != '':
			user = db.db_session.query(
			db.PractitionerDetails).filter(db.PractitionerDetails.phone == phonenumber).one()
			db.db_session.close()
		else:
			return jsonify({'message': 'missing details'}), 400
	except Exception as e:
		return jsonify({'message': 'user not found'}), 404
	if user.check_password(password):
		return jsonify({
			    "address": user.address,
			    "first_names": user.first_names,
			    "gender": user.gender,
			    "id": user.id,
			    "occupation_id": user.occupation_id,
			    "phone": phonenumber,
			    "surname": user.surname
			}), 200
	else:
		return jsonify({"message": "user and password do not match"}), 401

@app.route('/api/change-password/<int:userid>', methods=['POST'])
def change_password(userid):
	old_password = request.json.get('old', '')
	new_password = request.json.get('new', '')

	user = db.db_session.query(db.PractitionerDetails).get(userid)
	if user is not None:
		if(user.check_password(old_password)):
			try:
				user.password = generate_password_hash(new_password)
				db.db_session.commit()
				return jsonify({'message': 'Successful'}), 200
			except:
				return jsonify({'message': 'Internal Server Error'}), 500
		else:
			return jsonify({'message': 'Invalid password'}), 401
	else:
		return jsonify({'message': 'Invalid user id!'}), 400

if __name__ == "__main__":
	app.run(port=5000, host='0.0.0.0', debug=True, threaded=True)