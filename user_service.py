import datetime
import os
from app.main import db
from app.main.model.user import User

curr_env = os.environ.get('DEPLOY_ENV', 'DEV')
cookie_secure = curr_env == 'PRODUCTION'


def save_new_user(data):
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        new_user = User(
            email=data['email'],
            first_name=data['first_name'],
            password=data['password'],
            registered_on=datetime.datetime.utcnow(),
            birthdate=datetime.datetime.strptime(
                data['birthdate'],
                "%m/%d/%Y"
            ).date(),
            sex=data['sex']
        )
        save_changes(new_user)
        return register_user(new_user)
    else:
        response_object = {
            'status': 'fail',
            'message': 'User already exists. Please log in.',
        }
        return response_object, 409


def set_cookie(response, data):
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return response
    elif user.check_password(data['password']):
        token = user.encode_auth_token(user.id)
        response.set_cookie(
            'auth_token', value=token,
            secure=cookie_secure,
            httponly=True,
            samesite=None
        )
        return response
    return response


def get_all_users(auth_object):
    return {
        'users': User.query.all(),
        'status': 'success'
    }, 200


def get_user_by_id(id):
    return User.query.filter_by(id=id).first()


def save_changes(data):
    db.session.add(data)
    db.session.commit()


def register_user(user):
    try:
        response_object = {
            'status': 'success',
            'message': 'Successfully registered.'
        }
        return response_object, 201
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': 'An error occurred. Please try again.'
        }
        print(e)
        return response_object, 401


def edit_user_settings(json, auth_object):
    response_object = {}
    user = User.query.filter_by(
        id=auth_object['auth_object']['data']['user_id']
    ).first()
    if not user:
        response_object = {
            'status': 'failure',
            'message': 'Failed to find user info.'
        }
        return response_object, 404
    try:
        if json.get('email'):
            u = User.query.filter_by(email=json['email']).first()
            if not u:
                user.email = json['email']
            else:
                response_object = {
                    'status': 'failure',
                    'message': 'User with email already exists'
                }
                return response_object, 409
        if json.get('first_name'):
            user.first_name = json['first_name']
        if json.get('birthdate'):
            user.birthdate = datetime.datetime.strptime(
                json['birthdate'],
                "%Y-%m-%dT%H:%M:%S.000Z"
            )
        if json.get('current_password'):
            if user.check_password(json.get('current_password')) and json.get('password'):  # noqa: E501
                user.password = json['password']
                db.session.add(user)
                db.session.commit()
                return {
                    'status': 'success',
                    'message': 'Successfully changed current password.'
                }, 200
            else:
                return {
                    'status': 'failure',
                    'message': 'Incorrect password entered.'
                }, 401
        if json.get('sex'):
            user.sex = json['sex']
        db.session.add(user)
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': 'Successfully edited user\'s settings'
        }
    except Exception as e:
        print(e)
        response_object = {
            'status': 'fail',
            'message': 'An error occurred. Please try again.'
        }
        return response_object, 400
    return response_object, 200
