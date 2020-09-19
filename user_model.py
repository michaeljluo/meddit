from .. import db, flask_bcrypt

import datetime
import jwt
from app.main.model.blacklist import BlacklistToken
from ..config import key
from .. import login_manager
from flask_login import UserMixin
from .action import Action  # noqa: F401
from .illness import Illness, Symptom  # noqa: F401


class User(db.Model):
    """ User Model for storing all user details """
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    birthdate = db.Column(db.Date, nullable=False)
    first_name = db.Column(db.String(50))
    password_hash = db.Column(db.String(100))
    symptoms = db.relationship('Symptom', backref='user')
    illnesses = db.relationship('Illness', backref='user')
    # sex can be Male, Female or None
    sex = db.Column(db.String(50), nullable=False, default="None")

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = flask_bcrypt.generate_password_hash(
            password
        ).decode('utf-8')

    def check_password(self, password):
        return flask_bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<User '{}'>".format(self.first_name)

    def encode_auth_token(self, user_id):
        """
        Generates the authentication token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(
                    days=30,
                ),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                key,
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, key)
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class AdminUser(UserMixin, db.Model):
    """ User Model for storing all user details """
    __tablename__ = "adminuser"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    username = db.Column(db.String(255))

    actions = db.relationship('Action', backref='user')
    surveys = db.relationship('Survey', backref='user')

    role = db.Column(db.String(50), nullable=False, default="regular")

    registered_on = db.Column(db.DateTime, nullable=False)
    password_hash = db.Column(db.String(100))

    @staticmethod
    @login_manager.user_loader
    def load_user(id):
        return AdminUser.query.get(int(id))

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = flask_bcrypt.generate_password_hash(
            password
        ).decode('utf-8')

    def check_password(self, password):
        return flask_bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<User '{}'>".format(self.username)
