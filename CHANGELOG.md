# Changelog

All notable changes to the OpenDiscourse project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive monorepo structure with packages, apps, and tools
- External government data source repositories in `external-sources/`
- Knowledge base for AI assistance in `KNOWLEDGE_BASE.md`
- Agent setup guide in `AGENT_SETUP_GUIDE.md`
- Organized documentation in `packages/docs/` with research, guides, and content sections
- Data collection modules in `packages/data-collector/`
- RAG (Retrieval Augmented Generation) engine in `packages/rag-engine/`

### Changed
- Restructured project from flat directory to monorepo architecture
- Organized all research and documentation into structured packages
- Updated README files to reflect new monorepo structure
- Consolidated configuration files in appropriate packages

### Removed
- Duplicate and experimental files from various directories
- Unorganized documentation into structured packages

---

## [2025-10-14] - Initial Monorepo Setup

### Added
- Created `apps/` directory with api-server, web-client, and admin-panel
- Created `external-sources/` with opengovt and openstates repositories
- Created `packages/` directory with api, data-collector, docs, infrastructure, rag-engine, shared, and web packages
- Created `tools/` directory with diagnostic-tools, scripts, and testing utilities
- Added comprehensive documentation files: KNOWLEDGE_BASE.md, ESSENTIAL_COMPONENTS.md, PROJECT_OVERVIEW.md
- Added setup guide: AGENT_SETUP_GUIDE.md

### Changed
- Moved all original files into appropriate package directories
- Restructured the entire project to follow monorepo best practices
- Updated package.json and pnpm-workspace.yaml for new structure
- Updated README.md to reflect new monorepo organization

---

## [2025-09-XX] - Research and API Integration

### Added
- Core API implementations in opendiscourse package
- API specifications and documentation
- Data collection modules for various government sources
- NLP and analysis utilities

### Changed
- Established initial project structure for government data collection
- Created various research documents in the original structure

---

## [2025-06-XX] - Initial Project Creation

### Added
- Initial project files and documentation
- Basic data collection components
- Research and development documentation