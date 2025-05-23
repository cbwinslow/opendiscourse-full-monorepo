# OpenDiscourse - Government Document Analysis Platform

A platform for analyzing and processing government documents using advanced NLP and entity extraction techniques.

## Features

- Entity extraction from government documents
- Relationship inference between entities
- Document processing and analysis
- Vector database integration for semantic search
- PostgreSQL database for structured data storage
- API endpoints for document processing

## Tech Stack

- Backend: Python with Flask
- Database: PostgreSQL
- AI/ML: Transformers and OpenAI models
- Vector Database: Pinecone
- Document Processing: BeautifulSoup and Requests
- Logging: Python logging module

## Project Structure

```
.
├── api/              # API endpoints
├── processors/       # Document processing components
├── services/         # External service integrations
├── models/           # Data models
├── utils/            # Utility functions
├── config/           # Configuration files
└── tests/           # Test files
```

## Getting Started

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Linux/Mac: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up environment variables (see below)
6. Run database migrations: `python setup-postgres.sh`
7. Start the services:
   - API: `python opendiscourse-api.py`
   - Document processor: `python govinfo_document_processor.py`
   - Scraper: `python govinfo_scraper.py`

## Environment Variables

```
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=opendiscourse
DB_USER=postgres
DB_PASSWORD=your_password

# Vector Database
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_pinecone_environment

# AI/ML
OPENAI_API_KEY=your_openai_api_key

# Document Processing
DOWNLOAD_DIR=/path/to/download/directory
PROCESSING_DIR=/path/to/processing/directory
COMPLETED_DIR=/path/to/completed/directory
ERROR_DIR=/path/to/error/directory
```

## License

MIT
