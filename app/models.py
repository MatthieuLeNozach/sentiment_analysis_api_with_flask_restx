from .extensions import db
from datetime import datetime

"""
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(100))
    role = db.Column(db.String(50))  # field indicating the user's role
    access_v1 = db.Column(db.Boolean, default=False)  # Indicates access to NLP Model v1
    access_v2 = db.Column(db.Boolean, default=False)  # Indicates access to NLP Model v2
"""    
    

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    address = db.Column(db.String(50))
    password_hash = db.Column(db.String(100))
    entity = db.Column(db.String(50))  # field indicating the user's entity
    usage_purpose = db.Column(db.String(50))  # field indicating the user's target usage
    role = db.Column(db.String(50))  # field indicating the user's role
    access_v1 = db.Column(db.Boolean, default=False)  # Indicates access to NLP Model v1
    access_v2 = db.Column(db.Boolean, default=False)  # Indicates access to NLP Model v2
    access_v3 = db.Column(db.Boolean, default=False)  # Indicates access to NLP Model v3
    

class UsageTracking(db.Model):
    __tablename__ = 'tracking'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    model_name = db.Column(db.String(128), nullable=False)
    request_count = db.Column(db.Integer, default=0)
    total_input_size = db.Column(db.Integer, default=0)
    last_user = db.Column(db.DateTime, default=datetime.utcnow)
    

class RequestResponseLog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    model_name = db.Column(db.String(128), nullable=False)
    request_content = db.Column(db.Text, nullable=False)
    positive = db.Column(db.Float)
    neutral = db.Column(db.Float)
    negative = db.Column(db.Float)
    score = db.Column(db.Float)
    interpretation = db.Column(db.String(128))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)