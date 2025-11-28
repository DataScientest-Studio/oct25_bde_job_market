"""
MongoDB Client Module (Optional)

This module provides placeholder functions for MongoDB integration.
MongoDB can be used for storing unstructured or semi-structured data such as:
  - Full job descriptions with rich formatting
  - Raw API responses for historical analysis
  - User interaction logs
  - ML model predictions and metadata
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

load_dotenv()


def get_mongodb_client():
    """
    Create and return MongoDB client connection.
    
    Returns:
        pymongo.MongoClient: MongoDB client or None if not configured
    """
    try:
        from pymongo import MongoClient
        
        mongodb_uri = os.getenv('MONGODB_URI')
        
        if not mongodb_uri:
            logger.warning("MONGODB_URI not configured in .env file")
            return None
        
        client = MongoClient(mongodb_uri)
        
        client.admin.command('ping')
        
        logger.info("MongoDB connection successful")
        return client
        
    except ImportError:
        logger.warning("pymongo not installed. Install with: pip install pymongo")
        return None
    
    except Exception as e:
        logger.error(f"MongoDB connection failed: {str(e)}")
        return None


def get_database(db_name=None):
    """
    Get MongoDB database instance.
    
    Args:
        db_name (str): Database name (reads from env if not provided)
        
    Returns:
        pymongo.database.Database: Database instance or None
    """
    client = get_mongodb_client()
    
    if not client:
        return None
    
    if not db_name:
        db_name = os.getenv('MONGODB_DB_NAME', 'jobs_db')
    
    return client[db_name]


def insert_job_description(job_id, title, description, metadata=None):
    """
    Insert job description into MongoDB.
    
    Args:
        job_id (str): Adzuna job ID
        title (str): Job title
        description (str): Full job description text
        metadata (dict): Additional metadata
        
    Returns:
        dict: Insert result
    """
    try:
        db = get_database()
        
        if db is None:
            return {
                'success': False,
                'message': 'MongoDB not configured'
            }
        
        collection = db['job_descriptions']
        
        document = {
            'job_id': job_id,
            'title': title,
            'description': description,
            'created_at': datetime.now(),
            'metadata': metadata or {}
        }
        
        result = collection.insert_one(document)
        
        logger.info(f"Inserted job description: {job_id}")
        
        return {
            'success': True,
            'inserted_id': str(result.inserted_id),
            'job_id': job_id
        }
        
    except Exception as e:
        logger.error(f"Error inserting job description: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def insert_raw_api_response(response_data, search_params=None):
    """
    Store raw API response in MongoDB for historical analysis.
    
    Args:
        response_data (dict): Raw API response
        search_params (dict): Search parameters used
        
    Returns:
        dict: Insert result
    """
    try:
        db = get_database()
        
        if db is None:
            return {
                'success': False,
                'message': 'MongoDB not configured'
            }
        
        collection = db['api_responses']
        
        document = {
            'response': response_data,
            'search_params': search_params or {},
            'captured_at': datetime.now()
        }
        
        result = collection.insert_one(document)
        
        logger.info("Inserted raw API response to MongoDB")
        
        return {
            'success': True,
            'inserted_id': str(result.inserted_id)
        }
        
    except Exception as e:
        logger.error(f"Error inserting API response: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def get_job_description(job_id):
    """
    Retrieve job description from MongoDB.
    
    Args:
        job_id (str): Adzuna job ID
        
    Returns:
        dict: Job description document or None
    """
    try:
        db = get_database()
        
        if db is None:
            return None
        
        collection = db['job_descriptions']
        
        document = collection.find_one({'job_id': job_id})
        
        if document:
            document['_id'] = str(document['_id'])
        
        return document
        
    except Exception as e:
        logger.error(f"Error retrieving job description: {str(e)}")
        return None


def test_mongodb_connection():
    """
    Test MongoDB connection.
    
    Returns:
        dict: Connection test result
    """
    try:
        client = get_mongodb_client()
        
        if not client:
            return {
                'success': False,
                'message': 'MongoDB not configured or connection failed'
            }
        
        db_name = os.getenv('MONGODB_DB_NAME', 'jobs_db')
        db = client[db_name]
        
        collections = db.list_collection_names()
        
        return {
            'success': True,
            'message': f'MongoDB connection successful. Database: {db_name}',
            'collections': collections
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'MongoDB connection failed: {str(e)}'
        }
