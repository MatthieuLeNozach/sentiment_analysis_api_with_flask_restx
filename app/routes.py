import random
import string
import json
from flask import request
from flask_restx import Resource, Namespace
from flask_jwt_extended import jwt_required, current_user
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_jwt_extended import create_access_token
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

from .nlp_sentiment import predict_sentiment_v1, predict_sentiment_vader
from .models import User
from .api_models import user_model, user_input_model, login_model, change_password_input_model
from .api_models import prediction_input_model, prediction_model_v1, prediction_model_vader 
from .extensions import db
from .utils import log_request_response

# from .extensions import jwt

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
        data = request.get_json()
        user = User(
            username=data['username'], 
            role='customer',
            password_hash=generate_password_hash(data['password']))
        db.session.add(user)
        db.session.commit()
        return user, 201

@ns_login.route('/login')
class Login(Resource):
    @ns_login.expect(login_model)
    @ns_login.doc(params={'username': "The username of the user", 'password': "The password of the user"})
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        if not user:
            return {'error': "User does not exists"}, 401
        if not check_password_hash(user.password_hash, data['password']):
            return {'error': "Incorrect password"}, 401
        return {'access token': create_access_token(identity=user)}




from flask import request

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
        data = request.get_json()
        logged_in_user = User.query.filter_by(username=data['username']).first()
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
        data = request.get_json()
        password = ''.join(random.choice(string.digits) for _ in range(4))
        hashed_password = generate_password_hash(password)
        user = User(username=data['username'], 
                    password_hash=hashed_password,
                    role=data['role'])
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
        data = request.get_json()
        user = User.query.get(id)
        user.username = data['username']
        user.access_v1 = data['access_v1']
        user.access_v2 = data['access_v2']
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
        data = request.get_json()
        old_password = data['old_password']
        new_password = data['new_password']
        if not check_password_hash(user.password_hash, old_password):
            ns_private.abort(403, "Forbidden, password is incorrect")
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        return user, 200

@ns_private.route('/v1/sentiment')
class NLPSentimentPredictorV1(Resource):
    method_decorators = [jwt_required()]
    @ns_private.expect(prediction_input_model)
    @ns_private.marshal_with(prediction_model_v1)
    @ns_private.doc(security='jsonWebToken')
    def post(self):
        user_id = get_jwt_identity()
        # Assuming current_user is set up by the JWT extension to represent the logged-in user
        if not current_user.access_v1 and 'admin' not in current_user.role:
            ns_private.abort(403, "Forbidden, user does not have access to NLP Model V1")
        data = request.get_json()
        text = data.get('text')
        sentiment, score = predict_sentiment_v1(text)
        
        log_request_response(current_user.id, 'v1', text, sentiment)
        return {'text': text, 'sentiment': sentiment, 'score': score}, 200

@ns_private.route('/v2/sentiment')
class NLPSentimentPredictorVader(Resource):
    method_decorators = [jwt_required()]
    @ns_private.expect(prediction_input_model)
    @ns_private.marshal_with(prediction_model_vader)
    @ns_private.doc(security='jsonWebToken')
    def post(self):
        if not current_user.access_v2 and 'admin' not in current_user.role:
            ns_private.abort(403, "Forbidden, user does not have access to NLP Model V1")
        
        data = request.get_json()
        text = data.get('text')
        analysis = predict_sentiment_vader(text)
        
        # Prepare the response content
        response_content = json.dumps({
            'text': text, 
            'positive': analysis['pos'],
            'neutral': analysis['neu'], 
            'negative': analysis['neg'],
            'score': analysis['compound'],
            'interpretation': analysis['interpretation']
        })
        
        log_request_response(current_user.id, 'v2', text, response_content)
        
        return json.loads(response_content) 
    
    
    
