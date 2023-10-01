from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="FastAPI Skeleton Project",
    version="1.0",
    author="Basil T T",
    author_email="basil.tt@hpe.com",
    description="Boiler plate full stack FastApi application",
    packages=find_packages(),
    install_requires=requirements,
)
