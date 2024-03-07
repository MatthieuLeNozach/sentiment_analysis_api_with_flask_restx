import random
import string
from flask import request
from flask_restx import Resource, Namespace
from flask_jwt_extended import jwt_required, current_user
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import create_access_token
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

from .nlp_sentiment import predict_sentiment_v1, predict_sentiment_vader
from .models import User
from .api_models import user_model, user_input_model, login_model, change_password_input_model
from .api_models import prediction_input_model, prediction_model_v1, prediction_model_vader 
from .extensions import db

#from .extensions import jwt

authorizations = {
    'jsonWebToken': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization'
    }
}

ns_public = Namespace('public')
ns_login = Namespace('auth')
ns_admin = Namespace('admin', authorizations=authorizations)
ns_private = Namespace('private', authorizations=authorizations)


def admin_required(f):
    @wraps(f)
    @jwt_required()
    def wrapper(*args, **kwargs):
        if not current_user or current_user.role != 'admin':
            return {'error': 'Unauthorized'}, 403
        return f(*args, **kwargs)
    return wrapper


@ns_public.route('/hello')
class Hello(Resource):
    def get(self):
        return {'Welcome': 'NLP Sentiment Predictor API'}, 200


@ns_login.route('/register')
class Register(Resource):
    @ns_login.expect(login_model)
    @ns_login.marshal_with(user_model)
    def post(self):
        user = User(
            username=ns_login.payload['username'], 
            role='customer',
            password_hash=generate_password_hash(ns_login.payload['password']))
        db.session.add(user)
        db.session.commit()
        return user, 201


@ns_login.route('/login')
class Login(Resource):
    @ns_login.expect(login_model)
    @ns_login.doc(params={'username': "The username of the user", 'password': "The password of the user"})
    def post(self):
        user = User.query.filter_by(username=ns_login.payload['username']).first()
        if not user:
            return {'error': "User does not exists"}, 401
        if not check_password_hash(user.password_hash, ns_login.payload['password']):
            return {'error': "Incorrect password"}, 401
        return {'access token': create_access_token(identity=user)}




@ns_admin.route('/users')
class GetUsers(Resource):
    method_decorators = [jwt_required()]

    @ns_admin.expect(user_input_model)
    @ns_admin.marshal_with(user_model)
    @ns_admin.doc(security='jsonWebToken')
    def get(self):
        return User.query.all()


@ns_private.route('/users/<int:id>')
class GetUserID(Resource):
    method_decorators = [jwt_required()]

    @ns_private.expect(user_input_model)
    @ns_private.marshal_with(user_model)
    def get(self, id):
        logged_in_user = User.query.filter_by(username=ns_private.payload['username']).first()
        if logged_in_user.id != id:
            ns_private.abort(403, "Forbidden, user can only access their own information")
        return logged_in_user, 201





@ns_admin.route('/users')
class AddUsers(Resource):
    method_decorators = [jwt_required()]
    @jwt_required()
    @ns_admin.expect(user_input_model)
    @ns_admin.marshal_with(user_model)
    @ns_admin.doc(security='jsonWebToken')
    def post(self):
        current_user = current_user()
        print(current_user)
        if current_user is None:
            ns_admin.abort(404, "User not found")
        if current_user.role != 'admin':
            ns_admin.abort(403, "Forbidden, only admins can create users")
        password = ''.join(random.choice(string.digits) for _ in range(4))
        hashed_password = generate_password_hash(password)
        user = User(username=ns_admin.payload['username'], 
                    password_hash=hashed_password,
                    role=ns_admin.payload['role'])
        db.session.add(user)
        db.session.commit()
        return {'user': user, 'password': password}, 201
    
    
    
@ns_admin.route('/users/<int:id>')
class EditUsers(Resource):
    method_decorators = [jwt_required()]
    @ns_admin.expect(user_input_model)
    @ns_admin.marshal_with(user_model)
    @ns_admin.doc(security='jsonWebToken')
    def put(self, id):
        user = User.query.get(id)
        user.username = ns_admin.payload['username']
        user.access_v1 = ns_admin.payload['access_v1']
        user.access_v2 = ns_admin.payload['access_v2']
        db.session.commit()
        return user, 200
    

    @ns_private.doc(security='jsonWebToken')
    def delete(self, id):
        user = User.query.get(id)
        db.session.delete(user)
        db.session.commit()
        return f"user {user} has been deleted", 204




@ns_private.route('/users/<int:id>/change_password')
class UserChangePasswordAPI(Resource):
    @ns_private.expect(change_password_input_model)
    @ns_private.marshal_with(user_model)
    @ns_private.doc(security='jsonWebToken')
    def put(self, id):
        user = User.query.get(id)
        if user is None:
            ns_private.abort(404, f"user with id {id} does not exist")
        old_password = request.json['old_password']
        new_password = request.json['new_password']
        if not check_password_hash(user.password_hash, old_password):
            ns_private.abort(403, "Forbidden, password is incorrect")
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return user, 200
    
    
from flask import request
from flask_jwt_extended import current_user

@ns_private.route('/v1/sentiment')
class NLPSentimentPredictorV1(Resource):
    method_decorators = [jwt_required()]
    @ns_private.expect(prediction_input_model)
    @ns_private.marshal_with(prediction_model_v1)
    @ns_private.doc(security='jsonWebToken')
    def post(self):
        # Assuming current_user is set up by the JWT extension to represent the logged-in user
        if not current_user.access_v1 and 'admin' not in current_user.role:
            ns_private.abort(403, "Forbidden, user does not have access to NLP Model V1")
        
        data = request.json
        text = data.get('text')
        sentiment, score = predict_sentiment_v1(text)
        
        return {'text': text, 'sentiment': sentiment, 'score': score}, 200

@ns_private.route('/v2/sentiment')
class NLPSentimentPredictorVader(Resource):
    method_decorators = [jwt_required()]
    @ns_private.expect(prediction_input_model)
    @ns_private.marshal_with(prediction_model_vader)
    @ns_private.doc(security='jsonWebToken')
    def post(self):
        # Assuming current_user is set up by the JWT extension to represent the logged-in user
        if not current_user.access_v1 and 'admin' not in current_user.role:
            ns_private.abort(403, "Forbidden, user does not have access to NLP Model V1")
        
        data = request.json
        text = data.get('text')
        analysis = predict_sentiment_vader(text)
        
        response = {
            'text': text, 
            'positive': analysis['pos'],
            'neutral': analysis['neu'], 
            'negative': analysis['neg'],
            'score': analysis['compound'],
            'interpretation': analysis['interpretation']
        }, 200
        
        return response