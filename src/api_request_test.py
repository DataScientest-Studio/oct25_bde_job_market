import requests
from pprint import pprint

base_url = "http://localhost:8000"

# Check functionaity
url = base_url + "/health"

print(requests.get(url).json())

# Start ingestion pipeline
url = base_url + "/data"

print(requests.put(url).json())

# Get Postings
url = base_url + "/data/postings"

parameters = {
    "columns":["job_id", "longitude", "company_name"]
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
    """
}

pprint(requests.get(url, params=parameters).json())
