from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    make_response
)

import jwt
app = Flask(__name__)

# Login and get JWT token
@app.route('/login', methods=['POST'])
def login():
    auth = request.get_json()
    if not auth or not auth.get('username') or not auth.get('password'):
        return jsonify({'message': 'Could not verify', 'WWW-Authenticate': 'Basic auth="Login required"'}), 401

    username = auth.get('username')
    password = auth.get('password')

    if username == '1' and  password == '2':
        token = auth_manager.generate_token(username)

        response = make_response(redirect(url_for('main')))
        response.set_cookie('token', 'abobas-token', httponly=True, secure=True)
        return response

    return jsonify({'message': 'Invalid credentials'}), 401


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('login.html')


@app.route('/main')
def main():
    return render_template('main.html')


@app.route('/logout')
@token_manager.token_required
def logout(username):
    response = make_response(redirect(url_for('index')))
    response.set_cookie('token', '', expires=0)
    return response


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
