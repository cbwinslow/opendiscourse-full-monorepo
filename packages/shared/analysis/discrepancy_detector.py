"""
Discrepancy Detection System

This module identifies discrepancies between voting records and public statements
to assess truthfulness and consistency of government officials.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import Json

# Add the project root to the path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from opendiscourse.analysis.nlp_analyzer import NLPAnalyzer, SentimentAnalysisResult
from opendiscourse.profiles.profile_models import ProfileVoteRecord, ProfileStatement

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiscrepancyDetector:
    """Detects discrepancies between voting behavior and public statements."""
    
    def __init__(self, db_connection_string: str):
        """
        Initialize the discrepancy detector.
        
        Args:
            db_connection_string: PostgreSQL connection string
        """
        self.db_connection_string = db_connection_string
        self.nlp_analyzer = NLPAnalyzer()
        logger.info("Discrepancy detector initialized")
    
    def detect_discrepancies_for_person(self, person_id: str) -> List[Dict[str, Any]]:
        """
        Detect discrepancies for a specific person.
        
        Args:
            person_id: Person ID
            
        Returns:
            List of discrepancy findings
        """
        logger.info(f"Detecting discrepancies for person {person_id}")
        
        try:
            # Get voting records
            vote_records = self._get_vote_records(person_id)
            
            # Get public statements
            statements = self._get_statements(person_id)
            
            # Identify issues from voting records
            issues = self._identify_issues_from_votes(vote_records)
            
            # Detect discrepancies for each issue
            discrepancies = []
            for issue in issues:
                issue_discrepancies = self._detect_issue_discrepancies(
                    person_id, issue, vote_records, statements
                )
                discrepancies.extend(issue_discrepancies)
            
            # Store discrepancies in database
            self._store_discrepancies(discrepancies)
            
            logger.info(f"Found {len(discrepancies)} discrepancies for person {person_id}")
            return discrepancies
            
        except Exception as e:
            logger.error(f"Error detecting discrepancies for person {person_id}: {e}")
            raise
    
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
                LIMIT 2000  -- Limit for performance
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
    
    def _get_statements(self, person_id: str) -> List[ProfileStatement]:
        """
        Get public statements for a person.
        
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
                SELECT id, content, posted_at, platform, url,
                       likes_count, shares_count, comments_count, sentiment_score
                FROM social_media_posts
                WHERE person_id = %s
                ORDER BY posted_at DESC
                LIMIT 1000  -- Limit for performance
            """, (person_id,))
            
            rows = cursor.fetchall()
            cursor.close()
            db_conn.close()
            
            for row in rows:
                statement = ProfileStatement(
                    id=row[0] or '',
                    content=row[1] or '',
                    posted_at=row[2].strftime('%Y-%m-%d %H:%M:%S') if row[2] else '',
                    platform=row[3] or 'unknown',
                    url=row[4],
                    likes=row[5] or 0,
                    shares=row[6] or 0,
                    comments=row[7] or 0,
                    sentiment_score=float(row[8]) if row[8] else None
                )
                statements.append(statement)
            
        except Exception as e:
            logger.error(f"Error getting statements for person {person_id}: {e}")
            raise
        
        return statements
    
    def _identify_issues_from_votes(self, vote_records: List[ProfileVoteRecord]) -> List[str]:
        """
        Identify key issues from voting records.
        
        Args:
            vote_records: List of vote records
            
        Returns:
            List of issue topics
        """
        issues = set()
        
        # Extract issues from bill subjects and classifications
        for vote_record in vote_records:
            # Add subjects
            if vote_record.bill_subject:
                if isinstance(vote_record.bill_subject, list):
                    issues.update(vote_record.bill_subject)
                elif isinstance(vote_record.bill_subject, str):
                    issues.add(vote_record.bill_subject)
            
            # Add classifications
            if vote_record.bill_classification:
                if isinstance(vote_record.bill_classification, list):
                    issues.update(vote_record.bill_classification)
                elif isinstance(vote_record.bill_classification, str):
                    issues.add(vote_record.bill_classification)
        
        # Use NLP to extract additional issues from bill titles
        for vote_record in vote_records:
            if vote_record.bill_title:
                topics = self.nlp_analyzer.extract_topics(vote_record.bill_title)
                for topic, _ in topics.topics:
                    if topic != 'unknown':
                        issues.add(topic)
        
        return list(issues)
    
    def _detect_issue_discrepancies(self, person_id: str, issue: str,
                                  vote_records: List[ProfileVoteRecord],
                                  statements: List[ProfileStatement]) -> List[Dict[str, Any]]:
        """
        Detect discrepancies related to a specific issue.
        
        Args:
            person_id: Person ID
            issue: Issue topic
            vote_records: List of vote records
            statements: List of public statements
            
        Returns:
            List of discrepancy findings
        """
        discrepancies = []
        
        try:
            # Find relevant votes for this issue
            relevant_votes = self._filter_votes_by_issue(vote_records, issue)
            
            # Find relevant statements for this issue
            relevant_statements = self._filter_statements_by_issue(statements, issue)
            
            # If we have both votes and statements on this issue, check for consistency
            if relevant_votes and relevant_statements:
                # For each vote, check if there are consistent statements
                for vote in relevant_votes:
                    vote_discrepancies = self._check_vote_statement_consistency(
                        person_id, issue, vote, relevant_statements
                    )
                    discrepancies.extend(vote_discrepancies)
        
        except Exception as e:
            logger.error(f"Error detecting discrepancies for issue {issue}: {e}")
        
        return discrepancies
    
    def _filter_votes_by_issue(self, vote_records: List[ProfileVoteRecord], issue: str) -> List[ProfileVoteRecord]:
        """
        Filter vote records by relevance to an issue.
        
        Args:
            vote_records: List of vote records
            issue: Issue topic
            
        Returns:
            List of relevant vote records
        """
        relevant_votes = []
        issue_lower = issue.lower()
        
        for vote_record in vote_records:
            # Check subject
            if vote_record.bill_subject:
                if isinstance(vote_record.bill_subject, list):
                    if any(issue_lower in str(subject).lower() for subject in vote_record.bill_subject):
                        relevant_votes.append(vote_record)
                elif issue_lower in str(vote_record.bill_subject).lower():
                    relevant_votes.append(vote_record)
            
            # Check classification
            if vote_record.bill_classification:
                if isinstance(vote_record.bill_classification, list):
                    if any(issue_lower in str(classification).lower() for classification in vote_record.bill_classification):
                        relevant_votes.append(vote_record)
                elif issue_lower in str(vote_record.bill_classification).lower():
                    relevant_votes.append(vote_record)
            
            # Check title using NLP
            if vote_record.bill_title:
                topics = self.nlp_analyzer.extract_topics(vote_record.bill_title)
                if any(topic.lower() == issue_lower for topic, _ in topics.topics):
                    relevant_votes.append(vote_record)
        
        return relevant_votes
    
    def _filter_statements_by_issue(self, statements: List[ProfileStatement], issue: str) -> List[ProfileStatement]:
        """
        Filter statements by relevance to an issue.
        
        Args:
            statements: List of statements
            issue: Issue topic
            
        Returns:
            List of relevant statements
        """
        relevant_statements = []
        issue_lower = issue.lower()
        
        for statement in statements:
            # Check content directly
            if issue_lower in statement.content.lower():
                relevant_statements.append(statement)
                continue
            
            # Use NLP to check topics
            topics = self.nlp_analyzer.extract_topics(statement.content)
            if any(topic.lower() == issue_lower for topic, _ in topics.topics):
                relevant_statements.append(statement)
                continue
            
            # Check entities
            entities = self.nlp_analyzer.extract_entities(statement.content)
            if issue_lower in [e.lower() for e in entities.policy_areas]:
                relevant_statements.append(statement)
        
        return relevant_statements
    
    def _check_vote_statement_consistency(self, person_id: str, issue: str,
                                        vote_record: ProfileVoteRecord,
                                        statements: List[ProfileStatement]) -> List[Dict[str, Any]]:
        """
        Check consistency between a vote and related statements.
        
        Args:
            person_id: Person ID
            issue: Issue topic
            vote_record: Vote record
            statements: List of relevant statements
            
        Returns:
            List of discrepancy findings
        """
        discrepancies = []
        
        # Get the sentiment of relevant statements
        statement_sentiments = []
        evidence_snippets = []
        
        for statement in statements:
            # Analyze statement content
            analysis = self.nlp_analyzer.analyze_statement_content(statement.content)
            sentiment = analysis['sentiment']
            
            if sentiment:
                statement_sentiments.append(sentiment)
                # Create evidence snippet
                evidence_snippets.append({
                    'text_snippet': statement.content[:200] + '...' if len(statement.content) > 200 else statement.content,
                    'source_type': 'statement',
                    'source_id': statement.id,
                    'relevance_score': 0.8  # Placeholder
                })
        
        # If we have statement sentiments, compare with vote
        if statement_sentiments:
            # Determine overall statement position
            positive_count = sum(1 for s in statement_sentiments if s.sentiment == 'positive')
            negative_count = sum(1 for s in statement_sentiments if s.sentiment == 'negative')
            neutral_count = sum(1 for s in statement_sentiments if s.sentiment == 'neutral')
            
            total = len(statement_sentiments)
            if total > 0:
                if positive_count > negative_count and positive_count > neutral_count:
                    statement_position = 'positive'
                    avg_confidence = sum(s.confidence for s in statement_sentiments if s.sentiment == 'positive') / positive_count
                elif negative_count > positive_count and negative_count > neutral_count:
                    statement_position = 'negative'
                    avg_confidence = sum(s.confidence for s in statement_sentiments if s.sentiment == 'negative') / negative_count
                else:
                    statement_position = 'neutral'
                    avg_confidence = sum(s.confidence for s in statement_sentiments if s.sentiment == 'neutral') / neutral_count if neutral_count > 0 else 0.5
                
                # Compare with vote position
                vote_position = vote_record.vote_position.lower()
                
                # Map vote positions to sentiment expectations
                vote_sentiment_mapping = {
                    'yes': 'positive',
                    'no': 'negative',
                    'abstain': 'neutral',
                    'not voting': 'neutral'
                }
                
                expected_sentiment = vote_sentiment_mapping.get(vote_position, 'neutral')
                
                # Check for discrepancy
                if expected_sentiment != statement_position:
                    # Create discrepancy finding
                    discrepancy = {
                        'id': f"disc-{person_id}-{vote_record.bill_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        'person_id': person_id,
                        'issue': issue,
                        'vote_position': vote_position,
                        'statement_position': statement_position,
                        'confidence_score': avg_confidence,
                        'evidence': evidence_snippets,
                        'created_at': datetime.now(),
                        'resolved': False
                    }
                    discrepancies.append(discrepancy)
        
        return discrepancies
    
    def _store_discrepancies(self, discrepancies: List[Dict[str, Any]]) -> None:
        """
        Store discrepancy findings in the database.
        
        Args:
            discrepancies: List of discrepancy findings
        """
        if not discrepancies:
            return
        
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            for discrepancy in discrepancies:
                cursor.execute("""
                    INSERT INTO discrepancies (id, person_id, issue, vote_position, statement_position, 
                                             confidence_score, evidence, resolved, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        issue = EXCLUDED.issue,
                        vote_position = EXCLUDED.vote_position,
                        statement_position = EXCLUDED.statement_position,
                        confidence_score = EXCLUDED.confidence_score,
                        evidence = EXCLUDED.evidence,
                        updated_at = EXCLUDED.updated_at
                """, (
                    discrepancy['id'],
                    discrepancy['person_id'],
                    discrepancy['issue'],
                    discrepancy['vote_position'],
                    discrepancy['statement_position'],
                    discrepancy['confidence_score'],
                    Json(discrepancy['evidence']),
                    discrepancy['resolved'],
                    discrepancy['created_at'],
                    datetime.now()
                ))
            
            db_conn.commit()
            cursor.close()
            db_conn.close()
            
        except Exception as e:
            logger.error(f"Error storing discrepancies: {e}")
            raise
    
    def get_discrepancies_for_person(self, person_id: str) -> List[Dict[str, Any]]:
        """
        Get stored discrepancies for a person.
        
        Args:
            person_id: Person ID
            
        Returns:
            List of discrepancy findings
        """
        discrepancies = []
        
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            cursor.execute("""
                SELECT id, person_id, issue, vote_position, statement_position,
                       confidence_score, evidence, resolved, resolution_notes,
                       created_at, updated_at
                FROM discrepancies
                WHERE person_id = %s
                ORDER BY confidence_score DESC, created_at DESC
            """, (person_id,))
            
            rows = cursor.fetchall()
            cursor.close()
            db_conn.close()
            
            for row in rows:
                discrepancy = {
                    'id': row[0],
                    'person_id': row[1],
                    'issue': row[2],
                    'vote_position': row[3],
                    'statement_position': row[4],
                    'confidence_score': float(row[5]) if row[5] else 0.0,
                    'evidence': row[6] if row[6] else [],
                    'resolved': row[7],
                    'resolution_notes': row[8],
                    'created_at': row[9],
                    'updated_at': row[10]
                }
                discrepancies.append(discrepancy)
            
        except Exception as e:
            logger.error(f"Error getting discrepancies for person {person_id}: {e}")
            raise
        
        return discrepancies
    
    def get_top_discrepancies(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get the most confident discrepancy findings.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of discrepancy findings
        """
        discrepancies = []
        
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            cursor.execute("""
                SELECT id, person_id, issue, vote_position, statement_position,
                       confidence_score, evidence, resolved, resolution_notes,
                       created_at, updated_at
                FROM discrepancies
                WHERE resolved = FALSE
                ORDER BY confidence_score DESC, created_at DESC
                LIMIT %s
            """, (limit,))
            
            rows = cursor.fetchall()
            cursor.close()
            db_conn.close()
            
            for row in rows:
                discrepancy = {
                    'id': row[0],
                    'person_id': row[1],
                    'issue': row[2],
                    'vote_position': row[3],
                    'statement_position': row[4],
                    'confidence_score': float(row[5]) if row[5] else 0.0,
                    'evidence': row[6] if row[6] else [],
                    'resolved': row[7],
                    'resolution_notes': row[8],
                    'created_at': row[9],
                    'updated_at': row[10]
                }
                discrepancies.append(discrepancy)
            
        except Exception as e:
            logger.error(f"Error getting top discrepancies: {e}")
            raise
        
        return discrepancies
    
    def resolve_discrepancy(self, discrepancy_id: str, resolution_notes: str) -> bool:
        """
        Mark a discrepancy as resolved.
        
        Args:
            discrepancy_id: Discrepancy ID
            resolution_notes: Notes about the resolution
            
        Returns:
            True if successful, False otherwise
        """
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            cursor.execute("""
                UPDATE discrepancies
                SET resolved = TRUE, resolution_notes = %s, updated_at = %s
                WHERE id = %s
            """, (resolution_notes, datetime.now(), discrepancy_id))
            
            db_conn.commit()
            cursor.close()
            db_conn.close()
            
            logger.info(f"Resolved discrepancy {discrepancy_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resolving discrepancy {discrepancy_id}: {e}")
            return False
    
    def detect_discrepancies_batch(self, person_ids: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Detect discrepancies for multiple people.
        
        Args:
            person_ids: List of person IDs
            
        Returns:
            Dictionary mapping person IDs to lists of discrepancy findings
        """
        results = {}
        
        logger.info(f"Detecting discrepancies for {len(person_ids)} people")
        
        for person_id in person_ids:
            try:
                discrepancies = self.detect_discrepancies_for_person(person_id)
                results[person_id] = discrepancies
            except Exception as e:
                logger.error(f"Error detecting discrepancies for person {person_id}: {e}")
                results[person_id] = []
                continue
        
        logger.info(f"Completed discrepancy detection for {len(results)} people")
        return results

# Example usage
if __name__ == "__main__":
    # Example of how to use the discrepancy detector
    # detector = DiscrepancyDetector(
    #     db_connection_string="postgresql://user:password@localhost/opendiscourse"
    # )
    # 
    # # Detect discrepancies for a specific person
    # discrepancies = detector.detect_discrepancies_for_person("person-123")
    # print(f"Found {len(discrepancies)} discrepancies")
    # 
    # # Get stored discrepancies
    # stored_discrepancies = detector.get_discrepancies_for_person("person-123")
    # print(f"Retrieved {len(stored_discrepancies)} stored discrepancies")
    # 
    # # Get top discrepancies
    # top_discrepancies = detector.get_top_discrepancies(10)
    # print(f"Top 10 discrepancies: {len(top_discrepancies)}")
    pass