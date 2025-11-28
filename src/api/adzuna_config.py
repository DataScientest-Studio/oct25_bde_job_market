"""
Adzuna API Field Mapping Configuration

This module defines how Adzuna API response fields map to PostgreSQL database columns.
Modify this configuration to change which fields are extracted and stored without
changing any other code in the application.

FIELD_MAPPING structure:
    - Key: Database column name (from models.Job)
    - Value: Dot-notation path to field in Adzuna API response
    
Example Adzuna API response structure:
{
    "id": "1234567",
    "title": "Python Developer",
    "company": {
        "display_name": "Tech Company GmbH"
    },
    "location": {
        "display_name": "Berlin",
        "area": ["Germany", "Berlin"]
    },
    "description": "Job description text...",
    "salary_min": 50000,
    "salary_max": 70000,
    "contract_type": "permanent",
    "contract_time": "full_time",
    "category": {
        "label": "IT Jobs",
        "tag": "it-jobs"
    },
    "redirect_url": "https://...",
    "created": "2024-01-15T10:30:00Z"
}
"""

FIELD_MAPPING = {
    'adzuna_id': 'id',
    'title': 'title',
    'company': 'company.display_name',
    'location': 'location.display_name',
    'location_area': 'location.area',
    'description': 'description',
    'salary_min': 'salary_min',
    'salary_max': 'salary_max',
    'salary_currency': 'salary_currency',
    'contract_type': 'contract_type',
    'contract_time': 'contract_time',
    'category_label': 'category.label',
    'category_tag': 'category.tag',
    'redirect_url': 'redirect_url',
    'created_date': 'created'
}


API_SEARCH_PARAMS = {
    'country': 'de',
    'results_per_page': 50,
    'sort_by': 'date',
    'content-type': 'application/json'
}


API_ENDPOINTS = {
    'base_url': 'https://api.adzuna.com/v1/api',
    'search': '/jobs/{country}/search/{page}',
    'job_details': '/jobs/{country}/view/{id}'
}


def get_search_endpoint(country='de', page=1):
    """
    Get the full URL for job search endpoint.
    
    Args:
        country (str): Country code (default: 'de' for Germany)
        page (int): Page number for pagination
        
    Returns:
        str: Full API endpoint URL
    """
    base = API_ENDPOINTS['base_url']
    path = API_ENDPOINTS['search'].format(country=country, page=page)
    return base + path


def get_job_details_endpoint(country='de', job_id=''):
    """
    Get the full URL for job details endpoint.
    
    Args:
        country (str): Country code (default: 'de' for Germany)
        job_id (str): Adzuna job ID
        
    Returns:
        str: Full API endpoint URL
    """
    base = API_ENDPOINTS['base_url']
    path = API_ENDPOINTS['job_details'].format(country=country, id=job_id)
    return base + path
