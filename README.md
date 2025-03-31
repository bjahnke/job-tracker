# Job Tracker

A tool to help track job applications, interviews, and follow-ups throughout your job search process.

## Features (Planned)
- A company table which lists all of the unique company names in the DB
- Track job applications and their status
- Manage interview schedules and follow-ups
- Store company information and contact details
- Generate reports and analytics
- Set reminders for follow-ups and deadlines

## Getting Started

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation
1. Clone the repository:
```bash
git clone $(gh-repo-ssh job-tracker)
cd job-tracker
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application
1. Make sure your virtual environment is activated:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Start the Streamlit application:
```bash
streamlit run src/job_tracker/app.py
```

3. The application will open in your default web browser. If it doesn't, you can access it at http://localhost:8501

4. Use the file uploader to upload your Simplify.jobs CSV file
5. Click "Sync Data" to import your applications into the database
6. Use the search bar to filter applications in the table

### Command Line Interface
The project includes a CLI using Invoke to simplify common tasks:

```bash
# Set up the development environment
invoke setup

# Run the application
invoke run

# Run tests
invoke test
invoke test --no-coverage  # Run tests without coverage report

# Code formatting and linting
invoke format  # Format code using black and isort
invoke lint    # Run flake8 linter

# Database management
invoke db show  # Show database status
invoke db reset # Reset the database

# Clean up temporary files
invoke clean

# Install dependencies
invoke install
```

## Project Structure
```
job-tracker/
├── src/               # Source code
│   └── job_tracker/   # Main application package
│       ├── app.py     # Streamlit application
│       ├── models.py  # Database models
│       └── __init__.py
├── tests/             # Test files
├── docs/              # Documentation
├── requirements.txt   # Python dependencies
├── tasks.py          # CLI tasks
└── README.md         # This file
```

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details. 