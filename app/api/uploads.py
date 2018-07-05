import os
from app.api import bp
from flask_socketio import emit
from flask import jsonify, url_for, send_from_directory, request
from werkzeug.utils import secure_filename
from app import socketio

basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = basedir + '/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/uploads', methods=['POST'])
@socketio.on('uploads', namespace='/uploads')
def upload_file():
    # check if post has file part
    print ('cool')
    if 'file' not in request.files:
        response = {'error': 'request has no file part'}
        return jsonify(response)
    file = request.files['file']
    # if user does not select file,
    # or submit and empty part without file
    if file.filename == '':
        response = {'error': 'no selected file'}
        return jsonify(response)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        response = {
                        'message': 'uploaded file',
                        'url': url_for('api.download_file', filename=filename)
                    }
        return jsonify(response)

@bp.route('/downloads/<string:filename>', methods=['GET'])
@socketio.on('downloads', namespace='/downloads')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)
