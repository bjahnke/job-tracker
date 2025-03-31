from invoke.tasks import task
import os
import shutil

@task
def install(ctx):
    """Install the project dependencies"""
    ctx.run("pip install -r requirements.txt")

@task
def run(ctx):
    """Run the Streamlit application"""
    ctx.run("streamlit run src/job_tracker/app.py")

@task
def test(ctx, coverage=True):
    """Run the test suite"""
    cmd = "python -m pytest tests/"
    if coverage:
        cmd += " -v --cov=src/job_tracker"
    ctx.run(cmd)

@task
def format(ctx):
    """Format code using black and isort"""
    ctx.run("black src/ tests/")
    ctx.run("isort src/ tests/")

@task
def lint(ctx):
    """Run flake8 linter"""
    ctx.run("flake8 src/ tests/")

@task
def clean(ctx):
    """Clean up temporary files and build artifacts"""
    patterns = [
        "*.pyc",
        "__pycache__",
        ".pytest_cache",
        ".coverage",
        "htmlcov",
        "*.db",
        "*.log",
        ".DS_Store",
    ]
    
    for pattern in patterns:
        if os.path.isfile(pattern):
            os.remove(pattern)
        elif os.path.isdir(pattern):
            shutil.rmtree(pattern)

@task
def setup(ctx):
    """Set up the development environment"""
    print("Setting up development environment...")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        ctx.run("python -m venv venv")
    
    # Install dependencies
    print("Installing dependencies...")
    install(ctx)
    
    # Run initial tests
    print("Running initial tests...")
    test(ctx)
    
    print("Setup complete!")

@task
def db(ctx, action="show"):
    """Database management commands"""
    if action == "show":
        if os.path.exists("job_tracker.db"):
            size = os.path.getsize("job_tracker.db")
            print(f"Database exists: job_tracker.db ({size} bytes)")
        else:
            print("No database file found")
    elif action == "reset":
        if os.path.exists("job_tracker.db"):
            os.remove("job_tracker.db")
            print("Database reset")
        else:
            print("No database file to reset")
    else:
        print(f"Unknown action: {action}")
        print("Available actions: show, reset") 