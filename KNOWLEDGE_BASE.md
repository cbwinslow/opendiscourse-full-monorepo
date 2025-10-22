# OpenDiscourse Knowledge Base

## 📋 Project Overview
This knowledge base contains comprehensive information about government data sources, tools, and methodologies for analyzing political discourse and government activities.

## 🏛️ Source Repositories

### 1. OpenGovt (cbwinslow/opengovt)
- **Description**: Custom open government project by cbwinslow
- **Focus**: Government data collection and analysis tools
- **Location**: `external-sources/opengovt/`

### 2. OpenStates Ecosystem (openstates/*)
- **openstates/master**: Core legislative data collection system
  - **Location**: `external-sources/openstates/master/`
  - **Focus**: US state legislation tracking and data collection

- **openstates/people**: Legislator data and biographical information
  - **Location**: `external-sources/openstates/people/`
  - **Focus**: Detailed information about legislators

- **openstates/website**: OpenStates.org website codebase
  - **Location**: `external-sources/openstates/website/`
  - **Focus**: Frontend for legislative data presentation

- **openstates/core**: Core data processing and API framework
  - **Location**: `external-sources/openstates/core/`
  - **Focus**: Backend systems and data models

- **openstates/documentation**: Project documentation and guidelines
  - **Location**: `external-sources/openstates/documentation/`
  - **Focus**: How-to guides and technical documentation

- **openstates/pyopenstates**: Python library for accessing OpenStates API
  - **Location**: `external-sources/openstates/pyopenstates/`
  - **Focus**: Programmatic access to legislative data

## 📊 Data Sources Covered

### Legislative Data
- US Federal legislation (Congress.gov, GovInfo)
- US State legislation (OpenStates, OpenLegislation)
- International government sources

### Key APIs and Data Endpoints
- Congressional data APIs
- State legislative APIs
- Government document repositories
- Government data portals

## 🛠️ Technical Components

### Data Collection
- Web scrapers and crawlers
- API connectors
- Data validation and cleaning tools
- Schedule and event tracking systems

### Data Processing
- NLP and text analysis tools
- Document parsing and extraction
- Data normalization and standardization
- Cross-referencing systems

### Analysis and Research
- Sentiment analysis tools
- Topic modeling frameworks
- Network analysis of legislative relationships
- Policy tracking and change detection

## 🔍 Research Focus Areas

### Political Discourse Analysis
- Legislative text analysis
- Voting pattern analysis
- Policy change tracking
- Partisan language identification

### Government Transparency
- Document accessibility tools
- Data standardization across jurisdictions
- Open government initiatives
- Civic technology solutions

## 📚 Documentation and Resources

### Existing Documentation
- Core OpenDiscourse documentation
- API specifications
- Development guides
- Architecture documentation
- Research methodologies

### Best Practices
- Data accuracy verification
- Bias detection in government sources
- Privacy considerations for government data
- Ethics in political data analysis

## 🤖 LLM Usage Guidelines

When working with this knowledge base:

1. **Start with existing documentation** in `packages/docs/` for core OpenDiscourse systems
2. **Refer to external sources** in `external-sources/` for implementation patterns and data sources
3. **Consider data provenance** - be aware of the source and potential bias of each data set
4. **Use established tools** like those in the OpenStates ecosystem as reference implementations
5. **Review research methodologies** in the documentation to understand analytical approaches

## 🎯 Project Goals

### Primary Objectives
- Automate collection of government documents and data
- Apply advanced NLP techniques to analyze political discourse
- Create accessible tools for civic engagement and research
- Establish standards for open government data processing

### Technical Goals
- Scalable data collection architecture
- Accurate document processing and classification
- Real-time or near real-time data updates
- Comprehensive coverage across all government levels

## 🚀 Getting Started

1. Review the core OpenDiscourse architecture in the main packages
2. Examine the OpenStates codebase for patterns on handling government data
3. Identify which legislative APIs are most relevant to your research focus
4. Set up data collection pipelines based on examples in external sources
5. Implement analysis tools using the NLP frameworks referenced in documentation

This knowledge base provides comprehensive context for developing and extending the OpenDiscourse platform with insights from existing open government projects.