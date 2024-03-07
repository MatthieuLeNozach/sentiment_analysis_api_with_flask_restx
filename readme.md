# **FLask Exam: Création d'une API d'analyse de Sentiment**

## **Librairies**

- **Outils**
  - dotenv
- **API**
  - flask
  - flask-restx
  - swagger
- **Database**
  - sqlalchemy
  - sqlite3
- **Modèle**
  - vaderSentiment

## **Structure**

```text
/project
    /app
        __init__.py
        models.py
        routes.py
        nlp_sentiment.py
        extensions.py
        api_models.py
        main.py
    /bin
        builder.py
    venv/

```

#### Dossier ***env***

- Environnement virtuel python dédié

#### Dossier ***app***

- \__init\_\_.py: Création de l'instance Flask
- models: clases d'objets passés dans la base de données, en l'occurence la class User
- db_models: spécifications des formats  d'input et d'output des classes de route
- routes.py: création de classes de routes, qui partagent des caractéristiques déterminées par les Namespaces (ex. public, privé, admin...) donnera un endpoint `/api/hello`
- extensions.py: Lancement de l'instance `flask_restx.API()`, de l'instance de base de données `SQLAlchemy()` et de l'instance de sécurisation `jwt`
- nlp_sentiment.py: modèles et outils d'analyse de sentiment

## **Commandes**

#### **Setup de l'environnement**

```
bash
python3 -m venv venv

/env/bin/activate

pip install requirements.txt
```

## **Implémentation du code**

#### **Création de `main.py`**

```py
from app import app

if __name__ == '__main__':
    app.run(debug=True)
```



#### **Création de la classe `User` dans `models.py`**

```py
from .extensions import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(100))
    role = db.Column(db.String(50))
    access_v1 = db.Column(db.Boolean, default=False)  # Indicates access to NLP Model v1
    access_v2 = db.Column(db.Boolean, default=False)  # Indicates access to NLP Model v2
```


#### **Création des formats d'input / output de l'API dans `api_models.py`**

```
py
from flask_restx import fields
from .extensions import api

user_model = api.model("User", { # defining the structure of the User object that gets 'marshalled' in the API
    "id": fields.Integer,
    "username": fields.String,
    "role": fields.String,  # roles: customer / admin
    "nlp_v1": fields.Boolean,  # brings the information of the NLPModels to which the user has access
    "nlp_v2": fields.Boolean
})

user_input_model = api.model("UserInput", {
    "username": fields.String,
    "role": fields.String,  
})

login_model = api.model("LoginModel", {
    "username": fields.String,
    "password": fields.String
})

...
```

#### **Création de `__init__.py`**

```py
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


```

#### **Création des instances de l'API, de la base de données SQL et du JWT manager (sécurité par tokens)**

```py
# file to create and manage Flask-RestX and SQLAlchemy extensions
from flask_sqlalchemy import SQLAlchemy # Database management
from flask_restx import Api  # API creation
from flask_jwt_extended import JWTManager  # Security and authentication


# instantiating the classes, creating extension objects
api = Api()
db = SQLAlchemy()
jwt = JWTManager()

```



#### **Création des routes publiques**

```py
ns_public = Namespace('Rest API - Flask RESTX')


@ns_public.route('/hello')
class Hello(Resource):
    def get(self):
        return {'Welcome': 'NLP Sentiment Predictor API'}

```

#### **Implémentation des routes sécurisées**

Un `Namespace` dédié permet de créer un compte ou se connecter

```py
ns_login = Namespace('Login-Register')

@ns_login.route('/register')
class Register(Resource):
    @ns_login.expect(login_model)
    @ns_login.marshal_with(user_model)
    def post(self):
        user = User(username=ns_login.payload['username'], password_hash=generate_password_hash(ns_login.payload['password']))
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
```

L'espace réservé aux utilisateurs connectés, permettant d'utiliser les modèles, obtenir des infos sur son compte ou réinitialiser son mot de passe

```py
ns_private = Namespace('Logged-Area', authorizations=authorizations)

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
    
```



On implémente la fonctionnalité de l'API  

```py
class NLPSentimentPredictorV1(Resource):
    method_decorators = [jwt_required()]
    @ns_private.expect(prediction_input_model)
    @ns_private.marshal_with(prediction_model_v1)
    @ns_private.doc(security='jsonWebToken')
    def post(self):
        user = User.query.filter_by(username=ns_private.payload['username']).first()
        if user is None:
            ns_private.abort(404, "User not found")
        if not user.access_v1 and 'admin' not in user.role:
            ns_private.abort(403, "Forbidden, user does not have access to NLP Model V1")
            
        text = ns_private.payload['text']
        sentiment, score = predict_sentiment_v1(text)
        
        return {'text': text, 'sentiment': sentiment, 'score': score}, 200
    
    
@ns_private.route('/v2/sentiment')
class NLPSentimentPredictorVader(Resource):
    method_decorators = [jwt_required()]
    @ns_private.expect(prediction_input_model)
    @ns_private.marshal_with(prediction_model_vader)
    @ns_private.doc(security='jsonWebToken')
    def post(self):
        user = User.query.filter_by(username=ns_private.payload['username']).first()
        if user is None:
            ns_private.abort(404, "User not found")
        if not user.access_v1 and 'admin' not in user.role:
            ns_private.abort(403, "Forbidden, user does not have access to NLP Model V1")
            
        text = ns_private.payload['text']
        analysis = predict_sentiment_vader(text)
        
        response =  {
            'text': text, 
            'positive': analysis['pos'],
            'neutral': analysis['neu'], 
            'negative': analysis['neg'],
            'score': analysis['compound'],
            'interpretation': analysis['interpretation']
        }, 200
        
        return response
```

L'espace réservé aux admins permet d'éditer et supprimer un compte, ajouter des accès aux modèles NLP, obtenir une liste des utilisateurs etc.

```py
ns_admin = Namespace('Admin-Only', authorizations=authorizations)

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
```



#### **Modèles d'analyse de sentiment dans `nlp_sentiment.py`** 

```py
import random
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Prédiction aléatoire
def predict_sentiment_v1(text: str):
    prediction = []
    for word in text.split():
        prediction.append(random.uniform(-1, 1))
    result = sum(prediction) / len(text.split())
    if result > 1/6:
        return 'Positive', round(result, 2)
    elif result < -1/6:
        return 'Negative', round(result, 2)
    else:
        return 'Neutral', round(result, 2)


def interpret_vader(score: float):
    if score <= -0.75:
        return 'Very Negative'
    elif score <= -0.25:
        return 'Negative'
    elif score <= -0.05:
        return 'Slightly Negative'
    elif score < 0.05:
        return 'Neutral'
    elif score < 0.25:
        return 'Slightly Positive'
    elif score < 0.75:
        return 'Positive'
    else:
        return 'Very Positive'

# Modèle VADER
def predict_sentiment_vader(text: str):
    analyzer = SentimentIntensityAnalyzer()
    analysis = analyzer.polarity_scores(text)
    analysis['interpretation'] = interpret_vader(analysis['compound'])
    return analysis

```



#### **Scripts d'initialisation**

Initialisation de la DB

```py
import os
import sys

# Calculate the path to the root of the project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the project root to the Python path
sys.path.append(project_root)

from app import db, create_app

def init_db(force=False):
    if force:
        db.drop_all()
    db.create_all()
    print('Database initialized')

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        force = sys.argv[1].lower() == 'true' if len(sys.argv) > 1 else False
        init_db(force)
```

Ajout du premier admin `creator`

```py
import os
import sys

# Calculate the path to the root of the project
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add the project root to the Python path
sys.path.append(project_root)

from app import create_app  
from app.models import User 
from werkzeug.security import generate_password_hash
from app import db

app = create_app()  # Create an instance of the Flask application

def add_creator():
    with app.app_context():  # Push an application context
        password_hash = generate_password_hash('8888')
        creator = User(username='creator', password_hash=password_hash, role='admin')
        db.session.add(creator)
        db.session.commit()

if __name__ == '__main__':
    add_creator()
        
```

Ajout du fichier clients existant, le mot de passe ne sera pas stocké directement sur la base de données créée pour des raisons de sécurité

```py
import os
import sys

# Calculate the path to the root of the project
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add the project root to the Python path
sys.path.append(project_root)

from app import create_app  # Import the Flask application factory
from app.models import User  # Assuming User model is correctly imported in app/__init__.py or models.py
from werkzeug.security import generate_password_hash
from app import db

app = create_app()  # Create an instance of the Flask application

def add_creator():
    with app.app_context():  # Push an application context
        password_hash = generate_password_hash('8888')
        creator = User(username='creator', password_hash=password_hash, role='admin')
        db.session.add(creator)
        db.session.commit()

if __name__ == '__main__':
    add_creator()
```

Création du script `builder.py` qui lance les 3 tâches précédentes

```py
import os
import sys
import subprocess

# Get the directory of this script
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the parent directory to the Python path
sys.path.append(project_root)

# Change the working directory to the script directory
print(project_root)
os.chdir(project_root)

# Run the scripts as separate processes
subprocess.run(['python', 'bin/initialize_db.py'])
subprocess.run(['python', 'bin/confidential/add_creator.py'])
subprocess.run(['python', 'bin/add_customer_base.py'])
```

La base de données ressemble maintenant à cela:

![image-20240306161116580](/home/mln/.config/Typora/typora-user-images/image-20240306161116580.png)





### **Sécurisation de l'API**

#### **1. Authentification et permissions**

- **Objectif**: Seuls les utilisateurs authentifiés peuvent accéder à certaines parties de l'API. Plusieurs niveaux de permissions sont établis pour l'accès aux différents modèles d'analyse de sentiment, ainsi que pour les tâches administrateur. 
- **Implémentation**: Les JWT (JSON Web Token) sont des tokens que l'utilisateur reçoit lorsqu'il se connecte avec ses identifiants. Ce token est ensuite passé dans l'entête des requêtes HTTP pour garantir la légitimité de ses accès aux endpoints protégés.
- **Code**:  L'utilisation des décorateurs de `Namespace` restreignent les accès aux endpoints protégés, le décorateur `@jwt_required` ajoute une couche de sécurité en obligeant la présence d'un token valable dans l'entête.



#### **2. Hachage de mot de passe**

- **Objectif**: Ne pas stocker directement les mots de passe des utilisateurs sur la base de données pour des raisons évidentes de sécurité.  Les administrateurs ne doivent pas non plus avoir accès aux mots de passe d'autres utilisateurs. Le chiffrement des mots de passe doit être suffisamment robuste pour décourager les attaques. 
- **Implémentation**: Nous utilisons les fonctions des fonctionnalités de la librairie `Werkzeug` . Lorsqu'un utilisateur est créé ou modifie son mot de passe, celui ci est haché avant d'être stocké dans la base de données.
- **Référence du code**: Le hachage du mot de passe se fait avec la fonction `generate_password_hash` et la vérification de l'intégrité du mot de passe se fait avec  `check_password_hash`



#### **3. Configuration sécurisée**

- **Objectif**: Préparer l'application à ne pas avoir à stocker des données sensibles dans le code au moment du passage en production. Les clés secrètes doivent être passées en variables d'environnement ou fichier de configuration. 
- **Implémentation**:  Pour les besoins de l'environnement de développement, la configuration sécurisée n'est pas encore implémentée

