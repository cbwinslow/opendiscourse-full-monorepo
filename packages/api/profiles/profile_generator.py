"""
Member Profile Generator

This module generates comprehensive member profiles from collected government data.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import psycopg2
from psycopg2.extras import Json

# Add the project root to the path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from opendiscourse.profiles.profile_models import (
    MemberProfile, ProfileBasicInfo, ProfileRole, ProfilePartyAffiliation,
    ProfileSocialMedia, ProfileKPI, ProfileVoteRecord, ProfileBillSponsorship,
    ProfileCommitteeMembership, ProfileStatement, ProfileDiscrepancy,
    ProfileActivitySummary
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfileGenerator:
    """Generates member profiles from government data."""
    
    def __init__(self, db_connection_string: str):
        """
        Initialize the profile generator.
        
        Args:
            db_connection_string: PostgreSQL connection string
        """
        self.db_connection_string = db_connection_string
        logger.info("Profile generator initialized")
    
    def generate_profile(self, person_id: str) -> Optional[MemberProfile]:
        """
        Generate a complete profile for a member.
        
        Args:
            person_id: Person ID
            
        Returns:
            MemberProfile object or None if person not found
        """
        logger.info(f"Generating profile for person {person_id}")
        
        try:
            # Get basic information
            basic_info = self._get_basic_info(person_id)
            if not basic_info:
                logger.warning(f"No basic information found for person {person_id}")
                return None
            
            # Get roles
            roles = self._get_roles(person_id)
            
            # Get party affiliations
            party_affiliations = self._get_party_affiliations(person_id)
            
            # Get social media accounts
            social_media = self._get_social_media(person_id)
            
            # Get voting records
            vote_records = self._get_vote_records(person_id)
            
            # Get bill sponsorships
            bill_sponsorships = self._get_bill_sponsorships(person_id)
            
            # Get committee memberships
            committee_memberships = self._get_committee_memberships(person_id)
            
            # Get public statements (social media posts)
            statements = self._get_statements(person_id)
            
            # Calculate KPIs
            kpis = self._calculate_kpis(vote_records, bill_sponsorships, statements)
            
            # Identify discrepancies
            discrepancies = self._identify_discrepancies(vote_records, statements)
            
            # Generate activity summaries
            activity_summaries = self._generate_activity_summaries(
                bill_sponsorships, vote_records, statements, committee_memberships
            )
            
            # Calculate profile score
            profile_score = self._calculate_profile_score(
                basic_info, roles, party_affiliations, vote_records, 
                bill_sponsorships, committee_memberships, statements
            )
            
            # Create profile
            profile = MemberProfile(
                basic_info=basic_info,
                roles=roles,
                party_affiliations=party_affiliations,
                social_media=social_media,
                kpis=kpis,
                vote_records=vote_records,
                bill_sponsorships=bill_sponsorships,
                committee_memberships=committee_memberships,
                statements=statements,
                discrepancies=discrepancies,
                activity_summaries=activity_summaries,
                data_sources=self._identify_data_sources(person_id),
                profile_score=profile_score
            )
            
            logger.info(f"Successfully generated profile for {basic_info.name}")
            return profile
            
        except Exception as e:
            logger.error(f"Error generating profile for person {person_id}: {e}")
            raise
    
    def _get_basic_info(self, person_id: str) -> Optional[ProfileBasicInfo]:
        """
        Get basic information for a person.
        
        Args:
            person_id: Person ID
            
        Returns:
            ProfileBasicInfo object or None if not found
        """
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            cursor.execute("""
                SELECT id, name, given_name, family_name, email, gender, biography, 
                       birth_date, image_url, source_url
                FROM people 
                WHERE id = %s
            """, (person_id,))
            
            row = cursor.fetchone()
            cursor.close()
            db_conn.close()
            
            if row:
                return ProfileBasicInfo(
                    id=row[0],
                    name=row[1] or '',
                    given_name=row[2],
                    family_name=row[3],
                    email=row[4],
                    gender=row[5],
                    bio=row[6],
                    birth_date=row[7],
                    image_url=row[8],
                    website=row[9]
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting basic info for person {person_id}: {e}")
            raise
    
    def _get_roles(self, person_id: str) -> List[ProfileRole]:
        """
        Get roles for a person.
        
        Args:
            person_id: Person ID
            
        Returns:
            List of ProfileRole objects
        """
        roles = []
        
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            cursor.execute("""
                SELECT pr.type, pr.district, pr.jurisdiction_id, pr.start_date, pr.end_date,
                       j.name as jurisdiction_name, pr.created_at, pr.updated_at
                FROM person_roles pr
                LEFT JOIN jurisdictions j ON pr.jurisdiction_id = j.id
                WHERE pr.person_id = %s
                ORDER BY pr.start_date DESC
            """, (person_id,))
            
            rows = cursor.fetchall()
            cursor.close()
            db_conn.close()
            
            for row in rows:
                # Determine if this is a current role
                current = False
                if row[4] is None:  # No end date means current
                    current = True
                elif row[4] and row[4] > datetime.now().date():  # End date in future
                    current = True
                
                role = ProfileRole(
                    type=row[0] or '',
                    jurisdiction_id=row[2] or '',
                    jurisdiction_name=row[5] or '',
                    district=row[1],
                    start_date=row[3].strftime('%Y-%m-%d') if row[3] else None,
                    end_date=row[4].strftime('%Y-%m-%d') if row[4] else None,
                    current=current
                )
                roles.append(role)
            
        except Exception as e:
            logger.error(f"Error getting roles for person {person_id}: {e}")
            raise
        
        return roles
    
    def _get_party_affiliations(self, person_id: str) -> List[ProfilePartyAffiliation]:
        """
        Get party affiliations for a person.
        
        Args:
            person_id: Person ID
            
        Returns:
            List of ProfilePartyAffiliation objects
        """
        affiliations = []
        
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            cursor.execute("""
                SELECT p.name, ppa.start_date, ppa.end_date, ppa.created_at, ppa.updated_at
                FROM person_party_affiliations ppa
                JOIN parties p ON ppa.party_id = p.id
                WHERE ppa.person_id = %s
                ORDER BY ppa.start_date DESC
            """, (person_id,))
            
            rows = cursor.fetchall()
            cursor.close()
            db_conn.close()
            
            for row in rows:
                # Determine if this is a current affiliation
                current = False
                if row[2] is None:  # No end date means current
                    current = True
                elif row[2] and row[2] > datetime.now().date():  # End date in future
                    current = True
                
                affiliation = ProfilePartyAffiliation(
                    name=row[0] or '',
                    start_date=row[1].strftime('%Y-%m-%d') if row[1] else None,
                    end_date=row[2].strftime('%Y-%m-%d') if row[2] else None,
                    current=current
                )
                affiliations.append(affiliation)
            
        except Exception as e:
            logger.error(f"Error getting party affiliations for person {person_id}: {e}")
            raise
        
        return affiliations
    
    def _get_social_media(self, person_id: str) -> ProfileSocialMedia:
        """
        Get social media accounts for a person.
        
        Args:
            person_id: Person ID
            
        Returns:
            ProfileSocialMedia object
        """
        social_media = ProfileSocialMedia()
        
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            cursor.execute("""
                SELECT psma.username, smp.name as platform_name, psma.url
                FROM person_social_media_accounts psma
                JOIN social_media_platforms smp ON psma.platform_id = smp.id
                WHERE psma.person_id = %s
            """, (person_id,))
            
            rows = cursor.fetchall()
            cursor.close()
            db_conn.close()
            
            for row in rows:
                platform_name = row[1].lower() if row[1] else ''
                url = row[2] or ''
                
                if platform_name == 'twitter':
                    social_media.twitter = url
                elif platform_name == 'facebook':
                    social_media.facebook = url
                elif platform_name == 'youtube':
                    social_media.youtube = url
                elif platform_name == 'instagram':
                    social_media.instagram = url
                elif platform_name == 'linkedin':
                    social_media.linkedin = url
            
        except Exception as e:
            logger.error(f"Error getting social media accounts for person {person_id}: {e}")
            raise
        
        return social_media
    
    def _get_vote_records(self, person_id: str) -> List[ProfileVoteRecord]:
        """
        Get voting records for a person.
        
        Args:
            person_id: Person ID
            
        Returns:
            List of ProfileVoteRecord objects
        """
        vote_records = []
        
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            cursor.execute("""
                SELECT vd.option, v.date, v.motion_text, v.result, v.bill_id,
                       b.identifier as bill_identifier, b.title as bill_title,
                       b.subject as bill_subject, b.classification as bill_classification
                FROM vote_details vd
                JOIN votes v ON vd.vote_id = v.id
                LEFT JOIN bills b ON v.bill_id = b.id
                WHERE vd.person_id = %s
                ORDER BY v.date DESC
                LIMIT 1000  -- Limit for performance
            """, (person_id,))
            
            rows = cursor.fetchall()
            cursor.close()
            db_conn.close()
            
            for row in rows:
                vote_record = ProfileVoteRecord(
                    bill_id=row[4] or '',
                    bill_identifier=row[5] or '',
                    bill_title=row[6] or '',
                    vote_date=row[1].strftime('%Y-%m-%d') if row[1] else '',
                    vote_position=row[0] or '',
                    vote_result=row[3] or '',
                    bill_subject=row[7],
                    bill_classification=row[8]
                )
                vote_records.append(vote_record)
            
        except Exception as e:
            logger.error(f"Error getting vote records for person {person_id}: {e}")
            raise
        
        return vote_records
    
    def _get_bill_sponsorships(self, person_id: str) -> List[ProfileBillSponsorship]:
        """
        Get bill sponsorships for a person.
        
        Args:
            person_id: Person ID
            
        Returns:
            List of ProfileBillSponsorship objects
        """
        sponsorships = []
        
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            cursor.execute("""
                SELECT bs.bill_id, bs.classification, bs.created_at,
                       b.identifier as bill_identifier, b.title as bill_title,
                       b.subject as bill_subject, b.extras as bill_extras
                FROM bill_sponsors bs
                JOIN bills b ON bs.bill_id = b.id
                WHERE bs.person_id = %s
                ORDER BY bs.created_at DESC
                LIMIT 1000  -- Limit for performance
            """, (person_id,))
            
            rows = cursor.fetchall()
            cursor.close()
            db_conn.close()
            
            for row in rows:
                # Determine sponsorship type
                sponsorship_type = 'cosponsor'
                if row[1] and 'primary' in row[1].lower():
                    sponsorship_type = 'primary'
                
                # Extract bill status from extras
                bill_status = None
                if row[6]:  # extras JSON
                    try:
                        extras = row[6] if isinstance(row[6], dict) else json.loads(row[6])
                        bill_status = extras.get('latest_major_action', '')
                    except:
                        pass
                
                sponsorship = ProfileBillSponsorship(
                    bill_id=row[0] or '',
                    bill_identifier=row[3] or '',
                    bill_title=row[4] or '',
                    sponsorship_type=sponsorship_type,
                    sponsorship_date=row[2].strftime('%Y-%m-%d') if row[2] else '',
                    bill_subject=row[5],
                    bill_status=bill_status
                )
                sponsorships.append(sponsorship)
            
        except Exception as e:
            logger.error(f"Error getting bill sponsorships for person {person_id}: {e}")
            raise
        
        return sponsorships
    
    def _get_committee_memberships(self, person_id: str) -> List[ProfileCommitteeMembership]:
        """
        Get committee memberships for a person.
        
        Args:
            person_id: Person ID
            
        Returns:
            List of ProfileCommitteeMembership objects
        """
        memberships = []
        
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            cursor.execute("""
                SELECT cm.committee_id, c.name as committee_name, cm.role, 
                       cm.start_date, cm.end_date, cm.created_at, cm.updated_at
                FROM committee_memberships cm
                JOIN committees c ON cm.committee_id = c.id
                WHERE cm.person_id = %s
                ORDER BY cm.start_date DESC
            """, (person_id,))
            
            rows = cursor.fetchall()
            cursor.close()
            db_conn.close()
            
            for row in rows:
                # Determine if this is a current membership
                current = False
                if row[4] is None:  # No end date means current
                    current = True
                elif row[4] and row[4] > datetime.now().date():  # End date in future
                    current = True
                
                membership = ProfileCommitteeMembership(
                    committee_id=row[0] or '',
                    committee_name=row[1] or '',
                    role=row[2] or 'member',
                    start_date=row[3].strftime('%Y-%m-%d') if row[3] else None,
                    end_date=row[4].strftime('%Y-%m-%d') if row[4] else None,
                    current=current
                )
                memberships.append(membership)
            
        except Exception as e:
            logger.error(f"Error getting committee memberships for person {person_id}: {e}")
            raise
        
        return memberships
    
    def _get_statements(self, person_id: str) -> List[ProfileStatement]:
        """
        Get public statements (social media posts) for a person.
        
        Args:
            person_id: Person ID
            
        Returns:
            List of ProfileStatement objects
        """
        statements = []
        
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            cursor.execute("""
                SELECT smp.id, smp.content, smp.posted_at, smp.post_url,
                       smp.likes_count, smp.shares_count, smp.comments_count,
                       smp.sentiment_score, smp.created_at, smp.updated_at,
                       smp.platform_id, smp.post_id,
                       smpa.username, smp.platform_name
                FROM social_media_posts smp
                JOIN (
                    SELECT psma.person_id, psma.platform_id, smp.name as platform_name, psma.username
                    FROM person_social_media_accounts psma
                    JOIN social_media_platforms smp ON psma.platform_id = smp.id
                ) smpa ON smp.person_id = smpa.person_id AND smp.platform_id = smpa.platform_id
                WHERE smp.person_id = %s
                ORDER BY smp.posted_at DESC
                LIMIT 500  -- Limit for performance
            """, (person_id,))
            
            rows = cursor.fetchall()
            cursor.close()
            db_conn.close()
            
            for row in rows:
                statement = ProfileStatement(
                    id=row[0] or '',
                    content=row[1] or '',
                    posted_at=row[2].strftime('%Y-%m-%d %H:%M:%S') if row[2] else '',
                    platform=row[12].lower() if row[12] else 'unknown',
                    url=row[3],
                    likes=row[4] or 0,
                    shares=row[5] or 0,
                    comments=row[6] or 0,
                    sentiment_score=float(row[7]) if row[7] else None
                )
                statements.append(statement)
            
        except Exception as e:
            logger.error(f"Error getting statements for person {person_id}: {e}")
            raise
        
        return statements
    
    def _calculate_kpis(self, vote_records: List[ProfileVoteRecord], 
                       bill_sponsorships: List[ProfileBillSponsorship],
                       statements: List[ProfileStatement]) -> List[ProfileKPI]:
        """
        Calculate key performance indicators for a member.
        
        Args:
            vote_records: List of vote records
            bill_sponsorships: List of bill sponsorships
            statements: List of public statements
            
        Returns:
            List of ProfileKPI objects
        """
        kpis = []
        
        try:
            # Voting participation rate
            if vote_records:
                total_votes = len(vote_records)
                # In a real implementation, we would compare to total possible votes
                voting_participation = min(1.0, total_votes / 100.0)  # Simplified
                kpis.append(ProfileKPI(
                    name="Voting Participation Rate",
                    value=f"{voting_participation:.1%}",
                    description="Percentage of votes participated in",
                    category="voting",
                    percentile=90.0  # Placeholder
                ))
            
            # Bill sponsorship count
            primary_sponsorships = len([s for s in bill_sponsorships if s.sponsorship_type == 'primary'])
            kpis.append(ProfileKPI(
                name="Bills Sponsored",
                value=primary_sponsorships,
                description="Number of bills primarily sponsored",
                category="legislation",
                percentile=75.0  # Placeholder
            ))
            
            # Public engagement score
            if statements:
                total_engagement = sum(s.likes + s.shares + s.comments for s in statements)
                avg_engagement = total_engagement / len(statements) if statements else 0
                kpis.append(ProfileKPI(
                    name="Average Social Media Engagement",
                    value=round(avg_engagement, 1),
                    description="Average engagement per social media post",
                    category="engagement",
                    percentile=85.0  # Placeholder
                ))
            
            # Effectiveness score (simplified)
            effectiveness_score = (len(bill_sponsorships) * 0.3 + 
                                 len(vote_records) * 0.2 + 
                                 len(statements) * 0.1) / 10
            kpis.append(ProfileKPI(
                name="Overall Effectiveness Score",
                value=round(effectiveness_score, 1),
                description="Composite score based on legislative and public engagement",
                category="effectiveness",
                percentile=80.0  # Placeholder
            ))
            
        except Exception as e:
            logger.error(f"Error calculating KPIs: {e}")
        
        return kpis
    
    def _identify_discrepancies(self, vote_records: List[ProfileVoteRecord],
                               statements: List[ProfileStatement]) -> List[ProfileDiscrepancy]:
        """
        Identify discrepancies between voting records and public statements.
        
        Args:
            vote_records: List of vote records
            statements: List of public statements
            
        Returns:
            List of ProfileDiscrepancy objects
        """
        discrepancies = []
        
        # This is a simplified implementation
        # In a real system, this would use NLP to analyze statement content
        # and compare it with voting positions on similar issues
        
        try:
            # For demonstration, we'll create some placeholder discrepancies
            # if there are both votes and statements
            if vote_records and statements:
                discrepancy = ProfileDiscrepancy(
                    id="disc-1",
                    issue="Generic Policy Issue",
                    vote_position="yes",
                    statement_position="negative sentiment",
                    confidence_score=0.75,
                    evidence=[
                        "Voted YES on related bill",
                        "Made negative statement about similar issue"
                    ]
                )
                discrepancies.append(discrepancy)
        
        except Exception as e:
            logger.error(f"Error identifying discrepancies: {e}")
        
        return discrepancies
    
    def _generate_activity_summaries(self, bill_sponsorships: List[ProfileBillSponsorship],
                                   vote_records: List[ProfileVoteRecord],
                                   statements: List[ProfileStatement],
                                   committee_memberships: List[ProfileCommitteeMembership]) -> List[ProfileActivitySummary]:
        """
        Generate activity summaries for different time periods.
        
        Args:
            bill_sponsorships: List of bill sponsorships
            vote_records: List of vote records
            statements: List of public statements
            committee_memberships: List of committee memberships
            
        Returns:
            List of ProfileActivitySummary objects
        """
        summaries = []
        
        try:
            # Generate summary for last 30 days
            period_end = datetime.now()
            period_start = period_end - timedelta(days=30)
            
            # Filter activities for the period (simplified)
            recent_bills = [b for b in bill_sponsorships 
                           if datetime.strptime(b.sponsorship_date, '%Y-%m-%d') > period_start]
            recent_votes = [v for v in vote_records 
                           if datetime.strptime(v.vote_date, '%Y-%m-%d') > period_start]
            recent_statements = [s for s in statements 
                                if datetime.strptime(s.posted_at, '%Y-%m-%d %H:%M:%S') > period_start]
            
            summary = ProfileActivitySummary(
                period_start=period_start.strftime('%Y-%m-%d'),
                period_end=period_end.strftime('%Y-%m-%d'),
                bills_sponsored=len([b for b in recent_bills if b.sponsorship_type == 'primary']),
                bills_cosponsored=len([b for b in recent_bills if b.sponsorship_type == 'cosponsor']),
                votes_cast=len(recent_votes),
                statements_made=len(recent_statements),
                committee_meetings=0,  # Simplified
                engagement_score=self._calculate_engagement_score(recent_bills, recent_votes, recent_statements)
            )
            summaries.append(summary)
            
        except Exception as e:
            logger.error(f"Error generating activity summaries: {e}")
        
        return summaries
    
    def _calculate_engagement_score(self, bills: List[ProfileBillSponsorship],
                                  votes: List[ProfileVoteRecord],
                                  statements: List[ProfileStatement]) -> float:
        """
        Calculate an engagement score based on recent activities.
        
        Args:
            bills: List of recent bill sponsorships
            votes: List of recent votes
            statements: List of recent statements
            
        Returns:
            Engagement score (0.0 - 100.0)
        """
        # Simplified scoring algorithm
        bill_score = len(bills) * 10
        vote_score = len(votes) * 5
        statement_score = len(statements) * 2
        
        total_score = bill_score + vote_score + statement_score
        
        # Normalize to 0-100 scale
        normalized_score = min(100.0, total_score / 2.0)
        
        return round(normalized_score, 1)
    
    def _calculate_profile_score(self, basic_info: ProfileBasicInfo,
                                roles: List[ProfileRole],
                                party_affiliations: List[ProfilePartyAffiliation],
                                vote_records: List[ProfileVoteRecord],
                                bill_sponsorships: List[ProfileBillSponsorship],
                                committee_memberships: List[ProfileCommitteeMembership],
                                statements: List[ProfileStatement]) -> float:
        """
        Calculate an overall profile completeness score.
        
        Args:
            basic_info: Basic information
            roles: List of roles
            party_affiliations: List of party affiliations
            vote_records: List of vote records
            bill_sponsorships: List of bill sponsorships
            committee_memberships: List of committee memberships
            statements: List of statements
            
        Returns:
            Profile completeness score (0.0 - 1.0)
        """
        # Calculate completeness based on available data
        total_components = 7.0
        completed_components = 0.0
        
        if basic_info.name:
            completed_components += 1
        if roles:
            completed_components += 1
        if party_affiliations:
            completed_components += 1
        if vote_records:
            completed_components += 1
        if bill_sponsorships:
            completed_components += 1
        if committee_memberships:
            completed_components += 1
        if statements:
            completed_components += 1
        
        return round(completed_components / total_components, 2)
    
    def _identify_data_sources(self, person_id: str) -> List[str]:
        """
        Identify which data sources contributed to this profile.
        
        Args:
            person_id: Person ID
            
        Returns:
            List of data source identifiers
        """
        sources = set()
        
        try:
            if person_id.startswith('openstates-'):
                sources.add('openstates')
            elif person_id.startswith('congressgov-'):
                sources.add('congressgov')
            elif person_id.startswith('openlegislation-'):
                sources.add('openlegislation')
            
            # Check for GovInfo data
            # This would require checking specific data elements
            # For now, we'll just return the source-based identification
            
        except Exception as e:
            logger.error(f"Error identifying data sources for person {person_id}: {e}")
        
        return list(sources)
    
    def generate_profiles_batch(self, person_ids: List[str]) -> Dict[str, MemberProfile]:
        """
        Generate profiles for multiple people.
        
        Args:
            person_ids: List of person IDs
            
        Returns:
            Dictionary mapping person IDs to MemberProfile objects
        """
        profiles = {}
        
        logger.info(f"Generating profiles for {len(person_ids)} people")
        
        for person_id in person_ids:
            try:
                profile = self.generate_profile(person_id)
                if profile:
                    profiles[person_id] = profile
            except Exception as e:
                logger.error(f"Error generating profile for person {person_id}: {e}")
                continue
        
        logger.info(f"Successfully generated {len(profiles)} profiles")
        return profiles
    
    def get_all_person_ids(self) -> List[str]:
        """
        Get all person IDs from the database.
        
        Returns:
            List of person IDs
        """
        person_ids = []
        
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            cursor.execute("SELECT id FROM people")
            rows = cursor.fetchall()
            
            cursor.close()
            db_conn.close()
            
            person_ids = [row[0] for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting person IDs: {e}")
            raise
        
        return person_ids

# Example usage
if __name__ == "__main__":
    # Example of how to use the profile generator
    # generator = ProfileGenerator(
    #     db_connection_string="postgresql://user:password@localhost/opendiscourse"
    # )
    # 
    # # Generate a profile for a specific person
    # profile = generator.generate_profile("openstates-ocd-person/123")
    # if profile:
    #     print(f"Generated profile for {profile.basic_info.name}")
    #     print(f"Profile score: {profile.profile_score}")
    #     print(f"Number of KPIs: {len(profile.kpis)}")
    # 
    # # Generate profiles for all people
    # all_person_ids = generator.get_all_person_ids()
    # profiles = generator.generate_profiles_batch(all_person_ids[:10])  # First 10 only
    # print(f"Generated {len(profiles)} profiles")
    pass