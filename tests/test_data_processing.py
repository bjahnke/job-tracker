import pandas as pd
import pytest
from datetime import datetime
from src.job_tracker.app import clean_value, process_csv
from src.job_tracker.models import JobApplication

def test_clean_value():
    """Test the clean_value function handles different input types"""
    # Test None values
    assert clean_value(None) is None
    assert clean_value(pd.NA) is None
    assert clean_value(float('nan')) is None
    
    # Test string values
    assert clean_value('test') == 'test'
    assert clean_value('') == ''
    
    # Test numeric values
    assert clean_value(123) == '123'
    assert clean_value(123.45) == '123.45'

def test_process_csv(test_db, sample_csv_data):
    """Test processing CSV data into the database"""
    # Process the sample data with test database session
    process_csv(sample_csv_data, session=test_db)
    
    # Check that both records were saved
    applications = test_db.query(JobApplication).all()
    assert len(applications) == 2
    
    # Check the record with complete data
    app1 = test_db.query(JobApplication).filter_by(simplify_id='12345').first()
    assert app1 is not None
    assert app1.job_title == 'Software Engineer'
    assert app1.company_name == 'Test Company'
    assert app1.status == 'APPLIED'
    assert not app1.archived
    
    # Check the record with null values
    app2 = test_db.query(JobApplication).filter_by(company_name='Another Company').first()
    assert app2 is not None
    assert app2.applied_date is None
    assert app2.notes is None
    assert app2.archived is True
    assert isinstance(app2.simplify_id, str)  # Should have generated a unique ID

def test_duplicate_prevention(test_db, sample_csv_data):
    """Test that processing the same CSV twice doesn't create duplicates"""
    # Process the data twice with test database session
    process_csv(sample_csv_data, session=test_db)
    process_csv(sample_csv_data, session=test_db)
    
    # Check that we still only have two records
    applications = test_db.query(JobApplication).all()
    assert len(applications) == 2

def test_data_types(test_db, sample_csv_data):
    """Test that data types are correctly converted"""
    process_csv(sample_csv_data, session=test_db)
    
    app = test_db.query(JobApplication).filter_by(simplify_id='12345').first()
    
    # Check date fields
    assert isinstance(app.applied_date, datetime)
    assert isinstance(app.status_date, datetime)
    
    # Check boolean field
    assert isinstance(app.archived, bool)
    
    # Check string fields
    assert isinstance(app.job_title, str)
    assert isinstance(app.company_name, str)
    assert isinstance(app.status, str)

def test_invalid_data(test_db):
    """Test handling of invalid data"""
    # Create DataFrame with invalid data
    invalid_data = pd.DataFrame([{
        'Job Title': 123,  # Number instead of string
        'Company Name': 'Test Company',
        'Applied Date': 'not-a-date',  # Invalid date
        'Status': None,
        'Archived': 'not-a-boolean',  # Invalid boolean
        'id': '12345'
    }])
    
    # Should not raise an exception
    process_csv(invalid_data, session=test_db)
    
    # Check that the data was cleaned and saved
    app = test_db.query(JobApplication).filter_by(simplify_id='12345').first()
    assert app is not None
    assert app.job_title == '123'  # Converted to string
    assert app.applied_date is None  # Invalid date becomes None
    assert app.status is None  # None status preserved
    assert app.archived is False  # Invalid boolean becomes False 