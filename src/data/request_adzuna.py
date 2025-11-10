import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the environment variables
API_URL = os.getenv("API_URL")
API_ID = os.getenv("API_ID")
API_KEY = os.getenv("API_KEY")

params = {
    "app_id": API_ID,
    "app_key": API_KEY,
    "category": "it-jobs"
}

page_number = 1

while True:
    url = f"{API_URL}{page_number}"
    response = requests.get(url, params=params)
    page_number += 1

    print(response.json())
    if not response.ok:
        print(f"End at page {page_number}")
        break 






