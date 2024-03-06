from .extensions import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(100))
    role = db.Column(db.String(50))  # field indicating the user's role
    access_v1 = db.Column(db.Boolean, default=False)  # Indicates access to NLP Model v1
    access_v2 = db.Column(db.Boolean, default=False)  # Indicates access to NLP Model v2
    

