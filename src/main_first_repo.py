"""
Main ETL Orchestrator

This module orchestrates the complete ETL pipeline:
  Extract → Transform → Load

It can be run from command line or called from the Streamlit app.
"""

import argparse
from datetime import datetime
from src.etl.extract import extract_jobs
from src.etl.transform import transform_jobs
from src.etl.load import load_jobs_to_database, validate_database_connection
from src.db.db_config import init_db
from src.utils.logging_utils import get_logger, log_etl_step

logger = get_logger(__name__)


def run_etl_pipeline(
    what='',
    where='',
    max_pages=1,
    results_per_page=50,
    sort_by='date',
    country='de'
):
    """
    Run the complete ETL pipeline.
    
    Args:
        what (str): Job search keywords
        where (str): Location
        max_pages (int): Number of pages to fetch
        results_per_page (int): Results per page
        sort_by (str): Sort order
        country (str): Country code
        
    Returns:
        dict: Pipeline execution results
    """
    logger.info("=" * 80)
    logger.info("Starting ETL Pipeline")
    logger.info(f"Search: what='{what}', where='{where}', pages={max_pages}")
    logger.info("=" * 80)
    
    pipeline_start = datetime.now()
    
    results = {
        'pipeline_start': pipeline_start.isoformat(),
        'steps': {}
    }
    
    log_etl_step('extract', 'started')
    extract_result = extract_jobs(
        what=what,
        where=where,
        max_pages=max_pages,
        results_per_page=results_per_page,
        sort_by=sort_by,
        country=country,
        save_raw=True
    )
    
    if not extract_result['success']:
        log_etl_step('extract', 'failed', extract_result.get('error'))
        results['success'] = False
        results['error'] = f"Extract failed: {extract_result.get('error')}"
        return results
    
    log_etl_step('extract', 'completed', {'jobs': extract_result['count']})
    results['steps']['extract'] = extract_result
    
    log_etl_step('transform', 'started')
    transform_result = transform_jobs(extract_result['jobs'])
    
    if not transform_result['success']:
        log_etl_step('transform', 'failed', transform_result.get('error'))
        results['success'] = False
        results['error'] = f"Transform failed: {transform_result.get('error')}"
        return results
    
    log_etl_step('transform', 'completed', {
        'valid_jobs': transform_result['count'],
        'removed': transform_result.get('removed_count', 0)
    })
    results['steps']['transform'] = transform_result
    
    log_etl_step('load', 'started')
    load_result = load_jobs_to_database(transform_result['jobs'])
    
    if not load_result['success']:
        log_etl_step('load', 'failed', load_result.get('error'))
        results['success'] = False
        results['error'] = f"Load failed: {load_result.get('error')}"
        return results
    
    log_etl_step('load', 'completed', {
        'loaded': load_result['jobs_loaded'],
        'skipped': load_result['jobs_skipped']
    })
    results['steps']['load'] = load_result
    
    pipeline_end = datetime.now()
    pipeline_duration = (pipeline_end - pipeline_start).total_seconds()
    
    results['success'] = True
    results['pipeline_end'] = pipeline_end.isoformat()
    results['duration_seconds'] = pipeline_duration
    
    logger.info("=" * 80)
    logger.info("ETL Pipeline Completed Successfully")
    logger.info(f"Duration: {pipeline_duration:.2f} seconds")
    logger.info(f"Jobs extracted: {extract_result['count']}")
    logger.info(f"Jobs transformed: {transform_result['count']}")
    logger.info(f"Jobs loaded: {load_result['jobs_loaded']}")
    logger.info(f"Jobs skipped (duplicates): {load_result['jobs_skipped']}")
    logger.info(f"Total jobs in database: {load_result['total_jobs_in_db']}")
    logger.info("=" * 80)
    
    return results


def main():
    """
    Command-line entry point for running the ETL pipeline.
    """
    parser = argparse.ArgumentParser(
        description='Adzuna Job Data ETL Pipeline'
    )
    
    parser.add_argument(
        '--what',
        type=str,
        default='',
        help='Job search keywords (e.g., "Python Developer")'
    )
    
    parser.add_argument(
        '--where',
        type=str,
        default='',
        help='Location (e.g., "Berlin")'
    )
    
    parser.add_argument(
        '--pages',
        type=int,
        default=1,
        help='Number of pages to fetch (default: 1)'
    )
    
    parser.add_argument(
        '--results-per-page',
        type=int,
        default=50,
        help='Results per page (max 50, default: 50)'
    )
    
    parser.add_argument(
        '--sort-by',
        type=str,
        default='date',
        choices=['date', 'relevance', 'salary'],
        help='Sort order (default: date)'
    )
    
    parser.add_argument(
        '--country',
        type=str,
        default='de',
        help='Country code (default: de for Germany)'
    )
    
    parser.add_argument(
        '--init-db',
        action='store_true',
        help='Initialize database (create tables)'
    )
    
    parser.add_argument(
        '--test-db',
        action='store_true',
        help='Test database connection'
    )
    
    args = parser.parse_args()
    
    if args.init_db:
        print("Initializing database...")
        init_db()
        print("Database initialized successfully!")
        return
    
    if args.test_db:
        print("Testing database connection...")
        result = validate_database_connection()
        print(result['message'])
        return
    
    results = run_etl_pipeline(
        what=args.what,
        where=args.where,
        max_pages=args.pages,
        results_per_page=args.results_per_page,
        sort_by=args.sort_by,
        country=args.country
    )
    
    if results['success']:
        print("\n✓ ETL Pipeline completed successfully!")
    else:
        print(f"\n✗ ETL Pipeline failed: {results.get('error')}")


if __name__ == '__main__':
    main()
