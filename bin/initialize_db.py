import os
import sys

# Calculate the path to the root of the project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
        
        
