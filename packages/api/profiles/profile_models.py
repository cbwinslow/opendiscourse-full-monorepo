"""
Member Profile Data Model

This module defines the data models for member profiles and related entities.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime

@dataclass
class ProfileBasicInfo:
    """Basic information about a member."""
    id: str
    name: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    image_url: Optional[str] = None
    bio: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    office: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    contact_form: Optional[str] = None

@dataclass
class ProfileRole:
    """Role information for a member."""
    type: str  # e.g., 'representative', 'senator', 'governor'
    jurisdiction_id: str
    jurisdiction_name: str
    district: Optional[str] = None
    state: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    senate_class: Optional[str] = None
    state_rank: Optional[str] = None
    current: bool = False

@dataclass
class ProfilePartyAffiliation:
    """Party affiliation information."""
    name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    current: bool = False

@dataclass
class ProfileSocialMedia:
    """Social media accounts."""
    twitter: Optional[str] = None
    facebook: Optional[str] = None
    youtube: Optional[str] = None
    instagram: Optional[str] = None
    linkedin: Optional[str] = None

@dataclass
class ProfileKPI:
    """Key Performance Indicators for a member."""
    name: str
    value: Any
    description: str
    category: str  # e.g., 'voting', 'engagement', 'effectiveness'
    trend: Optional[str] = None  # 'increasing', 'decreasing', 'stable'
    percentile: Optional[float] = None
    historical_data: List[Dict] = field(default_factory=list)

@dataclass
class ProfileVoteRecord:
    """Voting record information."""
    bill_id: str
    bill_identifier: str
    bill_title: str
    vote_date: str
    vote_position: str  # 'yes', 'no', 'abstain', 'not voting'
    vote_result: str  # 'pass', 'fail'
    bill_subject: Optional[str] = None
    bill_classification: Optional[List[str]] = None

@dataclass
class ProfileBillSponsorship:
    """Bill sponsorship information."""
    bill_id: str
    bill_identifier: str
    bill_title: str
    sponsorship_type: str  # 'primary', 'cosponsor'
    sponsorship_date: str
    bill_subject: Optional[str] = None
    bill_status: Optional[str] = None

@dataclass
class ProfileCommitteeMembership:
    """Committee membership information."""
    committee_id: str
    committee_name: str
    role: str  # 'member', 'chair', 'ranking member'
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    current: bool = False

@dataclass
class ProfileStatement:
    """Public statement information."""
    id: str
    content: str
    posted_at: str
    platform: str  # 'twitter', 'facebook', 'youtube', 'press_release'
    url: Optional[str] = None
    likes: Optional[int] = None
    shares: Optional[int] = None
    comments: Optional[int] = None
    sentiment_score: Optional[float] = None
    topics: List[str] = field(default_factory=list)

@dataclass
class ProfileDiscrepancy:
    """Discrepancy between voting record and public statements."""
    id: str
    issue: str
    vote_position: str
    statement_position: str
    confidence_score: float
    evidence: List[str] = field(default_factory=list)
    resolved: bool = False
    resolution_notes: Optional[str] = None

@dataclass
class ProfileActivitySummary:
    """Summary of recent activity."""
    period_start: str
    period_end: str
    bills_sponsored: int
    bills_cosponsored: int
    votes_cast: int
    statements_made: int
    committee_meetings: int
    engagement_score: float

@dataclass
class MemberProfile:
    """Complete member profile."""
    # Basic information
    basic_info: ProfileBasicInfo
    
    # Political affiliations
    roles: List[ProfileRole]
    party_affiliations: List[ProfilePartyAffiliation]
    social_media: ProfileSocialMedia
    
    # Performance metrics
    kpis: List[ProfileKPI]
    
    # Legislative activity
    vote_records: List[ProfileVoteRecord]
    bill_sponsorships: List[ProfileBillSponsorship]
    committee_memberships: List[ProfileCommitteeMembership]
    
    # Public statements
    statements: List[ProfileStatement]
    
    # Discrepancies
    discrepancies: List[ProfileDiscrepancy]
    
    # Activity summaries
    activity_summaries: List[ProfileActivitySummary]
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    data_sources: List[str] = field(default_factory=list)
    profile_score: float = 0.0  # Completeness score 0.0 - 1.0

    def get_current_role(self) -> Optional[ProfileRole]:
        """Get the current role of the member."""
        current_roles = [role for role in self.roles if role.current]
        return current_roles[0] if current_roles else None
    
    def get_current_party(self) -> Optional[ProfilePartyAffiliation]:
        """Get the current party affiliation of the member."""
        current_parties = [party for party in self.party_affiliations if party.current]
        return current_parties[0] if current_parties else None
    
    def get_key_kpis(self, category: Optional[str] = None) -> List[ProfileKPI]:
        """Get key performance indicators, optionally filtered by category."""
        if category:
            return [kpi for kpi in self.kpis if kpi.category == category]
        return self.kpis
    
    def get_recent_activity(self, days: int = 30) -> ProfileActivitySummary:
        """Get recent activity summary for the specified number of days."""
        # In a real implementation, this would filter activity by date
        # For now, we'll return the most recent summary
        return self.activity_summaries[-1] if self.activity_summaries else None
    
    def get_voting_history(self, subject: Optional[str] = None) -> List[ProfileVoteRecord]:
        """Get voting history, optionally filtered by subject."""
        if subject:
            return [vote for vote in self.vote_records if vote.bill_subject and subject.lower() in vote.bill_subject.lower()]
        return self.vote_records
    
    def get_statement_history(self, platform: Optional[str] = None) -> List[ProfileStatement]:
        """Get statement history, optionally filtered by platform."""
        if platform:
            return [statement for statement in self.statements if statement.platform == platform]
        return self.statements
    
    def get_discrepancies_by_issue(self, issue: str) -> List[ProfileDiscrepancy]:
        """Get discrepancies related to a specific issue."""
        return [disc for disc in self.discrepancies if disc.issue.lower() == issue.lower()]

# Example usage
if __name__ == "__main__":
    # Example of creating a member profile
    # basic_info = ProfileBasicInfo(
    #     id="person-123",
    #     name="John Doe",
    #     given_name="John",
    #     family_name="Doe",
    #     image_url="https://example.com/image.jpg"
    # )
    # 
    # profile = MemberProfile(
    #     basic_info=basic_info,
    #     roles=[],
    #     party_affiliations=[],
    #     social_media=ProfileSocialMedia(),
    #     kpis=[],
    #     vote_records=[],
    #     bill_sponsorships=[],
    #     committee_memberships=[],
    #     statements=[],
    #     discrepancies=[],
    #     activity_summaries=[]
    # )
    # 
    # print(f"Created profile for {profile.basic_info.name}")
    pass