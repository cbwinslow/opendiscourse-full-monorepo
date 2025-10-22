# OpenStates API Documentation and Helper Functions

## API Overview

The OpenStates API v3 provides access to state legislative information including:
- Jurisdictions (states, DC, Puerto Rico)
- People (legislators, governors, etc.)
- Bills (proposed legislation)
- Committees
- Events

## Base URL
https://v3.openstates.org/

## Authentication
API keys are required and can be passed via:
- X-API-KEY header
- ?apikey query parameter

## Available Endpoints

### Jurisdictions
- GET /jurisdictions - List all available jurisdictions
- GET /jurisdictions/{jurisdiction_id} - Get detailed metadata for a specific jurisdiction

### People
- GET /people - List or search people
- GET /people.geo - Get legislators for a given location
- GET /people/{person_id} - Get detailed information about a specific person

### Bills
- GET /bills - Search bills by various criteria
- GET /bills/ocd-bill/{uuid} - Get bill by internal ID
- GET /bills/{jurisdiction}/{session}/{id} - Get bill by jurisdiction, session, and ID

### Committees
- GET /committees - Get list of committees by jurisdiction
- GET /committees/{committee_id} - Get details on committee by internal ID

### Events
- GET /events - Get list of events by jurisdiction
- GET /events/{event_id} - Get details on event by internal ID

## Common Query Parameters

### For /people endpoint:
- name: Filter by name
- jurisdiction: Filter by jurisdiction ID
- district: Filter by district
- chamber: Filter by chamber (upper/lower)

### For /bills endpoint:
- jurisdiction: Filter by jurisdiction ID
- session: Filter by session
- chamber: Filter by chamber
- sponsor: Filter by sponsor ID
- subject: Filter by subject
- updated_since: Filter by updated date
- created_since: Filter by created date
- search: Full text search
- sort: Sort field (created_at, updated_at)

## Data Models

### Jurisdiction
- id: String (OCD ID)
- name: String
- classification: String (state, municipality)
- division: Object (division information)
- url: String (official website)
- legislative_sessions: Array (session information)

### Person
- id: String (OCD ID)
- name: String
- given_name: String
- family_name: String
- email: String
- gender: String
- biography: String
- birth_date: String (YYYY-MM-DD)
- death_date: String (YYYY-MM-DD)
- image: String (URL)
- links: Array (official websites)
- sources: Array (data sources)
- extras: Object (additional information)
- offices: Array (office information)
- party: Array (party affiliations)
- roles: Array (current and past roles)

### Bill
- id: String (OCD ID)
- session: String
- jurisdiction: Object (jurisdiction information)
- identifier: String (bill number)
- title: String
- classification: Array (bill type)
- subject: Array (subjects)
- extras: Object (additional information)
- created_at: String (timestamp)
- updated_at: String (timestamp)
- openstates_url: String (URL to OpenStates page)
- sponsorships: Array (sponsor information)
- actions: Array (legislative actions)
- votes: Array (vote information)
- versions: Array (bill versions)
- documents: Array (supporting documents)
- sources: Array (data sources)

### Committee
- id: String (OCD ID)
- name: String
- chamber: String (upper/lower/joint)
- jurisdiction: Object (jurisdiction information)
- members: Array (committee members)
- sources: Array (data sources)
- links: Array (official websites)
- extras: Object (additional information)
- created_at: String (timestamp)
- updated_at: String (timestamp)

### Event
- id: String (OCD ID)
- name: String
- jurisdiction: Object (jurisdiction information)
- description: String
- classification: String
- start_date: String (timestamp)
- end_date: String (timestamp)
- all_day: Boolean
- status: String
- location: Object (location information)
- media: Array (media information)
- documents: Array (documents)
- links: Array (links)
- sources: Array (data sources)
- participants: Array (participants)
- agenda: Array (agenda items)
- extras: Object (additional information)
- created_at: String (timestamp)
- updated_at: String (timestamp)