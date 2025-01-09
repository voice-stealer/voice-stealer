from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    make_response
)

from work_manager import WorkManager
from file_manager import FileManager
from auth_manager import AuthManager, TokenManager
from request_manager import RequestManager
from db_manager import DatabaseManager

import os


class Config:
    SECRET_KEY = os.environ['SECRET_KEY'].strip()

    DB_HOST = os.environ['DB_HOST'].strip()
    DB_PORT = os.environ['DB_PORT'].strip()
    DB_NAME = os.environ['DB_NAME'].strip()
    DB_USER = os.environ['DB_USER'].strip()
    DB_PASSWORD = os.environ['DB_PASSWORD'].strip()

    KAFKA_HOST = os.environ['KAFKA_HOST'].strip()
    KAFKA_PORT = os.environ['KAFKA_PORT'].strip()

    S3_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID'].strip()
    S3_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY'].strip()




app = Flask(__name__)
app.config.from_object(Config)

db_config = f"host={Config.DB_HOST} port={Config.DB_PORT} sslmode=verify-full dbname={Config.DB_NAME} user={Config.DB_USER} password={Config.DB_PASSWORD} target_session_attrs=read-write"

kafka_conf = {
    'bootstrap.servers': f"{Config.KAFKA_HOST}:{Config.KAFKA_PORT}"
}

auth_config = {
    'SECRET_KEY': Config.SECRET_KEY
}

s3_config = {
    'aws_access_key_id': Config.S3_ACCESS_KEY_ID,
    'aws_secret_access_key': Config.S3_SECRET_ACCESS_KEY,
}

token_manager = TokenManager(auth_config)

request_manager = RequestManager()
db_manager = DatabaseManager(db_config)
file_manager = FileManager(s3_config, db_manager)
auth_manager = AuthManager(auth_config, db_manager)
work_manager = WorkManager(kafka_conf, db_manager)




# Login and get JWT token
@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Could not verify', 'WWW-Authenticate': 'Basic auth="Login required"'}), 401

    username = auth.get('username')
    password = auth.get('password')

    if auth_manager.authenticate(username, password):
        token = auth_manager.generate_token(username)

        response = make_response(redirect(url_for('main')))
        response.set_cookie('token', token, httponly=True, secure=True)
        return response

    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/registration', methods=['POST'])
def registration():
    reg = request.get_json()
    username = reg.get('username')
    password1 = reg.get('password1')
    password2 = reg.get('password2')
    if password1 != password2:
        return jsonify({'message': 'Passwords do not match'}), 400

    password = password1
    print(username, password)
    if not username or not password:
        return jsonify({'message': 'Could not create user without username or password'}), 400

    err = auth_manager.register(username, password)
    if err:
        return jsonify({'message': err}), 400
    # redirect to login page
    return redirect(url_for('index'))


# Save user's audio to s3 like: /{username}/{filename}.wav
@app.route('/upload/wav', methods=['POST'])
@token_manager.token_required
def upload_wav(username):
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']

    if not file.filename:
        return jsonify({'message': 'No selected file'}), 400

    max_file_size = 500 * 1024 * 1024  # 500 MB в байтах
    if len(file.read()) > max_file_size:
        return jsonify({'message': 'File is too large. Maximum file size is 500MB.'}), 400
    file.seek(0)


    if file_manager.save_file_for_user(username, file):
        return jsonify({'message': f'File {file.filename} uploaded successfully'}), 200

    return jsonify({'message': 'Invalid file format, only WAV accepted'}), 400


# @app.route('/get/wav/<filename>', methods=['GET'])
# @token_manager.token_required
# def get_wav(username, filename):
#     try:
#         if not filename.endswith('.wav'):
#             return jsonify({'message': 'Invalid file type requested'}), 400

#         return file_manager.get_file(filename)
#     except FileNotFoundError:
#         return jsonify({'message': 'File not found'}), 404


# Return processed audio or {status: in_progress}
@app.route('/result/<request_id>', methods=['GET'])
@token_manager.token_required
def get_result(username, request_id):
    # Fetch request status from DB, check if it is 'done'
    status = db_manager.fetch_status(request_id)
    if status == 'done':
        return file_manager.get_file(f"{request_id}.wav")
    return jsonify({'status': status}), 200



# POST method to receive and print message
@app.route('/generate', methods=['POST'])
@request_manager.generate_request_id
@token_manager.token_required
def generate_audio(username, request_id):
    data = request.get_json()
    message = data.get("message")
    selected_audio = data.get("selected_audio")

    if message and selected_audio:
        work_manager.create_task(request_id, username, message, selected_audio)
        print(username, message, selected_audio)
        return jsonify({'reqid': request_id}), 200
    return jsonify({'message': 'No message or selected audio provided'}), 400




@app.route('/')
@app.route('/index.html')
def index():
    return render_template('login.html')


@app.route('/main')
@token_manager.token_required
def main(username):
    speakers = db_manager.fetch_speakers_for_user_by_name(username)
    return render_template('main.html', audio_files=speakers)


@app.route('/logout')
@token_manager.token_required
def logout(username):
    response = make_response(redirect(url_for('index')))
    response.set_cookie('token', '', expires=0)
    return response


if __name__ == '__main__':
    app.run(debug=False, port=5000, host='0.0.0.0',
            #ssl_context=('/etc/api-certificate/certificate.crt', '/etc/api-certificate-key/certificate.key')
        )