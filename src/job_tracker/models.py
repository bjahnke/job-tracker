from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean, create_engine, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True)
    job_title = Column(String(255))
    company_name = Column(String(255), nullable=False)
    job_url = Column(String(512))
    applied_date = Column(DateTime)
    status = Column(String(50))
    status_date = Column(DateTime)
    archived = Column(Boolean, default=False)
    date_archived = Column(DateTime)
    notes = Column(Text)
    simplify_id = Column(String(255), unique=True)  # To prevent duplicates

    def __repr__(self):
        return f"<JobApplication(company='{self.company_name}', position='{self.job_title}')>"

class UserPreferences(Base):
    __tablename__ = 'user_preferences'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Column visibility preferences
    show_job_title = Column(Boolean, default=True)
    show_company = Column(Boolean, default=True)
    show_status = Column(Boolean, default=True)
    show_applied_date = Column(Boolean, default=True)
    show_status_date = Column(Boolean, default=False)
    show_archived = Column(Boolean, default=False)
    show_date_archived = Column(Boolean, default=False)
    show_notes = Column(Boolean, default=True)
    show_job_url = Column(Boolean, default=True)  # Add Job URL preference

    @classmethod
    def get_default_preferences(cls):
        """Get default column visibility preferences"""
        return {
            'Job Title': True,
            'Company': True,
            'Status': True,
            'Applied Date': True,
            'Status Date': False,
            'Archived': False,
            'Date Archived': False,
            'Notes': True,
            'Job URL': True  # Add Job URL to defaults
        }

    def to_dict(self):
        """Convert preferences to dictionary"""
        return {
            'Job Title': self.show_job_title,
            'Company': self.show_company,
            'Status': self.show_status,
            'Applied Date': self.show_applied_date,
            'Status Date': self.show_status_date,
            'Archived': self.show_archived,
            'Date Archived': self.show_date_archived,
            'Notes': self.show_notes,
            'Job URL': self.show_job_url  # Add Job URL to dictionary conversion
        }

    @classmethod
    def from_dict(cls, session, preferences_dict):
        """Create or update preferences from dictionary"""
        # Get the first preferences record or create new one
        prefs = session.query(cls).first()
        if not prefs:
            prefs = cls()
            session.add(prefs)
        
        # Update preferences
        prefs.show_job_title = preferences_dict.get('Job Title', True)
        prefs.show_company = preferences_dict.get('Company', True)
        prefs.show_status = preferences_dict.get('Status', True)
        prefs.show_applied_date = preferences_dict.get('Applied Date', True)
        prefs.show_status_date = preferences_dict.get('Status Date', False)
        prefs.show_archived = preferences_dict.get('Archived', False)
        prefs.show_date_archived = preferences_dict.get('Date Archived', False)
        prefs.show_notes = preferences_dict.get('Notes', True)
        prefs.show_job_url = preferences_dict.get('Job URL', True)  # Add Job URL to preference update
        
        session.commit()
        return prefs

# Create database engine and session
def init_db(db_url="sqlite:///job_tracker.db"):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session() 