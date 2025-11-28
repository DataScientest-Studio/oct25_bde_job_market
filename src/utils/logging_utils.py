"""
Logging Utilities Module

This module provides centralized logging configuration for the entire application.
"""

import logging
import os
from datetime import datetime


LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}


def setup_logging(log_level='INFO', log_to_file=False, log_dir='logs'):
    """
    Configure logging for the application.
    
    Args:
        log_level (str): Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        log_to_file (bool): Whether to log to file in addition to console
        log_dir (str): Directory for log files
    """
    level = LOG_LEVELS.get(log_level.upper(), logging.INFO)
    
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    handlers = []
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    handlers.append(console_handler)
    
    if log_to_file:
        os.makedirs(log_dir, exist_ok=True)
        
        log_filename = f'app_{datetime.now().strftime("%Y%m%d")}.log'
        log_filepath = os.path.join(log_dir, log_filename)
        
        file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=handlers,
        force=True
    )


def get_logger(name):
    """
    Get a logger instance with the specified name.
    
    Args:
        name (str): Logger name (typically __name__ of the module)
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)


def log_etl_step(step_name, status, details=None):
    """
    Log an ETL pipeline step with standardized format.
    
    Args:
        step_name (str): Name of the ETL step ('extract', 'transform', 'load')
        status (str): Status ('started', 'completed', 'failed')
        details (dict): Additional details to log
    """
    logger = get_logger('etl_pipeline')
    
    message = f"ETL Step: {step_name.upper()} - Status: {status.upper()}"
    
    if details:
        message += f" - Details: {details}"
    
    if status.lower() == 'failed':
        logger.error(message)
    elif status.lower() == 'completed':
        logger.info(message)
    else:
        logger.info(message)


def log_api_request(endpoint, params, status_code=None, error=None):
    """
    Log API request details.
    
    Args:
        endpoint (str): API endpoint
        params (dict): Request parameters
        status_code (int): HTTP status code
        error (str): Error message if request failed
    """
    logger = get_logger('api_client')
    
    message = f"API Request: {endpoint}"
    
    if params:
        message += f" - Params: {params}"
    
    if status_code:
        message += f" - Status: {status_code}"
    
    if error:
        logger.error(f"{message} - Error: {error}")
    else:
        logger.info(message)


def log_database_operation(operation, table, count=None, error=None):
    """
    Log database operation details.
    
    Args:
        operation (str): Database operation ('insert', 'update', 'delete', 'select')
        table (str): Table name
        count (int): Number of rows affected
        error (str): Error message if operation failed
    """
    logger = get_logger('database')
    
    message = f"DB Operation: {operation.upper()} on {table}"
    
    if count is not None:
        message += f" - Rows: {count}"
    
    if error:
        logger.error(f"{message} - Error: {error}")
    else:
        logger.info(message)


setup_logging(log_level='INFO')
