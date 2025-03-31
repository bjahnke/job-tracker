import pytest
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.job_tracker.models import Base, JobApplication

@pytest.fixture
def test_db():
    """Create a test database in memory"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

@pytest.fixture
def sample_csv_data():
    """Create sample CSV data for testing"""
    return pd.DataFrame([
        {
            'Job Title': 'Software Engineer',
            'Company Name': 'Test Company',
            'Job URL': 'https://example.com/job',
            'Applied Date': '2025-03-31',
            'Status': 'APPLIED',
            'Status Date': '2025-03-31',
            'Archived': False,
            'Date Archived': None,
            'Notes': 'Test notes',
            'id': '12345'
        },
        {
            'Job Title': 'Senior Developer',
            'Company Name': 'Another Company',
            'Job URL': 'https://example.com/job2',
            'Applied Date': None,  # Testing null date
            'Status': 'SAVED',
            'Status Date': '2025-03-30',
            'Archived': True,
            'Date Archived': '2025-03-31',
            'Notes': None,  # Testing null notes
            'id': None  # Testing null ID
        }
    ])

@pytest.fixture
def sample_job_application():
    """Create a sample job application for testing"""
    return JobApplication(
        job_title='Software Engineer',
        company_name='Test Company',
        job_url='https://example.com/job',
        applied_date=pd.to_datetime('2025-03-31'),
        status='APPLIED',
        status_date=pd.to_datetime('2025-03-31'),
        archived=False,
        date_archived=None,
        notes='Test notes',
        simplify_id='12345'
    ) 