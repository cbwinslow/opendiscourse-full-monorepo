# Working Examples: NLP for Legislative and Political Analysis

## Overview
This document provides concrete, working examples of how to apply NLP techniques to legislative documents and political content using various tools and models.

## Example 1: Bill Similarity Analysis with Sentence-BERT

### Installation Requirements
```bash
pip install sentence-transformers scikit-learn numpy pandas
```

### Implementation Code
```python
"""
Bill Similarity Analysis using Sentence-BERT
This example demonstrates how to find similar bills using semantic embeddings.
"""

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd

class BillSimilarityAnalyzer:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the analyzer with a Sentence-BERT model.
        
        Args:
            model_name (str): Name of the Sentence-BERT model to use
        """
        self.model = SentenceTransformer(model_name)
        print(f"Loaded model: {model_name}")
    
    def create_bill_embeddings(self, bills):
        """
        Create embeddings for a collection of bills.
        
        Args:
            bills (list): List of bill dictionaries with 'id', 'title', 'summary' keys
            
        Returns:
            dict: Dictionary with bill IDs as keys and embeddings as values
        """
        # Combine title and summary for richer representation
        texts = [f"{bill['title']}. {bill['summary']}" for bill in bills]
        
        # Generate embeddings
        embeddings = self.model.encode(texts)
        
        # Create mapping from bill ID to embedding
        bill_embeddings = {}
        for i, bill in enumerate(bills):
            bill_embeddings[bill['id']] = embeddings[i]
            
        return bill_embeddings
    
    def find_similar_bills(self, target_bill_id, bill_embeddings, top_k=5):
        """
        Find bills most similar to a target bill.
        
        Args:
            target_bill_id (str): ID of the target bill
            bill_embeddings (dict): Dictionary of bill embeddings
            top_k (int): Number of similar bills to return
            
        Returns:
            list: List of tuples (bill_id, similarity_score)
        """
        if target_bill_id not in bill_embeddings:
            raise ValueError(f"Bill ID {target_bill_id} not found in embeddings")
        
        # Get target embedding
        target_embedding = bill_embeddings[target_bill_id].reshape(1, -1)
        
        # Calculate similarities with all other bills
        similarities = {}
        for bill_id, embedding in bill_embeddings.items():
            if bill_id != target_bill_id:
                similarity = cosine_similarity(target_embedding, embedding.reshape(1, -1))[0][0]
                similarities[bill_id] = similarity
        
        # Sort by similarity and return top K
        sorted_similarities = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        return sorted_similarities[:top_k]

# Example usage
if __name__ == "__main__":
    # Sample bill data (in practice, this would come from your database)
    sample_bills = [
        {
            "id": "S1234-2023",
            "title": "Relates to renewable energy standards",
            "summary": "Establishes renewable energy standards for utilities and provides incentives for solar and wind power installations"
        },
        {
            "id": "S5678-2023",
            "title": "Relates to solar energy incentives",
            "summary": "Provides tax incentives for residential and commercial solar energy installations and establishes rebate programs"
        },
        {
            "id": "S9012-2023",
            "title": "Relates to education funding",
            "summary": "Increases funding for public education and establishes new teacher training programs"
        },
        {
            "id": "S3456-2023",
            "title": "Relates to wind energy development",
            "summary": "Encourages wind energy development through regulatory streamlining and financial incentives"
        },
        {
            "id": "S7890-2023",
            "title": "Relates to teacher salary increases",
            "summary": "Provides funding for teacher salary increases and establishes performance-based pay systems"
        }
    ]
    
    # Initialize analyzer
    analyzer = BillSimilarityAnalyzer()
    
    # Create embeddings
    print("Creating bill embeddings...")
    bill_embeddings = analyzer.create_bill_embeddings(sample_bills)
    
    # Find similar bills to S1234-2023 (renewable energy bill)
    print("\nFinding bills similar to S1234-2023...")
    similar_bills = analyzer.find_similar_bills("S1234-2023", bill_embeddings)
    
    print("Similar bills:")
    for bill_id, similarity in similar_bills:
        bill = next(b for b in sample_bills if b["id"] == bill_id)
        print(f"  {bill_id}: {similarity:.3f} - {bill['title']}")
```

## Example 2: Legal Entity Recognition with Blackstone

### Installation Requirements
```bash
pip install spacy
python -m spacy download en_core_web_sm
# Note: Blackstone needs to be installed from source or specific repository
```

### Implementation Code
```python
"""
Legal Entity Recognition using spaCy and Blackstone
This example demonstrates how to extract legal entities from legislative text.
"""

import spacy
import re
from collections import defaultdict

class LegalEntityExtractor:
    def __init__(self):
        """
        Initialize the legal entity extractor.
        Note: This example uses a general spaCy model. For production use,
        you would use the Blackstone model specifically designed for legal text.
        """
        try:
            # Try to load Blackstone model first
            self.nlp = spacy.load("en_blackstone_proto")
            print("Loaded Blackstone model")
        except OSError:
            # Fallback to general model for demonstration
            self.nlp = spacy.load("en_core_web_sm")
            print("Loaded general spaCy model (Blackstone not available)")
    
    def extract_legal_entities(self, text):
        """
        Extract legal entities from text.
        
        Args:
            text (str): Legal text to analyze
            
        Returns:
            dict: Dictionary of entity types and their occurrences
        """
        doc = self.nlp(text)
        
        entities = defaultdict(list)
        for ent in doc.ents:
            entities[ent.label_].append({
                "text": ent.text,
                "start": ent.start_char,
                "end": ent.end_char
            })
        
        return dict(entities)
    
    def extract_citations(self, text):
        """
        Extract legal citations from text using regex patterns.
        
        Args:
            text (str): Legal text to analyze
            
        Returns:
            list: List of citation matches
        """
        # Common citation patterns
        citation_patterns = [
            r'\b\d+\s+[Uu]\.?[Ss]\.?[Cc]\.?\s+§?\s*\d+[a-zA-Z]*\b',  # US Code
            r'\b\d+\s+[Uu]\.?[Ss]\.?[Cc]\.?\s+\d+\s+[Uu]\.?[Ss]\.?\s*\d+\b',  # USC citations
            r'\b\d+\s+F\.\d+d?\s+\d+\b',  # Federal Reporter
            r'\b\d+\s+S\.\d+d?\s+\d+\b',  # Supreme Court Reporter
        ]
        
        citations = []
        for pattern in citation_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                citations.append({
                    "text": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "type": "citation"
                })
        
        return citations
    
    def extract_legislative_references(self, text):
        """
        Extract references to legislative acts and sections.
        
        Args:
            text (str): Legislative text to analyze
            
        Returns:
            dict: Dictionary of legislative references
        """
        # Patterns for legislative acts
        act_pattern = r'\b[A-Z][a-zA-Z\s]+Act\s+(?:of\s+)?\d{4}\b'
        section_pattern = r'\b(?:section|§)\s*\d+[a-zA-Z]*\b'
        subsection_pattern = r'\b(?:subsection|paragraph)\s*\([^)]+\)\b'
        
        acts = re.findall(act_pattern, text)
        sections = re.findall(section_pattern, text)
        subsections = re.findall(subsection_pattern, text)
        
        return {
            "acts": acts,
            "sections": sections,
            "subsections": subsections
        }

# Example usage
if __name__ == "__main__":
    # Sample legislative text
    sample_text = """
    The Environmental Protection Act of 1970, as amended by section 12 of the 
    Clean Air Act Amendments of 1990, requires the Administrator of the 
    Environmental Protection Agency to establish standards under 42 U.S.C. § 7401 
    for the protection of public health and welfare. Pursuant to section 108 of 
    the Act, the EPA has promulgated regulations found at 40 C.F.R. Part 50.
    """
    
    # Initialize extractor
    extractor = LegalEntityExtractor()
    
    # Extract entities
    print("Extracting legal entities...")
    entities = extractor.extract_legal_entities(sample_text)
    for entity_type, entity_list in entities.items():
        print(f"  {entity_type}: {[e['text'] for e in entity_list]}")
    
    # Extract citations
    print("\nExtracting citations...")
    citations = extractor.extract_citations(sample_text)
    for citation in citations:
        print(f"  {citation['text']}")
    
    # Extract legislative references
    print("\nExtracting legislative references...")
    references = extractor.extract_legislative_references(sample_text)
    for ref_type, ref_list in references.items():
        print(f"  {ref_type}: {ref_list}")
```

## Example 3: Sentiment Analysis for Political Statements

### Installation Requirements
```bash
pip install vaderSentiment textblob transformers torch
```

### Implementation Code
```python
"""
Sentiment Analysis for Political Statements
This example demonstrates multiple approaches to sentiment analysis for political content.
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from transformers import pipeline
import pandas as pd

class PoliticalSentimentAnalyzer:
    def __init__(self):
        """
        Initialize sentiment analyzers.
        """
        # VADER for social media text
        self.vader_analyzer = SentimentIntensityAnalyzer()
        
        # TextBlob for general sentiment
        # BERT-based model for contextual sentiment (optional, requires more resources)
        try:
            self.bert_analyzer = pipeline("sentiment-analysis", 
                                        model="cardiffnlp/twitter-roberta-base-sentiment-latest")
            print("Loaded BERT-based sentiment analyzer")
        except Exception as e:
            self.bert_analyzer = None
            print("BERT analyzer not available, using fallback methods")
    
    def analyze_with_vader(self, text):
        """
        Analyze sentiment using VADER.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Sentiment scores
        """
        scores = self.vader_analyzer.polarity_scores(text)
        return {
            "method": "VADER",
            "compound": scores["compound"],
            "positive": scores["pos"],
            "neutral": scores["neu"],
            "negative": scores["neg"],
            "sentiment": self._classify_sentiment(scores["compound"])
        }
    
    def analyze_with_textblob(self, text):
        """
        Analyze sentiment using TextBlob.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Sentiment scores
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        return {
            "method": "TextBlob",
            "polarity": polarity,
            "subjectivity": subjectivity,
            "sentiment": self._classify_sentiment(polarity)
        }
    
    def analyze_with_bert(self, text):
        """
        Analyze sentiment using BERT-based model.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Sentiment scores
        """
        if self.bert_analyzer is None:
            return {"method": "BERT", "error": "Model not available"}
        
        try:
            result = self.bert_analyzer(text)[0]
            return {
                "method": "BERT",
                "label": result["label"],
                "score": result["score"],
                "sentiment": result["label"].replace("LABEL_", "").lower()
            }
        except Exception as e:
            return {"method": "BERT", "error": str(e)}
    
    def _classify_sentiment(self, score):
        """
        Classify sentiment based on score.
        
        Args:
            score (float): Sentiment score
            
        Returns:
            str: Sentiment classification
        """
        if score > 0.05:
            return "positive"
        elif score < -0.05:
            return "negative"
        else:
            return "neutral"
    
    def comprehensive_analysis(self, text):
        """
        Perform comprehensive sentiment analysis using multiple methods.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Results from all analyzers
        """
        results = {}
        results["VADER"] = self.analyze_with_vader(text)
        results["TextBlob"] = self.analyze_with_textblob(text)
        if self.bert_analyzer:
            results["BERT"] = self.analyze_with_bert(text)
        
        return results

# Example usage
if __name__ == "__main__":
    # Sample political statements
    sample_statements = [
        "I am proud to support this groundbreaking legislation that will protect our environment for future generations. #CleanEnergy #ClimateAction",
        "This bill is a disaster that will hurt working families and destroy our economy. We must oppose it at all costs.",
        "The committee has completed its review of the proposed amendments and will report to the full chamber next week.",
        "Healthcare is a fundamental right that every American deserves. We must expand access and lower costs for everyone.",
        "The budget proposal includes important investments in infrastructure while maintaining fiscal responsibility."
    ]
    
    # Initialize analyzer
    analyzer = PoliticalSentimentAnalyzer()
    
    # Analyze each statement
    for i, statement in enumerate(sample_statements, 1):
        print(f"\nStatement {i}: {statement}")
        print("-" * 50)
        
        results = analyzer.comprehensive_analysis(statement)
        
        for method, result in results.items():
            if "error" in result:
                print(f"  {method}: Error - {result['error']}")
            else:
                print(f"  {method}: {result}")
```

## Example 4: Politician Position Tracking

### Implementation Code
```python
"""
Politician Position Tracking System
This example demonstrates how to track and analyze politician positions over time.
"""

import json
from datetime import datetime
from collections import defaultdict
import numpy as np

class PoliticianPositionTracker:
    def __init__(self):
        """
        Initialize the position tracker.
        """
        self.politician_data = defaultdict(list)
        self.issue_positions = defaultdict(lambda: defaultdict(list))
    
    def add_voting_record(self, politician_id, bill_id, bill_title, vote, date, issues=None):
        """
        Add a voting record for a politician.
        
        Args:
            politician_id (str): Unique identifier for politician
            bill_id (str): Unique identifier for bill
            bill_title (str): Title of the bill
            vote (str): Vote position ('yes', 'no', 'abstain', 'absent')
            date (str): Date of vote (YYYY-MM-DD)
            issues (list): List of policy issues related to the bill
        """
        record = {
            "type": "vote",
            "bill_id": bill_id,
            "bill_title": bill_title,
            "position": vote,
            "date": date,
            "issues": issues or []
        }
        
        self.politician_data[politician_id].append(record)
        
        # Track positions by issue
        if issues:
            for issue in issues:
                self.issue_positions[issue][politician_id].append({
                    "bill_id": bill_id,
                    "position": vote,
                    "date": date
                })
    
    def add_public_statement(self, politician_id, content, platform, date, issues=None):
        """
        Add a public statement from a politician.
        
        Args:
            politician_id (str): Unique identifier for politician
            content (str): Content of the statement
            platform (str): Platform where statement was made (twitter, facebook, speech, etc.)
            date (str): Date of statement (YYYY-MM-DD)
            issues (list): List of policy issues addressed
        """
        record = {
            "type": "statement",
            "content": content,
            "platform": platform,
            "date": date,
            "issues": issues or []
        }
        
        self.politician_data[politician_id].append(record)
    
    def get_politician_timeline(self, politician_id):
        """
        Get chronological timeline of a politician's positions.
        
        Args:
            politician_id (str): Unique identifier for politician
            
        Returns:
            list: Chronologically sorted list of positions
        """
        timeline = self.politician_data[politician_id]
        return sorted(timeline, key=lambda x: x["date"])
    
    def analyze_issue_position(self, politician_id, issue):
        """
        Analyze a politician's position on a specific issue.
        
        Args:
            politician_id (str): Unique identifier for politician
            issue (str): Policy issue to analyze
            
        Returns:
            dict: Analysis of position consistency and evolution
        """
        # Get all records related to this issue
        issue_records = []
        for record in self.politician_data[politician_id]:
            if issue in record.get("issues", []):
                issue_records.append(record)
        
        if not issue_records:
            return {"error": f"No records found for {politician_id} on {issue}"}
        
        # Separate votes and statements
        votes = [r for r in issue_records if r["type"] == "vote"]
        statements = [r for r in issue_records if r["type"] == "statement"]
        
        # Analyze voting pattern
        vote_positions = [v["position"] for v in votes if v["position"] in ["yes", "no"]]
        if vote_positions:
            yes_votes = vote_positions.count("yes")
            no_votes = vote_positions.count("no")
            vote_consistency = abs(yes_votes - no_votes) / len(vote_positions)
        else:
            vote_consistency = None
        
        return {
            "politician_id": politician_id,
            "issue": issue,
            "total_records": len(issue_records),
            "votes": len(votes),
            "statements": len(statements),
            "vote_breakdown": {
                "yes": vote_positions.count("yes"),
                "no": vote_positions.count("no"),
                "abstain/absent": len(votes) - len(vote_positions)
            },
            "vote_consistency": vote_consistency,
            "timeline": sorted(issue_records, key=lambda x: x["date"])
        }
    
    def find_position_discrepancies(self, politician_id, issue):
        """
        Find discrepancies between voting records and public statements.
        
        Args:
            politician_id (str): Unique identifier for politician
            issue (str): Policy issue to analyze
            
        Returns:
            list: List of potential discrepancies
        """
        # This is a simplified example - in practice, you would use NLP
        # to analyze the sentiment and content of statements
        discrepancies = []
        
        # Get all records for this politician and issue
        records = self.get_politician_timeline(politician_id)
        issue_records = [r for r in records if issue in r.get("issues", [])]
        
        # Simple discrepancy detection (in practice, use NLP sentiment analysis)
        for record in issue_records:
            # This is a placeholder - real implementation would analyze content
            if record["type"] == "statement":
                # Simulate sentiment analysis
                content = record["content"].lower()
                if "support" in content or "favor" in content:
                    statement_sentiment = "support"
                elif "oppose" in content or "against" in content:
                    statement_sentiment = "oppose"
                else:
                    statement_sentiment = "neutral"
                
                record["analyzed_sentiment"] = statement_sentiment
        
        return issue_records

# Example usage
if __name__ == "__main__":
    # Initialize tracker
    tracker = PoliticianPositionTracker()
    
    # Add sample voting records
    tracker.add_voting_record(
        politician_id="senator_smith",
        bill_id="S1234",
        bill_title="Renewable Energy Standards Act",
        vote="yes",
        date="2023-03-15",
        issues=["environment", "energy"]
    )
    
    tracker.add_voting_record(
        politician_id="senator_smith",
        bill_id="S5678",
        bill_title="Tax Relief for Families Act",
        vote="no",
        date="2023-04-22",
        issues=["taxes", "economy"]
    )
    
    # Add sample public statements
    tracker.add_public_statement(
        politician_id="senator_smith",
        content="I'm proud to support renewable energy initiatives that will create jobs and protect our environment",
        platform="twitter",
        date="2023-03-10",
        issues=["environment", "energy"]
    )
    
    tracker.add_public_statement(
        politician_id="senator_smith",
        content="We must oppose tax cuts that benefit the wealthy while hurting working families",
        platform="speech",
        date="2023-04-18",
        issues=["taxes", "economy"]
    )
    
    # Analyze positions
    print("Analyzing Senator Smith's position on environment issues...")
    environment_analysis = tracker.analyze_issue_position("senator_smith", "environment")
    print(json.dumps(environment_analysis, indent=2, default=str))
    
    print("\nAnalyzing Senator Smith's position on tax issues...")
    tax_analysis = tracker.analyze_issue_position("senator_smith", "taxes")
    print(json.dumps(tax_analysis, indent=2, default=str))
    
    # Check for discrepancies
    print("\nChecking for discrepancies in environment positions...")
    discrepancies = tracker.find_position_discrepancies("senator_smith", "environment")
    for record in discrepancies:
        print(f"  {record['date']} - {record['type']}: {record.get('analyzed_sentiment', 'N/A')}")
```

## Example 5: Topic Modeling for Legislative Analysis

### Installation Requirements
```bash
pip install gensim scikit-learn matplotlib
```

### Implementation Code
```python
"""
Topic Modeling for Legislative Documents
This example demonstrates how to perform topic modeling on legislative text.
"""

from gensim import corpora, models
from gensim.parsing.preprocessing import preprocess_string, strip_tags, strip_punctuation, strip_multiple_whitespaces, strip_numeric, remove_stopwords, strip_short
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
import numpy as np

class LegislativeTopicModeler:
    def __init__(self):
        """
        Initialize the topic modeler.
        """
        # Preprocessing filters
        self.filters = [
            strip_tags, 
            strip_punctuation, 
            strip_multiple_whitespaces, 
            strip_numeric, 
            remove_stopwords, 
            strip_short
        ]
        
        # Gensim LDA model
        self.lda_model = None
        self.dictionary = None
        self.corpus = None
    
    def preprocess_documents(self, documents):
        """
        Preprocess a list of documents.
        
        Args:
            documents (list): List of text documents
            
        Returns:
            list: List of preprocessed token lists
        """
        processed_docs = []
        for doc in documents:
            tokens = preprocess_string(doc, self.filters)
            processed_docs.append(tokens)
        return processed_docs
    
    def create_lda_model(self, documents, num_topics=5, passes=10):
        """
        Create an LDA topic model from documents.
        
        Args:
            documents (list): List of text documents
            num_topics (int): Number of topics to extract
            passes (int): Number of training passes
            
        Returns:
            gensim.models.LdaModel: Trained LDA model
        """
        # Preprocess documents
        processed_docs = self.preprocess_documents(documents)
        
        # Create dictionary and corpus
        self.dictionary = corpora.Dictionary(processed_docs)
        self.corpus = [self.dictionary.doc2bow(doc) for doc in processed_docs]
        
        # Train LDA model
        self.lda_model = models.LdaModel(
            corpus=self.corpus,
            id2word=self.dictionary,
            num_topics=num_topics,
            passes=passes,
            alpha='auto',
            eta='auto'
        )
        
        return self.lda_model
    
    def get_document_topics(self, document_text):
        """
        Get topic distribution for a document.
        
        Args:
            document_text (str): Text of document to analyze
            
        Returns:
            list: Topic distribution as (topic_id, probability) tuples
        """
        if self.lda_model is None:
            raise ValueError("Model not trained. Call create_lda_model first.")
        
        # Preprocess document
        processed_doc = preprocess_string(document_text, self.filters)
        
        # Convert to bag of words
        bow = self.dictionary.doc2bow(processed_doc)
        
        # Get topic distribution
        topics = self.lda_model.get_document_topics(bow)
        
        return topics
    
    def get_topic_words(self, topic_id, top_n=10):
        """
        Get the most probable words for a topic.
        
        Args:
            topic_id (int): Topic ID
            top_n (int): Number of top words to return
            
        Returns:
            list: List of (word, probability) tuples
        """
        if self.lda_model is None:
            raise ValueError("Model not trained. Call create_lda_model first.")
        
        return self.lda_model.show_topic(topic_id, top_n)
    
    def print_topics(self, num_words=10):
        """
        Print all topics with their top words.
        
        Args:
            num_words (int): Number of top words per topic
        """
        if self.lda_model is None:
            raise ValueError("Model not trained. Call create_lda_model first.")
        
        topics = self.lda_model.print_topics(num_words=num_words)
        for topic_id, topic_words in topics:
            print(f"Topic {topic_id}: {topic_words}")

# Example usage
if __name__ == "__main__":
    # Sample legislative documents
    sample_bills = [
        """
        An act to establish renewable energy standards for electric utilities in the state. 
        This legislation requires utilities to generate 50% of their electricity from 
        renewable sources by 2030, with provisions for solar, wind, and hydroelectric power. 
        The bill includes incentives for residential solar installations and establishes 
        a renewable energy credit trading system.
        """,
        """
        A bill to provide tax incentives for solar energy installations on residential 
        and commercial properties. The legislation creates a 30% tax credit for solar 
        panel installations and establishes streamlined permitting processes. The bill 
        also includes provisions for low-income households and rental properties.
        """,
        """
        An act to increase funding for public education and establish new teacher 
        training programs. This legislation provides $2 billion in additional funding 
        for K-12 education and creates professional development opportunities for 
        teachers. The bill includes provisions for special education and rural schools.
        """,
        """
        A bill to establish wind energy development zones and streamline the permitting 
        process for wind farms. The legislation identifies suitable areas for wind 
        development and reduces regulatory barriers for renewable energy projects. 
        The bill includes environmental protection measures and community benefit funds.
        """,
        """
        An act to provide funding for teacher salary increases and establish performance-based 
        pay systems. This legislation allocates resources for teacher compensation and 
        creates incentives for excellence in education. The bill includes provisions for 
        mentorship programs and career advancement opportunities.
        """,
        """
        A bill to establish clean energy standards for transportation fuels. The 
        legislation requires fuel suppliers to reduce carbon intensity and promotes 
        electric vehicle adoption. The bill includes infrastructure investments and 
        consumer incentives for clean transportation options.
        """,
        """
        An act to reform school funding formulas and ensure equitable distribution of 
        educational resources. This legislation addresses disparities in funding between 
        districts and provides additional support for high-need students. The bill 
        includes provisions for English language learners and students with disabilities.
        """,
        """
        A bill to establish energy efficiency standards for buildings and promote 
        weatherization programs. The legislation requires new construction to meet 
        energy efficiency benchmarks and provides rebates for home energy improvements. 
        The bill includes workforce development for energy efficiency contractors.
        """
    ]
    
    # Initialize modeler
    modeler = LegislativeTopicModeler()
    
    # Create LDA model
    print("Creating LDA model...")
    model = modeler.create_lda_model(sample_bills, num_topics=3, passes=15)
    
    # Print topics
    print("\nDiscovered Topics:")
    modeler.print_topics(num_words=8)
    
    # Analyze a new document
    new_bill = """
    An act to promote electric vehicle adoption through tax incentives and 
    infrastructure development. This legislation provides rebates for electric 
    vehicle purchases and establishes requirements for charging station installation 
    in new construction. The bill includes provisions for low-income consumers and 
    rural communities.
    """
    
    print(f"\nAnalyzing new bill: {new_bill[:50]}...")
    topics = modeler.get_document_topics(new_bill)
    print("Topic distribution:")
    for topic_id, probability in topics:
        print(f"  Topic {topic_id}: {probability:.3f}")
        words = modeler.get_topic_words(topic_id, 5)
        word_list = [word for word, prob in words]
        print(f"    Key words: {', '.join(word_list)}")
```

## Integration with OpenDiscourse Platform

### Example: Complete Analysis Pipeline
```python
"""
Complete Analysis Pipeline for OpenDiscourse
This example demonstrates how to integrate all NLP techniques into a complete pipeline.
"""

import json
from datetime import datetime
from typing import Dict, List, Any

class OpenDiscourseAnalyzer:
    def __init__(self):
        """
        Initialize the complete analysis pipeline.
        """
        self.bill_similarity_analyzer = BillSimilarityAnalyzer()
        self.entity_extractor = LegalEntityExtractor()
        self.sentiment_analyzer = PoliticalSentimentAnalyzer()
        self.position_tracker = PoliticianPositionTracker()
        self.topic_modeler = LegislativeTopicModeler()
    
    def analyze_legislation(self, bill_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform complete analysis of a legislative bill.
        
        Args:
            bill_data (dict): Bill data with 'id', 'title', 'summary', 'full_text'
            
        Returns:
            dict: Complete analysis results
        """
        analysis = {
            "bill_id": bill_data["id"],
            "timestamp": datetime.now().isoformat(),
            "entities": {},
            "topics": [],
            "similar_bills": [],
            "complexity_score": 0.0
        }
        
        # Extract legal entities
        full_text = f"{bill_data['title']}. {bill_data['summary']}. {bill_data.get('full_text', '')}"
        analysis["entities"] = self.entity_extractor.extract_legal_entities(full_text)
        
        # Extract citations and references
        analysis["citations"] = self.entity_extractor.extract_citations(full_text)
        analysis["references"] = self.entity_extractor.extract_legislative_references(full_text)
        
        # Analyze topics (if we have enough bills for topic modeling)
        # This would typically be done across the entire corpus
        
        # Calculate text complexity
        analysis["complexity_score"] = self._calculate_complexity(full_text)
        
        return analysis
    
    def analyze_politician(self, politician_id: str, statements: List[Dict], 
                          votes: List[Dict]) -> Dict[str, Any]:
        """
        Perform complete analysis of a politician's positions.
        
        Args:
            politician_id (str): Politician identifier
            statements (list): List of statement data
            votes (list): List of voting data
            
        Returns:
            dict: Complete analysis results
        """
        analysis = {
            "politician_id": politician_id,
            "timestamp": datetime.now().isoformat(),
            "sentiment_analysis": {},
            "position_consistency": {},
            "engagement_metrics": {},
            "topic_focus": []
        }
        
        # Analyze sentiment of statements
        statement_sentiments = []
        for statement in statements:
            sentiment = self.sentiment_analyzer.comprehensive_analysis(statement["content"])
            statement_sentiments.append({
                "statement_id": statement.get("id"),
                "content": statement["content"][:100] + "..." if len(statement["content"]) > 100 else statement["content"],
                "sentiment": sentiment
            })
        
        analysis["sentiment_analysis"] = statement_sentiments
        
        # Track positions and check consistency
        # (This would integrate with the position tracker)
        
        # Calculate engagement metrics
        analysis["engagement_metrics"] = self._calculate_engagement(statements)
        
        return analysis
    
    def _calculate_complexity(self, text: str) -> float:
        """
        Calculate text complexity score.
        
        Args:
            text (str): Text to analyze
            
        Returns:
            float: Complexity score (0-1)
        """
        # Simple complexity calculation based on sentence length and vocabulary
        sentences = text.split('.')
        if not sentences:
            return 0.0
        
        avg_sentence_length = sum(len(sentence.split()) for sentence in sentences) / len(sentences)
        
        # Count unique words
        words = text.lower().split()
        unique_words = len(set(words))
        total_words = len(words)
        vocabulary_richness = unique_words / total_words if total_words > 0 else 0
        
        # Normalize scores
        sentence_complexity = min(avg_sentence_length / 50.0, 1.0)  # Assume 50 words per sentence is complex
        vocabulary_complexity = vocabulary_richness
        
        return (sentence_complexity + vocabulary_complexity) / 2
    
    def _calculate_engagement(self, statements: List[Dict]) -> Dict[str, Any]:
        """
        Calculate engagement metrics from statements.
        
        Args:
            statements (list): List of statement data
            
        Returns:
            dict: Engagement metrics
        """
        if not statements:
            return {"total_statements": 0}
        
        total_statements = len(statements)
        platforms = {}
        issues = {}
        
        for statement in statements:
            platform = statement.get("platform", "unknown")
            platforms[platform] = platforms.get(platform, 0) + 1
            
            for issue in statement.get("issues", []):
                issues[issue] = issues.get(issue, 0) + 1
        
        return {
            "total_statements": total_statements,
            "platform_distribution": platforms,
            "issue_focus": issues,
            "avg_statements_per_month": total_statements / 12  # Simplified
        }

# Example usage
if __name__ == "__main__":
    # Initialize complete analyzer
    analyzer = OpenDiscourseAnalyzer()
    
    # Example bill analysis
    sample_bill = {
        "id": "S1234-2023",
        "title": "Relates to renewable energy standards",
        "summary": "Establishes renewable energy standards for utilities and provides incentives for solar and wind power installations",
        "full_text": """
        Section 1. Short Title. This Act may be cited as the Renewable Energy Standards Act.
        
        Section 2. Findings and Purpose. The Legislature finds that:
        (a) Climate change poses significant risks to public health and welfare.
        (b) Renewable energy technologies have become cost-competitive.
        (c) A transition to clean energy will create economic opportunities.
        
        Section 3. Renewable Energy Standard. By 2030, electric utilities shall 
        generate not less than 50% of their retail electricity sales from 
        eligible renewable energy resources as defined in Section 4.
        """
    }
    
    print("Analyzing sample bill...")
    bill_analysis = analyzer.analyze_legislation(sample_bill)
    print(json.dumps(bill_analysis, indent=2, default=str))
    
    # Example politician analysis
    sample_statements = [
        {
            "id": "stmt_001",
            "content": "I'm proud to support renewable energy initiatives that will create jobs and protect our environment",
            "platform": "twitter",
            "issues": ["environment", "energy", "jobs"]
        },
        {
            "id": "stmt_002",
            "content": "We must oppose tax cuts that benefit the wealthy while hurting working families",
            "platform": "speech",
            "issues": ["taxes", "economy"]
        }
    ]
    
    print("\nAnalyzing politician statements...")
    politician_analysis = analyzer.analyze_politician("senator_smith", sample_statements, [])
    print(json.dumps(politician_analysis, indent=2, default=str))
```

This comprehensive set of examples demonstrates how to apply various NLP techniques to legislative and political analysis. The examples cover:

1. **Bill similarity analysis** using Sentence-BERT embeddings
2. **Legal entity recognition** using spaCy and custom patterns
3. **Sentiment analysis** using multiple approaches (VADER, TextBlob, BERT)
4. **Politician position tracking** with voting records and public statements
5. **Topic modeling** using LDA for legislative document categorization
6. **Complete analysis pipeline** integrating all techniques

These examples can be adapted and extended for the OpenDiscourse platform to provide comprehensive analysis of legislative content and political discourse.