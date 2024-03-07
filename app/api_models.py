from flask_restx import fields
from .extensions import api


user_model = api.model("User", { # defining the structure of the User object that gets 'marshalled' in the API
    "id": fields.Integer,
    "username": fields.String,
    "role": fields.String,  # roles: customer / admin
    "nlp_v1": fields.Boolean,  # brings the information of the NLPModels to which the user has access
    "nlp_v2": fields.Boolean
})

user_extended_model = api.model("UserExtended", {
    "id": fields.Integer,
    "username": fields.String,
    "email": fields.String,
    "address": fields.String,
    "entity": fields.String,
    "usage_purpose": fields.String,
    "role": fields.String,
    "access_v1": fields.Boolean,
    "access_v2": fields.Boolean,
    "access_v3": fields.Boolean
})

user_input_model = api.model("UserInput", {
    "username": fields.String,
    "role": fields.String,  
})


login_model = api.model("LoginModel", {
    "username": fields.String,
    "password": fields.String
})


register_model = api.model("Register", {
    "username": fields.String(required=True),
    "email": fields.String(required=True),
    "password": fields.String(required=True),
    "entity": fields.String(required=True),
    "usage_purpose": fields.String(required=True),
})


change_password_input_model = api.model('ChangePassword', {
    'old_password': fields.String(required=True, description='Old password'),
    'new_password': fields.String(required=True, description='New password'),
    }
)


prediction_input_model = api.model('PredictionInput', {
    'username': fields.String(required=True, description='Username'),
    'text': fields.String(required=True, description='Text to predict')
})

prediction_model_v1 = api.model('Sentiment', {
    'text': fields.String(required=True, description='Text'),
    'sentiment': fields.String(required=True, description='Predicted sentiment'),
    'score': fields.Float(required=True, description='Sentiment score')
})

prediction_model_vader = api.model('Sentiment', {
    'text': fields.String(required=True, description='Text'),
    'positive': fields.Float(required=True, description='Positive sentiment score'),
    'neutral': fields.Float(required=True, description='Neutral sentiment score'),
    'negative': fields.Float(required=True, description='Negative sentiment score'),
    'score': fields.Float(required=True, description='Sentiment score'),
    'interpretation': fields.String(required=True, description='Predicted sentiment'),
})

      
