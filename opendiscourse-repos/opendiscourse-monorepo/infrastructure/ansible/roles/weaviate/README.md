# Weaviate Role

This role installs and configures Weaviate, an open-source vector search engine, for the OpenDiscourse platform.

## Features

- Single node or cluster deployment
- Vector search with HNSW and other algorithms
- Multi-tenancy support
- GraphQL and REST API
- Authentication and authorization
- Backup and restore
- Monitoring and metrics
- Module integration (text2vec, qna, etc.)
- Persistence layer configuration
- Resource management

## Requirements

- Docker and Docker Compose
- Minimum 4GB RAM (16GB+ recommended for production)
- Sufficient disk space for vector data
- Ports: 8080 (API), 50051 (gRPC)

## Role Variables

### Required Variables

```yaml
# Core Configuration
weaviate_enabled: true
weaviate_version: "1.19.0"
weaviate_host: "0.0.0.0"
weaviate_port: 8080

# Vectorizer Configuration
weaviate_vectorizer: "text2vec-transformers"  # or "none", "text2vec-openai", etc.

# Authentication
weaviate_auth_enabled: true
weaviate_auth_credentials:
  - username: "admin"
    password: "{{ vault_weaviate_admin_password }}"
    scopes: ["admin"]
```

### Optional Variables

```yaml
# Persistence
weaviate_persistence_enabled: true
weaviate_persistence_path: "/var/lib/weaviate"

# Resource Management
weaviate_memory_limit: "4g"
weaviate_shards: 1
weaviate_replicas: 1

# Module Configuration
weaviate_modules:
  - name: "text2vec-transformers"
    repo: "semitechnologies/transformers-inference:sentence-transformers-multi-qa-MiniLM-L6-cos-v1"
    tag: "latest"

# Backup Configuration
weaviate_backup_enabled: true
weaviate_backup_provider: "filesystem"
weaviate_backup_path: "/backups/weaviate"

# Monitoring
weaviate_metrics_enabled: true
weaviate_tracing_enabled: true

# Network
weaviate_cors_allowed_origins: ["*"]
weaviate_grpc_port: 50051
```

## Dependencies

- docker
- python3-pip
- jq (for backup/restore scripts)

## Example Playbook

```yaml
- hosts: weaviate_servers
  become: true
  roles:
    - role: weaviate
      vars:
        weaviate_enabled: true
        weaviate_version: "1.19.0"
        weaviate_vectorizer: "text2vec-transformers"
        weaviate_auth_enabled: true
        weaviate_auth_credentials:
          - username: "admin"
            password: "{{ vault_weaviate_admin_password }}"
            scopes: ["admin"]
        weaviate_persistence_enabled: true
        weaviate_modules:
          - name: "text2vec-transformers"
            repo: "semitechnologies/transformers-inference:sentence-transformers-multi-qa-MiniLM-L6-cos-v1"
```

## Configuration

### File Locations

- Configuration: `/etc/weaviate/weaviate.conf`
- Data: `/var/lib/weaviate`
- Logs: `/var/log/weaviate`
- Backups: `/backups/weaviate` (configurable)

### Vectorizers

Weaviate supports multiple vectorizers:

1. **text2vec-transformers** (local)
   - Runs a transformer model locally
   - Good for privacy and low-latency

2. **text2vec-openai**
   - Uses OpenAI's API
   - Requires API key

3. **img2vec-neural**
   - For image vectors
   - Requires a neural network model

4. **none**
   - No vectorizer
   - Vectors must be provided during import

### Schema Configuration

Example schema for documents:

```graphql
{
  "classes": [
    {
      "class": "Document",
      "description": "A document with text content",
      "properties": [
        {
          "name": "title",
          "dataType": ["text"],
          "description": "Document title"
        },
        {
          "name": "content",
          "dataType": ["text"],
          "description": "Document content"
        },
        {
          "name": "source",
          "dataType": ["string"],
          "description": "Document source"
        },
        {
          "name": "createdAt",
          "dataType": ["date"],
          "description": "Creation date"
        }
      ],
      "vectorizer": "text2vec-transformers"
    }
  ]
}
```

## Security

### Authentication

- API key authentication
- OIDC (OpenID Connect)
- Anonymous access (not recommended for production)

### Network Security

- TLS/SSL encryption
- CORS configuration
- IP whitelisting
- Rate limiting

### Data Protection

- Field-level security
- Multi-tenancy
- Data encryption at rest (filesystem level)

## Backup and Recovery

### Filesystem Backup

```bash
# Create backup
curl -X POST http://localhost:8080/v1/backups/filesystem \
  -H "Content-Type: application/json" \
  -d '{
    "id": "my-backup",
    "include": ["Document", "Paragraph"],
    "backend": "filesystem"
  }'

# Restore backup
curl -X POST http://localhost:8080/v1/backups/filesystem/my-backup/restore \
  -H "Content-Type: application/json" \
  -d '{"include": ["Document", "Paragraph"]}'
```

### S3 Backup

```bash
# Create backup
curl -X POST http://localhost:8080/v1/backups/s3 \
  -H "Content-Type: application/json" \
  -d '{
    "id": "my-s3-backup",
    "include": ["Document"],
    "backend": "s3",
    "config": {
      "bucket": "my-weaviate-backups",
      "region": "us-west-2"
    }
  }'
```

## Monitoring

### Built-in Metrics

- Prometheus metrics at `/v1/metrics`
- Health endpoints at `/v1/.well-known/ready` and `/v1/.well-known/live`
- Tracing with OpenTelemetry

### Logging

- Structured JSON logs
- Configurable log levels
- Log rotation

## Performance Tuning

### Indexing

- Configure HNSW parameters:
  - `efConstruction`: Higher = better recall, slower indexing
  - `maxConnections`: Higher = better recall, more memory
  - `ef`: Higher = better recall, slower search

### Query Optimization

- Use `_additional` for metadata
- Limit result sets
- Use caching
- Optimize schema design

## Scaling

### Vertical Scaling

- Increase memory limit
- Tune HNSW parameters
- Adjust resource allocations

### Horizontal Scaling

- Deploy multiple instances
- Use a load balancer
- Configure sharding

## Integration

### Python Client

```python
import weaviate

# Initialize client
client = weaviate.Client(
    url="http://localhost:8080",
    auth_client_secret=weaviate.AuthApiKey(api_key="YOUR-API-KEY"),
)

# Create schema
schema = {
    "classes": [{"class": "Document", "properties": [{"name": "title", "dataType": ["text"]}]}]
}
client.schema.create(schema)

# Add data
data_object = {"title": "Example Document"}
client.data_object.create(data_object, "Document")

# Query
result = client.query.get("Document", ["title"]).with_limit(5).do()
```

### LangChain Integration

```python
from langchain.vectorstores import Weaviate
from langchain.embeddings import OpenAIEmbeddings

# Initialize Weaviate client
embeddings = OpenAIEmbeddings()
vectorstore = Weaviate(
    client=weaviate.Client("http://localhost:8080"),
    index_name="Document",
    text_key="text",
    embedding=embeddings,
    by_text=False
)

# Add documents
vectorstore.add_texts(["Document 1 text", "Document 2 text"])

# Similarity search
docs = vectorstore.similarity_search("query", k=3)
```

## Tags

- `weaviate:install`: Installation tasks
- `weaviate:config`: Configuration tasks
- `weaviate:auth`: Authentication setup
- `weaviate:backup`: Backup configuration
- `weaviate:monitoring`: Monitoring setup

## License

Proprietary - All rights reserved
