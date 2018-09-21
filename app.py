from flask import Flask, redirect, request, render_template, url_for, abort, flash, jsonify
from flask_login import LoginManager, login_required, login_user, logout_user
from flask_cors import CORS
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
	return render_template('index.html')

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

	occupations = db.db_sessions.query(db.Occupation).all()
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
			practitioner = db.PractitionerDetails(firstnames=firstnames, surname=surname, gender=gender, phone=phone,
			 password=generate_password_hash(surname), address=address, occupation_id=occupation)
			db.db_session.add(practitioner)
			db.db_session.commit()
			flash('Successfully added practitioner.')
		except Exception as e:
			flash('Application error!')

	return render_template('new_record.html')

@app.route('/records/add-occupation', methods=['GET', 'POST'])
def add_occupation():
	if request.method == 'POST':
		try:
			occupation = db.Occupation(title=request.form.get('', ''))
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

	wards = raw_hospital_wards
	theaters = []

	for theater in raw_theaters:
		ward = db.db_session.query(db.Ward).get(int(theater.ward_id))
		theaters.append({
			'id': theater.id,
			'name': theater.name,
			'ward': ward.name
			})
	return render_template('hospital_details.html', wards=wards, theaters=theaters)

@app.route('/hospital/submit-details', methods=['GET', 'POST'])
@login_required
def submit_details():
	if request.method == 'POST':
		record_type = request.form.get('record', '')
	return render_template('hospital_details.html')


@app.route('/hospital/ward')
@login_required
def hospital_ward():
	return render_template('hospital_details.html')


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