#!/usr/bin/env python3
"""
Test script to verify data ingestion pipeline works correctly
"""
import os
import sys
import logging
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

def test_environment():
    """Check if all environment variables are set"""
    logger.info("=" * 60)
    logger.info("1. CHECKING ENVIRONMENT VARIABLES")
    logger.info("=" * 60)
    
    required_vars = ['APP_ID', 'APP_KEY', 'PG_CONN', 'MONGO_URI']
    all_set = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'PASS' in var or 'KEY' in var or 'URI' in var:
                masked = value[:10] + '***' if len(value) > 10 else '***'
            else:
                masked = value
            logger.info(f"✓ {var}: {masked}")
        else:
            logger.error(f"✗ {var}: NOT SET")
            all_set = False
    
    return all_set

def test_postgres_connection():
    """Test PostgreSQL connection"""
    logger.info("\n" + "=" * 60)
    logger.info("2. TESTING POSTGRES CONNECTION")
    logger.info("=" * 60)
    
    try:
        from sqlalchemy import create_engine, text
        pg_conn = os.getenv("PG_CONN")
        
        logger.info(f"Connecting to: {pg_conn.replace(os.getenv('POSTGRES_PASSWORD'), '***')}")
        engine = create_engine(pg_conn)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("✓ PostgreSQL connection successful")
            
            # Check existing tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            logger.info(f"✓ Existing tables: {tables if tables else 'None'}")
            
            # Check job count
            try:
                result = conn.execute(text("SELECT COUNT(*) FROM job"))
                count = result.scalar()
                logger.info(f"✓ Jobs in database: {count}")
            except Exception as e:
                logger.warning(f"Could not count jobs: {str(e)}")
        
        return True
    except Exception as e:
        logger.error(f"✗ PostgreSQL connection failed: {str(e)}")
        return False

def test_mongodb_connection():
    """Test MongoDB connection"""
    logger.info("\n" + "=" * 60)
    logger.info("3. TESTING MONGODB CONNECTION")
    logger.info("=" * 60)
    
    try:
        from pymongo import MongoClient
        mongo_uri = os.getenv("MONGO_URI")
        
        logger.info(f"Connecting to: {mongo_uri}")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Verify connection
        client.admin.command('ping')
        logger.info("✓ MongoDB connection successful")
        
        # Check collections
        db = client["adzuna"]
        collections = db.list_collection_names()
        logger.info(f"✓ Collections in 'adzuna' database: {collections if collections else 'None'}")
        
        # Check document count
        if "jobs" in collections:
            count = db["jobs"].count_documents({})
            logger.info(f"✓ Documents in 'jobs' collection: {count}")
        
        client.close()
        return True
    except Exception as e:
        logger.error(f"✗ MongoDB connection failed: {str(e)}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    logger.info("\n" + "=" * 60)
    logger.info("4. TESTING API ENDPOINTS")
    logger.info("=" * 60)
    
    try:
        import requests
        base_url = "http://localhost:8000"
        
        # Test health endpoint
        logger.info(f"Testing GET {base_url}/health")
        response = requests.get(f"{base_url}/health", timeout=5)
        logger.info(f"✓ Health check: {response.status_code} - {response.text}")
        
        return True
    except Exception as e:
        logger.error(f"✗ API tests failed: {str(e)}")
        logger.info("(This is expected if API is not running)")
        return False

def test_ingestion():
    """Test the data ingestion pipeline"""
    logger.info("\n" + "=" * 60)
    logger.info("5. TESTING DATA INGESTION")
    logger.info("=" * 60)
    
    try:
        logger.info("Starting ingestion with max_pages=1 (limited for testing)...")
        from src.data.main import main as ingestion_pipeline
        
        ingestion_pipeline(max_pages=1)
        
        logger.info("✓ Ingestion completed successfully")
        return True
    except Exception as e:
        logger.error(f"✗ Ingestion failed: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def main():
    logger.info("\n" + "=" * 60)
    logger.info("STARTING API INGESTION TEST SUITE")
    logger.info("=" * 60)
    
    results = {
        "Environment": test_environment(),
        "PostgreSQL": test_postgres_connection(),
        "MongoDB": test_mongodb_connection(),
        "API Endpoints": test_api_endpoints(),
        "Data Ingestion": test_ingestion(),
    }
    
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        logger.info(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    logger.info("=" * 60)
    
    if all_passed:
        logger.info("✓ All tests passed!")
    else:
        logger.warning("✗ Some tests failed - see details above")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
