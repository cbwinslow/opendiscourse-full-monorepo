# OpenDiscourse

OpenDiscourse is a powerful platform for analyzing and processing political discourse data.

## Features

- Document processing and analysis
- Entity extraction and management
- Vector-based document similarity search
- RESTful API for integration

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/opendiscourse.git
   cd opendiscourse
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .[dev]
   ```

## Usage

### Running the API

```bash
uvicorn opendiscourse.api.v1.routes:app --reload
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
ruff check --fix .
```

### Data Pipeline Workflow

To load documents into PostgreSQL, the project provides a pipeline script that
scrapes data from `govinfo.gov`, processes each document for entity extraction
and then stores the results. The pipeline requires a running PostgreSQL instance
and an API key.

Run locally with:

```bash
export POSTGRES_DB=opendiscourse
export POSTGRES_USER=opendiscourse
export POSTGRES_PASSWORD=opendiscourse
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export GOVINFO_API_KEY=<your api key>
python scripts/populate_database.py
```

This workflow is also available as a GitHub Action defined in
`.github/workflows/data-pipeline.yml` so it can be triggered manually or on a
schedule.

## Project Structure

```
opendiscourse/
├── opendiscourse/           # Main package
│   ├── api/                 # API endpoints
│   ├── core/                # Core functionality
│   ├── db/                  # Database models and connections
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
├── tests/                   # Test files
├── scripts/                 # Utility scripts
└── config/                  # Configuration files
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT
