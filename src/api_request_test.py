import requests
from pprint import pprint

base_url = "http://localhost:8000"

# Check functionaity
url = base_url + "/health"

print(requests.get(url).json())

# Start ingestion pipeline
url = base_url + "/data"

print(requests.put(url, params={"max_pages": 1}).json())

# Trigger training
url = base_url + "/training"

print(requests.get(url).json())

# Get Postings
url = base_url + "/data/postings"

parameters = {
    "columns":["company_name"]
}

pprint(requests.get(url, params=parameters).json())

# Get Predictions
url = base_url + "/data/predictions"

parameters = {
    "job_title": "Senior Python Developer",
    "job_description": """
    We are looking for a Senior Python Developer with 5+ years experience.
    Skills required: Python, AWS, Machine Learning.
    Remote work possible.
    """,
    "city":"Berlin",
    "contract_type":"Permanent",
    "contract_time":"Full Time"
}

pprint(requests.get(url, params=parameters).json())
