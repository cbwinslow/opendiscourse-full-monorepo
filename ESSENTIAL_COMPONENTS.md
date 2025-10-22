# OpenDiscourse Project - Essential Components Guide

This document outlines the essential components of the OpenDiscourse project and what can be safely removed if needed.

## 🎯 Essential Core Components

### 1. Data Collection Layer (`packages/data-collector/sources/`)
- `congress_gov_collector.py` - Collects data from Congress.gov
- `govinfo_collector.py` - Collects data from GovInfo
- `openstates_collector.py` - Collects data from OpenStates
- `openlegislation_collector.py` - Collects data from OpenLegislation
- `unified_collector.py` - Main entry point for data collection

### 2. Core API (`packages/api/opendiscourse-core/`)
- `govinfo_api.py` - Main API interface for government data
- `main.py` - Entry point for the core API
- Database modules in `db/` subdirectory
- Ingestion modules in `ingestion/` subdirectory

### 3. Data Processing (`packages/data-collector/processing/`)
- `data_transformer.py` - Transforms raw data for processing
- `data_validator.py` - Validates collected data
- `pipeline.py` - Main processing pipeline

### 4. Core Dependencies (`requirements/`)
- `requirements.txt` - Main Python dependencies
- `requirements-langchain.txt` - AI/NLP dependencies
- `requirements_integration.txt` - Integration dependencies

### 5. Web Interface (`apps/web-client/`)
- Main web interface for interacting with the system

## 📚 Important Documentation & Research
- `packages/docs/research/` - Contains your research and analysis
- `packages/docs/guides/` - Setup and operational guides
- `packages/docs/api-specs/` - API specifications

## 🔧 Infrastructure Components
- `packages/infrastructure/` - Deployment and infrastructure code
- Docker configurations
- Terraform configurations

## 🚫 Less Critical Components (Safe to Remove if Needed)
- Experimental features in various packages
- Backup files and temporary configurations
- Some of the diagnostic tools if not immediately needed
- Additional example files that may be duplicative

## ⚠️ Do NOT Remove
- Core database models and connections
- Main data collection scripts
- Essential API endpoints
- Main configuration files
- The documentation and research files (likely important to your work)

## 📝 Recommendation for Cleanup
If you want to simplify the project:

1. Keep the essential core components listed above
2. Preserve all documentation and research
3. Consider removing experimental features or code that's not actively used
4. Consolidate duplicate files or examples
5. Remove temporary or backup files that are no longer needed

This project appears to be a sophisticated system for collecting, processing, and analyzing government-related data using AI/ML techniques.