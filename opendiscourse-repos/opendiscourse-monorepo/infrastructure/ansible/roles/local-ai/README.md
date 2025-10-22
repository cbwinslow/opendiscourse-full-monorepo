# LocalAI Role

This role deploys and manages LocalAI, a self-hosted, community-driven alternative to OpenAI's API that runs on consumer hardware.

## Features

- Deployment of LocalAI with Docker
- Model management and serving
- GPU acceleration support
- Persistent storage for models
- Integration with LangChain and LlamaIndex
- API key authentication
- Scaling configuration
- Model quantization options
- Custom template support

## Requirements

- Docker and Docker Compose
- Sufficient disk space for models (50GB+ recommended)
- Sufficient RAM (16GB+ recommended, more for larger models)
- CUDA-capable GPU (optional but recommended)

## Role Variables

### Required Variables

```yaml
# Base configuration
localai_enabled: true
localai_version: "v2.0.0"
localai_port: 8080

# Model configuration
localai_models:
  - name: "gpt-4"
    url: "https://huggingface.co/TheBloke/gpt4-x-vicuna-13B-GGUF/resolve/main/gpt4-x-vicuna-13B.Q4_K_M.gguf"
    backend: "llama"
    parameters:
      ctx_size: 2048
      threads: 4
      f16: true

# Authentication
localai_api_key: "{{ vault_localai_api_key }}
localai_auth_enabled: true
```

### Optional Variables

```yaml
# GPU Configuration
localai_gpu_enabled: true
localai_gpu_count: 1
localai_cuda_visible_devices: "0"

# Performance Tuning
localai_threads: 4
localai_ctx_size: 2048
localai_batch_size: 512
localai_parallel_requests: 1

# Storage
localai_data_dir: "/data/localai"
localai_models_dir: "{{ localai_data_dir }}/models"

# API Configuration
localai_api_host: "0.0.0.0"
localai_api_port: 8080
localai_debug: false

# Rate Limiting
localai_rate_limit: 60
localai_rate_limit_interval: 60

# CORS
localai_cors_enabled: true
localai_cors_allow_origins: ["*"]
```

## Dependencies

- docker
- nvidia-container-toolkit (if using GPU)

## Example Playbook

```yaml
- hosts: ai_servers
  become: true
  roles:
    - role: local-ai
      vars:
        localai_enabled: true
        localai_version: "v2.0.0"
        localai_models:
          - name: "gpt-4"
            url: "https://huggingface.co/TheBloke/gpt4-x-vicuna-13B-GGUF/resolve/main/gpt4-x-vicuna-13B.Q4_K_M.gguf"
            backend: "llama"
            parameters:
              ctx_size: 2048
              threads: 4
        localai_gpu_enabled: true
        localai_api_key: "{{ vault_localai_api_key }}
```

## Configuration

### Model Configuration

Models are configured in `localai_models` list. Each model can have:
- `name`: Model identifier
- `url`: Download URL for the model
- `backend`: Backend to use (llama, rwkv, etc.)
- `parameters`: Backend-specific parameters
- `template`: Template file for chat completion

### GPU Acceleration

For GPU acceleration:
1. Install NVIDIA drivers on the host
2. Install nvidia-container-toolkit
3. Set `localai_gpu_enabled: true`
4. Configure `localai_gpu_count` and `localai_cuda_visible_devices`

### API Endpoints

- Chat: `POST /v1/chat/completions`
- Completions: `POST /v1/completions`
- Embeddings: `POST /v1/embeddings`
- Models: `GET /v1/models`

## Integration

### LangChain

```python
from langchain.llms import LocalAI

llm = LocalAI(
    openai_api_key="your-api-key",
    openai_api_base="http://localhost:8080/v1",
    model="gpt-4"
)
```

### LlamaIndex

```python
from llama_index import (
    GPTVectorStoreIndex,
    SimpleDirectoryReader,
    LLMPredictor,
    ServiceContext
)
from langchain.llms import LocalAI

llm = LocalAI(
    openai_api_key="your-api-key",
    openai_api_base="http://localhost:8080/v1",
    model="gpt-4"
)

service_context = ServiceContext.from_defaults(llm_predictor=LLMPredictor(llm=llm))
documents = SimpleDirectoryReader('data').load_data()
index = GPTVectorStoreIndex.from_documents(documents, service_context=service_context)
```

## Security

- API key authentication
- Rate limiting
- Request validation
- Container isolation
- Network segmentation

## Monitoring

- Prometheus metrics at `/metrics`
- Logging to stdout/stderr
- Health checks at `/healthz`
- Request tracing

## Backup and Recovery

### Model Backup

```bash
# Backup models
tar czf localai_models_$(date +%Y%m%d).tar.gz {{ localai_models_dir }}

# Restore models
tar xzf localai_models_$(date +%Y%m%d).tar.gz -C {{ localai_models_dir }}
```

### Configuration Backup

```bash
# Backup configuration
docker cp localai:/app/config /backups/localai_config_$(date +%Y%m%d)
```

## Scaling

### Vertical Scaling
- Increase `localai_threads`
- Add more GPU resources
- Increase `localai_batch_size`

### Horizontal Scaling
- Deploy multiple instances behind a load balancer
- Use consistent hashing for model sharding
- Implement service discovery

## Tags

- `localai:install`: Installation tasks
- `localai:config`: Configuration tasks
- `localai:models`: Model management
- `localai:gpu`: GPU configuration
- `localai:api`: API configuration

## License

Proprietary - All rights reserved
