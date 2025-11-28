"""
ETL Load Module

This module handles loading transformed job data into PostgreSQL database.
"""

from datetime import datetime
from src.db.repository import save_jobs, get_job_count
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


def load_jobs_to_database(jobs):
    """
    Load transformed jobs into PostgreSQL database.
    
    Args:
        jobs (list): List of transformed job dictionaries
        
    Returns:
        dict: Load statistics and results
    """
    logger.info(f"Starting database load of {len(jobs)} jobs")
    
    if not jobs:
        logger.warning("No jobs to load")
        return {
            'success': True,
            'jobs_loaded': 0,
            'jobs_skipped': 0,
            'errors': 0,
            'message': 'No jobs to load'
        }
    
    try:
        result = save_jobs(jobs)
        
        logger.info(
            f"Load complete: {result['saved']} saved, "
            f"{result['skipped']} skipped, "
            f"{result['errors']} errors"
        )
        
        return {
            'success': True,
            'jobs_loaded': result['saved'],
            'jobs_skipped': result['skipped'],
            'errors': result['errors'],
            'error_details': result.get('error_details', []),
            'total_jobs_in_db': get_job_count(),
            'loaded_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error loading jobs to database: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'jobs_loaded': 0,
            'jobs_skipped': 0,
            'errors': len(jobs)
        }


def validate_database_connection():
    """
    Validate that database connection is working.
    
    Returns:
        dict: Connection status
    """
    try:
        count = get_job_count()
        
        return {
            'success': True,
            'message': f'Database connection successful. Current job count: {count}',
            'job_count': count
        }
        
    except Exception as e:
        logger.error(f"Database connection validation failed: {str(e)}")
        return {
            'success': False,
            'message': f'Database connection failed: {str(e)}'
        }


def get_load_statistics():
    """
    Get statistics about loaded data in the database.
    
    Returns:
        dict: Database statistics
    """
    try:
        from src.db.repository import get_job_statistics
        
        stats = get_job_statistics()
        
        return {
            'success': True,
            'statistics': stats
        }
        
    except Exception as e:
        logger.error(f"Error getting load statistics: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }
