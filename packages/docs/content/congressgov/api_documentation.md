# Congress.gov API Documentation

## Overview
The Congress.gov API provides access to federal legislative information including bills, amendments, summaries, Congress members, the Congressional Record, committee reports, nominations, treaties, and House/Senate communications.

## Base URL
https://api.data.gov/congress/v3

## Authentication
API keys are required and must be obtained from api.data.gov. The key can be passed as a query parameter:
```
?api_key=YOUR_API_KEY
```

## Available Collections
Based on available information, the API covers:
- Bills
- Amendments
- Summaries
- Congress members
- Congressional Record
- Committee reports
- Nominations
- Treaties
- House Communications
- Senate Communications

## Data Format
Responses are returned in XML or JSON formats.

## Known Endpoints
While detailed documentation is limited, the following endpoints are known to exist:
- `/bill` - Bill information
- `/amendment` - Amendment information
- `/member` - Congress member information
- `/committee` - Committee information
- `/nomination` - Nomination information
- `/treaty` - Treaty information
- `/communication` - House/Senate communications
- `/crsreport` - Congressional Research Service reports
- `/congressional-record` - Congressional Record information

## Alternative: ProPublica Congress API
Since official documentation is limited, the ProPublica Congress API may be a viable alternative:
- Base URL: https://api.propublica.org/congress/v1
- Authentication: X-API-Key header
- Documentation: https://projects.propublica.org/api-docs/congress-api/
- Rate limit: 5000 requests per day
- License: Creative Commons Attribution-NonCommercial-NoDerivs 3.0 United States

## Data Models (Based on ProPublica Documentation)

### Member
- id: String
- title: String
- short_title: String
- api_uri: String
- first_name: String
- middle_name: String
- last_name: String
- suffix: String
- date_of_birth: String
- gender: String
- party: String
- leadership_role: String
- twitter_account: String
- facebook_account: String
- youtube_account: String
- govtrack_id: String
- cspan_id: String
- votesmart_id: String
- icpsr_id: String
- crp_id: String
- google_entity_id: String
- fec_candidate_id: String
- url: String
- rss_url: String
- contact_form: String
- in_office: Boolean
- cook_pvi: String
- dw_nominate: String
- ideal_point: String
- seniority: String
- next_election: String
- total_votes: Integer
- missed_votes: Integer
- total_present: Integer
- last_updated: String
- ocd_id: String
- office: String
- phone: String
- fax: String
- state: String
- senate_class: String
- state_rank: String
- district: String
- at_large: Boolean
- geoid: String
- missed_votes_pct: Float
- votes_with_party_pct: Float
- votes_against_party_pct: Float

### Bill
- bill_id: String
- bill_type: String
- number: String
- bill_uri: String
- title: String
- short_title: String
- sponsor_id: String
- congressdotgov_url: String
- govtrack_url: String
- introduced_date: String
- active: Boolean
- last_vote: String
- house_passage: String
- senate_passage: String
- enacted: String
- vetoed: String
- cosponsors: Integer
- cosponsors_by_party: Object
- committees: String
- primary_subject: String
- summary: String
- summary_short: String
- latest_major_action_date: String
- latest_major_action: String

### Vote
- member_id: String
- chamber: String
- congress: String
- session: String
- roll_call: String
- vote_uri: String
- bill: Object
- amendment: Object
- description: String
- question: String
- result: String
- date: String
- time: String
- position: String

## Recommendations
1. Register for an official Congress.gov API key at api.data.gov
2. Consider using ProPublica Congress API as a backup or alternative
3. Test endpoints to understand the actual data structure
4. Implement rate limiting to avoid exceeding quotas