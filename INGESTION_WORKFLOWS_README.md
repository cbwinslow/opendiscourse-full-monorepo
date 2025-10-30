# OpenDiscourse Data Ingestion Workflows

This repository contains comprehensive data ingestion workflows for three major US government data sources: **OpenStates**, **Congress.gov**, and **GovInfo.gov**. The workflows are designed to ingest legislative data into a PostgreSQL database with a unified schema.

## 📋 Overview

### Data Sources

1. **OpenStates** - State-level legislative data (bills, people, committees, events, votes)
2. **Congress.gov** - Federal legislative data (members, bills, committees, hearings, records, etc.)
3. **GovInfo.gov** - Official government publications (bill texts, actions, XML documents)

### Database Configuration

- **Host:** 172.28.82.205
- **Port:** 5432
- **Database:** opendiscourse
- **User:** opendiscourse
- **Password:** opendiscourse123

## 🚀 Quick Start

### 1. Database Setup

```bash
# Test database connectivity and run migrations
python3 setup_database.py
```

This will:
- Test connectivity to the PostgreSQL database
- Run the consolidated migration script to create all necessary tables
- Verify that all required tables exist

### 2. Run Sample Ingestions

```bash
# Run sample data ingestion for all workflows
python3 run_all_ingestions.py --mode sample
```

This will:
- Set up the database schema
- Download and ingest sample data from each source
- Generate a comprehensive report

### 3. Full Data Ingestion

```bash
# Run full data ingestion (requires API keys and more time)
python3 run_all_ingestions.py --mode full
```

## 📁 File Structure

```
├── database_config.env          # Database and API configuration
├── setup_database.py           # Database setup and migration script
├── test_database_connection.py # Database connectivity test
├── consolidated_database_migration.sql  # Complete database schema
├── ingest_openstates_data.py   # OpenStates data ingestion
├── ingest_congressgov_data.py  # Congress.gov data ingestion
├── ingest_govinfo_data.py      # GovInfo.gov data ingestion
├── run_all_ingestions.py       # Unified orchestration script
└── INGESTION_WORKFLOWS_README.md  # This documentation
```

## ⚙️ Configuration

### Environment Variables

Create or update `database_config.env` with your configuration:

```bash
# Database Configuration
DB_HOST=172.28.82.205
DB_PORT=5432
DB_NAME=opendiscourse
DB_USER=opendiscourse
DB_PASSWORD=opendiscourse123

# API Keys (required for data ingestion)
OPENSTATES_API_KEY=your_openstates_api_key_here
CONGRESS_API_KEY=your_congress_api_key_here
GOVINFO_API_KEY=your_govinfo_api_key_here  # Optional

# Ingestion Settings
BATCH_SIZE=50
MAX_RETRIES=3
RETRY_DELAY=5
```

### Obtaining API Keys

1. **OpenStates API Key**: Register at https://openstates.org/accounts/register/
2. **Congress.gov API Key**: Sign up at https://api.congress.gov/sign-up/
3. **GovInfo API Key**: Optional, register at https://api.govinfo.gov/sign-up/

## 📊 Individual Workflow Scripts

### OpenStates Data Ingestion

```bash
# Sample ingestion (limited data)
python3 ingest_openstates_data.py --mode sample

# Full ingestion (all data)
python3 ingest_openstates_data.py --mode full

# Specific data type
python3 ingest_openstates_data.py --data-type people --jurisdiction ca

# Specific jurisdiction only
python3 ingest_openstates_data.py --mode full --jurisdiction ca
```

**Supported Data Types:**
- `jurisdictions` - State and territorial jurisdictions
- `people` - Legislators and officials
- `bills` - Legislative bills
- `organizations` - Committees and organizations
- `events` - Legislative events and hearings

### Congress.gov Data Ingestion

```bash
# Sample ingestion
python3 ingest_congressgov_data.py --mode sample

# Full ingestion for specific Congress
python3 ingest_congressgov_data.py --mode full --congress 119

# Specific data type
python3 ingest_congressgov_data.py --data-type members --congress 119
```

**Supported Data Types:**
- `members` - Federal legislators
- `bills` - Federal bills and amendments
- `committees` - Congressional committees
- `hearings` - Congressional hearings
- `records` - Congressional records
- `register` - Federal register documents
- `laws` - Federal laws
- `nominations` - Executive nominations
- `treaties` - International treaties

### GovInfo Data Ingestion

```bash
# Sample ingestion (downloads sample files)
python3 ingest_govinfo_data.py --mode sample

# Full ingestion (process existing XML files)
python3 ingest_govinfo_data.py --mode full --xml-dir /path/to/xml/files

# Specific data type
python3 ingest_govinfo_data.py --data-type bills --xml-dir /path/to/xml/files
```

**Supported Data Types:**
- `bills` - Bill metadata and text
- `bill_actions` - Bill action history

## 🗄️ Database Schema

### OpenStates Tables (Open Civic Data Standard)
- `opencivicdata_jurisdiction` - State and territorial jurisdictions
- `opencivicdata_person` - Individual people (legislators, officials)
- `opencivicdata_bill` - Legislative bills
- `opencivicdata_billaction` - Bill actions and history
- `opencivicdata_voteevent` - Vote events and roll calls
- `opencivicdata_organization` - Organizations (committees, parties)

### Federal Tables (Congress.gov)
- `federal_members` - Federal legislators
- `federal_bills` - Federal bills, amendments, resolutions
- `federal_committees` - Congressional committees
- `federal_hearings` - Congressional hearings
- `federal_records` - Congressional records
- `federal_register_docs` - Federal register documents
- `federal_laws` - Federal laws
- `federal_nominations` - Executive nominations
- `federal_treaties` - International treaties

### GovInfo Tables
- `govinfo_bill` - Bill metadata from GovInfo
- `govinfo_bill_action` - Bill action history
- `govinfo_bill_cosponsor` - Bill cosponsors
- `govinfo_bill_committee` - Bill committee assignments

### Ingestion Tracking
- `master_ingestion_status` - Generic ingestion tracking
- `federal_member_ingestion_status` - Federal member-specific tracking

## 📈 Monitoring and Logs

### Log Files
- `openstates_ingestion.log` - OpenStates ingestion logs
- `congressgov_ingestion.log` - Congress.gov ingestion logs
- `govinfo_ingestion.log` - GovInfo ingestion logs
- `unified_ingestion.log` - Unified orchestration logs

### Results Files
- `ingestion_results_YYYYMMDD_HHMMSS.json` - Detailed results in JSON format
- Console output with progress indicators and summary statistics

### Sample Report Output

```
================================================================================
UNIFIED DATA INGESTION REPORT
================================================================================
Generated: 2025-10-30 12:41:55
Overall Duration: 0:05:23

SUMMARY:
  ✅ Completed: 3
  ❌ Failed: 0
  ⏭️ Skipped: 1

WORKFLOW DETAILS:
  Database Setup:
    Status: COMPLETED
    Duration: 0:00:03
  OpenStates Data:
    Status: COMPLETED
    Duration: 0:02:15
    Records Processed: 1250
    Records Successful: 1248
    Records Failed: 2
  Congress.gov Data:
    Status: COMPLETED
    Duration: 0:01:45
    Records Processed: 850
    Records Successful: 850
    Records Failed: 0
  GovInfo Data:
    Status: COMPLETED
    Duration: 0:01:20
    Records Processed: 25
    Records Successful: 25
    Records Failed: 0
```

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check if database server is running
   - Verify connection details in `database_config.env`
   - Ensure firewall allows connection on port 5432

2. **API Key Not Found**
   - Set API keys in `database_config.env`
   - Check for typos in environment variable names
   - Verify API keys are active and have proper permissions

3. **Rate Limiting**
   - All scripts include built-in rate limiting
   - Reduce `BATCH_SIZE` in configuration for slower processing
   - Check API documentation for specific rate limits

4. **XML Parsing Errors (GovInfo)**
   - Verify XML files are not corrupted
   - Check file format matches expected patterns
   - Review log files for specific parsing errors

### Debugging

```bash
# Test database connectivity only
python3 test_database_connection.py

# Run individual workflows with verbose logging
python3 ingest_openstates_data.py --mode sample

# Check specific data type
python3 ingest_congressgov_data.py --data-type members --congress 119
```

## 🔄 Advanced Usage

### Custom Database Setup

```bash
# Run only database migration
psql -h 172.28.82.205 -U opendiscourse -d opendiscourse -f consolidated_database_migration.sql
```

### Scheduled Ingestion

For production environments, consider setting up scheduled ingestion:

```bash
# Add to crontab for daily ingestion
0 2 * * * /usr/bin/python3 /path/to/run_all_ingestions.py --mode full
```

### Monitoring

```bash
# Check recent ingestion results
tail -f unified_ingestion.log

# Monitor database table sizes
psql -h 172.28.82.205 -U opendiscourse -d opendiscourse -c "
SELECT schemaname, tablename, n_tup_ins, n_tup_upd 
FROM pg_stat_user_tables 
WHERE schemaname = 'public' 
ORDER BY n_tup_ins DESC;"
```

## 📝 Schema Migrations

The `consolidated_database_migration.sql` file contains the complete database schema. To apply updates:

1. Modify the migration file
2. Run the setup script: `python3 setup_database.py`
3. Verify changes: Check table structures in database

## 🤝 Contributing

When adding new data sources or modifying existing workflows:

1. Follow the established patterns in existing scripts
2. Update the database schema in `consolidated_database_migration.sql`
3. Add comprehensive logging and error handling
4. Update this documentation
5. Test with sample data before full deployment

## 📞 Support

For issues or questions:

1. Check the log files for error messages
2. Review the troubleshooting section above
3. Verify API keys and database connectivity
4. Test with sample mode before full ingestion

---

**Last Updated:** October 30, 2025  
**Version:** 1.0.0