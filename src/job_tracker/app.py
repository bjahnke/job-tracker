import pandas as pd
import streamlit as st
from datetime import datetime
from models import JobApplication, init_db

# Initialize database session
db = init_db()

def process_csv(df):
    """Process the CSV data and sync with database"""
    for _, row in df.iterrows():
        # Check if application already exists
        existing = db.query(JobApplication).filter_by(simplify_id=str(row.get('id'))).first()
        
        if not existing:
            application = JobApplication(
                company_name=row.get('company_name', ''),
                position=row.get('position', ''),
                status=row.get('status', ''),
                application_date=pd.to_datetime(row.get('application_date')) if row.get('application_date') else None,
                last_updated=pd.to_datetime(row.get('last_updated')) if row.get('last_updated') else None,
                job_url=row.get('job_url', ''),
                notes=row.get('notes', ''),
                location=row.get('location', ''),
                salary_range=row.get('salary_range', ''),
                job_type=row.get('job_type', ''),
                simplify_id=str(row.get('id'))
            )
            db.add(application)
    
    db.commit()

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
    
    # Get all applications from database
    applications = db.query(JobApplication).all()
    
    if applications:
        # Convert to DataFrame for display
        data = []
        for app in applications:
            data.append({
                'Company': app.company_name,
                'Position': app.position,
                'Status': app.status,
                'Application Date': app.application_date,
                'Last Updated': app.last_updated,
                'Location': app.location,
                'Job Type': app.job_type,
                'Salary Range': app.salary_range
            })
        
        df_display = pd.DataFrame(data)
        
        # Add search functionality
        search_term = st.text_input("Search applications", "")
        if search_term:
            df_display = df_display[df_display.apply(lambda x: x.astype(str).str.contains(search_term, case=False, na=False)).any(axis=1)]
        
        st.dataframe(df_display)
    else:
        st.info("No applications found. Upload a CSV file to get started!")

if __name__ == "__main__":
    main() 