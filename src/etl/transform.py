"""
ETL Transform Module

This module handles data transformation and cleaning of job postings.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


def transform_jobs(jobs):
    """
    Transform and clean raw job data from Adzuna API.
    
    Args:
        jobs (list): List of raw job dictionaries from API
        
    Returns:
        dict: Dictionary containing transformed jobs and metadata
    """
    logger.info(f"Starting transformation of {len(jobs)} jobs")
    
    if not jobs:
        logger.warning("No jobs to transform")
        return {
            'success': True,
            'jobs': [],
            'count': 0,
            'transformations_applied': []
        }
    
    try:
        transformations = []
        
        cleaned_jobs = clean_job_data(jobs)
        transformations.append('data_cleaning')
        
        validated_jobs = validate_jobs(cleaned_jobs)
        transformations.append('data_validation')
        
        logger.info(f"Transformation complete: {len(validated_jobs)} valid jobs")
        
        return {
            'success': True,
            'jobs': validated_jobs,
            'count': len(validated_jobs),
            'original_count': len(jobs),
            'removed_count': len(jobs) - len(validated_jobs),
            'transformations_applied': transformations,
            'transformed_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error during transformation: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'jobs': jobs,
            'count': len(jobs)
        }


def clean_job_data(jobs):
    """
    Clean and normalize job data.
    
    Args:
        jobs (list): Raw job dictionaries
        
    Returns:
        list: Cleaned job dictionaries
    """
    cleaned = []
    
    for job in jobs:
        cleaned_job = job.copy()
        
        if 'title' in cleaned_job and cleaned_job['title']:
            cleaned_job['title'] = cleaned_job['title'].strip()
        
        if 'description' in cleaned_job and cleaned_job['description']:
            cleaned_job['description'] = clean_description(cleaned_job['description'])
        
        if 'company' in cleaned_job and isinstance(cleaned_job['company'], dict):
            if 'display_name' in cleaned_job['company']:
                cleaned_job['company']['display_name'] = cleaned_job['company']['display_name'].strip()
        
        if 'location' in cleaned_job and isinstance(cleaned_job['location'], dict):
            if 'area' in cleaned_job['location'] and isinstance(cleaned_job['location']['area'], list):
                cleaned_job['location']['area'] = ', '.join(cleaned_job['location']['area'])
        
        if 'salary_min' in cleaned_job:
            cleaned_job['salary_min'] = normalize_salary(cleaned_job.get('salary_min'))
        
        if 'salary_max' in cleaned_job:
            cleaned_job['salary_max'] = normalize_salary(cleaned_job.get('salary_max'))
        
        cleaned.append(cleaned_job)
    
    return cleaned


def clean_description(description):
    """
    Clean job description text.
    
    Args:
        description (str): Raw description text
        
    Returns:
        str: Cleaned description
    """
    if not description:
        return ''
    
    cleaned = description.strip()
    
    cleaned = ' '.join(cleaned.split())
    
    if len(cleaned) > 5000:
        cleaned = cleaned[:5000] + '...'
    
    return cleaned


def normalize_salary(salary):
    """
    Normalize salary values.
    
    Args:
        salary: Salary value (could be float, int, or None)
        
    Returns:
        float or None: Normalized salary value
    """
    if salary is None:
        return None
    
    try:
        salary_float = float(salary)
        
        if salary_float < 0:
            return None
        
        if salary_float > 1000000:
            return None
        
        return salary_float
    
    except (ValueError, TypeError):
        return None


def validate_jobs(jobs):
    """
    Validate jobs and remove invalid entries.
    
    Args:
        jobs (list): Cleaned job dictionaries
        
    Returns:
        list: Valid job dictionaries
    """
    valid_jobs = []
    
    for job in jobs:
        if is_valid_job(job):
            valid_jobs.append(job)
        else:
            logger.debug(f"Removed invalid job: {job.get('id', 'unknown')}")
    
    return valid_jobs


def is_valid_job(job):
    """
    Check if a job entry is valid.
    
    Args:
        job (dict): Job dictionary
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not job.get('id'):
        return False
    
    if not job.get('title') or len(job.get('title', '').strip()) == 0:
        return False
    
    return True


def jobs_to_dataframe(jobs):
    """
    Convert list of jobs to pandas DataFrame for analysis.
    
    Args:
        jobs (list): List of job dictionaries
        
    Returns:
        pandas.DataFrame: Jobs as DataFrame
    """
    if not jobs:
        return pd.DataFrame()
    
    df = pd.DataFrame(jobs)
    
    return df


def export_to_csv(jobs, filepath='data/processed/jobs.csv'):
    """
    Export transformed jobs to CSV file.
    
    Args:
        jobs (list): List of job dictionaries
        filepath (str): Output file path
        
    Returns:
        bool: True if successful
    """
    try:
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        df = jobs_to_dataframe(jobs)
        
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        logger.info(f"Exported {len(jobs)} jobs to {filepath}")
        return True
        
    except Exception as e:
        logger.error(f"Error exporting to CSV: {str(e)}")
        return False
