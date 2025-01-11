import jwt
import datetime
from functools import wraps
from flask import (
    request,
    redirect,
    url_for
)
from db_manager import DatabaseManager


class AuthManager:
    def __init__(self, auth_config, db: DatabaseManager):
        self.auth_config = auth_config
        self.db = db

    def authenticate(self, username, password):
        return self.db.authenticate_user(username, password)

    def generate_token(self, username):
        return jwt.encode({
            'username': username,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=1440)
        }, self.auth_config['SECRET_KEY'])

    def register(self, username, password):
        if self.db.create_user_account(username, password):
            return None
        return "User already exists"


class TokenManager:
    def __init__(self, auth_config):
        self.auth_config = auth_config

    def token_required(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.cookies.get('token')
            if not token:
                return redirect(url_for('index'))
            try:
                data = jwt.decode(token, self.auth_config['SECRET_KEY'], algorithms=["HS256"])
                username = data.get('username')
            except jwt.ExpiredSignatureError:
                print('Token has expired!')
                return redirect(url_for('index'))
                # return jsonify({'message': 'Token has expired!'}), 403
            except jwt.InvalidTokenError:
                print('Token is invalid!')
                return redirect(url_for('index'))
                # return jsonify({'message': 'Token is invalid!'}), 403
            return f(username, *args, **kwargs)
        return decorated
