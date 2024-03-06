import os
import sys
from werkzeug.security import generate_password_hash

current_directory = os.getcwd()
sys.path.insert(0, current_directory)

from app import create_app, db
from app.models import NLPModel, User

import pandas as pd

app = create_app() # calls the flask app from __init__.py

with app.app_context(): # Push application context (scripted `flask run` session)
    db.create_all() # Create tables
    
    if not NLPModel.query.filter_by(name="V1").first(): # creates a NLPModel instance if V1 not in db yet
        db.session.add(NLPModel(name="V1"))
    if not NLPModel.query.filter_by(name="V2").first():
        db.session.add(NLPModel(name="V2"))
    db.session.commit()
    
    if not User.query.filter_by(username='admin').first():
        admin = User(username='creator', password_hash=generate_password_hash('8888'), role='admin')
        db.session.add(admin)
        db.session.commit()
    
    df = pd.read_csv('data/credentials.csv')
    
    for index, row in df.iterrows(): # loop thru df
        existing_user = User.query.filter_by(username=row['username']).first()
        if existing_user is None:  # Only go forward if this user isn't in the db already
            user = User(username=row['username'], password_hash=generate_password_hash(str(row['password'])), role='customer')
            db.session.add(user) # temporarily add user to the session to avoid the warning at NLPModel decla
            
            model_v1 = NLPModel.query.filter_by(name='V1').first() # if the row has a value for v1 and v1 exists...
            if row['v1'] and model_v1:
                user.nlpmodels.append(model_v1)
                
            model_v2 = NLPModel.query.filter_by(name='V2').first()
            if row['v2'] and model_v2:
                user.nlpmodels.append(model_v2)

            db.session.add(user) # adds the user to the db
    
    db.session.commit() # pushes the changes to the db