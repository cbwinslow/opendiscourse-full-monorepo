"""
API Blueprint for OpenDiscourse Web Application

This module defines the REST API endpoints for the web application.
"""

from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
import logging
import psycopg2
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('api', __name__, url_prefix='/api')

def get_db_connection():
    """Get database connection."""
    return psycopg2.connect(current_app.config['DATABASE_URL'])

@bp.route('/members', methods=['GET'])
def get_members():
    """Get list of government members."""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '', type=str)
        sort = request.args.get('sort', 'name', type=str)
        
        # Validate parameters
        per_page = min(per_page, 100)  # Max 100 per page
        offset = (page - 1) * per_page
        
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        
        # Build query
        if search:
            cursor.execute("""
                SELECT id, name, given_name, family_name, image_url, 
                       (SELECT STRING_AGG(p.name, ', ') 
                        FROM person_party_affiliations ppa 
                        JOIN parties p ON ppa.party_id = p.id 
                        WHERE ppa.person_id = people.id) as party,
                       (SELECT STRING_AGG(pr.type || ' - ' || j.name, ', ') 
                        FROM person_roles pr 
                        JOIN jurisdictions j ON pr.jurisdiction_id = j.id 
                        WHERE pr.person_id = people.id AND pr.end_date IS NULL) as current_role
                FROM people
                WHERE name ILIKE %s
                ORDER BY """ + sort + """
                LIMIT %s OFFSET %s
            """, (f'%{search}%', per_page, offset))
        else:
            cursor.execute("""
                SELECT id, name, given_name, family_name, image_url,
                       (SELECT STRING_AGG(p.name, ', ') 
                        FROM person_party_affiliations ppa 
                        JOIN parties p ON ppa.party_id = p.id 
                        WHERE ppa.person_id = people.id) as party,
                       (SELECT STRING_AGG(pr.type || ' - ' || j.name, ', ') 
                        FROM person_roles pr 
                        JOIN jurisdictions j ON pr.jurisdiction_id = j.id 
                        WHERE pr.person_id = people.id AND pr.end_date IS NULL) as current_role
                FROM people
                ORDER BY """ + sort + """
                LIMIT %s OFFSET %s
            """, (per_page, offset))
        
        rows = cursor.fetchall()
        
        # Get total count
        if search:
            cursor.execute("SELECT COUNT(*) FROM people WHERE name ILIKE %s", (f'%{search}%',))
        else:
            cursor.execute("SELECT COUNT(*) FROM people")
        total = cursor.fetchone()[0]
        
        cursor.close()
        db_conn.close()
        
        # Format results
        members = []
        for row in rows:
            members.append({
                'id': row[0],
                'name': row[1],
                'given_name': row[2],
                'family_name': row[3],
                'image_url': row[4],
                'party': row[5],
                'current_role': row[6]
            })
        
        return jsonify({
            'members': members,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting members: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/members/<person_id>', methods=['GET'])
def get_member(person_id):
    """Get detailed information for a specific member."""
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        
        # Get basic info
        cursor.execute("""
            SELECT id, name, given_name, family_name, email, gender, biography, 
                   birth_date, image_url, source_url
            FROM people 
            WHERE id = %s
        """, (person_id,))
        
        row = cursor.fetchone()
        if not row:
            cursor.close()
            db_conn.close()
            return jsonify({'error': 'Member not found'}), 404
        
        member = {
            'id': row[0],
            'name': row[1],
            'given_name': row[2],
            'family_name': row[3],
            'email': row[4],
            'gender': row[5],
            'biography': row[6],
            'birth_date': row[7].strftime('%Y-%m-%d') if row[7] else None,
            'image_url': row[8],
            'source_url': row[9]
        }
        
        # Get roles
        cursor.execute("""
            SELECT pr.type, pr.district, j.name as jurisdiction_name, 
                   pr.start_date, pr.end_date
            FROM person_roles pr
            JOIN jurisdictions j ON pr.jurisdiction_id = j.id
            WHERE pr.person_id = %s
            ORDER BY pr.start_date DESC
        """, (person_id,))
        
        role_rows = cursor.fetchall()
        member['roles'] = []
        for role_row in role_rows:
            member['roles'].append({
                'type': role_row[0],
                'district': role_row[1],
                'jurisdiction': role_row[2],
                'start_date': role_row[3].strftime('%Y-%m-%d') if role_row[3] else None,
                'end_date': role_row[4].strftime('%Y-%m-%d') if role_row[4] else None
            })
        
        # Get party affiliations
        cursor.execute("""
            SELECT p.name, ppa.start_date, ppa.end_date
            FROM person_party_affiliations ppa
            JOIN parties p ON ppa.party_id = p.id
            WHERE ppa.person_id = %s
            ORDER BY ppa.start_date DESC
        """, (person_id,))
        
        party_rows = cursor.fetchall()
        member['party_affiliations'] = []
        for party_row in party_rows:
            member['party_affiliations'].append({
                'name': party_row[0],
                'start_date': party_row[1].strftime('%Y-%m-%d') if party_row[1] else None,
                'end_date': party_row[2].strftime('%Y-%m-%d') if party_row[2] else None
            })
        
        # Get recent voting records
        cursor.execute("""
            SELECT vd.option, v.date, v.motion_text, v.result, 
                   b.identifier as bill_identifier, b.title as bill_title
            FROM vote_details vd
            JOIN votes v ON vd.vote_id = v.id
            LEFT JOIN bills b ON v.bill_id = b.id
            WHERE vd.person_id = %s
            ORDER BY v.date DESC
            LIMIT 10
        """, (person_id,))
        
        vote_rows = cursor.fetchall()
        member['recent_votes'] = []
        for vote_row in vote_rows:
            member['recent_votes'].append({
                'position': vote_row[0],
                'date': vote_row[1].strftime('%Y-%m-%d') if vote_row[1] else None,
                'motion': vote_row[2],
                'result': vote_row[3],
                'bill_identifier': vote_row[4],
                'bill_title': vote_row[5]
            })
        
        # Get recent bills sponsored
        cursor.execute("""
            SELECT b.identifier, b.title, bs.classification, bs.created_at
            FROM bill_sponsors bs
            JOIN bills b ON bs.bill_id = b.id
            WHERE bs.person_id = %s
            ORDER BY bs.created_at DESC
            LIMIT 10
        """, (person_id,))
        
        bill_rows = cursor.fetchall()
        member['recent_bills'] = []
        for bill_row in bill_rows:
            member['recent_bills'].append({
                'identifier': bill_row[0],
                'title': bill_row[1],
                'type': bill_row[2],
                'date': bill_row[3].strftime('%Y-%m-%d') if bill_row[3] else None
            })
        
        cursor.close()
        db_conn.close()
        
        return jsonify(member)
        
    except Exception as e:
        logger.error(f"Error getting member {person_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/bills', methods=['GET'])
def get_bills():
    """Get list of bills."""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '', type=str)
        jurisdiction = request.args.get('jurisdiction', '', type=str)
        session = request.args.get('session', '', type=str)
        
        # Validate parameters
        per_page = min(per_page, 100)  # Max 100 per page
        offset = (page - 1) * per_page
        
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        
        # Build query
        where_conditions = []
        params = []
        
        if search:
            where_conditions.append("title ILIKE %s")
            params.append(f'%{search}%')
        
        if jurisdiction:
            where_conditions.append("jurisdiction_id = %s")
            params.append(jurisdiction)
        
        if session:
            where_conditions.append("session_id = %s")
            params.append(session)
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        params.extend([per_page, offset])
        
        cursor.execute(f"""
            SELECT id, identifier, title, jurisdiction_id, session_id, 
                   created_at, updated_at
            FROM bills
            {where_clause}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """, params)
        
        rows = cursor.fetchall()
        
        # Get total count
        count_params = params[:-2]  # Remove limit and offset
        cursor.execute(f"""
            SELECT COUNT(*) FROM bills
            {where_clause}
        """, count_params)
        total = cursor.fetchone()[0]
        
        cursor.close()
        db_conn.close()
        
        # Format results
        bills = []
        for row in rows:
            bills.append({
                'id': row[0],
                'identifier': row[1],
                'title': row[2],
                'jurisdiction_id': row[3],
                'session_id': row[4],
                'created_at': row[5].strftime('%Y-%m-%d') if row[5] else None,
                'updated_at': row[6].strftime('%Y-%m-%d') if row[6] else None
            })
        
        return jsonify({
            'bills': bills,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting bills: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/bills/<bill_id>', methods=['GET'])
def get_bill(bill_id):
    """Get detailed information for a specific bill."""
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        
        # Get basic bill info
        cursor.execute("""
            SELECT id, identifier, title, classification, subject, extras,
                   created_at, updated_at, openstates_url, congress_gov_url, govinfo_url
            FROM bills
            WHERE id = %s
        """, (bill_id,))
        
        row = cursor.fetchone()
        if not row:
            cursor.close()
            db_conn.close()
            return jsonify({'error': 'Bill not found'}), 404
        
        bill = {
            'id': row[0],
            'identifier': row[1],
            'title': row[2],
            'classification': row[3],
            'subject': row[4],
            'extras': row[5],
            'created_at': row[6].strftime('%Y-%m-%d') if row[6] else None,
            'updated_at': row[7].strftime('%Y-%m-%d') if row[7] else None,
            'urls': {
                'openstates': row[8],
                'congress_gov': row[9],
                'govinfo': row[10]
            }
        }
        
        # Get sponsors
        cursor.execute("""
            SELECT p.name, bs.entity_type, bs.primary_sponsor, bs.classification
            FROM bill_sponsors bs
            LEFT JOIN people p ON bs.person_id = p.id
            WHERE bs.bill_id = %s
        """, (bill_id,))
        
        sponsor_rows = cursor.fetchall()
        bill['sponsors'] = []
        for sponsor_row in sponsor_rows:
            bill['sponsors'].append({
                'name': sponsor_row[0],
                'entity_type': sponsor_row[1],
                'primary': sponsor_row[2],
                'classification': sponsor_row[3]
            })
        
        # Get actions
        cursor.execute("""
            SELECT organization_name, description, date, classification
            FROM bill_actions
            WHERE bill_id = %s
            ORDER BY date DESC
        """, (bill_id,))
        
        action_rows = cursor.fetchall()
        bill['actions'] = []
        for action_row in action_rows:
            bill['actions'].append({
                'organization': action_row[0],
                'description': action_row[1],
                'date': action_row[2].strftime('%Y-%m-%d') if action_row[2] else None,
                'classification': action_row[3]
            })
        
        # Get votes
        cursor.execute("""
            SELECT id, motion_text, result, date, organization_name
            FROM votes
            WHERE bill_id = %s
            ORDER BY date DESC
        """, (bill_id,))
        
        vote_rows = cursor.fetchall()
        bill['votes'] = []
        for vote_row in vote_rows:
            bill['votes'].append({
                'id': vote_row[0],
                'motion': vote_row[1],
                'result': vote_row[2],
                'date': vote_row[3].strftime('%Y-%m-%d') if vote_row[3] else None,
                'organization': vote_row[4]
            })
        
        cursor.close()
        db_conn.close()
        
        return jsonify(bill)
        
    except Exception as e:
        logger.error(f"Error getting bill {bill_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/discrepancies', methods=['GET'])
def get_discrepancies():
    """Get list of discrepancies."""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        person_id = request.args.get('person_id', '', type=str)
        issue = request.args.get('issue', '', type=str)
        resolved = request.args.get('resolved', '', type=str)
        
        # Validate parameters
        per_page = min(per_page, 100)  # Max 100 per page
        offset = (page - 1) * per_page
        
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        
        # Build query
        where_conditions = []
        params = []
        
        if person_id:
            where_conditions.append("person_id = %s")
            params.append(person_id)
        
        if issue:
            where_conditions.append("issue ILIKE %s")
            params.append(f'%{issue}%')
        
        if resolved == 'true':
            where_conditions.append("resolved = TRUE")
        elif resolved == 'false':
            where_conditions.append("resolved = FALSE")
        
        where_clause = "WHERE " + " AND ".join(where_conditions) if where_conditions else ""
        params.extend([per_page, offset])
        
        cursor.execute(f"""
            SELECT id, person_id, issue, vote_position, statement_position,
                   confidence_score, resolved, created_at
            FROM discrepancies
            {where_clause}
            ORDER BY confidence_score DESC, created_at DESC
            LIMIT %s OFFSET %s
        """, params)
        
        rows = cursor.fetchall()
        
        # Get total count
        count_params = params[:-2]  # Remove limit and offset
        cursor.execute(f"""
            SELECT COUNT(*) FROM discrepancies
            {where_clause}
        """, count_params)
        total = cursor.fetchone()[0]
        
        # Get person names
        person_ids = [row[1] for row in rows]
        person_names = {}
        if person_ids:
            cursor.execute("""
                SELECT id, name FROM people WHERE id = ANY(%s)
            """, (person_ids,))
            for person_row in cursor.fetchall():
                person_names[person_row[0]] = person_row[1]
        
        cursor.close()
        db_conn.close()
        
        # Format results
        discrepancies = []
        for row in rows:
            discrepancies.append({
                'id': row[0],
                'person_id': row[1],
                'person_name': person_names.get(row[1], 'Unknown'),
                'issue': row[2],
                'vote_position': row[3],
                'statement_position': row[4],
                'confidence_score': float(row[5]) if row[5] else 0.0,
                'resolved': row[6],
                'created_at': row[7].strftime('%Y-%m-%d') if row[7] else None
            })
        
        return jsonify({
            'discrepancies': discrepancies,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting discrepancies: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/search', methods=['GET'])
def search():
    """Search across all data types."""
    try:
        query = request.args.get('q', '', type=str)
        data_type = request.args.get('type', 'all', type=str)
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        results = {
            'query': query,
            'members': [],
            'bills': [],
            'total_members': 0,
            'total_bills': 0
        }
        
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        
        # Search members
        if data_type in ['all', 'members']:
            cursor.execute("""
                SELECT id, name, given_name, family_name, image_url
                FROM people
                WHERE name ILIKE %s
                ORDER BY name
                LIMIT 20
            """, (f'%{query}%',))
            
            member_rows = cursor.fetchall()
            results['members'] = []
            for row in member_rows:
                results['members'].append({
                    'id': row[0],
                    'name': row[1],
                    'given_name': row[2],
                    'family_name': row[3],
                    'image_url': row[4]
                })
            
            # Get total count
            cursor.execute("SELECT COUNT(*) FROM people WHERE name ILIKE %s", (f'%{query}%',))
            results['total_members'] = cursor.fetchone()[0]
        
        # Search bills
        if data_type in ['all', 'bills']:
            cursor.execute("""
                SELECT id, identifier, title
                FROM bills
                WHERE title ILIKE %s OR identifier ILIKE %s
                ORDER BY created_at DESC
                LIMIT 20
            """, (f'%{query}%', f'%{query}%'))
            
            bill_rows = cursor.fetchall()
            results['bills'] = []
            for row in bill_rows:
                results['bills'].append({
                    'id': row[0],
                    'identifier': row[1],
                    'title': row[2]
                })
            
            # Get total count
            cursor.execute("SELECT COUNT(*) FROM bills WHERE title ILIKE %s OR identifier ILIKE %s", 
                          (f'%{query}%', f'%{query}%'))
            results['total_bills'] = cursor.fetchone()[0]
        
        cursor.close()
        db_conn.close()
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error searching: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get platform statistics."""
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        
        # Get counts
        cursor.execute("SELECT COUNT(*) FROM people")
        total_members = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM bills")
        total_bills = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM votes")
        total_votes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM discrepancies WHERE resolved = FALSE")
        total_discrepancies = cursor.fetchone()[0]
        
        # Get recent activity
        cursor.execute("""
            SELECT COUNT(*) FROM people 
            WHERE created_at > NOW() - INTERVAL '30 days'
        """)
        new_members = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM bills 
            WHERE created_at > NOW() - INTERVAL '30 days'
        """)
        new_bills = cursor.fetchone()[0]
        
        cursor.close()
        db_conn.close()
        
        return jsonify({
            'total_members': total_members,
            'total_bills': total_bills,
            'total_votes': total_votes,
            'total_discrepancies': total_discrepancies,
            'new_members_30_days': new_members,
            'new_bills_30_days': new_bills,
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return jsonify({'error': 'Internal server error'}), 500