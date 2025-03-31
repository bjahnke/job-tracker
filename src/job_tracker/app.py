import pandas as pd
import streamlit as st
from datetime import datetime
from job_tracker.models import JobApplication, init_db
import numpy as np
import hashlib

# Initialize database session for the Streamlit app
db = init_db()

def clean_value(value):
    """Clean a value from the DataFrame, handling NaN and None"""
    if pd.isna(value) or value is None:
        return None
    return str(value)

def parse_date(date_str):
    """Parse a date string, returning None if invalid"""
    if pd.isna(date_str):
        return None
    try:
        return pd.to_datetime(date_str)
    except (ValueError, TypeError):
        return None

def generate_unique_id(row):
    """Generate a consistent unique ID for a row using a hash of key fields
    
    Creates a SHA-256 hash of company name, job title, and URL to ensure uniqueness
    while maintaining consistency for the same job data.
    """
    # Collect key fields that identify a unique job
    key_fields = [
        clean_value(row.get('Company Name', '')),
        clean_value(row.get('Job Title', '')),
        clean_value(row.get('Job URL', '')),
        clean_value(row.get('Applied Date', '')),  # Include date to differentiate repostings
    ]
    
    # Create a string from non-None values
    unique_str = '_'.join([str(field) for field in key_fields if field is not None])
    
    # Generate SHA-256 hash
    hash_obj = hashlib.sha256(unique_str.encode())
    # Take first 12 characters of the hex digest for a shorter but still unique ID
    return f"gen_{hash_obj.hexdigest()[:12]}"

def process_csv(df, session=None):
    """Process the CSV data and sync with database
    
    Args:
        df: pandas DataFrame containing job application data
        session: SQLAlchemy session to use (optional, defaults to global db session)
    """
    # Use provided session or fall back to global db
    db_session = session or db
    
    for _, row in df.iterrows():
        # Generate a unique ID if none exists
        simplify_id = clean_value(row.get('id'))
        if not simplify_id:
            # Create a consistent unique ID for the same job
            simplify_id = generate_unique_id(row)
        
        # Check if application already exists
        existing = db_session.query(JobApplication).filter_by(simplify_id=simplify_id).first()
        
        if not existing:
            # Clean and convert values
            applied_date = parse_date(row.get('Applied Date'))
            status_date = parse_date(row.get('Status Date'))
            date_archived = parse_date(row.get('Date Archived'))
            
            # Convert archived to boolean
            archived_str = clean_value(row.get('Archived', ''))
            archived = archived_str.lower() == 'true' if archived_str else False
            
            application = JobApplication(
                job_title=clean_value(row.get('Job Title')),
                company_name=clean_value(row.get('Company Name')),
                job_url=clean_value(row.get('Job URL')),
                applied_date=applied_date,
                status=clean_value(row.get('Status')),
                status_date=status_date,
                archived=archived,
                date_archived=date_archived,
                notes=clean_value(row.get('Notes')),
                simplify_id=simplify_id
            )
            db_session.add(application)
    
    try:
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e

def main():
    st.title("Job Application Tracker")
    st.write("Upload your Simplify.jobs CSV file to sync your applications")

    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("File uploaded successfully!")
            
            if st.button("Sync Data"):
                with st.spinner("Syncing data..."):
                    process_csv(df)
                st.success("Data synced successfully!")
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

    # Display data table
    st.subheader("Your Applications")
    
    try:
        # Get all applications from database
        applications = db.query(JobApplication).all()
        
        if applications:
            # Convert to DataFrame for display
            data = []
            for app in applications:
                data.append({
                    'Job Title': app.job_title,
                    'Company': app.company_name,
                    'Status': app.status,
                    'Applied Date': app.applied_date,
                    'Status Date': app.status_date,
                    'Archived': app.archived,
                    'Date Archived': app.date_archived,
                    'Notes': app.notes
                })
            
            df_display = pd.DataFrame(data)
            
            # Add search functionality
            search_term = st.text_input("Search applications", "")
            if search_term:
                df_display = df_display[df_display.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)]
            
            st.dataframe(df_display)
        else:
            st.info("No applications found. Upload a CSV file to get started!")
    except Exception as e:
        st.error(f"Error displaying applications: {str(e)}")
        db.rollback()

if __name__ == "__main__":
    main() 