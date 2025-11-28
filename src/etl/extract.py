"""
ETL Extract Module

This module handles data extraction from the Adzuna API.
"""

import json
import os
from datetime import datetime
from src.api.adzuna_client import search_jobs, fetch_multiple_pages, AdzunaAPIError
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


def extract_jobs(
    what='',
    where='',
    max_pages=1,
    results_per_page=50,
    sort_by='date',
    country='de',
    save_raw=True
):
    """
    Extract job postings from Adzuna API.
    
    Args:
        what (str): Job title or keywords to search for
        where (str): Location to search in
        max_pages (int): Maximum number of pages to fetch
        results_per_page (int): Number of results per page (max 50)
        sort_by (str): Sort order ('date', 'relevance', 'salary')
        country (str): Country code (default: 'de' for Germany)
        save_raw (bool): Whether to save raw JSON response to file
        
    Returns:
        dict: Dictionary containing extracted jobs and metadata
    """
    logger.info(f"Starting job extraction: what='{what}', where='{where}', pages={max_pages}")
    
    try:
        if max_pages == 1:
            response = search_jobs(
                what=what,
                where=where,
                page=1,
                results_per_page=results_per_page,
                sort_by=sort_by,
                country=country
            )
            
            jobs = response['results']
            total_count = response['count']
            pages_fetched = 1
            
        else:
            response = fetch_multiple_pages(
                what=what,
                where=where,
                max_pages=max_pages,
                results_per_page=results_per_page,
                sort_by=sort_by,
                country=country
            )
            
            jobs = response['results']
            total_count = response['total_count']
            pages_fetched = response['pages_fetched']
        
        logger.info(f"Extracted {len(jobs)} jobs from {pages_fetched} pages")
        
        if save_raw and jobs:
            save_raw_data(jobs, what, where)
        
        return {
            'success': True,
            'jobs': jobs,
            'count': len(jobs),
            'total_available': total_count,
            'pages_fetched': pages_fetched,
            'search_params': {
                'what': what,
                'where': where,
                'sort_by': sort_by,
                'country': country
            },
            'extracted_at': datetime.now().isoformat()
        }
        
    except AdzunaAPIError as e:
        logger.error(f"API error during extraction: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'jobs': [],
            'count': 0
        }
    
    except Exception as e:
        logger.error(f"Unexpected error during extraction: {str(e)}")
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}",
            'jobs': [],
            'count': 0
        }


def save_raw_data(jobs, what='', where=''):
    """
    Save raw job data to JSON file in data/raw directory.
    
    Args:
        jobs (list): List of job dictionaries
        what (str): Search keywords (for filename)
        where (str): Search location (for filename)
    """
    try:
        os.makedirs('data/raw', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        what_clean = what.replace(' ', '_')[:30] if what else 'all'
        where_clean = where.replace(' ', '_')[:30] if where else 'germany'
        
        filename = f"adzuna_jobs_{what_clean}_{where_clean}_{timestamp}.json"
        filepath = os.path.join('data/raw', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'extracted_at': datetime.now().isoformat(),
                'search_params': {'what': what, 'where': where},
                'count': len(jobs),
                'jobs': jobs
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Raw data saved to {filepath}")
        
    except Exception as e:
        logger.error(f"Error saving raw data: {str(e)}")


def load_raw_data(filepath):
    """
    Load raw job data from JSON file.
    
    Args:
        filepath (str): Path to JSON file
        
    Returns:
        list: List of job dictionaries
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('jobs', [])
    
    except Exception as e:
        logger.error(f"Error loading raw data: {str(e)}")
        return []
