# API Schema Analysis for Government Legislative Data Sources

## OpenStates API v3 Schema Analysis

### Base URL
https://v3.openstates.org

### Authentication
- API key required via X-API-KEY header or ?apikey query parameter
- Register at https://openstates.org/account/profile/ for API key

### Endpoints

#### Jurisdictions
- **GET /jurisdictions** - List all available jurisdictions
  - Parameters:
    - page (int): Page number for pagination
    - per_page (int): Results per page (default 100)
  - Response:
    {
      "results": [
        {
          "id": "ocd-jurisdiction/country:us/state:ca/government",
          "name": "California",
          "classification": "state",
          "division": {
            "id": "ocd-division/country:us/state:ca",
            "name": "California"
          },
          "url": "https://ca.gov",
          "legislative_sessions": [
            {
              "identifier": "20232024",
              "name": "2023-2024 Regular Session",
              "classification": "primary",
              "start_date": "2022-12-05",
              "end_date": "2024-11-30"
            }
          ]
        }
      ],
      "meta": {
        "page": 1,
        "per_page": 100,
        "total_pages": 5
      }
    }

- **GET /jurisdictions/{jurisdiction_id}** - Get detailed metadata for a particular jurisdiction
  - Response: Single jurisdiction object as above

#### People
- **GET /people** - List or search people (legislators, governors, etc.)
  - Parameters:
    - name (string): Filter by name
    - jurisdiction (string): Filter by jurisdiction ID
    - district (string): Filter by district
    - chamber (string): Filter by chamber (upper/lower)
    - page (int): Page number for pagination
    - per_page (int): Results per page (default 100)
  - Response:
    {
      "results": [
        {
          "id": "ocd-person/12345678-1234-1234-1234-123456789012",
          "name": "John Smith",
          "given_name": "John",
          "family_name": "Smith",
          "email": "john.smith@state.gov",
          "gender": "Male",
          "biography": "Biographical text",
          "birth_date": "1960-01-01",
          "image": "https://example.com/image.jpg",
          "links": [
            {
              "url": "https://legislator.example.com",
              "note": "Official Website"
            }
          ],
          "sources": [
            {
              "url": "https://example.com/source",
              "note": "Source"
            }
          ],
          "party": [
            {
              "name": "Democratic"
            }
          ],
          "roles": [
            {
              "type": "lower",
              "district": "10",
              "jurisdiction": "ocd-jurisdiction/country:us/state:ca/government",
              "start_date": "2020-12-07"
            }
          ]
        }
      ]
    }

- **GET /people.geo** - Get legislators for a given location
  - Parameters:
    - lat (float): Latitude
    - lng (float): Longitude
  - Response: List of people representing the location

- **GET /people/{person_id}** - Get detailed information about a specific person
  - Response: Single person object as above

#### Bills
- **GET /bills** - Search bills by various criteria
  - Parameters:
    - jurisdiction (string): Filter by jurisdiction ID
    - session (string): Filter by session
    - chamber (string): Filter by chamber
    - sponsor (string): Filter by sponsor ID
    - subject (string): Filter by subject
    - updated_since (string): Filter by updated date (YYYY-MM-DD)
    - created_since (string): Filter by created date (YYYY-MM-DD)
    - search (string): Full text search
    - sort (string): Sort field (created_at, updated_at)
    - page (int): Page number for pagination
    - per_page (int): Results per page (default 100)
  - Response:
    {
      "results": [
        {
          "id": "ocd-bill/12345678-1234-1234-1234-123456789012",
          "session": "20232024",
          "jurisdiction": {
            "id": "ocd-jurisdiction/country:us/state:ca/government",
            "name": "California"
          },
          "identifier": "AB 1234",
          "title": "An act to establish renewable energy standards",
          "classification": ["bill"],
          "subject": ["Energy", "Environment"],
          "extras": {},
          "created_at": "2023-01-15T10:30:00Z",
          "updated_at": "2023-02-20T14:45:00Z",
          "openstates_url": "https://openstates.org/ca/bills/20232024/AB1234/",
          "sponsorships": [
            {
              "name": "John Smith",
              "entity_type": "person",
              "primary": true,
              "classification": "primary"
            }
          ],
          "actions": [
            {
              "organization": {
                "name": "Assembly"
              },
              "description": "Introduced",
              "date": "2023-01-15",
              "classification": ["introduction"],
              "order": 0
            }
          ],
          "votes": [
            {
              "id": "ocd-vote/12345678-1234-1234-1234-123456789012",
              "motion_text": "Passage",
              "result": "pass",
              "date": "2023-03-15",
              "organization": {
                "name": "Assembly"
              }
            }
          ],
          "versions": [
            {
              "note": "Introduced",
              "date": "2023-01-15",
              "links": [
                {
                  "url": "https://example.com/bill-text.pdf",
                  "media_type": "application/pdf"
                }
              ]
            }
          ],
          "documents": [
            {
              "note": "Fiscal Analysis",
              "date": "2023-01-20",
              "links": [
                {
                  "url": "https://example.com/analysis.pdf",
                  "media_type": "application/pdf"
                }
              ]
            }
          ],
          "sources": [
            {
              "url": "https://example.com/bill-source",
              "note": "Source"
            }
          ]
        }
      ]
    }

- **GET /bills/ocd-bill/{uuid}** - Get bill by internal ID
  - Response: Single bill object as above

- **GET /bills/{jurisdiction}/{session}/{id}** - Get bill by jurisdiction, session, and ID
  - Response: Single bill object as above

#### Committees
- **GET /committees** - Get list of committees by jurisdiction
  - Parameters:
    - jurisdiction (string): Jurisdiction ID
    - page (int): Page number for pagination
    - per_page (int): Results per page (default 100)
  - Response:
    {
      "results": [
        {
          "id": "ocd-organization/12345678-1234-1234-1234-123456789012",
          "name": "Energy Committee",
          "chamber": "lower",
          "jurisdiction": {
            "id": "ocd-jurisdiction/country:us/state:ca/government",
            "name": "California"
          },
          "members": [
            {
              "person": {
                "id": "ocd-person/12345678-1234-1234-1234-123456789012",
                "name": "John Smith"
              },
              "role": "Chair"
            }
          ],
          "sources": [
            {
              "url": "https://example.com/committee",
              "note": "Source"
            }
          ],
          "links": [
            {
              "url": "https://example.com/committee",
              "note": "Official Website"
            }
          ],
          "extras": {},
          "created_at": "2023-01-01T00:00:00Z",
          "updated_at": "2023-01-01T00:00:00Z"
        }
      ]
    }

- **GET /committees/{committee_id}** - Get details on committee by internal ID
  - Response: Single committee object as above

#### Events
- **GET /events** - Get list of events by jurisdiction
  - Parameters:
    - jurisdiction (string): Jurisdiction ID
    - page (int): Page number for pagination
    - per_page (int): Results per page (default 100)
  - Response:
    {
      "results": [
        {
          "id": "ocd-event/12345678-1234-1234-1234-123456789012",
          "name": "Energy Committee Hearing",
          "jurisdiction": {
            "id": "ocd-jurisdiction/country:us/state:ca/government",
            "name": "California"
          },
          "description": "Hearing on renewable energy legislation",
          "classification": "committee-meeting",
          "start_date": "2023-03-15T10:00:00Z",
          "end_date": "2023-03-15T12:00:00Z",
          "all_day": false,
          "status": "confirmed",
          "location": {
            "name": "State Capitol, Room 100",
            "url": "https://example.com/location"
          },
          "media": [
            {
              "note": "Video Stream",
              "date": "2023-03-15",
              "links": [
                {
                  "url": "https://example.com/video",
                  "media_type": "text/html"
                }
              ]
            }
          ],
          "documents": [
            {
              "note": "Agenda",
              "date": "2023-03-10",
              "links": [
                {
                  "url": "https://example.com/agenda.pdf",
                  "media_type": "application/pdf"
                }
              ]
            }
          ],
          "links": [
            {
              "url": "https://example.com/event",
              "note": "Event Website"
            }
          ],
          "sources": [
            {
              "url": "https://example.com/source",
              "note": "Source"
            }
          ],
          "participants": [
            {
              "name": "John Smith",
              "entity_type": "person",
              "note": "Chair"
            }
          ],
          "agenda": [
            {
              "description": "Call to Order",
              "order": 0,
              "subjects": [],
              "media": [],
              "notes": [],
              "related_entities": []
            }
          ],
          "extras": {},
          "created_at": "2023-03-01T00:00:00Z",
          "updated_at": "2023-03-01T00:00:00Z"
        }
      ]
    }

- **GET /events/{event_id}** - Get details on event by internal ID
  - Response: Single event object as above

## Congress.gov API Schema Analysis

### Base URL
https://api.data.gov/congress/v3

### Authentication
- API key required via ?api_key query parameter
- Register at https://api.data.gov/signup/ for API key

### Endpoints

#### Bills
- **GET /bill** - Get list of bills
- **GET /bill/{bill_type}** - Get bills by type (introduced, updated, active, passed, enacted)
- **GET /bill/{bill_type}/{congress}** - Get bills by type and congress
- **GET /bill/{bill_type}/{congress}/{chamber}** - Get bills by type, congress, and chamber
- **GET /bill/{bill_id}** - Get detailed information about a specific bill

#### Members
- **GET /member** - Get list of members of Congress
- **GET /member/{congress}** - Get members for specific congress
- **GET /member/{congress}/{chamber}** - Get members for specific congress and chamber
- **GET /member/{member_id}** - Get detailed information about a specific member
- **GET /member/{member_id}/votes** - Get voting history for a member

#### Committees
- **GET /committee** - Get list of committees
- **GET /committee/{congress}** - Get committees for specific congress
- **GET /committee/{congress}/{chamber}** - Get committees for specific congress and chamber

#### Nominations
- **GET /nomination** - Get list of nominations
- **GET /nomination/{congress}** - Get nominations for specific congress

## OpenLegislation API Schema Analysis

### Base URL
https://legislation.nysenate.gov/api/3

### Authentication
- API key may be required via ?key query parameter

### Endpoints

#### Bills
- **GET /bills/{bill_id}-{year}.{format}** - Get a specific bill by ID and year
  - Example: /bills/S1234-2021.json

#### Meetings
- **GET /meetings/{committee}-{MM}-{DD}-{YYYY}.{format}** - Get a specific meeting
  - Example: /meetings/Finance-06-24-2021.json

#### Calendars
- **GET /calendars/{floor|active}-{MM}-{DD}-{YYYY}.{format}** - Get a specific calendar
  - Example: /calendars/floor-06-24-2021.json

#### Transcripts
- **GET /transcripts/{regular|special}-session-{MM}-{DD}-{YYYY}.{format}** - Get a specific transcript
  - Example: /transcripts/regular-session-08-03-2021.json

#### Search
- **GET /search.{format}** - Search for documents using Lucene query syntax
  - Parameters:
    - term (string): Lucene search term
    - pageSize (int): Results per page (1-1000)
    - pageIdx (int): Page index (1+)
    - sortOrder (boolean): Sort order (true=descending, false=ascending)
    - sort (string): Field to sort by
    - callback (string): JSONP callback function name

## GovInfo.gov API Schema Analysis

### Base URL
https://www.govinfo.gov

### Authentication
- Most services don't require authentication

### Services

#### Bulk Data
- **GET /bulkdata** - Access bulk data collections
- **GET /bulkdata/{collection}** - Access specific collection
  - Collections include: CFR (Code of Federal Regulations), FR (Federal Register), USCODE (U.S. Code), PUBLICLAWS (Public Laws), PRIVATELAWS (Private Laws), STATUTE (Statutes at Large), CREC (Congressional Record), BILLS
- **GET /bulkdata/{collection}/{year}** - Access specific collection and year

#### Link Service
- **GET /link** - Create links to content using query parameters
  - Parameters:
    - collection (string): Collection name (required)
    - congress (string): Congress number (for bills)
    - billType (string): Bill type (hr, s, hjres, etc.)
    - billNumber (string): Bill number
    - title (string): Title number (for CFR)
    - part (string): Part number (for CFR)
    - section (string): Section number
    - granuleId (string): Granule ID for specific document
    - packageId (string): Package ID for specific document
    - page (string): Page number
    - gridPosition (string): Grid position

#### RSS Feeds
- **GET /rss/{collection}.xml** - Get RSS feed for collection
  - Collections include: CFR, FR, USCODE, PUBLICLAWS, PRIVATELAWS, STATUTE, CREC, BILLS