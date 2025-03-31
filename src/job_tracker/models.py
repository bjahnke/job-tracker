from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, Boolean, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

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

# Create database engine and session
def init_db(db_url="sqlite:///job_tracker.db"):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session() 