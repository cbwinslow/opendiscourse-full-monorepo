"""
Profile Storage System

This module provides functions for storing and retrieving member profiles.
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import psycopg2
from psycopg2.extras import Json

# Add the project root to the path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from opendiscourse.profiles.profile_models import MemberProfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfileStorage:
    """Handles storage and retrieval of member profiles."""
    
    def __init__(self, db_connection_string: str, file_storage_path: Optional[str] = None):
        """
        Initialize the profile storage system.
        
        Args:
            db_connection_string: PostgreSQL connection string
            file_storage_path: Optional path for file-based profile storage
        """
        self.db_connection_string = db_connection_string
        self.file_storage_path = file_storage_path
        
        # Create file storage directory if needed
        if self.file_storage_path:
            os.makedirs(self.file_storage_path, exist_ok=True)
        
        logger.info("Profile storage system initialized")
    
    def save_profile_to_database(self, profile: MemberProfile) -> bool:
        """
        Save a profile to the database.
        
        Args:
            profile: MemberProfile object to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            # Convert profile to dictionary for storage
            profile_dict = self._profile_to_dict(profile)
            
            # Insert or update profile
            cursor.execute("""
                INSERT INTO member_profiles (person_id, profile_data, profile_score, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (person_id) DO UPDATE SET
                    profile_data = EXCLUDED.profile_data,
                    profile_score = EXCLUDED.profile_score,
                    updated_at = EXCLUDED.updated_at
            """, (
                profile.basic_info.id,
                Json(profile_dict),
                profile.profile_score,
                profile.created_at,
                profile.updated_at
            ))
            
            db_conn.commit()
            cursor.close()
            db_conn.close()
            
            logger.info(f"Saved profile for {profile.basic_info.name} to database")
            return True
            
        except Exception as e:
            logger.error(f"Error saving profile for {profile.basic_info.id} to database: {e}")
            return False
    
    def save_profile_to_file(self, profile: MemberProfile) -> bool:
        """
        Save a profile to a JSON file.
        
        Args:
            profile: MemberProfile object to save
            
        Returns:
            True if successful, False otherwise
        """
        if not self.file_storage_path:
            logger.warning("No file storage path configured")
            return False
        
        try:
            # Create filename based on person ID
            filename = f"{profile.basic_info.id.replace('/', '_').replace(':', '_')}.json"
            filepath = os.path.join(self.file_storage_path, filename)
            
            # Convert profile to dictionary
            profile_dict = self._profile_to_dict(profile)
            
            # Save to file
            with open(filepath, 'w') as f:
                json.dump(profile_dict, f, indent=2, default=str)
            
            logger.info(f"Saved profile for {profile.basic_info.name} to file {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving profile for {profile.basic_info.id} to file: {e}")
            return False
    
    def save_profile(self, profile: MemberProfile) -> bool:
        """
        Save a profile to both database and file storage (if configured).
        
        Args:
            profile: MemberProfile object to save
            
        Returns:
            True if successful, False otherwise
        """
        success = True
        
        # Save to database
        if not self.save_profile_to_database(profile):
            success = False
        
        # Save to file if configured
        if self.file_storage_path and not self.save_profile_to_file(profile):
            success = False
        
        return success
    
    def load_profile_from_database(self, person_id: str) -> Optional[MemberProfile]:
        """
        Load a profile from the database.
        
        Args:
            person_id: Person ID
            
        Returns:
            MemberProfile object or None if not found
        """
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            cursor.execute("""
                SELECT profile_data, created_at, updated_at
                FROM member_profiles
                WHERE person_id = %s
            """, (person_id,))
            
            row = cursor.fetchone()
            cursor.close()
            db_conn.close()
            
            if row:
                profile_dict = row[0]
                profile = self._dict_to_profile(profile_dict)
                return profile
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading profile for {person_id} from database: {e}")
            return None
    
    def load_profile_from_file(self, person_id: str) -> Optional[MemberProfile]:
        """
        Load a profile from a JSON file.
        
        Args:
            person_id: Person ID
            
        Returns:
            MemberProfile object or None if not found
        """
        if not self.file_storage_path:
            return None
        
        try:
            # Create filename based on person ID
            filename = f"{person_id.replace('/', '_').replace(':', '_')}.json"
            filepath = os.path.join(self.file_storage_path, filename)
            
            # Check if file exists
            if not os.path.exists(filepath):
                return None
            
            # Load from file
            with open(filepath, 'r') as f:
                profile_dict = json.load(f)
            
            profile = self._dict_to_profile(profile_dict)
            return profile
            
        except Exception as e:
            logger.error(f"Error loading profile for {person_id} from file: {e}")
            return None
    
    def load_profile(self, person_id: str) -> Optional[MemberProfile]:
        """
        Load a profile from database or file storage.
        
        Args:
            person_id: Person ID
            
        Returns:
            MemberProfile object or None if not found
        """
        # Try database first
        profile = self.load_profile_from_database(person_id)
        if profile:
            return profile
        
        # Try file storage
        profile = self.load_profile_from_file(person_id)
        return profile
    
    def get_profile_summary(self, person_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a summary of a profile without loading the full profile.
        
        Args:
            person_id: Person ID
            
        Returns:
            Dictionary with profile summary or None if not found
        """
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            cursor.execute("""
                SELECT profile_score, created_at, updated_at, 
                       profile_data->'basic_info'->>'name' as name,
                       profile_data->'basic_info'->>'image_url' as image_url,
                       profile_data->'roles' as roles
                FROM member_profiles
                WHERE person_id = %s
            """, (person_id,))
            
            row = cursor.fetchone()
            cursor.close()
            db_conn.close()
            
            if row:
                return {
                    'person_id': person_id,
                    'name': row[3],
                    'image_url': row[4],
                    'profile_score': row[0],
                    'created_at': row[1],
                    'updated_at': row[2],
                    'roles': row[5] if row[5] else []
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting profile summary for {person_id}: {e}")
            return None
    
    def search_profiles(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search for profiles by name or other criteria.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of profile summaries
        """
        summaries = []
        
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            # Search by name in profile data
            cursor.execute("""
                SELECT person_id, profile_score, updated_at,
                       profile_data->'basic_info'->>'name' as name,
                       profile_data->'basic_info'->>'image_url' as image_url
                FROM member_profiles
                WHERE profile_data->'basic_info'->>'name' ILIKE %s
                ORDER BY profile_score DESC, updated_at DESC
                LIMIT %s
            """, (f"%{query}%", limit))
            
            rows = cursor.fetchall()
            cursor.close()
            db_conn.close()
            
            for row in rows:
                summaries.append({
                    'person_id': row[0],
                    'name': row[3],
                    'image_url': row[4],
                    'profile_score': row[1],
                    'updated_at': row[2]
                })
            
        except Exception as e:
            logger.error(f"Error searching profiles: {e}")
        
        return summaries
    
    def get_top_profiles(self, limit: int = 50, sort_by: str = 'profile_score') -> List[Dict[str, Any]]:
        """
        Get top profiles sorted by a specific criterion.
        
        Args:
            limit: Maximum number of results
            sort_by: Field to sort by ('profile_score', 'updated_at', 'name')
            
        Returns:
            List of profile summaries
        """
        summaries = []
        
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            # Validate sort_by parameter
            valid_sort_fields = ['profile_score', 'updated_at', 'name']
            if sort_by not in valid_sort_fields:
                sort_by = 'profile_score'
            
            # Build order by clause
            if sort_by == 'name':
                order_clause = "profile_data->'basic_info'->>'name'"
            else:
                order_clause = sort_by
            
            cursor.execute(f"""
                SELECT person_id, profile_score, updated_at,
                       profile_data->'basic_info'->>'name' as name,
                       profile_data->'basic_info'->>'image_url' as image_url
                FROM member_profiles
                ORDER BY {order_clause} DESC
                LIMIT %s
            """, (limit,))
            
            rows = cursor.fetchall()
            cursor.close()
            db_conn.close()
            
            for row in rows:
                summaries.append({
                    'person_id': row[0],
                    'name': row[3],
                    'image_url': row[4],
                    'profile_score': row[1],
                    'updated_at': row[2]
                })
            
        except Exception as e:
            logger.error(f"Error getting top profiles: {e}")
        
        return summaries
    
    def _profile_to_dict(self, profile: MemberProfile) -> Dict[str, Any]:
        """
        Convert a MemberProfile object to a dictionary.
        
        Args:
            profile: MemberProfile object
            
        Returns:
            Dictionary representation of the profile
        """
        # This is a simplified conversion
        # In a production system, you might want to use a more robust serialization approach
        
        def serialize_dataclass(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return {field: serialize_dataclass(getattr(obj, field)) 
                       for field in obj.__dataclass_fields__.keys()}
            elif isinstance(obj, list):
                return [serialize_dataclass(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: serialize_dataclass(value) for key, value in obj.items()}
            else:
                return obj
        
        return serialize_dataclass(profile)
    
    def _dict_to_profile(self, profile_dict: Dict[str, Any]) -> MemberProfile:
        """
        Convert a dictionary to a MemberProfile object.
        
        Args:
            profile_dict: Dictionary representation of a profile
            
        Returns:
            MemberProfile object
        """
        # This is a simplified conversion
        # In a production system, you would want to properly reconstruct the dataclass objects
        
        # For now, we'll create a basic profile structure
        # A full implementation would reconstruct all the nested objects
        
        from opendiscourse.profiles.profile_models import (
            ProfileBasicInfo, ProfileRole, ProfilePartyAffiliation,
            ProfileSocialMedia, ProfileKPI, ProfileVoteRecord, ProfileBillSponsorship,
            ProfileCommitteeMembership, ProfileStatement, ProfileDiscrepancy,
            ProfileActivitySummary, MemberProfile
        )
        
        try:
            basic_info_data = profile_dict.get('basic_info', {})
            basic_info = ProfileBasicInfo(
                id=basic_info_data.get('id', ''),
                name=basic_info_data.get('name', ''),
                given_name=basic_info_data.get('given_name'),
                family_name=basic_info_data.get('family_name'),
                image_url=basic_info_data.get('image_url'),
                bio=basic_info_data.get('bio'),
                birth_date=basic_info_data.get('birth_date'),
                gender=basic_info_data.get('gender'),
                email=basic_info_data.get('email'),
                website=basic_info_data.get('website'),
                office=basic_info_data.get('office'),
                phone=basic_info_data.get('phone'),
                fax=basic_info_data.get('fax'),
                contact_form=basic_info_data.get('contact_form')
            )
            
            # Create a basic profile with the essential information
            profile = MemberProfile(
                basic_info=basic_info,
                roles=[],
                party_affiliations=[],
                social_media=ProfileSocialMedia(),
                kpis=[],
                vote_records=[],
                bill_sponsorships=[],
                committee_memberships=[],
                statements=[],
                discrepancies=[],
                activity_summaries=[],
                created_at=datetime.fromisoformat(profile_dict.get('created_at', datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(profile_dict.get('updated_at', datetime.now().isoformat())),
                data_sources=profile_dict.get('data_sources', []),
                profile_score=profile_dict.get('profile_score', 0.0)
            )
            
            return profile
            
        except Exception as e:
            logger.error(f"Error converting dictionary to profile: {e}")
            # Return a minimal profile if conversion fails
            return MemberProfile(
                basic_info=ProfileBasicInfo(id='unknown', name='Unknown'),
                roles=[],
                party_affiliations=[],
                social_media=ProfileSocialMedia(),
                kpis=[],
                vote_records=[],
                bill_sponsorships=[],
                committee_memberships=[],
                statements=[],
                discrepancies=[],
                activity_summaries=[]
            )

# SQL migration to create the member_profiles table
def create_member_profiles_table(db_connection_string: str) -> bool:
    """
    Create the member_profiles table in the database.
    
    Args:
        db_connection_string: PostgreSQL connection string
        
    Returns:
        True if successful, False otherwise
    """
    try:
        db_conn = psycopg2.connect(db_connection_string)
        cursor = db_conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS member_profiles (
                person_id TEXT PRIMARY KEY,
                profile_data JSONB NOT NULL,
                profile_score NUMERIC(3,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indices for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_member_profiles_score 
            ON member_profiles (profile_score DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_member_profiles_updated 
            ON member_profiles (updated_at DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_member_profiles_name 
            ON member_profiles ((profile_data->'basic_info'->>'name'))
        """)
        
        db_conn.commit()
        cursor.close()
        db_conn.close()
        
        logger.info("Created member_profiles table")
        return True
        
    except Exception as e:
        logger.error(f"Error creating member_profiles table: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # Example of how to use the profile storage system
    # storage = ProfileStorage(
    #     db_connection_string="postgresql://user:password@localhost/opendiscourse",
    #     file_storage_path="/path/to/profile/files"
    # )
    # 
    # # Create the member_profiles table
    # create_member_profiles_table("postgresql://user:password@localhost/opendiscourse")
    # 
    # # Save a profile
    # # success = storage.save_profile(profile)
    # 
    # # Load a profile
    # # profile = storage.load_profile("person-123")
    # 
    # # Search profiles
    # # results = storage.search_profiles("John")
    pass