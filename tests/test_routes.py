import unittest
import json
import sys
import os
import jwt

# Ensure the project root is in the path for correct imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app import create_app, db


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(testing=True)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def create_mock_user(self, username, password, role, access_v1=True, access_v2=True):
        from app.models import User
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash(password)
        user = User(username=username, password_hash=password_hash, role=role, access_v1=access_v1, access_v2=access_v2)
        db.session.add(user)
        db.session.commit()
        




class PublicRoutesTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_hello_route(self):
        # Adjust the URL to include the namespace prefix 'public'
        response = self.client.get('/public/hello')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['Welcome'], 'NLP Sentiment Predictor API')


class LoginRegisterRoutesTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword'
        }

    def test_register_route(self):
        # Adjust the URL to include the namespace prefix 'auth'
        response = self.client.post('/auth/register', json=self.user_data)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['username'], self.user_data['username'])
        self.assertEqual(data['role'], 'customer')

    def test_login_route(self):
        # Register the user with the adjusted URL
        self.client.post('/auth/register', json=self.user_data)
        # Adjust the URL for login as well
        response = self.client.post('/auth/login', json=self.user_data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access token', data)
        
        
        
class LoginRegisterRoutesTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword'
        }

    def test_register_route(self):
        # Adjust the URL to include the namespace prefix 'auth'
        response = self.client.post('/auth/register', json=self.user_data)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['username'], self.user_data['username'])
        self.assertEqual(data['role'], 'customer')

    def test_login_route(self):
        # Register the user with the adjusted URL
        self.client.post('/auth/register', json=self.user_data)
        # Adjust the URL for login as well
        response = self.client.post('/auth/login', json=self.user_data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('access token', data)
        
        
class PrivateRoutesTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        
        self.user_data = {
            'username': 'Megan', # Customer having access to all models
            'password': '6837',
            'role': 'customer'
        }
        
        self.create_mock_user(self.user_data['username'], self.user_data['password'], self.user_data['role'])
        
        response = self.client.post('/auth/login', json=self.user_data)
        self.token = json.loads(response.data)['access token']
        print(self.token)
        decoded_token = jwt.decode(self.token, options={"verify_signature": False})
        print(decoded_token)
        
        
    def test_v1_sentiment_route(self):
        headers = {'Authorization': f"Bearer {self.token}"}
        response = self.client.post('/private/v1/sentiment', json={'username': 'Megan', 'text': 'I would have loved this movie, if I was super stupid'}, headers=headers)
        print(response.data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('sentiment', data)
        self.assertIn('score', data)
        
        
        
    def test_v2_sentiment_route(self):
        headers = {'Authorization': f"Bearer {self.token}"}
        response = self.client.post('/private/v2/sentiment', json={'username': 'Megan', 'text': 'I would have loved this movie, if I was super stupid'}, headers=headers)
        print(response.data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('positive', data)
        self.assertIn('neutral', data)
        self.assertIn('negative', data)
        self.assertIn('score', data)
        self.assertIn('interpretation', data)