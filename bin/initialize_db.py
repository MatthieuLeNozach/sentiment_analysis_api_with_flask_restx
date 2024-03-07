import os
import sys

# Calculate the path to the root of the project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
print("project_root from initializa_db.py", project_root, end='\n\n')

from app import db, create_app
from app.models import User

def initialize_db(force=False):
    app = create_app()
    with app.app_context():
        if force:
            db.session.remove()  # Remove any existing sessions
            db.metadata.clear()  # Clear any existing metadata
            db.drop_all()  # Drop the existing database

        db.create_all()  # Create the new database
        print('Database initialized')

if __name__ == "__main__":
    force = sys.argv[1].lower() == 'true' if len(sys.argv) > 1 else False
    initialize_db(force)