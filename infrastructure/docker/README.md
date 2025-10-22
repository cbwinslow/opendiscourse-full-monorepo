# OpenDiscourse Infrastructure Setup

This directory contains the Docker Compose configuration for setting up the OpenDiscourse infrastructure, including PostgreSQL with pgvector, Qdrant vector database, Neo4j graph database, and Redis.

## Prerequisites

Before you begin, ensure you have the following installed:
- Docker
- Docker Compose

## Services Included

1. **PostgreSQL with pgvector** - Main relational database with vector similarity search capabilities
2. **pgAdmin** - Web-based administration tool for PostgreSQL
3. **Qdrant** - Vector similarity search engine
4. **Neo4j** - Graph database for relationship mapping
5. **Redis** - In-memory data structure store for caching

## Getting Started

### 1. Start the Services

From this directory, run:

```bash
docker-compose up -d
```

This will start all services in detached mode.

### 2. Access the Services

After the services start, you can access them at the following addresses:

- **PostgreSQL**: localhost:5432
- **pgAdmin**: http://localhost:5050
- **Qdrant**: http://localhost:6333
- **Neo4j Browser**: http://localhost:7474
- **Neo4j Bolt**: localhost:7687
- **Redis**: localhost:6379

### 3. Configure pgAdmin (Optional)

1. Open pgAdmin at http://localhost:5050
2. Log in with:
   - Email: admin@opendiscourse.net
   - Password: admin
3. Add a new server with the following details:
   - Host: postgres
   - Port: 5432
   - Username: opendiscourse
   - Password: opendiscourse
   - Database: opendiscourse

## Service Details

### PostgreSQL with pgvector

PostgreSQL is configured with the pgvector extension for storing and querying vector embeddings. The initialization script creates tables for:

- Documents with vector embeddings
- Document metadata
- Extracted entities
- Entity relationships
- Search queries and results

### Qdrant

Qdrant is a vector similarity search engine optimized for ANN (Approximate Nearest Neighbor) search. It's particularly useful for semantic search applications.

### Neo4j

Neo4j is a graph database used for storing and querying complex relationships between entities extracted from government documents.

### Redis

Redis provides in-memory caching for improved performance of frequently accessed data.

## Stopping the Services

To stop all services, run:

```bash
docker-compose down
```

To stop and remove all data volumes (warning: this will delete all data), run:

```bash
docker-compose down -v
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: If you see port binding errors, make sure no other services are using the required ports.
2. **Permission denied**: On Linux, you might need to run Docker commands with `sudo`.
3. **Insufficient memory**: Some services like Neo4j require significant memory. Adjust Docker resources if needed.

### Checking Service Status

To check the status of running containers:

```bash
docker-compose ps
```

### Viewing Logs

To view logs for a specific service:

```bash
docker-compose logs <service-name>
```

For example:

```bash
docker-compose logs postgres
```

## Customization

You can customize the configuration by modifying the `docker-compose.yml` file:

1. Change passwords in the environment variables
2. Adjust port mappings
3. Modify volume mounts
4. Change resource limits

For production deployments, make sure to:
1. Change default passwords
2. Set up proper SSL/TLS encryption
3. Configure backups
4. Monitor resource usage
5. Set up proper access controls