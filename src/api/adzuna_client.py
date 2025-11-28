import os
import requests
from dotenv import load_dotenv
from src.api.adzuna_config import get_search_endpoint, API_SEARCH_PARAMS

load_dotenv()


class AdzunaAPIError(Exception):
    """Custom exception for Adzuna API errors."""
    pass


def get_api_credentials():
    """
    Get Adzuna API credentials from environment variables.
    
    Returns:
        tuple: (app_id, app_key)
        
    Raises:
        ValueError: If credentials are not found in environment
    """
    app_id = os.getenv('ADZUNA_APP_ID')
    app_key = os.getenv('ADZUNA_APP_KEY')
    
    if not app_id or not app_key:
        raise ValueError(
            "Adzuna API credentials not found. "
            "Please set ADZUNA_APP_ID and ADZUNA_APP_KEY in your .env file."
        )
    
    return app_id, app_key


def search_jobs(
    what='',
    where='',
    page=1,
    results_per_page=50,
    sort_by='date',
    country='de',
    timeout=30
):
    """
    Search for jobs using the Adzuna API.
    
    Args:
        what (str): Job title or keywords (optional)
        where (str): Location (optional)
        page (int): Page number for pagination (default: 1)
        results_per_page (int): Number of results per page (default: 50, max: 50)
        sort_by (str): Sort order ('date', 'relevance', 'salary') (default: 'date')
        country (str): Country code (default: 'de' for Germany)
        timeout (int): Request timeout in seconds (default: 30)
        
    Returns:
        dict: API response containing job listings
        
    Raises:
        AdzunaAPIError: If API request fails
    """
    try:
        app_id, app_key = get_api_credentials()
        
        endpoint = get_search_endpoint(country=country, page=page)
        
        params = {
            'app_id': app_id,
            'app_key': app_key,
            'results_per_page': min(results_per_page, 50),
            'sort_by': sort_by
        }
        
        if what:
            params['what'] = what
        
        if where:
            params['where'] = where
        
        response = requests.get(endpoint, params=params, timeout=timeout)
        
        response.raise_for_status()
        
        data = response.json()
        
        return {
            'success': True,
            'count': data.get('count', 0),
            'results': data.get('results', []),
            'page': page,
            'total_pages': (data.get('count', 0) // results_per_page) + 1
        }
        
    except requests.exceptions.Timeout:
        raise AdzunaAPIError(f"Request timeout after {timeout} seconds")
    
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        if status_code == 401:
            raise AdzunaAPIError("Invalid API credentials")
        elif status_code == 429:
            raise AdzunaAPIError("API rate limit exceeded")
        elif status_code == 404:
            raise AdzunaAPIError("API endpoint not found")
        else:
            raise AdzunaAPIError(f"HTTP error {status_code}: {str(e)}")
    
    except requests.exceptions.ConnectionError:
        raise AdzunaAPIError("Connection error - please check your internet connection")
    
    except requests.exceptions.RequestException as e:
        raise AdzunaAPIError(f"Request failed: {str(e)}")
    
    except ValueError as e:
        raise AdzunaAPIError(f"Invalid JSON response: {str(e)}")
    
    except Exception as e:
        raise AdzunaAPIError(f"Unexpected error: {str(e)}")


def fetch_multiple_pages(
    what='',
    where='',
    max_pages=5,
    results_per_page=50,
    sort_by='date',
    country='de'
):
    """
    Fetch multiple pages of job listings.
    
    Args:
        what (str): Job title or keywords
        where (str): Location
        max_pages (int): Maximum number of pages to fetch
        results_per_page (int): Results per page
        sort_by (str): Sort order
        country (str): Country code
        
    Returns:
        dict: Combined results from all pages
    """
    all_results = []
    total_count = 0
    pages_fetched = 0
    
    for page in range(1, max_pages + 1):
        try:
            response = search_jobs(
                what=what,
                where=where,
                page=page,
                results_per_page=results_per_page,
                sort_by=sort_by,
                country=country
            )
            
            if response['success']:
                all_results.extend(response['results'])
                total_count = response['count']
                pages_fetched += 1
                
                if len(response['results']) == 0:
                    break
            else:
                break
                
        except AdzunaAPIError as e:
            print(f"Error fetching page {page}: {str(e)}")
            break
    
    return {
        'success': True,
        'total_count': total_count,
        'results': all_results,
        'pages_fetched': pages_fetched
    }


def test_api_connection():
    """
    Test the Adzuna API connection with a simple request.
    
    Returns:
        dict: Test result with status and message
    """
    try:
        result = search_jobs(
            what='Python',
            where='Berlin',
            page=1,
            results_per_page=1
        )
        
        return {
            'success': True,
            'message': f"API connection successful! Found {result['count']} jobs.",
            'sample_count': result['count']
        }
        
    except AdzunaAPIError as e:
        return {
            'success': False,
            'message': f"API connection failed: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'message': f"Unexpected error: {str(e)}"
        }
