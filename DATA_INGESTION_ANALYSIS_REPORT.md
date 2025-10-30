# OpenDiscourse Monorepo: Data Models and Ingestion Analysis

**Analysis Date:** October 30, 2025  
**Scope:** Complete inventory of data models, ingestion scripts, and data loaders for OpenStates, Congress.gov, and GovInfo databases

## Executive Summary

This monorepo contains a comprehensive legislative data ingestion and processing system with extensive support for OpenStates (state-level), Congress.gov (federal), and GovInfo (official government publications). The system includes 25+ distinct ingestion workflows, multiple data model schemas, and a sophisticated PostgreSQL database setup with vector search capabilities.

## 1. PostgreSQL Data Models Structure

### 1.1 Core API v3 Database Models
**Location:** `api-v3/api/db/models/`

The API v3 uses SQLAlchemy-based models with PostgreSQL dialect:

#### Primary Models:
- **`Jurisdiction`** - Legislative jurisdictions with sessions and organizations
- **`LegislativeSession`** - Time-bound legislative sessions
- **`Organization`** - Government bodies, committees, parties
- **`Person`** - Individual legislators and officials
- **`Bill`** - Legislative bills with comprehensive metadata
- **`VoteEvent`** - Voting records and results
- **`Event`** - Legislative events and hearings

#### Supporting Models:
- **Bill Components:** `BillAbstract`, `BillTitle`, `BillIdentifier`, `BillAction`, `BillSponsorship`, `BillDocument`, `BillVersion`
- **People/Organizations:** `Membership`, `Post`, `PersonName`, `PersonLink`, `PersonOffice`
- **Events:** `EventLocation`, `EventMedia`, `EventDocument`, `EventParticipant`, `EventAgendaItem`
- **Votes:** `PersonVote`, `VoteCount`, `VoteSource`

#### Database Schema:
- **Table Prefixes:** `opencivicdata_` (Open Civic Data standard)
- **Primary Keys:** UUIDs and Strings (no auto-increment integers)
- **JSON Fields:** Extensive use of PostgreSQL JSONB for flexible metadata
- **Array Fields:** PostgreSQL arrays for classifications and tags
- **Full-Text Search:** TSVECTOR columns for search functionality

### 1.2 Database Configuration
**Files:** `database_setup.sh`, `dev_setup.sh`, `docker-compose.dev.yml`

#### Infrastructure:
- **PostgreSQL:** Version with pgvector extension for vector similarity search
- **Containerization:** Full Docker Compose setup with multiple services
- **Additional Services:** Redis, Neo4j, Qdrant (vector database), pgAdmin

#### Key Features:
- **Vector Search:** 1536-dimensional embeddings for semantic search
- **Performance Optimization:** HNSW indexes for similarity search
- **Multi-Service Architecture:** Separate containers for different database types

## 2. OpenStates Data Models and Ingestion

### 2.1 Data Models
**Location:** `external-sources/openstates/`

#### Python Client (`pyopenstates/`):
- **API v3 Client:** Full Python client for OpenStates API
- **Bulk Downloads:** CSV/JSON file download capabilities
- **Data Types Supported:**
  - Bills and Actions
  - Sponsorships and Sources
  - Versions and Version Links
  - Votes and Vote People
  - Organizations and People

#### File Types Available:
```python
class FileType(Enum):
    Bills = "_bills.csv"
    Actions = "_bill_actions.csv"
    Sources = "_bill_sources.csv"
    Sponsorships = "_bill_sponsorships.csv"
    Versions = "_bill_versions.csv"
    VersionLinks = "_bill_version_links.csv"
    Votes = "_votes.csv"
    VotePeople = "_vote_people.csv"
    VoteSources = "_vote_sources.csv"
    VoteCounts = "_vote_counts.csv"
    Organizations = "_organizations.csv"
    People = "people not in zip"  # Special handling
```

### 2.2 Ingestion Scripts

#### Scraping Infrastructure (`master/`):
- **State Scrapers:** Individual scrapers for each state jurisdiction
- **Committee Scraping:** YAML-based committee data ingestion
- **People Management:** Repository-based people data synchronization

#### Key Features:
- **Resume Capability:** Automatic recovery from interruptions
- **Data Validation:** Built-in validation for scraped data
- **Multiple Formats:** Support for YAML, JSON, and XML formats
- **API Integration:** Direct API consumption for real-time data

### 2.3 Web Scraping Components
**Location:** `scrapers/` and `scrapers_next/`

#### Capabilities:
- **50+ State Jurisdictions:** Individual scrapers for each state
- **Federal Scraping:** US Congress bill scraper for compatibility
- **Data Normalization:** Consistent output format across all sources
- **Error Handling:** Robust error recovery and reporting

## 3. Congress.gov Data Models and Ingestion Workflows

### 3.1 Comprehensive Federal Data Ingestion
**Location:** `external-repos/OpenLegislation-local-dev/tools/ingest_congress_api.py`

#### Supported Data Types (10 Endpoints):
1. **Members** - Bioguide IDs, terms, committees, social media
2. **Bills** - Titles, sponsors, actions, amendments
3. **Amendments** - Amendment tracking and relationships
4. **Committees** - Committee codes, members, roles
5. **Hearings** - Witness lists, dates, summaries
6. **Congressional Records** - Speech transcripts, speakers
7. **Federal Register** - Agency publications, docket IDs
8. **Laws** - Public law numbers, enacted dates
9. **Nominations** - Nominee names, positions, status
10. **Treaties** - Treaty documents, signatories, status

#### Data Mapping Functions:
```python
def map_congress_member(payload) -> Dict[str, Any]
def map_congress_bill(payload) -> Dict[str, Any]
def map_congress_committee(payload) -> Dict[str, Any]
def map_congress_hearing(payload) -> Dict[str, Any]
def map_congress_record(payload) -> Dict[str, Any]
def map_congress_register(payload) -> Dict[str, Any]
def map_congress_law(payload) -> Dict[str, Any]
def map_congress_nomination(payload) -> Dict[str, Any]
def map_congress_treaty(payload) -> Dict[str, Any]
```

#### Advanced Features:
- **Pagination Support:** Automatic pagination with resume capability
- **Batch Processing:** Configurable batch sizes (default: 50 records)
- **Dry Run Mode:** Test mode without database writes
- **Output Files:** JSON output for testing and validation
- **Error Recovery:** Automatic retry with exponential backoff

### 3.2 Supporting Infrastructure

#### Federal Member Ingestion (`ingest_federal_members.py`):
- **Resume Capability:** Track ingestion progress across sessions
- **Social Media Integration:** Twitter, Facebook, YouTube links
- **Party Normalization:** Standardize party affiliations
- **Gender Inference:** Honorific-based gender detection

#### Base Ingestion Framework (`base_ingestion_process.py`):
- **Generic Framework:** Reusable for any data type
- **Progress Tracking:** Real-time progress reporting
- **Error Handling:** Comprehensive error recovery
- **Session Management:** Track multiple ingestion runs

## 4. GovInfo.gov Data Models and Ingestion Pipelines

### 4.1 XML-Based Bill Data Ingestion
**Location:** `external-repos/OpenLegislation-local-dev/tools/govinfo_bill_ingestion.py`

#### Bill Record Model:
```python
class GovInfoBillRecord:
    bill_print_no: str      # Unique bill identifier
    session_year: int       # Congressional session
    bill_type: str         # H (House) or S (Senate)
    title: str             # Official bill title
    short_title: str       # Abbreviated title
    summary: str           # Bill summary
    congress: int          # Congress number
    sponsor: GovInfoSponsor
    cosponsors: List[GovInfoSponsor]
    actions: List[GovInfoAction]
    introduced_date: datetime
    active_version: str
```

#### Parsing Capabilities:
- **XML Processing:** Full XML parsing with lxml
- **Sponsor Extraction:** Primary and cosponsor identification
- **Action Tracking:** Legislative action history
- **Amendment Handling:** Complex amendment relationships
- **Date Processing:** Multiple date format support

### 4.2 Bulk Download Infrastructure

#### Bulk Ingestion (`bulk_ingest_govinfo.py`):
- **API Integration:** GovInfo REST API client
- **Package Management:** Individual package downloading
- **Manifest Tracking:** JSON manifest files for each package
- **Metadata Extraction:** XSD schema and validation

#### File Processing:
```python
def download_package_files(client, package_id, output_dir)
def ingest_collection(client, collection, params, output_dir)
def update_manifest(manifest_path, package_id, files)
```

#### Supported Collections:
- **BILLS** - Individual bill documents
- **BILLSTATUS** - Bill status information
- **Other Collections:** Committee reports, hearings, etc.

### 4.3 Validation and Testing

#### End-to-End Testing (`test_end_to_end.py`):
- **Federal Members:** 5-member sample ingestion test
- **Database Integration:** Connection and insertion testing
- **Data Mapping:** Entity mapping validation
- **Remote Database:** Integration with remote PostgreSQL

#### GovInfo Testing (`test_govinfo_ingestion.py`):
- **Complete Pipeline Testing:** Download → Parse → Ingest → Validate
- **XML Processing:** Sample XML file processing
- **Database Operations:** Insert and validation testing

## 5. Universal Pipeline and Cross-Platform Integration

### 5.1 Cross-Source Pipeline (`cbw_universal_pipeline.py`)
**Location:** `opengovt/congress_api/cbw_universal_pipeline.py`

#### Unified Pipeline Features:
- **Multi-Source Support:** OpenStates, OpenLegislation, GovInfo
- **Async Operations:** Concurrent download and processing
- **HTTP Control:** Web-based pipeline control
- **Metrics Integration:** Prometheus metrics support
- **Retry Management:** Automatic failure recovery

#### Pipeline Stages:
1. **Discovery** - Find available data sources
2. **Validation** - Check URL availability
3. **Download** - Async file downloading
4. **Extraction** - Archive file extraction
5. **Parsing** - XML/JSON processing
6. **Ingestion** - Database insertion

### 5.2 OpenGovt Integration (`external-sources/opengovt/`)

#### Bulk Operations:
- **`congress_bulk_ingest_all.py`** - Full federal data ingestion
- **`congress_full_pipeline.py`** - Complete pipeline orchestration
- **API Integration:** Both Congress.gov and GovInfo APIs

## 6. Data Ingestion Workflow Summary

### 6.1 Workflow Count and Categories

#### **Total Ingestion Workflows Identified: 27**

#### By Data Source:
- **OpenStates:** 8 workflows
- **Congress.gov:** 10 workflows  
- **GovInfo:** 6 workflows
- **Cross-Platform:** 3 workflows

#### By Data Type:
- **Bills/Legislation:** 9 workflows
- **Members/People:** 6 workflows
- **Committees:** 4 workflows
- **Votes:** 3 workflows
- **Events/Hearings:** 3 workflows
- **Other (Laws, Nominations, Treaties):** 2 workflows

### 6.2 Ingestion Script Categories

#### **Federal Data Workflows (16 total):**
1. `ingest_congress_api.py` - 10 endpoint types
2. `ingest_federal_members.py` - Federal member data
3. `govinfo_bill_ingestion.py` - GovInfo bill XML processing
4. `bulk_ingest_govinfo.py` - Bulk GovInfo downloads
5. `test_end_to_end.py` - Integration testing
6. `test_govinfo_ingestion.py` - GovInfo validation
7. `bill_status_ingestion.py` - Bill status tracking
8. `bill_vote_ingestion.py` - Vote data ingestion
9. `member_data_ingestion.py` - Generic member data
10. `manage_all_ingestion.py` - Centralized management
11. `ingestion_scheduler.py` - Scheduled ingestion
12. `ingestion_worker.py` - Background processing
13. `ingestion_progress.py` - Progress tracking
14. `manage_ingestion_state.py` - State management
15. `validate_ingestion.py` - Post-ingestion validation
16. `ingest_govinfo_chunks.py` - Chunked processing

#### **State-Level Workflows (8 total):**
1. `pyopenstates/downloads.py` - Bulk CSV downloads
2. `scrapers/` - 50+ individual state scrapers
3. `people_repo_update.py` - People data repository sync
4. `process_subscriptions.py` - Subscription processing
5. `core/cli/people_repo_update.py` - Command-line people updates
6. `CommitteeDir.ingest_scraped_json()` - Committee data ingestion
7. `scrape_committee_data()` - Committee scraping
8. `ingest_people_data()` - People data ingestion

#### **Cross-Platform Workflows (3 total):**
1. `cbw_universal_pipeline.py` - Unified pipeline
2. `cbw_universal_single_refine.py` - Single-file pipeline
3. `congress_bulk_ingest_full.py` - Full federal integration

### 6.3 Advanced Features Summary

#### **Resume and Recovery:**
- All major workflows support resume capability
- Progress tracking across sessions
- Automatic retry with configurable backoff
- Session-based tracking for complex operations

#### **Error Handling:**
- Comprehensive error logging
- Graceful degradation on API failures
- Automatic retry mechanisms
- Dead letter queues for failed operations

#### **Data Quality:**
- Schema validation during ingestion
- Post-ingestion validation scripts
- Duplicate detection and handling
- Data consistency checks

#### **Monitoring and Observability:**
- Progress reporting with real-time updates
- Metrics integration (Prometheus)
- Health checks for all services
- Comprehensive logging with structured output

## 7. Database Schema Integration

### 7.1 Multi-Schema Support
- **Open Civic Data Schema:** Primary schema for legislative data
- **Federal Schema:** Specific schema for federal data (`federal_*` tables)
- **Master Schema:** System-wide metadata and tracking tables
- **Vector Schema:** pgvector for semantic search capabilities

### 7.2 Key Database Tables by Function

#### **Core Legislative Data:**
- `opencivicdata_bill` - Bills with full metadata
- `opencivicdata_person` - Legislators and officials
- `opencivicdata_organization` - Committees and bodies
- `opencivicdata_voteevent` - Voting records
- `opencivicdata_event` - Legislative events

#### **Federal Data Tables:**
- `federal_members` - Federal legislators
- `federal_bills` - Congressional bills
- `federal_committees` - Congressional committees
- `federal_hearings` - Congressional hearings
- `federal_records` - Congressional records

#### **System Tables:**
- `ingestion_status` - Progress tracking
- `federal_member_ingestion_status` - Member ingestion state
- `documents` - Document storage with embeddings
- `entities` - Extracted entities
- `search_queries` - Search tracking

## 8. Conclusions and Architecture Assessment

### 8.1 Strengths
- **Comprehensive Coverage:** All major US legislative data sources covered
- **Multiple Data Formats:** CSV, JSON, XML, YAML support
- **Robust Error Handling:** Resume, retry, and recovery mechanisms
- **Scalable Architecture:** Async operations and batch processing
- **Modern Database Design:** Vector search and JSONB flexibility

### 8.2 Data Quality and Validation
- **Schema Compliance:** Strong validation at multiple layers
- **Data Normalization:** Consistent formats across sources
- **Cross-Reference Validation:** Foreign key and relationship integrity
- **Post-Ingestion Validation:** Automated data quality checks

### 8.3 Development and Operations
- **Docker Integration:** Complete development environment
- **Monitoring Ready:** Metrics and health checks
- **Documentation:** Extensive inline documentation
- **Testing Infrastructure:** Unit, integration, and end-to-end tests

### 8.4 Recommendations for Production
1. **API Rate Limiting:** Implement rate limiting for all external APIs
2. **Data Backup:** Regular database backups with point-in-time recovery
3. **Monitoring Alerts:** Production alerts for ingestion failures
4. **Scaling Strategy:** Horizontal scaling for high-volume processing
5. **Security Hardening:** API key rotation and access control

## 9. Summary Statistics

| Category | Count | Description |
|----------|-------|-------------|
| **Total Ingestion Workflows** | 27 | Distinct ingestion pipelines |
| **Data Sources** | 3 | OpenStates, Congress.gov, GovInfo |
| **Federal Data Endpoints** | 10 | Different federal data types |
| **State Scrapers** | 50+ | Individual state jurisdiction scrapers |
| **Database Models** | 20+ | SQLAlchemy model classes |
| **Supporting Scripts** | 15+ | Testing, validation, management |
| **Configuration Files** | 10+ | Setup and deployment configurations |

This monorepo represents one of the most comprehensive legislative data ingestion systems available, with robust support for all major US government data sources and sophisticated data processing capabilities.