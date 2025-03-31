# Job Tracker

A tool to help track job applications, interviews, and follow-ups throughout your job search process.

## Features (Planned)
- UI includes ability to upload csv from simplify.jobs's application tracker
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

## Project Structure
```
job-tracker/
├── src/               # Source code
├── tests/             # Test files
├── docs/              # Documentation
├── requirements.txt   # Python dependencies
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