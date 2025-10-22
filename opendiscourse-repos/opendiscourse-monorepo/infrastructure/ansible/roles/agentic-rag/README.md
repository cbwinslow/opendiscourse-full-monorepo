# Agentic RAG Role

This role deploys and manages an Agentic RAG (Retrieval-Augmented Generation) system that combines language models with external knowledge retrieval for enhanced question answering and information synthesis.

## Features

- Integration with multiple vector stores (Weaviate, Qdrant, FAISS)
- Document ingestion pipeline
- Chunking and embedding strategies
- Hybrid search capabilities
- Query planning and routing
- Response generation with citations
- Caching layer for performance
- API endpoints for search and generation
- Monitoring and metrics
- Web interface for interaction

## Requirements

- Python 3.8+
- Docker and Docker Compose
- Vector database (Weaviate, Qdrant, or FAISS)
- Language model API (LocalAI, OpenAI, etc.)
- Sufficient RAM and CPU/GPU resources

## Role Variables

### Required Variables

```yaml
# Core Configuration
agentic_rag_enabled: true
agentic_rag_version: "v0.1.0"
agentic_rag_port: 8000

# Vector Store Configuration
vector_store_type: "weaviate"  # weaviate, qdrant, or faiss
vector_store_url: "http://weaviate:8080"

# LLM Configuration
llm_provider: "localai"  # localai, openai, anthropic, etc.
llm_model: "gpt-4"
llm_api_key: "{{ vault_llm_api_key }}"
llm_api_base: "http://localai:8080/v1"

# Embedding Model
embedding_model: "text-embedding-ada-002"
embedding_dimension: 1536

# Document Storage
document_storage_path: "/data/agentic-rag/documents"
```

### Optional Variables

```yaml
# Performance Tuning
chunk_size: 1000
chunk_overlap: 200
max_concurrent_requests: 10
cache_ttl: 3600

# Search Configuration
search_top_k: 5
search_score_threshold: 0.7
hybrid_search_alpha: 0.5

# API Configuration
api_auth_enabled: true
api_rate_limit: "100/minute"
cors_allowed_origins: ["*"]

# Monitoring
enable_prometheus: true
enable_tracing: true
log_level: "INFO"
```

## Dependencies

- docker
- vector store (weaviate, qdrant, or faiss)
- llm service (local-ai, openai, etc.)

## Example Playbook

```yaml
- hosts: rag_servers
  become: true
  roles:
    - role: agentic-rag
      vars:
        agentic_rag_enabled: true
        vector_store_type: "weaviate"
        vector_store_url: "http://weaviate:8080"
        llm_provider: "localai"
        llm_model: "gpt-4"
        llm_api_base: "http://localai:8080/v1"
        document_storage_path: "/data/agentic-rag/documents"
        api_auth_enabled: true
        api_rate_limit: "100/minute"
```

## Configuration

### Document Ingestion

1. Place documents in the `document_storage_path`
2. Supported formats: PDF, DOCX, TXT, Markdown
3. Automatic chunking and embedding
4. Metadata extraction

### Search Configuration

- Hybrid search combining vector similarity and keyword matching
- Custom ranking functions
- Filtering by metadata
- Query expansion

### API Endpoints

- `POST /ingest`: Ingest documents
- `POST /search`: Semantic search
- `POST /ask`: Generate answers with citations
- `GET /status`: Service health
- `GET /metrics`: Prometheus metrics

## Integration

### LangChain

```python
from langchain.vectorstores import Weaviate
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

# Initialize components
embeddings = OpenAIEmbeddings(openai_api_base="http://agentic-rag:8000")
llm = ChatOpenAI(openai_api_base="http://agentic-rag:8000")
db = Weaviate(weaviate_url="http://weaviate:8080", embedding=embeddings)

# Create QA chain
qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=db.as_retriever()
)

# Query
result = qa.run("What is the capital of France?")
```

### LlamaIndex

```python
from llama_index import (
    GPTVectorStoreIndex,
    ServiceContext,
    StorageContext
)
from llama_index.vector_stores import WeaviateVectorStore

# Initialize components
vector_store = WeaviateVectorStore(weaviate_url="http://weaviate:8080")
storage_context = StorageContext.from_defaults(vector_store=vector_store)
service_context = ServiceContext.from_defaults(
    llm=llm,
    embed_model=embeddings
)

# Create index
index = GPTVectorStoreIndex(
    [],  # Empty list for no initial documents
    storage_context=storage_context,
    service_context=service_context
)

# Query
query_engine = index.as_query_engine()
response = query_engine.query("What is the capital of France?")
```

## Security

- API key authentication
- Rate limiting
- Input validation
- Output sanitization
- Container isolation
- Network segmentation

## Monitoring

- Prometheus metrics
- Request logging
- Error tracking
- Performance metrics
- Query analytics

## Backup and Recovery

### Data Backup

```bash
# Backup vector store
docker exec weaviate /bin/bash -c 'weaviate-backup create /backups/weaviate_$(date +%Y%m%d)'

# Backup documents
rsync -avz /data/agentic-rag/documents /backups/documents_$(date +%Y%m%d)
```

### Configuration Backup

```bash
# Backup configuration
docker cp agentic-rag:/app/config /backups/agentic_rag_config_$(date +%Y%m%d)
```

## Scaling

### Vertical Scaling
- Increase CPU/memory resources
- Use GPU acceleration
- Optimize chunk size and overlap

### Horizontal Scaling
- Deploy multiple instances
- Use a load balancer
- Shard vector store

## Tags

- `agentic-rag:install`: Installation tasks
- `agentic-rag:config`: Configuration tasks
- `agentic-rag:api`: API configuration
- `agentic-rag:ingest`: Document ingestion
- `agentic-rag:search`: Search configuration

## License

Proprietary - All rights reserved
