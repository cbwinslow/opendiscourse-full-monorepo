# LlamaIndex Role

This role deploys and configures LlamaIndex (formerly GPT Index), a data framework for LLM applications, for the OpenDiscourse platform.

## Features

- LlamaIndex service deployment
- Integration with multiple LLM providers (LocalAI, OpenAI, etc.)
- Support for various vector stores (Weaviate, Qdrant, FAISS, etc.)
- Document loaders for multiple formats (PDF, DOCX, HTML, etc.)
- Data connectors for various sources
- Query and chat engines
- Monitoring and logging
- Authentication and API keys
- Environment-specific configurations

## Requirements

- Python 3.8+
- Docker and Docker Compose
- Vector store (Weaviate, Qdrant, etc.)
- LLM service (LocalAI, OpenAI, etc.)
- Minimum 4GB RAM (16GB+ recommended for production)
- Ports: 8000 (API), 8080 (Web UI, optional)

## Role Variables

### Required Variables

```yaml
# Core Configuration
llamaindex_enabled: true
llamaindex_version: "0.9.0"
llamaindex_environment: "production"
llamaindex_secret_key: "{{ vault_llamaindex_secret_key }}"

# LLM Configuration
llamaindex_llm:
  provider: "localai"  # localai, openai, anthropic, etc.
  model: "gpt-4"
  api_key: "{{ vault_llm_api_key }}"
  api_base: "http://localai:8080/v1"
  temperature: 0.7
  max_tokens: 2048

# Vector Store Configuration
llamaindex_vector_store:
  type: "weaviate"  # weaviate, qdrant, faiss, etc.
  url: "http://weaviate:8080"
  api_key: "{{ vault_weaviate_api_key }}"
  index_name: "documents"
  embedding_dimension: 1536

# Storage Configuration
llamaindex_storage:
  type: "local"  # local, s3, gcs, etc.
  path: "/data/llamaindex"
  s3_bucket: ""
  s3_prefix: "llamaindex/"
```

### Optional Variables

```yaml
# API Configuration
llamaindex_api:
  host: "0.0.0.0"
  port: 8000
  workers: 4
  log_level: "info"
  cors_origins: ["*"]
  rate_limit: "100/minute"

# Web UI (Optional)
llamaindex_web:
  enabled: true
  port: 8080
  theme: "dark"
  disable_auth: false

# Authentication
llamaindex_auth:
  enabled: true
  admin_username: "admin"
  admin_password: "{{ vault_llamaindex_admin_password }}"
  jwt_secret: "{{ vault_llamaindex_jwt_secret }}"
  session_timeout: 86400  # seconds

# Document Processing
llamaindex_processing:
  chunk_size: 1024
  chunk_overlap: 200
  max_chunks_per_doc: 1000
  extract_metadata: true
  ocr_enabled: false
  language: "en"

# Monitoring
llamaindex_monitoring:
  prometheus_enabled: true
  sentry_dsn: ""
  log_level: "info"
  log_format: "json"

# Backup
llamaindex_backup:
  enabled: true
  schedule: "0 2 * * *"  # Daily at 2 AM
  retention_days: 30
  target: "local"  # local, s3, gcs
  s3_bucket: ""
  s3_path: "backups/llamaindex/"
```

## Dependencies

- python3
- docker
- vector store (weaviate, qdrant, etc.)
- llm service (local-ai, openai, etc.)

## Example Playbook

```yaml
- hosts: llamaindex_servers
  become: true
  roles:
    - role: llamaindex
      vars:
        llamaindex_enabled: true
        llamaindex_version: "0.9.0"
        
        llamaindex_llm:
          provider: "localai"
          model: "gpt-4"
          api_key: "{{ vault_llm_api_key }}"
          api_base: "http://localai:8080/v1"
        
        llamaindex_vector_store:
          type: "weaviate"
          url: "http://weaviate:8080"
          api_key: "{{ vault_weaviate_api_key }}"
          index_name: "documents"
        
        llamaindex_storage:
          type: "local"
          path: "/data/llamaindex"
        
        llamaindex_auth:
          admin_username: "admin"
          admin_password: "{{ vault_llamaindex_admin_password }}"
```

## Configuration

### File Structure

```
/opt/llamaindex/
├── docker-compose.yml
├── .env
├── config/
│   ├── api_config.yaml
│   ├── logging.conf
│   └── nginx/
│       └── nginx.conf
├── data/
│   ├── documents/
│   ├── indices/
│   └── cache/
└── backups/
```

### Environment Variables

Key environment variables:

- `LLAMA_INDEX_API_KEY`: API key for authentication
- `LLM_API_KEY`: LLM provider API key
- `VECTOR_STORE_URL`: Vector store connection URL
- `STORAGE_PATH`: Path for document storage
- `LOG_LEVEL`: Logging level (debug, info, warning, error)
- `ENVIRONMENT`: Deployment environment (production, staging, development)

## Integration

### Python Client

```python
from llama_index import (
    GPTVectorStoreIndex,
    SimpleDirectoryReader,
    LLMPredictor,
    ServiceContext
)
from langchain.llms import LocalAI

# Initialize LLM
llm = LocalAI(
    model_name="gpt-4",
    openai_api_key="your-api-key",
    openai_api_base="http://llamaindex:8000"
)

# Create service context
service_context = ServiceContext.from_defaults(
    llm_predictor=LLMPredictor(llm=llm)
)

# Load documents
documents = SimpleDirectoryReader('data').load_data()

# Create index
index = GPTVectorStoreIndex.from_documents(
    documents,
    service_context=service_context
)

# Query engine
query_engine = index.as_query_engine()
response = query_engine.query("What is the capital of France?")
print(response)
```

### REST API

```bash
# Create index
curl -X POST http://llamaindex:8000/api/v1/indexes \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "documents", "vector_store": "weaviate"}'

# Upload document
curl -X POST http://llamaindex:8000/api/v1/documents \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@document.pdf" \
  -F "index=documents"

# Query
curl -X POST http://llamaindex:8000/api/v1/query \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the capital of France?", "index": "documents"}'
```

## Security

### Authentication

- API key authentication
- JWT tokens
- Rate limiting
- CORS protection
- Input validation

### Data Protection

- Encryption at rest
- Secure communication (HTTPS)
- Access controls
- Audit logging

## Monitoring

### Built-in Metrics

- Request/response metrics
- Query performance
- Document processing stats
- Error rates
- Resource usage

### Integration

- Prometheus metrics endpoint
- Grafana dashboards
- Alerting rules
- Log aggregation

## Backup and Recovery

### Data Backup

```bash
# Create backup
curl -X POST http://llamaindex:8000/api/v1/backup \
  -H "Authorization: Bearer YOUR_API_KEY"

# List backups
curl http://llamaindex:8000/api/v1/backups \
  -H "Authorization: Bearer YOUR_API_KEY"

# Restore from backup
curl -X POST http://llamaindex:8000/api/v1/restore \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"backup_id": "backup-20230101"}'
```

### Manual Backup

```bash
# Backup data directory
tar czf llamaindex_backup_$(date +%Y%m%d).tar.gz /opt/llamaindex/data

# Backup indices
rsync -avz /opt/llamaindex/data/indices/ /backup/llamaindex/indices/

# Restore
rsync -avz /backup/llamaindex/indices/ /opt/llamaindex/data/indices/
```

## Scaling

### Vertical Scaling

- Increase CPU/memory resources
- Optimize vector store performance
- Tune chunking parameters

### Horizontal Scaling

- Deploy multiple API instances
- Use a load balancer
- Shard indices
- Implement caching

## Tags

- `llamaindex:install`: Installation tasks
- `llamaindex:config`: Configuration tasks
- `llamaindex:api`: API configuration
- `llamaindex:auth`: Authentication setup
- `llamaindex:backup`: Backup configuration
- `llamaindex:monitoring`: Monitoring setup

## License

Proprietary - All rights reserved
