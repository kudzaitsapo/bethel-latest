import api.v1.models as db
from api.v1.models import db_session as session
from werkzeug.security import generate_password_hash


def main():
	admins = session.query(db.Admin).count()
	if admins == 0:
		try:
			administrator = db.Admin(username='Administrator', email='admin@bethel.app', password=generate_password_hash('secret_password'))
			session.add(administrator)
			session.commit()
			message = 'The administrator has been registered. The email is admin@bethel.app, the password is secret_password'
		except Exception as e:
			message = str(e)

	else:
		message = 'An administrator has already been added! Please click the following link to login! <a href="' + url_for('login') + '">login</a>'
		

	print(message)



if __name__ == '__main__':
	main()