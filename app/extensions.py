# file to create and manage Flask-RestX and SQLAlchemy extensions
from flask_sqlalchemy import SQLAlchemy # Database management
from flask_restx import Api  # API creation
from flask_jwt_extended import JWTManager  # Security and authentication



# instantiating the classes, creating extension objects
api = Api()
db = SQLAlchemy()
jwt = JWTManager()
