import random
import os
import pandas as pd
from faker import Faker

# Calculate the path to the root of the project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

fake = Faker('fr_FR', seed=12)

def generate_customer_base():
    # Define the path for the CSV file where usernames and passwords will be saved
    csv_file_path = os.path.join(project_root, 'data/mock_customer_base.csv')

    data = []
    for i in range(100):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name}.{last_name}" + random.choice(['@gmail.com', '@yahoo.com', '@hotmail.com'])
        address = fake.address()
        password = random.randint(1000, 9999)
        entity = random.choice([fake.company(), 'individual'])
        role = 'customer'
        usage_purpose = random.choice(['stock_market', 'reviews', 'news'])

        access_v1 = random.choice([True, False])
        access_v2 = random.choice([True, False])
        access_v3 = random.choice([True, False])

        # Append the user data to the data list
        data.append({
            'username': f"{first_name}.{last_name}",
            'password': password,
            'email': email,
            'address': address,
            'entity': entity,
            'role': role,
            'usage_purpose': usage_purpose,
            'v1': access_v1,
            'v2': access_v2,
            'v3': access_v3
        })

    # Create a DataFrame from the data list
    df = pd.DataFrame(data)

    # Write the DataFrame to a CSV file
    df.to_csv(csv_file_path, index=False)

if __name__ == "__main__":
    generate_customer_base()