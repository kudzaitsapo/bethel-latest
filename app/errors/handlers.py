from app.errors import bp
from werkzeug.http import HTTP_STATUS_CODES
from flask import jsonify

@bp.route('/')
def index():
    return "dkd"

def error_resposnse(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Uknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response

def bad_request(messge):
    return error_resposnse(400, messge)

@bp.errorhandler(404)
def not_found():
    return jsonify({"error": "resources not found"})
