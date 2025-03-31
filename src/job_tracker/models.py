from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class JobApplication(Base):
    __tablename__ = "job_applications"

    id = Column(Integer, primary_key=True)
    company_name = Column(String(255), nullable=False)
    position = Column(String(255))
    status = Column(String(50))
    application_date = Column(DateTime)
    last_updated = Column(DateTime)
    job_url = Column(String(512))
    notes = Column(Text)
    location = Column(String(255))
    salary_range = Column(String(100))
    job_type = Column(String(50))
    simplify_id = Column(String(255), unique=True)  # To prevent duplicates

    def __repr__(self):
        return f"<JobApplication(company='{self.company_name}', position='{self.position}')>"

# Create database engine and session
def init_db(db_url="sqlite:///job_tracker.db"):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session() 