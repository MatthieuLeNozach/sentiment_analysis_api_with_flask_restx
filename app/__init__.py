from flask import Flask
from .models import User
from .extensions import api, db, jwt  # importing the objects created in extensions
from .routes import ns_public, ns_login, ns_admin, ns_private  # importing the namespace that registers the API routes
from .models import User

def create_app():
    
    app = Flask(__name__)  

    # passing configurations to the app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'  # the database will be created in the 'instance' folder
    app.config['JWT_SECRET_KEY'] = 'SecretKeyExample'    
    
    authorizations = {
        'jsonWebToken': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    }
    api.init_app(app, title='NLP Sentiment Predictor API', version='1.0', authorizations=authorizations)    
    
    db.init_app(app)
    jwt.init_app(app)

    # registering the namespaces in the api defined in 'routes'
    api.add_namespace(ns_public)
    api.add_namespace(ns_login)
    api.add_namespace(ns_admin)
    api.add_namespace(ns_private)
    
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.id

    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data['sub']
        return User.query.filter_by(id=identity).one_or_none()

    return app
