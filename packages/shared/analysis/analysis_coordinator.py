"""
Analysis Coordinator

This module coordinates all analysis activities including NLP processing,
discrepancy detection, and profile generation.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import Json

# Add the project root to the path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from opendiscourse.analysis.nlp_analyzer import NLPAnalyzer
from opendiscourse.analysis.discrepancy_detector import DiscrepancyDetector
from opendiscourse.profiles.profile_generator import ProfileGenerator
from opendiscourse.profiles.profile_storage import ProfileStorage, create_member_profiles_table

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisCoordinator:
    """Coordinates all analysis activities for government data."""
    
    def __init__(self, db_connection_string: str, file_storage_path: Optional[str] = None):
        """
        Initialize the analysis coordinator.
        
        Args:
            db_connection_string: PostgreSQL connection string
            file_storage_path: Optional path for file-based storage
        """
        self.db_connection_string = db_connection_string
        self.file_storage_path = file_storage_path
        
        # Initialize components
        self.nlp_analyzer = NLPAnalyzer()
        self.discrepancy_detector = DiscrepancyDetector(db_connection_string)
        self.profile_generator = ProfileGenerator(db_connection_string)
        self.profile_storage = ProfileStorage(db_connection_string, file_storage_path)
        
        # Ensure required database tables exist
        self._initialize_database()
        
        logger.info("Analysis coordinator initialized")
    
    def _initialize_database(self) -> None:
        """Initialize required database tables."""
        try:
            # Create member profiles table
            create_member_profiles_table(self.db_connection_string)
            
            # Ensure other required tables exist
            self._create_analysis_tables()
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def _create_analysis_tables(self) -> None:
        """Create additional analysis tables if they don't exist."""
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            # Create NLP analysis results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS nlp_analysis (
                    id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    results JSONB NOT NULL,
                    confidence_score NUMERIC(3,2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indices
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_nlp_analysis_entity 
                ON nlp_analysis (entity_type, entity_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_nlp_analysis_type 
                ON nlp_analysis (analysis_type)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_nlp_analysis_confidence 
                ON nlp_analysis (confidence_score DESC)
            """)
            
            db_conn.commit()
            cursor.close()
            db_conn.close()
            
        except Exception as e:
            logger.error(f"Error creating analysis tables: {e}")
            raise
    
    def analyze_person(self, person_id: str) -> Dict[str, Any]:
        """
        Perform complete analysis for a person.
        
        Args:
            person_id: Person ID
            
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Performing complete analysis for person {person_id}")
        
        results = {
            'person_id': person_id,
            'profile': None,
            'discrepancies': [],
            'nlp_analysis': {},
            'timestamp': datetime.now()
        }
        
        try:
            # Generate profile
            profile = self.profile_generator.generate_profile(person_id)
            if profile:
                results['profile'] = profile
                # Save profile
                self.profile_storage.save_profile(profile)
            
            # Detect discrepancies
            discrepancies = self.discrepancy_detector.detect_discrepancies_for_person(person_id)
            results['discrepancies'] = discrepancies
            
            # Perform NLP analysis on recent statements
            statements = self._get_recent_statements(person_id, 50)
            nlp_results = self._analyze_statements_nlp(statements)
            results['nlp_analysis'] = nlp_results
            
            # Store NLP analysis results
            self._store_nlp_analysis(person_id, nlp_results)
            
            logger.info(f"Completed analysis for person {person_id}")
            
        except Exception as e:
            logger.error(f"Error analyzing person {person_id}: {e}")
            raise
        
        return results
    
    def _get_recent_statements(self, person_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent statements for a person.
        
        Args:
            person_id: Person ID
            limit: Maximum number of statements
            
        Returns:
            List of statement dictionaries
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
                LIMIT %s
            """, (person_id, limit))
            
            rows = cursor.fetchall()
            cursor.close()
            db_conn.close()
            
            for row in rows:
                statement = {
                    'id': row[0],
                    'content': row[1],
                    'posted_at': row[2],
                    'platform': row[3],
                    'url': row[4],
                    'likes': row[5] or 0,
                    'shares': row[6] or 0,
                    'comments': row[7] or 0,
                    'sentiment_score': float(row[8]) if row[8] else None
                }
                statements.append(statement)
            
        except Exception as e:
            logger.error(f"Error getting recent statements for person {person_id}: {e}")
            raise
        
        return statements
    
    def _analyze_statements_nlp(self, statements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform NLP analysis on statements.
        
        Args:
            statements: List of statements
            
        Returns:
            Dictionary with NLP analysis results
        """
        nlp_results = {
            'total_statements': len(statements),
            'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
            'top_topics': {},
            'engagement_metrics': {
                'total_likes': 0,
                'total_shares': 0,
                'total_comments': 0,
                'avg_sentiment_score': 0.0
            }
        }
        
        total_sentiment_score = 0.0
        sentiment_count = 0
        
        for statement in statements:
            content = statement.get('content', '')
            if not content:
                continue
            
            # Analyze sentiment
            sentiment = self.nlp_analyzer.analyze_sentiment(content)
            
            # Update sentiment distribution
            nlp_results['sentiment_distribution'][sentiment.sentiment] += 1
            
            # Update average sentiment score
            if sentiment.sentiment != 'neutral':
                total_sentiment_score += sentiment.confidence
                sentiment_count += 1
            
            # Extract topics
            topics = self.nlp_analyzer.extract_topics(content)
            for topic, probability in topics.topics:
                if topic != 'unknown':
                    if topic in nlp_results['top_topics']:
                        nlp_results['top_topics'][topic] += probability
                    else:
                        nlp_results['top_topics'][topic] = probability
            
            # Update engagement metrics
            nlp_results['engagement_metrics']['total_likes'] += statement.get('likes', 0)
            nlp_results['engagement_metrics']['total_shares'] += statement.get('shares', 0)
            nlp_results['engagement_metrics']['total_comments'] += statement.get('comments', 0)
        
        # Calculate averages
        if sentiment_count > 0:
            nlp_results['engagement_metrics']['avg_sentiment_score'] = total_sentiment_score / sentiment_count
        
        # Sort topics by total probability
        nlp_results['top_topics'] = dict(
            sorted(nlp_results['top_topics'].items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        return nlp_results
    
    def _store_nlp_analysis(self, person_id: str, nlp_results: Dict[str, Any]) -> None:
        """
        Store NLP analysis results in the database.
        
        Args:
            person_id: Person ID
            nlp_results: NLP analysis results
        """
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            # Create analysis ID
            analysis_id = f"nlp-{person_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            cursor.execute("""
                INSERT INTO nlp_analysis (id, entity_type, entity_id, analysis_type, results, confidence_score, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    results = EXCLUDED.results,
                    confidence_score = EXCLUDED.confidence_score,
                    updated_at = EXCLUDED.updated_at
            """, (
                analysis_id,
                'person',
                person_id,
                'social_media_overview',
                Json(nlp_results),
                0.9,  # High confidence for overview analysis
                datetime.now(),
                datetime.now()
            ))
            
            db_conn.commit()
            cursor.close()
            db_conn.close()
            
        except Exception as e:
            logger.error(f"Error storing NLP analysis for person {person_id}: {e}")
            raise
    
    def analyze_all_people(self, limit: Optional[int] = None) -> Dict[str, Dict[str, Any]]:
        """
        Perform complete analysis for all people in the database.
        
        Args:
            limit: Optional limit on number of people to analyze
            
        Returns:
            Dictionary mapping person IDs to analysis results
        """
        logger.info("Performing complete analysis for all people")
        
        results = {}
        
        try:
            # Get all person IDs
            person_ids = self.profile_generator.get_all_person_ids()
            
            if limit:
                person_ids = person_ids[:limit]
            
            logger.info(f"Analyzing {len(person_ids)} people")
            
            # Analyze each person
            for i, person_id in enumerate(person_ids):
                try:
                    logger.info(f"Analyzing person {i+1}/{len(person_ids)}: {person_id}")
                    result = self.analyze_person(person_id)
                    results[person_id] = result
                except Exception as e:
                    logger.error(f"Error analyzing person {person_id}: {e}")
                    continue
            
            logger.info(f"Completed analysis for {len(results)} people")
            
        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            raise
        
        return results
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all analysis activities.
        
        Returns:
            Dictionary with analysis summary statistics
        """
        summary = {
            'total_people_analyzed': 0,
            'total_discrepancies_found': 0,
            'total_profiles_generated': 0,
            'nlp_analyses_performed': 0,
            'avg_profile_score': 0.0,
            'top_issues': [],
            'recent_activity': {}
        }
        
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            # Get total people with profiles
            cursor.execute("SELECT COUNT(*) FROM member_profiles")
            summary['total_profiles_generated'] = cursor.fetchone()[0]
            
            # Get average profile score
            cursor.execute("SELECT AVG(profile_score) FROM member_profiles")
            avg_score = cursor.fetchone()[0]
            summary['avg_profile_score'] = float(avg_score) if avg_score else 0.0
            
            # Get total discrepancies
            cursor.execute("SELECT COUNT(*) FROM discrepancies WHERE resolved = FALSE")
            summary['total_discrepancies_found'] = cursor.fetchone()[0]
            
            # Get total NLP analyses
            cursor.execute("SELECT COUNT(*) FROM nlp_analysis")
            summary['nlp_analyses_performed'] = cursor.fetchone()[0]
            
            # Get people with profiles
            cursor.execute("SELECT COUNT(DISTINCT person_id) FROM member_profiles")
            summary['total_people_analyzed'] = cursor.fetchone()[0]
            
            # Get top issues from discrepancies
            cursor.execute("""
                SELECT issue, COUNT(*) as count
                FROM discrepancies
                WHERE resolved = FALSE
                GROUP BY issue
                ORDER BY count DESC
                LIMIT 10
            """)
            summary['top_issues'] = [{'issue': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            # Get recent activity
            cursor.execute("""
                SELECT 
                    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '1 day') as today_profiles,
                    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '7 days') as week_profiles,
                    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '30 days') as month_profiles
                FROM member_profiles
            """)
            row = cursor.fetchone()
            summary['recent_activity'] = {
                'today': row[0],
                'week': row[1],
                'month': row[2]
            }
            
            cursor.close()
            db_conn.close()
            
        except Exception as e:
            logger.error(f"Error getting analysis summary: {e}")
            raise
        
        return summary
    
    def schedule_regular_analysis(self) -> None:
        """
        Schedule regular analysis tasks.
        
        This method would typically be called by a scheduler to perform
        regular updates and analysis.
        """
        logger.info("Scheduling regular analysis tasks")
        
        try:
            # Get people who need profile updates (not updated in last 7 days)
            people_to_update = self._get_people_needing_updates(days=7)
            
            logger.info(f"Found {len(people_to_update)} people needing profile updates")
            
            # Update profiles for these people
            for person_id in people_to_update:
                try:
                    self.analyze_person(person_id)
                except Exception as e:
                    logger.error(f"Error updating profile for person {person_id}: {e}")
                    continue
            
            # Detect new discrepancies
            self._detect_new_discrepancies()
            
            logger.info("Completed scheduled analysis tasks")
            
        except Exception as e:
            logger.error(f"Error in scheduled analysis: {e}")
            raise
    
    def _get_people_needing_updates(self, days: int = 7) -> List[str]:
        """
        Get list of people whose profiles need updates.
        
        Args:
            days: Number of days since last update
            
        Returns:
            List of person IDs
        """
        person_ids = []
        
        try:
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            cursor.execute("""
                SELECT person_id
                FROM member_profiles
                WHERE updated_at < NOW() - INTERVAL '%s days'
                ORDER BY updated_at ASC
            """, (days,))
            
            rows = cursor.fetchall()
            person_ids = [row[0] for row in rows]
            
            cursor.close()
            db_conn.close()
            
        except Exception as e:
            logger.error(f"Error getting people needing updates: {e}")
            raise
        
        return person_ids
    
    def _detect_new_discrepancies(self) -> None:
        """
        Detect new discrepancies that may have emerged from recent data.
        """
        logger.info("Detecting new discrepancies")
        
        try:
            # Get people with recent activity (new votes or statements in last 3 days)
            db_conn = psycopg2.connect(self.db_connection_string)
            cursor = db_conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT person_id
                FROM (
                    SELECT DISTINCT vd.person_id
                    FROM vote_details vd
                    JOIN votes v ON vd.vote_id = v.id
                    WHERE v.date > NOW() - INTERVAL '3 days'
                    
                    UNION
                    
                    SELECT DISTINCT person_id
                    FROM social_media_posts
                    WHERE posted_at > NOW() - INTERVAL '3 days'
                ) recent_activity
            """)
            
            rows = cursor.fetchall()
            active_person_ids = [row[0] for row in rows]
            
            cursor.close()
            db_conn.close()
            
            logger.info(f"Checking for new discrepancies for {len(active_person_ids)} active people")
            
            # Check for discrepancies for these people
            for person_id in active_person_ids:
                try:
                    self.discrepancy_detector.detect_discrepancies_for_person(person_id)
                except Exception as e:
                    logger.error(f"Error detecting discrepancies for person {person_id}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error detecting new discrepancies: {e}")
            raise

# Example usage
if __name__ == "__main__":
    # Example of how to use the analysis coordinator
    # coordinator = AnalysisCoordinator(
    #     db_connection_string="postgresql://user:password@localhost/opendiscourse",
    #     file_storage_path="/path/to/profile/files"
    # )
    # 
    # # Analyze a specific person
    # results = coordinator.analyze_person("person-123")
    # print(f"Analysis results: {results}")
    # 
    # # Get analysis summary
    # summary = coordinator.get_analysis_summary()
    # print(f"Analysis summary: {summary}")
    # 
    # # Schedule regular analysis
    # coordinator.schedule_regular_analysis()
    pass