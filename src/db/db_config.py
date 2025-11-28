import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

load_dotenv()

Base = declarative_base()


def get_database_url():
    """
    Get database URL from environment variables.
    Supports both DATABASE_URL (Replit) and individual components (local dev).
    
    Returns:
        str: Database connection URL
    """
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        return database_url
    
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'jobs_db')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', '')
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def get_engine(echo=False):
    """
    Create and return a SQLAlchemy engine.
    
    Args:
        echo (bool): If True, SQL statements will be logged
        
    Returns:
        sqlalchemy.engine.Engine: Database engine
    """
    database_url = get_database_url()
    engine = create_engine(
        database_url,
        echo=echo,
        poolclass=NullPool
    )
    return engine


def get_session():
    """
    Create and return a new database session.
    
    Returns:
        sqlalchemy.orm.Session: Database session
    """
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_db():
    """
    Initialize database by creating all tables defined in models.
    This function should be called once during setup.
    """
    from src.db.models import Job
    
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("Database tables created successfully!")


def drop_all_tables():
    """
    Drop all tables from the database.
    WARNING: This will delete all data!
    """
    engine = get_engine()
    Base.metadata.drop_all(engine)
    print("All tables dropped!")
