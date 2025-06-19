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

### RAG Database and Document Loaders

The repository includes helpers for building a retrieval augmented generation (RAG)
workflow. Document loaders in `opendiscourse/document_loaders.py` handle content
from websites, text files and PDFs. The `RAGDatabase` in `opendiscourse/rag_database.py`
wraps the vector store to store embeddings and search for relevant passages.

Example usage:

```python
from opendiscourse.document_loaders import HTMLLoader
from opendiscourse.rag_database import RAGDatabase
from opendiscourse.services.vector_store import vector_db

loader = HTMLLoader("https://example.com")
rag_db = RAGDatabase(vector_db)
rag_db.add_document(1, loader.load(), {"source": "example"})
results = rag_db.search("my query")
```

To populate the database with data from [govdata.gov](https://www.govdata.gov)
use the `GovDataAPI` helper:

```python
from opendiscourse.govdata_api import GovDataAPI

api = GovDataAPI()
datasets = api.list_datasets()
```

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
