# Government Data Sources Research - OpenDiscourse

## Overview
This document summarizes the research findings on government data sources that will be used in the OpenDiscourse platform. Four primary sources have been identified: OpenStates, Congress.gov, GovInfo.gov, and OpenLegislation (OpenLaws).

## Data Sources Analysis

### 1. OpenStates

#### API Access
- **Base URL**: https://v3.openstates.org/
- **Authentication**: API key required (X-API-KEY header or ?apikey query parameter)
- **Documentation**: 
  - Interactive docs: https://v3.openstates.org/docs/
  - Alternative docs: https://v3.openstates.org/redoc/

#### Available Data
- **Jurisdictions**: State-level legislative information (states, DC, Puerto Rico, some municipal governments)
- **People**: Legislators, governors, mayors with current and historical roles
- **Bills**: Proposed legislation including bills, resolutions, constitutional amendments with votes, sponsorships, and actions
- **Committees**: Legislative committee information
- **Events**: Legislative events and meetings

#### Key Features
- JSON API responses
- Geographic lookup for legislators (/people.geo)
- Detailed bill tracking with full history
- Committee membership and activity data

### 2. Congress.gov (Library of Congress)

#### API Access
- **Base URL**: https://api.data.gov/congress/v3
- **Authentication**: API key required (sign up at Data.gov)
- **Documentation**: api.congress.gov
- **Version**: v3

#### Available Data
- **Bill Information**: Federal legislation data
- **Member Data**: Congressional representative information
- **Committee Data**: House and Senate committee information
- **Hearing Information**: Congressional hearing records
- **Vote Data**: Roll call votes and voting records

#### Key Features
- XML or JSON response formats
- Comprehensive federal legislative data
- Historical data access
- Regular updates with current session information

### 3. GovInfo.gov (Library of Congress)

#### Research Findings
- Limited specific API documentation found
- Part of the broader Library of Congress APIs
- Likely accessed through the general loc.gov API or bulk data downloads
- Contains official government publications, Federal Register documents, and Congressional records

#### Available Data (Based on Library of Congress APIs)
- **Government Publications**: Official documents and reports
- **Federal Register**: Daily official journal of federal agency rules and notices
- **Congressional Records**: Official transcripts of congressional proceedings
- **Historical Documents**: Archives of government publications

#### Access Methods
- Likely through bulk data downloads or general LC APIs
- May require special access arrangements for comprehensive data

### 4. OpenLegislation (OpenLaws)

#### API Access
- **Access**: Requires request for access and API bearer token
- **Onboarding**: 25-minute session for use cases and sandbox access
- **Support**: Slack community for questions and requests

#### Available Data
- **Statutes**: State and federal statutory law
- **Regulations**: Rules and regulations data
- **Constitutions**: State and federal constitutional text
- **Case Law**: Published court opinions (beta)

#### Key Features
- Bluebook citation-based querying
- Hierarchical law structure organization
- Cross-jurisdiction law comparison
- Legal text validation and correction
- Webhooks for change notifications (Enterprise)

#### Data Structure
- **Jurisdictions**: 50 states, federal (FED), DC, Puerto Rico (PR)
- **Laws**: Organized by keys (e.g., FED-CFR, CA-RR)
- **Divisions**: Hierarchical structure (Titles, Chapters, Sections, etc.)
- **Paths**: URL-like strings identifying specific law divisions

## Integration Strategy

### Data Collection Approach
1. **OpenStates**: Direct API integration for state-level legislative data
2. **Congress.gov**: Direct API integration for federal legislative data
3. **GovInfo.gov**: Investigate bulk data downloads or general LC API access
4. **OpenLegislation**: Request access and implement API integration for legal text

### Data Processing Considerations
- **Rate Limiting**: Implement appropriate delays for API calls
- **Data Validation**: Cross-reference information between sources
- **Update Scheduling**: Regular data synchronization processes
- **Error Handling**: Robust retry mechanisms for failed requests
- **Storage Optimization**: Efficient database schema for legislative data

### Key Challenges
- **API Key Management**: Secure storage and rotation of API keys
- **Data Consistency**: Different formats and structures across sources
- **Rate Limits**: Managing request volumes within API constraints
- **Data Quality**: Handling inconsistencies and missing information
- **Access Restrictions**: Some data may require special permissions

## Recommendations

### Immediate Actions
1. Register for OpenStates API key
2. Register for Congress.gov API key through Data.gov
3. Request access to OpenLaws API
4. Investigate GovInfo.gov bulk data access options

### Technical Considerations
- Implement modular data collection components for each source
- Design flexible data storage schema to accommodate different data structures
- Create data validation and cross-referencing mechanisms
- Develop monitoring and alerting for data collection processes
- Plan for data archival and historical tracking

### Legal and Ethical Considerations
- Review terms of service for each data source
- Ensure proper attribution for all government data
- Implement data usage policies consistent with source requirements
- Consider privacy implications of social media integration
- Plan for data retention and deletion policies