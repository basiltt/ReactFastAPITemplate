from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="fastapi-skeleton-project",  # Change to a valid Python package name (no spaces or special characters)
    version="1.0",
    author="Basil T T",
    author_email="basil.tt@hpe.com",
    description="Boilerplate full-stack FastAPI application",
    packages=find_packages(),
    install_requires=requirements,
)
