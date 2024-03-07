import unittest
import sys
import os
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy import inspect
from werkzeug.security import check_password_hash


# Correctly set the project root to ensure imports work as expected
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app import create_app, db  # Correctly import create_app and db

class InitializeDBTest(unittest.TestCase):
    def setUp(self):
        # Setup app with test configuration
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_db_initialization(self):
        from bin.initialize_db import init_db
        init_db(force=True)  # Force re-initialization if needed

        # Use SQLAlchemy's inspect function to get table names
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        self.assertIn('user', tables, "User table should exist after initialization")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)


class AddCreatorTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_add_creator(self):
        from bin.confidential.add_creator import add_creator
        from app.models import User
        add_creator()
        
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        # Check if the user 'creator' with the role 'admin' and hashed password exists
        creator = User.query.filter_by(username='creator').first()
        self.assertIsNotNone(creator, "User 'creator' should exist")
        self.assertEqual(creator.role, 'admin', "User 'creator' should have role 'admin'")
        self.assertTrue(check_password_hash(creator.password_hash, '8888'), "User 'creator' password should be correctly hashed")
        
        
        
import pandas as pd
import os
from werkzeug.security import check_password_hash
from bin.add_customer_base import add_customer_base
from app.models import User

class AddCustomerBaseTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_customer_base(self):
        # Load the CSV file and count the number of rows
        csv_path = os.path.join(os.path.dirname(__file__), '../data/credentials.csv')
        df = pd.read_csv(csv_path)
        print(df.head(10))  # Print the first 10 rows of the CSV

        initial_user_count = User.query.count()
        add_customer_base()
        db.session.commit()
        # Count the number of users in the database again
        final_user_count = User.query.count()

        # Check if the number of users has increased by the number of rows in the CSV
        self.assertEqual(final_user_count - initial_user_count, len(df))

        # Check each user in the database
        for index, row in df.iterrows():
            user = User.query.filter_by(username=row['username']).first()
            self.assertIsNotNone(user, f"User '{row['username']}' should exist")
            self.assertEqual(user.access_v1, row['v1'])
            self.assertEqual(user.access_v2, row['v2'])
            self.assertTrue(check_password_hash(user.password_hash, str(row['password'])), f"User '{row['username']}' password should be correctly hashed")

        # Print the first 10 rows of the database
        print(User.query.limit(10).all())
