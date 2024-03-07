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
        
    def create_mock_user(self, username, password, role, access_v1=True, access_v2=True, access_v3=True):
        from app.models import User
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash(password)
        user = User(username=username, password_hash=password_hash, role=role, access_v1=access_v1, access_v2=access_v2)
        db.session.add(user)
        db.session.commit()
        


class PublicRoutesTestCase(BaseTestCase):
    def setUp(self):
        print("Setting up PublicRoutesTestCase")
        super().setUp()

    def test_hello_route(self):
        print("Testing hello route")
        response = self.client.get('/public/hello')
        print(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        print(f"Response data: {data}")
        self.assertEqual(data['Welcome'], 'NLP Sentiment Predictor API')

class LoginRegisterRoutesTestCase(BaseTestCase):
    def setUp(self):
        print("Setting up LoginRegisterRoutesTestCase")
        super().setUp()
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword'
        }

    def test_register_route(self):
        print("Testing register route")
        response = self.client.post('/auth/register', json=self.user_data)
        print(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        print(f"Response data: {data}")
        self.assertEqual(data['username'], self.user_data['username'])
        self.assertEqual(data['role'], 'customer')

    def test_login_route(self):
        print("Testing login route")
        self.client.post('/auth/register', json=self.user_data)
        response = self.client.post('/auth/login', json=self.user_data)
        print(f"Response status code: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        print(f"Response data: {data}")
        self.assertIn('access token', data)

class PrivateRoutesTestCase(BaseTestCase):
    def setUp(self):
        print("Setting up PrivateRoutesTestCase")
        super().setUp()
        self.user_data = {
            'username': 'admin1',
            'password': '8888',
            'role': 'admin',
        }
        self.create_mock_user(self.user_data['username'], self.user_data['password'], self.user_data['role'])
        response = self.client.post('/auth/login', json=self.user_data)
        self.token = json.loads(response.data)['access token']
        print(f"Access token: {self.token}")
        decoded_token = jwt.decode(self.token, options={"verify_signature": False})
        print(f"Decoded token: {decoded_token}")

    def test_v1_sentiment_route(self):
        print("Testing v1 sentiment route")
        headers = {'Authorization': f"Bearer {self.token}"}
        response = self.client.post('/private/v1/sentiment', json={'username': 'admin1', 'text': 'I would have loved this movie, if I was super stupid'}, headers=headers)
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        print(f"Response data: {data}")
        self.assertIn('sentiment', data)
        self.assertIn('score', data)

    def test_v2_sentiment_route(self):
        print("Testing v2 sentiment route")
        headers = {'Authorization': f"Bearer {self.token}"}
        response = self.client.post('/private/v2/sentiment', json={'username': 'admin1', 'text': 'I would have loved this movie, if I was super stupid'}, headers=headers)
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        print(f"Response data: {data}")
        self.assertIn('positive', data)
        self.assertIn('neutral', data)
        self.assertIn('negative', data)
        self.assertIn('score', data)
        self.assertIn('interpretation', data)