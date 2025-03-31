import pandas as pd
import streamlit as st
from datetime import datetime
from job_tracker.models import JobApplication, UserPreferences, init_db
import numpy as np
import hashlib
import uuid

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

def search_applications(df, query):
    """Search applications using pandas DataFrame query
    
    Args:
        df: pandas DataFrame containing application data
        query: Search query string to match against job title, company name, or notes
        
    Returns:
        DataFrame containing matching applications
    """
    if not query:
        return df
    
    # Create a case-insensitive search pattern
    search_pattern = query.lower()
    
    # Create a mask for matching rows
    mask = (
        df['Job Title'].str.lower().str.contains(search_pattern, na=False) |
        df['Company'].str.lower().str.contains(search_pattern, na=False) |
        df['Notes'].str.lower().str.contains(search_pattern, na=False)
    )
    
    return df[mask]

def get_visible_columns():
    """Get the list of columns to display based on user preferences"""
    st.sidebar.header("Column Visibility")
    
    # Get preferences from database or use defaults
    prefs = db.query(UserPreferences).first()
    if not prefs:
        prefs = UserPreferences.from_dict(db, UserPreferences.get_default_preferences())
    
    # Create checkboxes for each column
    visible_columns = {}
    preferences_dict = prefs.to_dict()
    changed = False
    
    for col, default_visible in preferences_dict.items():
        # Ensure we're using a boolean value
        current_value = bool(default_visible)
        new_value = st.sidebar.checkbox(f"Show {col}", value=current_value)
        visible_columns[col] = new_value
        
        if current_value != new_value:
            changed = True
    
    # Save preferences and rerun if they've changed
    if changed:
        UserPreferences.from_dict(db, visible_columns)
        st.rerun()
    
    # Return list of columns that are checked
    return [col for col, is_visible in visible_columns.items() if is_visible]

def format_job_url(url):
    """Format job URL as a clickable link if it exists"""
    if pd.isna(url) or not url:
        return ""  # Return empty string instead of None for better display
    return f'<a href="{url}" target="_blank">View Job</a>'

def get_company_stats(applications):
    """Calculate statistics for each company
    
    Args:
        applications: List of JobApplication objects
        
    Returns:
        DataFrame with company statistics
    """
    # Convert applications to DataFrame for easier analysis
    df = pd.DataFrame([{
        'Company': app.company_name,
        'Applied Date': app.applied_date
    } for app in applications])
    
    # Filter out rows with None dates
    df = df.dropna(subset=['Applied Date'])
    
    # Group by company and calculate stats
    stats = df.groupby('Company').agg({
        'Company': 'count',  # Number of applications
        'Applied Date': 'max'  # Most recent application
    }).rename(columns={
        'Company': 'Applications',
        'Applied Date': 'Most Recent'
    })
    
    # Calculate days since last application
    today = pd.Timestamp.now()
    stats['Days Since Last'] = (today - stats['Most Recent']).dt.days
    
    # Sort by number of applications (descending)
    stats = stats.sort_values('Applications', ascending=False)
    
    return stats

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

    try:
        # Get all applications from database
        applications = db.query(JobApplication).all()
        
        if applications:
            # Display company statistics
            st.subheader("Company Statistics")
            company_stats = get_company_stats(applications)
            st.dataframe(
                company_stats,
                use_container_width=True,
                height=300
            )
            
            # Display data table
            st.subheader("Your Applications")
            
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
                    'Notes': app.notes,
                    'Job URL': app.job_url
                })
            
            df_display = pd.DataFrame(data)
            
            # Get visible columns from sidebar
            visible_columns = get_visible_columns()
            
            # Add search functionality
            search_term = st.text_input("Search applications", "")
            
            # Filter DataFrame based on search term
            df_filtered = search_applications(df_display, search_term)
            
            if not df_filtered.empty:
                # Configure column settings
                kwargs = {}
                if 'Job URL' in df_filtered.columns and 'Job URL' in visible_columns:
                    kwargs['column_config'] = {
                        'Job URL': st.column_config.LinkColumn(
                            display_text='🔗 View Job',
                            width='small'
                        )
                    }
                    # Ensure Job URL appears first in the column order
                    kwargs['column_order'] = ['Job URL'] + [col for col in visible_columns if col != 'Job URL']
                
                # Generate a unique identifier for the session
                session_id = uuid.uuid4()
                st.session_state['session_id'] = session_id
                
                # Display DataFrame with styled columns
                st.data_editor(
                    df_filtered[visible_columns],
                    key=str(session_id),
                    use_container_width=True,
                    height=1000,
                    **kwargs
                )
            else:
                st.info("No applications found matching your search.")
        else:
            st.info("No applications found. Upload a CSV file to get started!")
    except Exception as e:
        st.error(f"Error displaying applications: {str(e)}")
        db.rollback()

if __name__ == "__main__":
    main() 