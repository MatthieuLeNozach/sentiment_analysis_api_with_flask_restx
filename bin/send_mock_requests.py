import requests
import pandas as pd
import random
import os
import sys
cwd = os.getcwd()

def main():
    # Ensure the project root is in the path for correct imports
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(project_root)

    users_df = pd.read_csv('data/mock_customer_base.csv')
    users_df['password'] = users_df['password'].astype(str)
    users_df = users_df[users_df['v2'] == 1]
    
    yelp_df = pd.read_csv('tests/yelp_text.csv')
    texts = pd.Series(yelp_df.iloc[:, 0])
    print(texts.head())

    for i, user in users_df.iterrows():
        login_url = 'http://localhost:5000/auth/login'
        login_data = {
            'username': user['username'],
            'password': user['password']
        }

        response = requests.post(login_url, json=login_data)
        print('\n\n', "response.json:", response.json())
        token = response.json()['access token']
        
        sentiment_url = 'http://localhost:5000/private/v2/sentiment'
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'username': user['username'],
            'text': random.choice(texts)
        }
        
        response = requests.post(sentiment_url, headers=headers, json=data)
        print(response.json())

if __name__ == '__main__':
    main()