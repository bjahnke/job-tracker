import pytest
from datetime import datetime
from src.job_tracker.models import JobApplication

def test_job_application_creation(sample_job_application):
    """Test that a job application can be created with all fields"""
    assert sample_job_application.job_title == 'Software Engineer'
    assert sample_job_application.company_name == 'Test Company'
    assert sample_job_application.status == 'APPLIED'
    assert not sample_job_application.archived

def test_job_application_db_operations(test_db, sample_job_application):
    """Test CRUD operations for job applications"""
    # Create
    test_db.add(sample_job_application)
    test_db.commit()
    
    # Read
    job = test_db.query(JobApplication).filter_by(simplify_id='12345').first()
    assert job is not None
    assert job.job_title == 'Software Engineer'
    assert job.company_name == 'Test Company'
    
    # Update
    job.status = 'INTERVIEW'
    test_db.commit()
    updated_job = test_db.query(JobApplication).filter_by(simplify_id='12345').first()
    assert updated_job.status == 'INTERVIEW'
    
    # Delete
    test_db.delete(job)
    test_db.commit()
    deleted_job = test_db.query(JobApplication).filter_by(simplify_id='12345').first()
    assert deleted_job is None

def test_duplicate_simplify_id(test_db, sample_job_application):
    """Test that duplicate Simplify IDs are not allowed"""
    test_db.add(sample_job_application)
    test_db.commit()
    
    # Try to add another application with the same Simplify ID
    duplicate_app = JobApplication(
        job_title='Another Job',
        company_name='Another Company',
        simplify_id='12345'  # Same ID as sample_job_application
    )
    
    with pytest.raises(Exception):  # Should raise an integrity error
        test_db.add(duplicate_app)
        test_db.commit()

def test_required_fields(test_db):
    """Test that required fields are enforced"""
    # Try to create an application without company_name (required field)
    invalid_app = JobApplication(
        job_title='Test Job',
        simplify_id='test123'
        # Missing company_name
    )
    
    with pytest.raises(Exception):  # Should raise an integrity error
        test_db.add(invalid_app)
        test_db.commit()

def test_date_fields(test_db):
    """Test that date fields are handled correctly"""
    # Test with datetime objects
    app = JobApplication(
        job_title='Test Job',
        company_name='Test Company',
        applied_date=datetime.strptime('2025-03-31', '%Y-%m-%d'),  # Convert string to datetime
        status_date=datetime.now(),
        simplify_id='test123'
    )
    
    test_db.add(app)
    test_db.commit()
    
    saved_app = test_db.query(JobApplication).filter_by(simplify_id='test123').first()
    assert isinstance(saved_app.applied_date, datetime)
    assert isinstance(saved_app.status_date, datetime) 