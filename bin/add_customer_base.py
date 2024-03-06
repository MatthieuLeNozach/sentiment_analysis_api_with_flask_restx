# add_customer_base.py

import os
import sys
import pandas as pd
from werkzeug.security import generate_password_hash

# Calculate the path to the root of the project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the project root to the Python path
sys.path.append(project_root)

from app import db, create_app
from app.models import User

def add_customer_base():
    # Load your DataFrame here, e.g., from a CSV file
    df = pd.read_csv('data/credentials.csv')
    
    for index, row in df.iterrows():
        existing_user = User.query.filter_by(username=row['username']).first()
        if existing_user is None:
            user = User(
                username=row['username'], 
                password_hash=generate_password_hash(str(row['password'])), 
                role='customer',
                access_v1=row['v1'],  # Assuming these columns exist in your CSV
                access_v2=row['v2']
            )
            db.session.add(user)

    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        add_customer_base()