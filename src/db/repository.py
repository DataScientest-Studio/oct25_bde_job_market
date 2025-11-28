from sqlalchemy.exc import IntegrityError
from datetime import datetime
from src.db.db_config import get_session
from src.db.models import Job
from src.api.adzuna_config import FIELD_MAPPING


def map_adzuna_to_job(adzuna_job):
    """
    Map Adzuna API response to Job model fields using the field mapping configuration.
    
    Args:
        adzuna_job (dict): Job data from Adzuna API
        
    Returns:
        dict: Mapped job data ready for database insertion
    """
    job_data = {}
    
    for db_field, api_path in FIELD_MAPPING.items():
        value = adzuna_job
        
        for key in api_path.split('.'):
            if isinstance(value, dict):
                value = value.get(key)
            else:
                value = None
                break
        
        job_data[db_field] = value
    
    job_data['raw_json'] = adzuna_job
    
    if job_data.get('created_date') and isinstance(job_data['created_date'], str):
        try:
            job_data['created_date'] = datetime.fromisoformat(job_data['created_date'].replace('Z', '+00:00'))
        except:
            job_data['created_date'] = None
    
    return job_data


def save_job(job_data):
    """
    Save a single job to the database.
    
    Args:
        job_data (dict): Mapped job data
        
    Returns:
        Job: Saved job object, or None if error occurred
    """
    session = get_session()
    
    try:
        job = Job(**job_data)
        session.add(job)
        session.commit()
        session.refresh(job)
        return job
    except IntegrityError:
        session.rollback()
        return None
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def save_jobs(jobs_list):
    """
    Save multiple jobs to the database using the field mapping configuration.
    Skips duplicates based on adzuna_id.
    
    Args:
        jobs_list (list): List of job dictionaries from Adzuna API
        
    Returns:
        dict: Statistics about the save operation
    """
    session = get_session()
    
    saved_count = 0
    skipped_count = 0
    error_count = 0
    errors = []
    
    try:
        for adzuna_job in jobs_list:
            try:
                job_data = map_adzuna_to_job(adzuna_job)
                
                existing_job = session.query(Job).filter_by(
                    adzuna_id=job_data['adzuna_id']
                ).first()
                
                if existing_job:
                    skipped_count += 1
                    continue
                
                job = Job(**job_data)
                session.add(job)
                saved_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(str(e))
        
        session.commit()
        
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
    
    return {
        'saved': saved_count,
        'skipped': skipped_count,
        'errors': error_count,
        'error_details': errors[:10]
    }


def get_all_jobs(limit=100, offset=0):
    """
    Retrieve all jobs from database with pagination.
    
    Args:
        limit (int): Maximum number of jobs to return
        offset (int): Number of jobs to skip
        
    Returns:
        list: List of Job objects
    """
    session = get_session()
    
    try:
        jobs = session.query(Job).order_by(Job.created_at.desc()).limit(limit).offset(offset).all()
        return jobs
    finally:
        session.close()


def get_job_by_id(job_id):
    """
    Retrieve a specific job by its database ID.
    
    Args:
        job_id (int): Job database ID
        
    Returns:
        Job: Job object or None
    """
    session = get_session()
    
    try:
        job = session.query(Job).filter_by(id=job_id).first()
        return job
    finally:
        session.close()


def get_job_by_adzuna_id(adzuna_id):
    """
    Retrieve a specific job by its Adzuna ID.
    
    Args:
        adzuna_id (str): Adzuna job ID
        
    Returns:
        Job: Job object or None
    """
    session = get_session()
    
    try:
        job = session.query(Job).filter_by(adzuna_id=adzuna_id).first()
        return job
    finally:
        session.close()


def get_job_count():
    """
    Get total number of jobs in database.
    
    Returns:
        int: Total job count
    """
    session = get_session()
    
    try:
        count = session.query(Job).count()
        return count
    finally:
        session.close()


def get_job_statistics():
    """
    Get statistics about jobs in the database.
    
    Returns:
        dict: Dictionary containing various statistics
    """
    session = get_session()
    
    try:
        from sqlalchemy import func
        
        total_jobs = session.query(Job).count()
        
        jobs_with_salary = session.query(Job).filter(
            Job.salary_min.isnot(None)
        ).count()
        
        unique_companies = session.query(func.count(func.distinct(Job.company))).scalar()
        
        unique_locations = session.query(func.count(func.distinct(Job.location))).scalar()
        
        top_categories = session.query(
            Job.category_label,
            func.count(Job.id).label('count')
        ).group_by(Job.category_label).order_by(func.count(Job.id).desc()).limit(5).all()
        
        return {
            'total_jobs': total_jobs,
            'jobs_with_salary': jobs_with_salary,
            'unique_companies': unique_companies,
            'unique_locations': unique_locations,
            'top_categories': [(cat, count) for cat, count in top_categories if cat]
        }
    finally:
        session.close()


def delete_job(job_id):
    """
    Delete a job from the database.
    
    Args:
        job_id (int): Job database ID
        
    Returns:
        bool: True if deleted, False if not found
    """
    session = get_session()
    
    try:
        job = session.query(Job).filter_by(id=job_id).first()
        if job:
            session.delete(job)
            session.commit()
            return True
        return False
    finally:
        session.close()


def delete_all_jobs():
    """
    Delete all jobs from the database.
    WARNING: This cannot be undone!
    
    Returns:
        int: Number of jobs deleted
    """
    session = get_session()
    
    try:
        count = session.query(Job).delete()
        session.commit()
        return count
    finally:
        session.close()
