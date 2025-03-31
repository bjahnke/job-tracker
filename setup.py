from setuptools import setup, find_packages

setup(
    name="job-tracker",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pandas",
        "streamlit",
        "sqlalchemy",
    ],
    python_requires=">=3.10",
) 