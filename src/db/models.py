from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.sql import func
from src.db.db_config import Base


class Job(Base):
    """
    SQLAlchemy model for storing job postings from Adzuna API.
    
    This table stores both structured fields (for easy querying) and
    the complete raw JSON response (for future analysis and ML features).
    """
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    adzuna_id = Column(String(255), unique=True, nullable=False, index=True)
    
    title = Column(String(500), nullable=False, index=True)
    
    company = Column(String(255), index=True)
    
    location = Column(String(255), index=True)
    
    location_area = Column(String(255))
    
    description = Column(Text)
    
    salary_min = Column(Float)
    
    salary_max = Column(Float)
    
    salary_currency = Column(String(10))
    
    contract_type = Column(String(100))
    
    contract_time = Column(String(100))
    
    category_label = Column(String(255), index=True)
    
    category_tag = Column(String(100))
    
    redirect_url = Column(Text)
    
    created_date = Column(DateTime)
    
    raw_json = Column(JSON)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Job(id={self.id}, adzuna_id='{self.adzuna_id}', title='{self.title}', company='{self.company}')>"
    
    def to_dict(self):
        """
        Convert job object to dictionary.
        
        Returns:
            dict: Job data as dictionary
        """
        return {
            'id': self.id,
            'adzuna_id': self.adzuna_id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'location_area': self.location_area,
            'description': self.description,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'salary_currency': self.salary_currency,
            'contract_type': self.contract_type,
            'contract_time': self.contract_time,
            'category_label': self.category_label,
            'category_tag': self.category_tag,
            'redirect_url': self.redirect_url,
            'created_date': self.created_date,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
