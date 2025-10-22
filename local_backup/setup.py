from setuptools import setup, find_packages

setup(
    name="opendiscourse",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
        "typing-extensions>=3.7.4",
    ],
    author="OpenDiscourse Team",
    description="A platform for tracking and analyzing political discourse",
    python_requires=">=3.8",
)