import unittest
import json
import sys
import os
import jwt
import pandas as pd
# Ensure the project root is in the path for correct imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
print(os.getcwd())

css = """
<style type=\"text/css\">
table {
border-collapse: collapse;
width: 100%;
color: #588c7e;
font-family: monospace;
font-size: 25px;
text-align: left;
}
th {
background-color: #588c7e;
color: white;
}
tr:nth-child(even) {background-color: #f2f2f2}
</style>
"""


print(project_root)
reviews = pd.read_csv('tests/yelp_text.csv')




from app import create_app, db
from .test_routes import BaseTestCase



class PrivateRoutesTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        
        self.user_data = {
            'username': 'admin1', # Customer having access to all models
            'password': '8888',
            'role': 'admin',
        }
        
        self.create_mock_user(self.user_data['username'], self.user_data['password'], self.user_data['role'])
        
        response = self.client.post('/auth/login', json=self.user_data)
        self.token = json.loads(response.data)['access token']
        print(self.token)
        decoded_token = jwt.decode(self.token, options={"verify_signature": False})
        print(decoded_token)
        
        
    def test_sentiment_binary_v1(self):
        review_sample = reviews.sample(20)

        for _, sample in review_sample.iterrows():
            headers = {'Authorization': f"Bearer {self.token}"}
            response_v1 = self.client.post('/private/v1/sentiment', json={'text': sample[0]}, headers=headers)
            print(response_v1.data)

    def test_sentiment_binary_vader(self):
        review_sample = reviews.sample(20)
        print(review_sample.info())
        results = []
        

        for _, sample in review_sample.iterrows():
            headers = {'Authorization': f"Bearer {self.token}"}
            response_vader = self.client.post('/private/v2/sentiment', json={'text': sample.iloc[0]}, headers=headers)
            response_data = json.loads(response_vader.data.decode('utf-8'))
            result_binary = 1 if response_data['score'] > 0 else 0

            expected_result = int(sample.iloc[1])
            if result_binary != expected_result:
                print(f"Warning: Expected {expected_result} but got {result_binary} for text: {sample.iloc[0]}")

            results.append([sample.iloc[0], response_data['score'], result_binary, expected_result])

        results_df = pd.DataFrame(results, columns=['Text', 'Score', 'Result', 'Expected'])
        html_table = results_df.to_html()

        with open('tests/vader_results.html', 'w') as f:
            f.write(css)
            f.write(html_table)
        
        
if __name__ == '__main__':
    unittest.main()