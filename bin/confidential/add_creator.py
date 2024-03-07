import os
import sys

# Calculate the path to the root of the project
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root) # Add the project root to the Python path

from app import create_app  # Import the Flask application factory
from app.models import User 
from werkzeug.security import generate_password_hash
from app import db

app = create_app()

def add_creator():
    with app.app_context():  # Push an application context
        password_hash = generate_password_hash('8888')
        creator = User(username='creator', password_hash=password_hash, role='admin')
        db.session.add(creator)
        db.session.commit()

if __name__ == '__main__':
    add_creator()
    
    

    