# OpenDiscourse Project - Agent Setup Guide

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Directory Structure](#directory-structure)
3. [Key Files and Their Purpose](#key-files-and-their-purpose)
4. [Agent Setup Instructions](#agent-setup-instructions)
5. [Working with the Codebase](#working-with-the-codebase)
6. [Task List](#task-list)
7. [Feature Suggestions](#feature-suggestions)
8. [Change Log](#change-log)
9. [Directory Cleanup Recommendations](#directory-cleanup-recommendations)

---

## 📖 Project Overview

The OpenDiscourse project is a sophisticated system designed to collect, process, and analyze government data from multiple sources. It combines legislative data from various government APIs and websites to enable research and analysis of political discourse and government activities.

- **Primary Focus**: Government data collection and analysis
- **Technology Stack**: Python backend, JavaScript/TypeScript frontend, with AI/ML components
- **Architecture**: Monorepo with multiple packages and applications
- **Data Sources**: Congress.gov, GovInfo, OpenStates, OpenLegislation, and other government APIs
- **AI Integration**: NLP and RAG (Retrieval Augmented Generation) components for analysis

---

## 🗂️ Directory Structure

```
opendiscourse/
├── apps/                          # Applications and services
│   ├── admin-panel/              # Administrative panel
│   ├── api-server/               # Main API server application
│   │   └── core/                 # Core API server files
│   ├── web-client/               # Main web client application
│   └── web-client-next/          # Next.js web client
├── external-sources/             # External government data source repositories
│   ├── opengovt/                 # cbwinslow's OpenGovt project
│   └── openstates/               # OpenStates ecosystem repositories
│       ├── core/                 # Core data processing
│       ├── documentation/        # Project documentation
│       ├── master/               # Main OpenStates codebase
│       ├── people/               # Legislator data
│       ├── pyopenstates/         # Python API library
│       └── website/              # OpenStates website code
├── packages/                     # Core packages
│   ├── api/                      # API services and business logic
│   │   ├── main-api/             # Main API components
│   │   ├── opendiscourse-core/   # Core OpenDiscourse API
│   │   └── profiles/             # Profile-related components
│   ├── data-collector/           # Data collection and processing
│   │   ├── data/                 # Data files
│   │   ├── processing/           # Data processing modules
│   │   └── sources/              # Data source collectors
│   ├── docs/                     # Documentation and research
│   │   ├── api-specs/            # API specifications
│   │   ├── content/              # Documentation content
│   │   ├── examples/             # Examples
│   │   ├── guides/               # Development guides
│   │   ├── misc/                 # Miscellaneous docs
│   │   └── research/             # Research documents
│   ├── infrastructure/           # Infrastructure as code
│   │   ├── ansible/              # Ansible playbooks
│   │   ├── caddy/                # Caddy server configurations
│   │   ├── config/               # Configuration files
│   │   ├── database/             # Database configurations
│   │   ├── database-migrations/  # Database migrations
│   │   ├── docker/               # Docker configurations
│   │   ├── k8s/                  # Kubernetes configurations
│   │   ├── terraform/            # Terraform configurations
│   │   └── sites/                # Site configurations
│   ├── rag-engine/               # RAG (Retrieval Augmented Generation) engine
│   │   ├── core/                 # Core RAG components
│   │   ├── document-processing/  # Document processing utilities
│   │   ├── search/               # Search components
│   │   └── vector-store/         # Vector store configurations
│   ├── shared/                   # Shared utilities and configurations
│   │   ├── analysis/             # Analysis utilities
│   │   ├── config/               # Shared configurations
│   │   ├── nlp/                  # NLP utilities
│   │   ├── python-config/        # Python configurations
│   │   ├── src/                  # Shared source code
│   │   ├── templates/            # Code templates
│   │   ├── testing/              # Shared testing utilities
│   │   ├── utils/                # Shared utilities
│   │   └── workflows/            # Shared workflows
│   └── web/                      # Web frontend components
├── requirements/                 # Python requirements
├── tools/                        # Utility tools
│   ├── diagnostic-tools/         # Diagnostic and monitoring tools
│   ├── scripts/                  # Utility scripts
│   │   ├── main/                 # Main scripts
│   │   ├── setup/                # Setup scripts
│   │   └── utilities/            # Utility scripts
│   └── testing/                  # Testing tools
├── .github/                      # GitHub configuration
├── .vscode/                      # VSCode configuration
├── infra/                        # Infrastructure configurations
├── local_backup/                 # Local backups
├── local_work_backup/            # Backup of original work
├── venv/                         # Python virtual environment (if exists)
├── CHANGELOG.md                  # Change log
├── ESSENTIAL_COMPONENTS.md       # Guide to core components
├── KNOWLEDGE_BASE.md             # Knowledge base for LLMs
├── PROJECT_OVERVIEW.md           # Project overview
├── README.md                     # Main README
├── README_MONOREPO.md            # Monorepo structure documentation
├── cleanup-non-essential.sh      # Cleanup script
├── package.json                  # Node.js package configuration
├── pnpm-workspace.yaml           # Pnpm workspace configuration
├── pyproject.toml                # Python project configuration
└── requirements.txt              # Main Python requirements
```

---

## 📄 Key Files and Their Purpose

| File/Directory | Purpose | Key Components |
|---|---|---|
| `packages/api/opendiscourse-core/` | Core API functionality | govinfo_api.py, main.py, database modules |
| `packages/data-collector/sources/` | Data collection from sources | congress_gov_collector.py, openstates_collector.py |
| `packages/data-collector/processing/` | Data processing | data_transformer.py, pipeline.py |
| `packages/rag-engine/` | AI/ML analysis components | RAG engine, vector stores |
| `external-sources/openstates/` | OpenStates reference implementations | Core data collection patterns |
| `packages/docs/research/` | Research documentation | Database schema, NLP research |
| `packages/docs/api-specs/` | API specifications | OpenAPI specs |
| `KNOWLEDGE_BASE.md` | LLM context | Comprehensive project overview for AI |
| `ESSENTIAL_COMPONENTS.md` | Core component guide | What to focus on |
| `requirements/` | Python dependencies | Various requirement files |

---

## 🤖 Agent Setup Instructions

### 1. Initial Environment Setup
1. Review `KNOWLEDGE_BASE.md` to understand the project's purpose and the external repositories
2. Read `PROJECT_OVERVIEW.md` to understand the current state of the project
3. Check `ESSENTIAL_COMPONENTS.md` to identify core components vs experimental features

### 2. Context Ingestion Process
1. **Core System Understanding**:
   - Read all files in `packages/docs/research/` for research context
   - Review `packages/docs/content/PROJECT_SUMMARY.md` for project goals
   - Examine `packages/docs/content/PROJECT_PLAN.md` for development roadmap

2. **API Understanding**:
   - Study `packages/docs/api/API_REFERENCE.md` for API specs
   - Review `packages/docs/api-specs/` for OpenAPI definitions
   - Examine `packages/api/opendiscourse-core/govinfo_api.py` as a reference

3. **Data Collection Process**:
   - Review `packages/data-collector/sources/` for collection patterns
   - Study `packages/data-collector/processing/pipeline.py` for processing flow
   - Check external reference implementations in `external-sources/openstates/`

4. **AI/ML Components**:
   - Study `packages/rag-engine/core/` for RAG implementation
   - Review `packages/shared/nlp/` for NLP utilities
   - Check `packages/docs/content/RAG_INTEGRATION.md` for RAG details

### 3. Focus Areas for Development
1. **Primary Focus**: Data collection and processing (`packages/data-collector/`)
2. **Secondary Focus**: API design and documentation (`packages/api/`)
3. **Tertiary Focus**: RAG engine and analysis (`packages/rag-engine/`)
4. **Reference**: External repositories in `external-sources/` for best practices

---

## 🔧 Working with the Codebase

### Development Workflow
1. **Data Collection**: Start in `packages/data-collector/sources/` 
2. **Data Processing**: Implement in `packages/data-collector/processing/`
3. **API Development**: Build in `packages/api/opendiscourse-core/`
4. **Analysis**: Implement in `packages/rag-engine/`
5. **Documentation**: Update in `packages/docs/`

### Key Technologies
- **Backend**: Python (Flask/FastAPI), with async support
- **Frontend**: JavaScript/TypeScript, React/Next.js
- **Database**: PostgreSQL, with potential for vector databases
- **AI/ML**: LangChain, various LLM integrations
- **Infrastructure**: Docker, Kubernetes, Terraform

### Configuration Files
- `requirements.txt` - Main Python dependencies
- `package.json` - Node.js dependencies
- `pyproject.toml` - Python project configuration
- `pnpm-workspace.yaml` - Pnpm monorepo configuration

---

## 📋 Task List

### Immediate Tasks
1. **Directory Cleanup**: Review and remove non-essential files
2. **Documentation Update**: Complete API documentation in `packages/docs/api/`
3. **Dependency Review**: Audit and update `requirements.txt`
4. **Code Organization**: Ensure consistent naming and structure

### Short-term Tasks
1. **Core API Development**: Implement unified API endpoints
2. **Data Collection**: Enhance collectors in `packages/data-collector/sources/`
3. **Testing**: Add unit and integration tests
4. **CI/CD**: Set up pipelines for automated testing

### Medium-term Tasks
1. **RAG Engine**: Improve retrieval and generation components
2. **NLP Components**: Enhance analysis capabilities
3. **UI/UX**: Improve web client interfaces
4. **Performance**: Optimize data processing pipelines

### Long-term Tasks
1. **Scalability**: Design for handling larger datasets
2. **Real-time**: Implement real-time data processing
3. **Analytics**: Advanced analytical dashboards
4. **API Expansion**: Support more government data sources

---

## 💡 Feature Suggestions

### High Priority
- **Unified Data Schema**: Create consistent schema across all data sources
- **Smart Caching**: Implement intelligent caching for frequently accessed data
- **API Rate Limiting**: Implement proper rate limiting and error handling
- **Data Validation**: Add comprehensive validation for collected data

### Medium Priority
- **Real-time Updates**: Implement webhooks for changes in government data
- **Advanced Search**: Full-text search across all collected documents
- **Data Export**: Multiple format export options
- **Dashboard**: Administrative dashboard for monitoring

### Low Priority
- **Social Media Integration**: Include social media mentions of legislation
- **Sentiment Analysis**: Advanced sentiment analysis for political discourse
- **Mobile App**: Native mobile application
- **Collaboration Tools**: Multi-user annotation and comment system

---

## 📝 Change Log

### 2025-10-14
- Created comprehensive monorepo structure with packages, apps, and tools
- Organized all research and documentation in `packages/docs/research/`
- Downloaded and integrated external repositories in `external-sources/`
- Created knowledge base for AI assistance in `KNOWLEDGE_BASE.md`
- Updated README files to reflect new structure

### Previous Changes
- Original project files organized from various sources
- Initial research documents and API specifications created
- Basic data collection components implemented

---

## 🧹 Directory Cleanup Recommendations

### Remove (with caution)
- `local_work_backup/` - Contains original work, keep only if needed
- `local_backup/` - Contains original files, archive if necessary
- Large binary files or tarballs if not actively used

### Organize
- Consolidate duplicate documentation files
- Group similar Python scripts in `tools/scripts/`
- Move configuration files to `packages/shared/config/`

### Review
- Check for temporary/intermediate files in various directories
- Verify which experimental packages are still needed
- Audit unused dependencies in requirement files

### Retain (Essential)
- All `packages/` directories - core functionality
- `external-sources/` - Reference implementations
- All documentation in `packages/docs/`
- Configuration files in root directory
- All test files and testing utilities

---

## 🚀 Getting Started for New Sessions

When resuming work on the project:

1. **Read the Knowledge Base**: Review `KNOWLEDGE_BASE.md` for context
2. **Check Current State**: Look at the change log above to see recent work
3. **Focus on Priority**: Look at the immediate tasks in the task list
4. **Reference External Sources**: Use `external-sources/openstates/` for best practices
5. **Follow Structure**: Work within the established package structure

This guide provides all necessary context for any agent to continue work on the OpenDiscourse project, with special attention to the AI-assisted development approach.