# OpenLegislation API Documentation

## Overview
OpenLegislation is an API that provides access to legislative information, primarily focused on New York State legislative data. The API exposes methods for retrieval of individual documents by object ID as well as retrieval of arbitrary feeds supported by the Lucene document search engine.

## Base URL
https://legislation.nysenate.gov/api/3/

## Available Formats
- JSON (default)
- XML
- RSS
- ATOM
- JSONP (with callback parameter)

## Document Types
The available top-level document types are:
- Bill
- Meeting
- Calendar
- Transcript
- Vote

## API Endpoints

### Document Requests
Format: `legislation/3/<object type>/<object id>.<format>`

#### Bill
- Format: `legislation/3/bills/<bill id>-<year>.json`
- Example: `legislation/3/bills/S1234-2011.json`

#### Meeting
- Format: `legislation/3/meetings/<committee>-<MM>-<DD>-<YYYY>.json`
- Example: `legislation/3/meetings/Finance-06-24-2011.json`

#### Calendar
- Format: `legislation/3/calendars/<floor|active>-<MM>-<DD>-<YYYY>.json`
- Example: `legislation/3/calendars/floor-06-24-2011.json`

#### Transcript
- Format: `legislation/3/transcripts/<regular|special>-session-<MM>-<DD>-<YYYY>.json`
- Example: `legislation/3/transcripts/regular-session-08-03-2011.json`

### Search Requests
Format: `legislation/3/search.<format>?term=<lucene query>`

Example: `legislation/3/search.json?term=billno:S1234`

## Search Parameters
| Parameter | Values | Description |
|-----------|--------|-------------|
| pageSize | 1-1000 | Limits the number of results returned |
| pageIdx | 1+ | Indicates which page of results to retrieve |
| sortOrder | true/false | true = Descending, false = Ascending by sort field |
| sort | any document field | Sorts the result set by the indicated field |
| callback | string | JSONP callback function name |

## Document Fields

### All Document Types
| Field | Description |
|-------|-------------|
| modified | Unix timestamp of last modification |
| active | Boolean indicating if document is active |
| oid | Unique object ID |
| otype | Document type |
| osearch | Default search field (content varies by type) |

### Bill Fields
| Field | Description |
|-------|-------------|
| year | Session year (2009, 2011, etc.) |
| senateBillNo | Bill number |
| title | Bill title |
| lawSection | Law section (e.g., Public Service Law) |
| sameAs | Sister document ID |
| sponsor | Bill sponsor information |
| coSponsors | Co-sponsors |
| summary | Bill summary text |
| currentCommittee | Current committee holding the bill |
| actions | List of bill actions |
| fulltext | Full bill text |
| memo | Bill memo |
| votes | List of votes on the bill |

### Action Fields
| Field | Description |
|-------|-------------|
| date | Unix timestamp of action |
| text | Action text |
| bill | Parent bill information |

### Vote Fields
| Field | Description |
|-------|-------------|
| voteType | 1 = Floor vote, 2 = Committee vote |
| voteDate | Unix timestamp of vote |
| ayes | List of senators voting yes |
| nays | List of senators voting no |
| abstains | List of senators abstaining |
| excused | List of senators excused |
| bill | Bill being voted on |

### Meeting Fields
| Field | Description |
|-------|-------------|
| meetingDateTime | Unix timestamp of meeting |
| committeeName | Name of committee |
| committeeChair | Committee chairperson |
| bills | List of bills discussed |
| notes | Meeting notes |

### Calendar Fields
| Field | Description |
|-------|-------------|
| year | Calendar year |
| type | Calendar type (floor or active) |
| no | Calendar number |
| supplementals | Calendar entries |

### Transcript Fields
| Field | Description |
|-------|-------------|
| timeStamp | Unix timestamp of recording |
| location | Location of transcript |
| type | Session type (Regular or Special) |
| transcriptText | Full transcript text |

## Response Structure
All requests return a response with the following structure:

```json
{
    "response": {
        "metadata": {
            "totalresults": <number>
        },
        "results": [
            {
                "type": <object type>,
                "oid": <unique object id>,
                "url": <url for corresponding webpage>,
                "data": {
                    // Object-specific data structure
                }
            }
        ]
    }
}
```

## Data Models

### Bill Data Structure
```json
{
    "year": "2011",
    "senateBillNo": "S607-2011",
    "title": "Relates to the definition of alternate energy production facilities",
    "lawSection": "Public Service Law",
    "sameAs": "A3536",
    "previousVersions": ["S8310-2009"],
    "sponsor": {
        "fullname": "MAZIARZ"
    },
    "coSponsors": null,
    "multiSponsors": null,
    "summary": "Adds lithium ion energy batteries to the definition of alternate energy production facilities.",
    "currentCommittee": null,
    "actions": [
        {
            "date": "1294185600000",
            "text": "REFERRED TO ENERGY AND TELECOMMUNICATIONS"
        }
    ],
    "fulltext": "A really long string",
    "memo": "A much shorter string",
    "law": "Amd S2, Pub Serv L",
    "votes": [
        {
            "voteType": "2",
            "voteDate": "1295947800000",
            "ayes": ["Maziarz", "Alesi", "Fuschillo", "Ritchie", "O'Mara", "Ranzenhofer", "Robach", "Parker", "Gianaris", "Kennedy"],
            "nays": null,
            "abstains": null,
            "excused": null,
            "ayeswr": ["Adams", "Kruger"],
            "description": "Energy and Telecommunications"
        }
    ]
}
```

### Action Data Structure
```json
{
    "date": "1316736000000",
    "text": "enacting clause stricken",
    "bill": {
        "year": "2011",
        "senateBillNo": "A8591-2011",
        "title": "Criminalizes unlawful conduct of a farm products dealer in certain circumstances",
        "sameAs": null,
        "sponsor": {
            "fullname": "Rabbitt"
        },
        "summary": "Criminalizes unlawful conduct of a farm products dealer in certain circumstances."
    }
}
```

### Vote Data Structure
```json
{
    "voteType": "1",
    "voteDate": "1308268800000",
    "ayes": ["Adams", "Addabbo", "Alesi", "Avella", "Ball", "Bonacic", "Breslin", "Carlucci", "DeFrancisco", "Diaz", "Dilan", "Duane", "Espaillat", "Farley", "Flanagan", "Fuschillo", "Gallivan", "Gianaris", "Golden", "Griffo", "Grisanti", "Hannon", "Hassell-Thompson", "Huntley", "Johnson", "Kennedy", "Klein", "Krueger", "Kruger", "Lanza", "Larkin", "LaValle", "Libous", "Little", "Marcellino", "Martins", "Maziarz", "McDonald", "Montgomery", "Nozzolio", "O'Mara", "Oppenheimer", "Parker", "Peralta", "Perkins", "Ranzenhofer", "Ritchie", "Rivera", "Robach", "Saland", "Sampson", "Savino", "Serrano", "Seward", "Skelos", "Smith", "Squadron", "Stavisky", "Stewart-Cousins", "Valesky", "Young", "Zeldin"],
    "nays": [],
    "abstains": [],
    "excused": [],
    "bill": {
        "year": "2011",
        "senateBillNo": "S2628A-2011",
        "title": "Relates to the practice of public accountancy by accountants who are not licensed in New York state; repealer",
        "sameAs": "A4881B",
        "sponsor": {
            "fullname": "LAVALLE"
        },
        "summary": "Relates to the practice of public accountancy by accountants who are not licensed in New York state; allows accountants licensed in other states to have practice privileges in New York."
    },
    "ayeswr": null,
    "description": null
}
```

### Meeting Data Structure
```json
{
    "meetingDateTime": "1308873600000",
    "meetday": "Wednesday",
    "location": null,
    "committeeName": "Rules",
    "committeeChair": "Dean G. Skelos",
    "bills": [
        {
            "year": "2011",
            "senateBillNo": "S553-2011",
            "title": "Authorizes the forest ranger force to establish a training program for volunteer search and rescue personnel to assist the forest rangers",
            "sameAs": "A5016",
            "sponsor": {
                "fullname": "LITTLE"
            },
            "summary": "Authorizes the forest ranger force to establish a training program for volunteer search and rescue personnel to assist the forest rangers in wild, remote and forested areas of the state."
        }
    ],
    "notes": "*ALL BILLS REPORTED DIRECT TO 3RD READING*\n\nMEETING TO BE CALLED OFF THE FLOOR",
    "addendums": [
        {
            "addendumId": "Q",
            "weekOf": "2011-06-20",
            "publicationDateTime": "1308939965000",
            "agenda": {
                "number": "20",
                "sessionYear": "2011",
                "year": "2011"
            }
        }
    ]
}
```

### Calendar Data Structure
Active calendars use sequences:
```json
{
    "year": "2011",
    "type": "active",
    "sessionYear": "2011",
    "no": "60",
    "supplementals": [
        {
            "calendarDate": null,
            "releaseDateTime": null,
            "sections": null,
            "sequence": {
                "no": "",
                "actCalDate": "1308873600000",
                "releaseDateTime": "1308937283000",
                "calendarEntries": [
                    {
                        "no": "545",
                        "bill": {
                            "year": "2011",
                            "senateBillNo": "S3907A-2011",
                            "title": "Includes the Advanced Energy Research and Technology Center (AERTC) at the State University of New York at Stony Brook in the center for excellence program",
                            "sameAs": "A4476A",
                            "sponsor": {
                                "fullname": "LAVALLE"
                            },
                            "summary": "Includes the Advanced Energy Research and Technology Center (AERTC) at the State University of New York at Stony Brook in the center for excellence program."
                        },
                        "billHigh": null,
                        "subBill": null,
                        "motionDate": null
                    }
                ]
            }
        }
    ],
    "id": "cal-active-00060-2011-2011"
}
```

Floor calendars use sections:
```json
{
    "year": "2011",
    "type": "floor",
    "sessionYear": "2011",
    "no": "60",
    "supplementals": [
        {
            "calendarDate": "1308873600000",
            "releaseDateTime": "1308871140000",
            "sections": [
                {
                    "name": "BILLS ON THIRD READING",
                    "type": "C",
                    "cd": "0400",
                    "calendarEntries": [
                        {
                            "no": "48",
                            "bill": {
                                "year": "2011",
                                "senateBillNo": "S922-2011",
                                "title": "Exempts operators of law enforcement vessels from laws which regulate vessels on the navigable waters of the state while responding to emergencies",
                                "sameAs": null,
                                "sponsor": {
                                    "fullname": "MARCELLINO"
                                },
                                "summary": "Exempts operators of law enforcement vessels from laws which regulate vessels on the navigable waters of the state while such operators are in the course of responding to emergencies."
                            },
                            "billHigh": null,
                            "subBill": null,
                            "motionDate": null
                        }
                    ]
                }
            ],
            "sequence": null
        }
    ]
}
```

### Transcript Data Structure
```json
{
    "timeStamp": "1312369200000",
    "location": "ALBANY, NEW YORK",
    "type": "REGULAR SESSION",
    "transcriptText": "Really Really long String Here"
}
```

## Recommendations
1. Use the search API for finding documents by various criteria
2. Use document requests for retrieving specific documents by ID
3. Implement pagination for large result sets
4. Handle different data structures based on document type
5. Convert Unix timestamps to readable dates
6. Be aware that the API is primarily focused on New York State legislative data