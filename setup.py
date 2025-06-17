from setuptools import find_packages, setup

setup(
    name="opendiscourse",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # Core dependencies
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pydantic>=1.8.0",
        "sqlalchemy>=1.4.0",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.5",
        "httpx>=0.23.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.5",
            "pytest-cov>=2.12.0",
            "black>=21.12b0",
            "isort>=5.10.1",
            "mypy>=0.910",
            "ruff>=0.0.237",
        ],
        "test": [
            "pytest>=6.2.5",
            "pytest-cov>=2.12.0",
            "httpx>=0.23.0",
        ],
    },
    python_requires=">=3.8",
)
