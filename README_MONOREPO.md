# OpenDiscourse Monorepo with Government Data Sources

This monorepo contains the OpenDiscourse platform along with comprehensive government data sources and documentation for AI-assisted development.

## 🏗️ Repository Structure

### Core OpenDiscourse Platform
- `packages/api/` - API services and core logic
- `packages/web/` - Web frontend components
- `packages/data-collector/` - Data collection and processing
- `packages/rag-engine/` - RAG (Retrieval Augmented Generation) engine
- `packages/docs/` - Documentation and research
- `packages/infrastructure/` - Infrastructure as code
- `packages/shared/` - Shared utilities and configurations
- `apps/` - Applications (API server, web client, etc.)

### External Government Data Sources
- `external-sources/opengovt/` - cbwinslow's OpenGovt project
- `external-sources/openstates/` - OpenStates ecosystem repositories:
  - `master/` - Core legislative data collection system
  - `people/` - Legislator data and biographical information
  - `website/` - OpenStates.org website codebase
  - `core/` - Core data processing and API framework
  - `documentation/` - Project documentation and guidelines
  - `pyopenstates/` - Python library for OpenStates API access

### Knowledge Base
- `KNOWLEDGE_BASE.md` - Comprehensive information for LLM assistance
- `ESSENTIAL_COMPONENTS.md` - Guide to core system components
- `PROJECT_OVERVIEW.md` - Overview of the project structure

## 🚀 Quick Start for Development

### 1. Understanding the Knowledge Base
- Review `KNOWLEDGE_BASE.md` for comprehensive context
- Check `ESSENTIAL_COMPONENTS.md` to identify core components
- Refer to `PROJECT_OVERVIEW.md` for project architecture

### 2. Using LLM Assistance
This repository is structured to provide LLMs with comprehensive context:
- Source code from government data projects
- Extensive documentation
- API specifications
- Research methodologies
- Best practices

### 3. Core Development
1. Set up the environment:
   ```bash
   # Install dependencies (if using pnpm)
   pnpm install
   ```

2. Run the main services:
   ```bash
   # Start the API server
   cd apps/api-server
   # Follow instructions in the specific app README
   
   # Start the web client
   cd apps/web-client
   # Follow instructions in the specific app README
   ```

### 4. Working with Government Data
- Refer to `external-sources/openstates/` for examples of legislative data handling
- Examine data collection patterns in the OpenStates codebase
- Use the Python libraries in `pyopenstates/` for API access
- Review API specifications in `packages/docs/api-specs/`

## 📚 Key Resources for LLMs

When developing or extending this system, LLMs should reference:

1. **Core System**: Understanding from `packages/` directories
2. **External Patterns**: Implementation examples from `external-sources/`
3. **Documentation**: Both internal docs and external project docs
4. **API Specifications**: In `packages/docs/api-specs/` and external sources
5. **Research**: Methodologies in `packages/docs/research/`

## 🔗 Important Links

- [KNOWLEDGE_BASE.md](./KNOWLEDGE_BASE.md) - The primary resource for understanding the system
- [ESSENTIAL_COMPONENTS.md](./ESSENTIAL_COMPONENTS.md) - Focus areas for development
- [External Documentation](./external-sources/) - Reference implementations

## 🎯 Project Purpose

OpenDiscourse is designed to:
- Collect government data from multiple sources (Congress.gov, GovInfo, OpenStates, etc.)
- Process and analyze this data using AI/ML techniques
- Provide web-based interfaces for data access and analysis
- Support research and analysis workflows in political discourse

The included external repositories provide proven patterns and tools for handling government data that can inform improvements to the OpenDiscourse platform.