from google.cloud import storage

import requests
import time
import random

# Configuration
LB_IP = "34.174.36.129"  # Replace with your Load Balancer Frontend IP
PORT = "8080"
URL = f"http://{LB_IP}:{PORT}"

# Sample data for testing
FILES = ["index.html", "data.parquet", "missing_file.txt", "secret.pdf"]
METHODS = ["GET", "POST", "PUT", "DELETE"]
COUNTRIES = ['United States', 'Canada', 'Mexico', 'Peru', 'France', 'Germany', 'Spain', 'Portugal', 'Luxembourg', 'North Korea', 'Iran', 'Cuba', 'Myanmar', 'Iraq', 'Libya', 'Sudan', 'Zimbabwe', 'Syria']
GENDER = ['Male', 'Female', 'Other']
INCOME = ['0-10k', '10k-20k', '20k-40k', '40k-60k', '60k-100k', '100k-150k', '150k-250k', '250k+']

def start_client():
    print(f"Starting client, targeting {URL}...")
    
    while True:
        # 1. Randomize request parameters
        target_file = f"?file=files/{random.randint(-10, 20042)}.html"
        method = random.choice(METHODS)
        country = random.choice(COUNTRIES)
        age = random.randint(1, 100) 
        gender = random.choice(GENDER)
        income = random.choice(INCOME)
        # 2. Prepare headers (including the required country header)
        headers = {
            "X-Country": country,
            "X-Age": str(age),
            "X-Gender": gender,
            "X-Income": income
        }

        try:
            # 3. Execute the request
            # Note: methods like POST/DELETE might return 405 if not implemented
            response = requests.request(
                method=method,
                url=f"{URL}/{target_file}",
                headers=headers,
                timeout=5
            )

            # 4. Extract the zone header sent by your server
            server_zone = response.headers.get("Server Zone")
            
            print(f"[{method}] File: {target_file:15} | Status: {response.status_code} | "
                  f"Country: {country} | Zone: {server_zone}")

        except requests.exceptions.RequestException as e:
            print(f"Connection Error: {e}")

        # 5. Frequency requirement: 1 request per second
        time.sleep(1)
        
if __name__ == "__main__":
    start_client()