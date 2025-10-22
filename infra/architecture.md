# OpenDiscourse Cloud Architecture Design

## Overview
This document outlines the cloud architecture for the OpenDiscourse platform using both Oracle Cloud Free Tier and Cloudflare services. The architecture is designed to leverage the free tiers of both providers to create a cost-effective, scalable, and performant solution.

## Architecture Components

### Oracle Cloud Free Tier Components
1. **Compute**: 
   - 2x AMD EPYC vCPUs for running lightweight applications
   - 947MB RAM for basic services
   - Oracle Linux with development tools

2. **Storage**:
   - 30GB root storage for OS and core applications
   - 15GB additional storage for data and logs
   - Block storage for persistent data

3. **Networking**:
   - Virtual Cloud Network (VCN) with public and private subnets
   - Internet Gateway for public access
   - Security lists and network security groups

### Cloudflare Components
1. **Workers**:
   - Serverless functions for API endpoints
   - Edge computing for low-latency responses
   - Request handling and routing

2. **D1 (SQLite)**:
   - Serverless SQL database at the edge
   - Caching layer for frequently accessed data
   - User preferences and lightweight data storage

3. **KV (Key-Value Storage)**:
   - High-performance key-value storage
   - Caching for API responses
   - Session storage and configuration data

4. **Hyperdrive**:
   - Connection pooling for regional databases
   - Accelerated database connections
   - Bridge between Workers and origin databases

5. **R2 (Object Storage)**:
   - Serverless object storage
   - Storage for documents, images, and backups
   - CDN integration for content delivery

6. **Workers AI**:
   - Machine learning models at the edge
   - NLP processing for legislative analysis
   - Sentiment analysis and entity extraction

7. **Queues**:
   - Message queuing for asynchronous processing
   - Task distribution for background jobs
   - Event-driven workflows

## Data Flow Architecture

1. **Frontend Requests**:
   - User requests routed through Cloudflare CDN
   - Static assets served from R2 with CDN
   - API requests handled by Workers

2. **API Processing**:
   - Workers process incoming requests
   - KV cache checked for frequently accessed data
   - D1 queried for lightweight data operations
   - Hyperdrive used for database connections when needed

3. **AI Processing**:
   - NLP tasks delegated to Workers AI
   - Complex analysis tasks queued for background processing
   - Results cached in KV for future requests

4. **Data Storage**:
   - Primary database hosted on Oracle Cloud
   - Frequently accessed data cached in D1/KV
   - Documents and media stored in R2
   - Backups stored in Oracle Cloud Block Storage

5. **Background Processing**:
   - Data collection jobs queued in Cloudflare Queues
   - Workers process queues asynchronously
   - Results stored in Oracle Cloud database

## AI Agent Architecture

1. **Agent Framework**:
   - Custom SDK for agentic programming
   - Integration with OpenRouter for diverse model access
   - Cloudflare Workers AI as fallback/edge processing

2. **Agent Types**:
   - Data Collection Agents (collect from government APIs)
   - Analysis Agents (NLP processing, discrepancy detection)
   - Profile Generation Agents (create politician profiles)
   - Report Generation Agents (generate KPI reports)

3. **Agent Communication**:
   - Message passing through Cloudflare Queues
   - Shared state in D1/KV storage
   - Coordination through Durable Objects

## Deployment Strategy

1. **Development Environment**:
   - Oracle Cloud VM for development and testing
   - Local Pulumi for infrastructure management
   - GitHub for version control

2. **Production Environment**:
   - Cloudflare Workers for edge computing
   - Oracle Cloud for origin services
   - CI/CD pipeline with GitHub Actions

3. **Monitoring and Scaling**:
   - Cloudflare Analytics for edge performance
   - Oracle Cloud Monitoring for origin services
   - Auto-scaling based on demand (where supported)

## Security Considerations

1. **Authentication**:
   - API keys for Oracle Cloud services
   - Cloudflare API tokens with least privilege
   - JWT tokens for user authentication

2. **Data Protection**:
   - Encryption at rest and in transit
   - Regular backups to Oracle Cloud storage
   - Access logging and audit trails

3. **Network Security**:
   - Security lists in Oracle Cloud
   - Cloudflare WAF for DDoS protection
   - Private subnets for sensitive services

## Cost Optimization

1. **Free Tier Utilization**:
   - Maximize Oracle Cloud Always Free resources
   - Leverage Cloudflare free tier services
   - Monitor usage to avoid paid services

2. **Caching Strategy**:
   - Extensive use of KV and D1 caching
   - CDN for static assets
   - Edge computing to reduce origin requests

3. **Resource Management**:
   - Right-sizing of Oracle Cloud instances
   - Efficient queue processing to minimize compute time
   - Scheduled processing during off-peak hours