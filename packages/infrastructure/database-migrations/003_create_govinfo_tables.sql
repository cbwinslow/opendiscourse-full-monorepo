-- Migration 003_create_govinfo_tables.sql
-- Create tables for GovInfo.gov data

-- Collections table
CREATE TABLE IF NOT EXISTS govinfo_collections (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Packages table (GovInfo content packages)
CREATE TABLE IF NOT EXISTS govinfo_packages (
    id TEXT PRIMARY KEY,
    collection_id INTEGER REFERENCES govinfo_collections(id),
    title TEXT,
    category TEXT,
    date_issued DATE,
    last_modified TIMESTAMP,
    package_id TEXT,
    package_slug TEXT,
    package_size TEXT,
    package_type TEXT,
    package_url TEXT,
    package_zip_url TEXT,
    package_pdf_url TEXT,
    package_xml_url TEXT,
    package_html_url TEXT,
    package_txt_url TEXT,
    package_json_url TEXT,
    package_dais_url TEXT,
    package_mods_url TEXT,
    package_premis_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CFR (Code of Federal Regulations) titles table
CREATE TABLE IF NOT EXISTS govinfo_cfr_titles (
    id SERIAL PRIMARY KEY,
    title_number INTEGER,
    title_name TEXT,
    agency_name TEXT,
    agency_acronym TEXT,
    agency_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CFR sections table
CREATE TABLE IF NOT EXISTS govinfo_cfr_sections (
    id TEXT PRIMARY KEY,
    title_number INTEGER,
    part_number INTEGER,
    section_number TEXT,
    section_name TEXT,
    content TEXT,
    date_issued DATE,
    last_modified TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Federal Register documents table
CREATE TABLE IF NOT EXISTS govinfo_fed_register_docs (
    id TEXT PRIMARY KEY,
    document_type TEXT,
    document_number TEXT,
    title TEXT,
    publication_date DATE,
    start_page INTEGER,
    end_page INTEGER,
    page_length INTEGER,
    cfr_references JSONB,
    agencies JSONB,
    action TEXT,
    summary TEXT,
    dates TEXT,
    further_info TEXT,
    supplementary_info TEXT,
    signer TEXT,
    signer_position TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- US Code tables table
CREATE TABLE IF NOT EXISTS govinfo_uscode_tables (
    id SERIAL PRIMARY KEY,
    title_number INTEGER,
    table_name TEXT,
    content TEXT,
    date_issued DATE,
    last_modified TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Public laws table
CREATE TABLE IF NOT EXISTS govinfo_public_laws (
    id TEXT PRIMARY KEY,
    congress_number INTEGER,
    law_number INTEGER,
    law_type TEXT,
    title TEXT,
    citation TEXT,
    enacted_date DATE,
    congress_session TEXT,
    statute_at_large_citation TEXT,
    statute_at_large_pages TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Statutes at Large table
CREATE TABLE IF NOT EXISTS govinfo_statutes_at_large (
    id TEXT PRIMARY KEY,
    volume_number INTEGER,
    page_start INTEGER,
    page_end INTEGER,
    law_number TEXT,
    law_title TEXT,
    session_number INTEGER,
    session_type TEXT,
    congress_number INTEGER,
    congress_session TEXT,
    date_approved DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Congressional Record tables
CREATE TABLE IF NOT EXISTS govinfo_congressional_record (
    id TEXT PRIMARY KEY,
    volume_number INTEGER,
    issue_number INTEGER,
    publication_date DATE,
    congress_number INTEGER,
    congress_session TEXT,
    start_page INTEGER,
    end_page INTEGER,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bill status table
CREATE TABLE IF NOT EXISTS govinfo_bill_status (
    id TEXT PRIMARY KEY,
    bill_type TEXT,
    bill_number TEXT,
    congress_number INTEGER,
    origin_chamber TEXT,
    origin_chamber_code TEXT,
    update_date TIMESTAMP,
    introduced_date DATE,
    latest_action JSONB,
    actions JSONB,
    cosponsors JSONB,
    committees JSONB,
    related_bills JSONB,
    subjects JSONB,
    policy_area JSONB,
    summaries JSONB,
    titles JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_govinfo_packages_collection ON govinfo_packages(collection_id);
CREATE INDEX IF NOT EXISTS idx_govinfo_packages_date_issued ON govinfo_packages(date_issued);
CREATE INDEX IF NOT EXISTS idx_govinfo_packages_last_modified ON govinfo_packages(last_modified);
CREATE INDEX IF NOT EXISTS idx_govinfo_cfr_sections_title ON govinfo_cfr_sections(title_number);
CREATE INDEX IF NOT EXISTS idx_govinfo_cfr_sections_part ON govinfo_cfr_sections(part_number);
CREATE INDEX IF NOT EXISTS idx_govinfo_fed_register_docs_date ON govinfo_fed_register_docs(publication_date);
CREATE INDEX IF NOT EXISTS idx_govinfo_fed_register_docs_type ON govinfo_fed_register_docs(document_type);
CREATE INDEX IF NOT EXISTS idx_govinfo_fed_register_docs_agencies ON govinfo_fed_register_docs USING gin(agencies);
CREATE INDEX IF NOT EXISTS idx_govinfo_public_laws_congress ON govinfo_public_laws(congress_number);
CREATE INDEX IF NOT EXISTS idx_govinfo_public_laws_date ON govinfo_public_laws(enacted_date);
CREATE INDEX IF NOT EXISTS idx_govinfo_statutes_at_large_volume ON govinfo_statutes_at_large(volume_number);
CREATE INDEX IF NOT EXISTS idx_govinfo_statutes_at_large_congress ON govinfo_statutes_at_large(congress_number);
CREATE INDEX IF NOT EXISTS idx_govinfo_congressional_record_date ON govinfo_congressional_record(publication_date);
CREATE INDEX IF NOT EXISTS idx_govinfo_congressional_record_volume ON govinfo_congressional_record(volume_number);
CREATE INDEX IF NOT EXISTS idx_govinfo_bill_status_congress ON govinfo_bill_status(congress_number);
CREATE INDEX IF NOT EXISTS idx_govinfo_bill_status_type ON govinfo_bill_status(bill_type);
CREATE INDEX IF NOT EXISTS idx_govinfo_bill_status_date ON govinfo_bill_status(introduced_date);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_govinfo_packages_fts ON govinfo_packages USING gin(to_tsvector('english', title || ' ' || coalesce(package_id, '')));
CREATE INDEX IF NOT EXISTS idx_govinfo_cfr_sections_fts ON govinfo_cfr_sections USING gin(to_tsvector('english', section_name || ' ' || coalesce(content, '')));
CREATE INDEX IF NOT EXISTS idx_govinfo_fed_register_docs_fts ON govinfo_fed_register_docs USING gin(to_tsvector('english', title || ' ' || coalesce(summary, '') || ' ' || coalesce(action, '')));
CREATE INDEX IF NOT EXISTS idx_govinfo_public_laws_fts ON govinfo_public_laws USING gin(to_tsvector('english', title || ' ' || coalesce(citation, '')));