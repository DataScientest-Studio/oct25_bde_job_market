"""
Machine Learning Preparation Module

This module provides placeholder functions for preparing job data for ML models.
Future ML features could include:
  - Job recommendation systems
  - Salary prediction models
  - Job category classification
  - Skills extraction from descriptions
  - Resume matching
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from src.db.repository import get_all_jobs
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


def prepare_dataset_for_ml(limit=1000):
    """
    Prepare job data from database for machine learning.
    
    Args:
        limit (int): Maximum number of jobs to retrieve
        
    Returns:
        dict: Prepared dataset with features and metadata
    """
    logger.info(f"Preparing ML dataset with up to {limit} jobs")
    
    try:
        jobs = get_all_jobs(limit=limit)
        
        if not jobs:
            logger.warning("No jobs available for ML preparation")
            return {
                'success': False,
                'message': 'No jobs in database'
            }
        
        df = pd.DataFrame([job.to_dict() for job in jobs])
        
        logger.info(f"Retrieved {len(df)} jobs for ML preparation")
        
        return {
            'success': True,
            'dataframe': df,
            'row_count': len(df),
            'features': list(df.columns)
        }
        
    except Exception as e:
        logger.error(f"Error preparing ML dataset: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def extract_features_for_salary_prediction(df):
    """
    Extract and engineer features for salary prediction model.
    
    Args:
        df (pandas.DataFrame): Job dataframe
        
    Returns:
        dict: Processed features and target variable
    """
    logger.info("Extracting features for salary prediction")
    
    df_ml = df[df['salary_min'].notna()].copy()
    
    if len(df_ml) == 0:
        return {
            'success': False,
            'message': 'No jobs with salary information'
        }
    
    df_ml['avg_salary'] = (df_ml['salary_min'] + df_ml['salary_max'].fillna(df_ml['salary_min'])) / 2
    
    df_ml['title_length'] = df_ml['title'].str.len()
    df_ml['has_description'] = df_ml['description'].notna().astype(int)
    df_ml['description_length'] = df_ml['description'].fillna('').str.len()
    
    return {
        'success': True,
        'dataframe': df_ml,
        'target_variable': 'avg_salary',
        'feature_count': len(df_ml.columns)
    }


def split_train_test(df, target_column, test_size=0.2, random_state=42):
    """
    Split dataset into training and testing sets.
    
    Args:
        df (pandas.DataFrame): Feature dataframe
        target_column (str): Name of target variable column
        test_size (float): Proportion of test set (default: 0.2)
        random_state (int): Random seed for reproducibility
        
    Returns:
        dict: Train and test splits
    """
    logger.info(f"Splitting dataset: {len(df)} samples, test_size={test_size}")
    
    try:
        feature_columns = [col for col in df.columns if col != target_column]
        
        X = df[feature_columns]
        y = df[target_column]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state
        )
        
        logger.info(f"Train set: {len(X_train)} samples, Test set: {len(X_test)} samples")
        
        return {
            'success': True,
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
        
    except Exception as e:
        logger.error(f"Error splitting dataset: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def export_ml_dataset(df, filepath='data/processed/ml_dataset.csv'):
    """
    Export prepared dataset to CSV for ML experiments.
    
    Args:
        df (pandas.DataFrame): Dataset to export
        filepath (str): Output file path
        
    Returns:
        dict: Export status
    """
    try:
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        df.to_csv(filepath, index=False)
        
        logger.info(f"ML dataset exported to {filepath}")
        
        return {
            'success': True,
            'filepath': filepath,
            'rows': len(df)
        }
        
    except Exception as e:
        logger.error(f"Error exporting ML dataset: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def get_ml_data_summary(df):
    """
    Get summary statistics for ML dataset.
    
    Args:
        df (pandas.DataFrame): Dataset
        
    Returns:
        dict: Summary statistics
    """
    summary = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
        'categorical_columns': len(df.select_dtypes(include=['object']).columns),
        'missing_values': df.isnull().sum().to_dict(),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2
    }
    
    return summary
