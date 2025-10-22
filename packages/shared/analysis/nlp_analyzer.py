"""
NLP Analysis Module

This module provides natural language processing capabilities for analyzing
government documents and social media content.
"""

import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import json

# Add the project root to the path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SentimentAnalysisResult:
    """Result of sentiment analysis."""
    sentiment: str  # 'positive', 'negative', 'neutral'
    confidence: float  # 0.0 - 1.0
    positive_score: float
    negative_score: float
    neutral_score: float

@dataclass
class TopicModelingResult:
    """Result of topic modeling."""
    topics: List[Tuple[str, float]]  # List of (topic, probability) tuples
    dominant_topic: str
    topic_diversity: float  # 0.0 - 1.0

@dataclass
class EntityExtractionResult:
    """Result of entity extraction."""
    people: List[str]
    organizations: List[str]
    locations: List[str]
    dates: List[str]
    policy_areas: List[str]

@dataclass
class DiscrepancyEvidence:
    """Evidence for a discrepancy finding."""
    text_snippet: str
    source_type: str  # 'vote', 'statement', 'bill'
    source_id: str
    relevance_score: float  # 0.0 - 1.0

@dataclass
class DiscrepancyFinding:
    """A discrepancy finding between voting behavior and public statements."""
    id: str
    person_id: str
    issue: str
    vote_position: str  # 'yes', 'no', 'abstain', 'not voting'
    statement_position: str  # 'positive', 'negative', 'neutral', 'mixed'
    confidence_score: float  # 0.0 - 1.0
    evidence: List[DiscrepancyEvidence]
    created_at: datetime = datetime.now()
    resolved: bool = False
    resolution_notes: Optional[str] = None

class NLPAnalyzer:
    """Provides NLP analysis capabilities for government data."""
    
    def __init__(self):
        """Initialize the NLP analyzer."""
        # In a real implementation, this would load NLP models
        # For now, we'll use rule-based approaches for demonstration
        logger.info("NLP analyzer initialized")
    
    def analyze_sentiment(self, text: str) -> SentimentAnalysisResult:
        """
        Analyze the sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            SentimentAnalysisResult object
        """
        if not text or not isinstance(text, str):
            return SentimentAnalysisResult(
                sentiment='neutral',
                confidence=0.0,
                positive_score=0.0,
                negative_score=0.0,
                neutral_score=1.0
            )
        
        # Simplified sentiment analysis using keyword matching
        # In a real implementation, this would use a proper NLP model
        
        text_lower = text.lower()
        
        # Positive keywords
        positive_keywords = [
            'support', 'endorse', 'approve', 'favor', 'agree', 'back', 'promote',
            'help', 'benefit', 'improve', 'strengthen', 'protect', 'defend',
            'good', 'great', 'excellent', 'wonderful', 'fantastic', 'amazing'
        ]
        
        # Negative keywords
        negative_keywords = [
            'oppose', 'reject', 'disapprove', 'against', 'disagree', 'fight',
            'harm', 'damage', 'hurt', 'threaten', 'danger', 'risk', 'problem',
            'bad', 'terrible', 'awful', 'horrible', 'disappointing', 'worst'
        ]
        
        # Count keyword matches
        positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
        negative_count = sum(1 for keyword in negative_keywords if keyword in text_lower)
        
        # Calculate scores
        total_keywords = positive_count + negative_count
        if total_keywords == 0:
            return SentimentAnalysisResult(
                sentiment='neutral',
                confidence=0.5,
                positive_score=0.33,
                negative_score=0.33,
                neutral_score=0.34
            )
        
        positive_score = positive_count / total_keywords
        negative_score = negative_count / total_keywords
        neutral_score = 1.0 - (positive_score + negative_score)
        
        # Determine sentiment
        if positive_score > negative_score and positive_score > neutral_score:
            sentiment = 'positive'
            confidence = positive_score
        elif negative_score > positive_score and negative_score > neutral_score:
            sentiment = 'negative'
            confidence = negative_score
        else:
            sentiment = 'neutral'
            confidence = neutral_score
        
        return SentimentAnalysisResult(
            sentiment=sentiment,
            confidence=confidence,
            positive_score=positive_score,
            negative_score=negative_score,
            neutral_score=neutral_score
        )
    
    def extract_topics(self, text: str) -> TopicModelingResult:
        """
        Extract topics from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            TopicModelingResult object
        """
        if not text or not isinstance(text, str):
            return TopicModelingResult(
                topics=[('unknown', 1.0)],
                dominant_topic='unknown',
                topic_diversity=0.0
            )
        
        # Simplified topic extraction using keyword categories
        # In a real implementation, this would use topic modeling algorithms
        
        text_lower = text.lower()
        
        # Topic keywords
        topic_keywords = {
            'healthcare': ['health', 'medical', 'hospital', 'doctor', 'patient', 'insurance', 'medicare', 'medicaid'],
            'education': ['school', 'student', 'teacher', 'college', 'university', 'education', 'learning', 'curriculum'],
            'economy': ['economy', 'job', 'employment', 'business', 'company', 'worker', 'income', 'tax'],
            'environment': ['environment', 'climate', 'pollution', 'green', 'sustainable', 'renewable', 'carbon', 'energy'],
            'security': ['security', 'defense', 'military', 'army', 'navy', 'air force', 'protection', 'safety'],
            'infrastructure': ['infrastructure', 'road', 'bridge', 'highway', 'transportation', 'construction', 'building'],
            'immigration': ['immigration', 'immigrant', 'border', 'visa', 'citizenship', 'deportation', 'asylum'],
            'criminal_justice': ['crime', 'criminal', 'police', 'law', 'court', 'justice', 'prison', 'sentence']
        }
        
        # Count matches for each topic
        topic_scores = {}
        total_matches = 0
        
        for topic, keywords in topic_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            topic_scores[topic] = matches
            total_matches += matches
        
        # Convert to probabilities
        topics = []
        if total_matches > 0:
            for topic, count in topic_scores.items():
                if count > 0:
                    probability = count / total_matches
                    topics.append((topic, probability))
            
            # Sort by probability
            topics.sort(key=lambda x: x[1], reverse=True)
            
            # Dominant topic
            dominant_topic = topics[0][0] if topics else 'unknown'
            
            # Topic diversity (number of topics with significant probability)
            significant_topics = [t for t, p in topics if p > 0.1]
            topic_diversity = min(1.0, len(significant_topics) / len(topic_keywords))
            
        else:
            topics = [('unknown', 1.0)]
            dominant_topic = 'unknown'
            topic_diversity = 0.0
        
        return TopicModelingResult(
            topics=topics,
            dominant_topic=dominant_topic,
            topic_diversity=topic_diversity
        )
    
    def extract_entities(self, text: str) -> EntityExtractionResult:
        """
        Extract entities from text.
        
        Args:
            text: Text to analyze
            
        Returns:
            EntityExtractionResult object
        """
        if not text or not isinstance(text, str):
            return EntityExtractionResult(
                people=[],
                organizations=[],
                locations=[],
                dates=[],
                policy_areas=[]
            )
        
        # Simplified entity extraction using regex patterns
        # In a real implementation, this would use NER models
        
        text_lower = text.lower()
        
        # Extract potential people names (simplified)
        people = []
        # Look for patterns like "Senator Smith" or "Representative Johnson"
        people_patterns = [
            r'senator\s+([a-z]+)',
            r'representative\s+([a-z]+)',
            r'congressman\s+([a-z]+)',
            r'congresswoman\s+([a-z]+)',
            r'governor\s+([a-z]+)'
        ]
        
        for pattern in people_patterns:
            matches = re.findall(pattern, text_lower)
            people.extend(matches)
        
        # Extract potential organizations
        organizations = []
        org_patterns = [
            r'\b(federal|state|local)\s+(government|agency|department)\b',
            r'\b(congress|senate|house)\b',
            r'\b(white house|supreme court)\b',
            r'\b(american|national|united)\s+[a-z]+\s+(association|organization|union|league)\b'
        ]
        
        for pattern in org_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                if isinstance(matches[0], tuple):
                    organizations.extend([' '.join(match) for match in matches])
                else:
                    organizations.extend(matches)
        
        # Extract potential locations
        locations = []
        location_patterns = [
            r'\b(new york|california|texas|florida|illinois|pennsylvania|ohio|michigan|georgia|north carolina|new jersey|virginia|washington|arizona|massachusetts|tennessee|indiana|missouri|maryland|wisconsin|minnesota|colorado|alabama|south carolina|louisiana|kentucky|oregon|oklahoma|connecticut|iowa|utah|nevada|arkansas|mississippi|kansas|new mexico|nebraska|west virginia|idaho|hawaii|new hampshire|maine|montana|rhode island|delaware|south dakota|north dakota|alaska|vermont|wyoming)\b',
            r'\b(washington\s+d\.?c\.?|district\s+of\s+columbia)\b'
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text_lower)
            locations.extend(matches)
        
        # Extract potential dates
        dates = []
        date_patterns = [
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4}\b',
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',
            r'\b\d{4}-\d{2}-\d{2}\b'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text_lower)
            dates.extend(matches)
        
        # Extract policy areas from topics
        topics_result = self.extract_topics(text)
        policy_areas = [topic for topic, _ in topics_result.topics if topic != 'unknown']
        
        return EntityExtractionResult(
            people=list(set(people)),
            organizations=list(set(organizations)),
            locations=list(set(locations)),
            dates=list(set(dates)),
            policy_areas=policy_areas
        )
    
    def analyze_statement_content(self, statement_text: str) -> Dict[str, Any]:
        """
        Comprehensive analysis of a statement's content.
        
        Args:
            statement_text: Text of the statement
            
        Returns:
            Dictionary with analysis results
        """
        if not statement_text or not isinstance(statement_text, str):
            return {
                'sentiment': None,
                'topics': None,
                'entities': None,
                'key_phrases': [],
                'tone_indicators': []
            }
        
        # Perform all analyses
        sentiment = self.analyze_sentiment(statement_text)
        topics = self.extract_topics(statement_text)
        entities = self.extract_entities(statement_text)
        
        # Extract key phrases (simplified)
        key_phrases = []
        # Look for phrases in quotes
        quoted_phrases = re.findall(r'"([^"]*)"', statement_text)
        key_phrases.extend(quoted_phrases)
        
        # Look for policy-related phrases
        policy_phrases = [
            'my position', 'I believe', 'I support', 'I oppose', 'we must',
            'we should', 'it is important', 'we need', 'this will help'
        ]
        for phrase in policy_phrases:
            if phrase in statement_text.lower():
                key_phrases.append(phrase)
        
        # Identify tone indicators
        tone_indicators = []
        tone_keywords = {
            'assertive': ['must', 'will', 'certainly', 'definitely'],
            'cautious': ['may', 'might', 'possibly', 'perhaps'],
            'emphatic': ['absolutely', 'clearly', 'obviously', 'undoubtedly'],
            'concerned': ['worried', 'concerned', 'troubled', 'alarmed'],
            'optimistic': ['hope', 'believe', 'confident', 'positive']
        }
        
        text_lower = statement_text.lower()
        for tone, keywords in tone_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                tone_indicators.append(tone)
        
        return {
            'sentiment': sentiment,
            'topics': topics,
            'entities': entities,
            'key_phrases': list(set(key_phrases)),
            'tone_indicators': tone_indicators
        }
    
    def compare_positions(self, vote_position: str, statement_sentiment: SentimentAnalysisResult) -> Tuple[str, float]:
        """
        Compare a voting position with statement sentiment to identify consistency.
        
        Args:
            vote_position: Voting position ('yes', 'no', 'abstain', 'not voting')
            statement_sentiment: Sentiment analysis result of statement
            
        Returns:
            Tuple of (consistency_label, confidence_score)
        """
        # Map vote positions to sentiment expectations
        vote_sentiment_mapping = {
            'yes': 'positive',
            'no': 'negative',
            'abstain': 'neutral',
            'not voting': 'neutral'
        }
        
        expected_sentiment = vote_sentiment_mapping.get(vote_position, 'neutral')
        actual_sentiment = statement_sentiment.sentiment
        
        # Calculate consistency
        if expected_sentiment == actual_sentiment:
            consistency = 'consistent'
            confidence = statement_sentiment.confidence
        elif expected_sentiment == 'neutral' or actual_sentiment == 'neutral':
            consistency = 'neutral'
            confidence = 0.5
        else:
            consistency = 'inconsistent'
            confidence = statement_sentiment.confidence
        
        return (consistency, confidence)

# Example usage
if __name__ == "__main__":
    # Example of how to use the NLP analyzer
    # analyzer = NLPAnalyzer()
    # 
    # # Analyze sample text
    # sample_text = "I strongly support this healthcare legislation that will benefit millions of Americans."
    # 
    # sentiment = analyzer.analyze_sentiment(sample_text)
    # print(f"Sentiment: {sentiment}")
    # 
    # topics = analyzer.extract_topics(sample_text)
    # print(f"Topics: {topics}")
    # 
    # entities = analyzer.extract_entities(sample_text)
    # print(f"Entities: {entities}")
    # 
    # # Compare positions
    # consistency, confidence = analyzer.compare_positions('yes', sentiment)
    # print(f"Consistency: {consistency}, Confidence: {confidence}")
    pass