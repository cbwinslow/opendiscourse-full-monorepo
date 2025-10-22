#!/usr/bin/env python3
"""
Data analysis functions for OpenStates research
This module provides common analytical functions used in legislative research
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

def load_and_clean_bills_data(json_data):
    """
    Load and clean bills data from OpenStates API response
    """
    # Flatten the JSON data into a DataFrame
    bills_list = []
    
    for bill in json_data.get('results', []):
        bill_record = {
            'id': bill.get('id'),
            'state': bill.get('state'),
            'session': bill.get('session'),
            'bill_id': bill.get('bill_id'),
            'title': bill.get('title'),
            'created_date': bill.get('created_date'),
            'updated_date': bill.get('updated_date'),
            'classification': bill.get('classification', [None])[0] if bill.get('classification') else None,
            'subject': ', '.join(bill.get('subject', [])),
            'sponsor_name': bill.get('sponsor', {}).get('name') if bill.get('sponsor') else None,
            'sponsor_id': bill.get('sponsor', {}).get('id') if bill.get('sponsor') else None,
            'chamber': bill.get('from_organization', {}).get('name') if bill.get('from_organization') else None,
            'actions_count': len(bill.get('actions', [])),
            'votes_count': len(bill.get('votes', [])),
            'sources_count': len(bill.get('sources', []))
        }
        
        # Extract status from the last action
        actions = bill.get('actions', [])
        if actions:
            last_action = actions[-1]
            bill_record['last_action_date'] = last_action.get('date')
            bill_record['last_action_description'] = last_action.get('description')
            bill_record['last_action_classification'] = last_action.get('classification', [None])[0] if last_action.get('classification') else None
        
        bills_list.append(bill_record)
    
    df = pd.DataFrame(bills_list)
    
    # Convert date columns to datetime
    date_columns = ['created_date', 'updated_date', 'last_action_date']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    return df

def analyze_bill_progression(df):
    """
    Analyze bill progression patterns
    """
    # Create a progression status based on last action
    def categorize_status(action_class):
        if action_class is None:
            return 'unknown'
        elif 'pass' in str(action_class).lower() or 'passed' in str(action_class).lower():
            return 'passed'
        elif 'fail' in str(action_class).lower() or 'failed' in str(action_class).lower():
            return 'failed'
        elif 'introduced' in str(action_class).lower():
            return 'introduced'
        elif 'committee' in str(action_class).lower():
            return 'in_committee'
        else:
            return 'in_progress'
    
    df['status_category'] = df['last_action_classification'].apply(categorize_status)
    
    # Calculate progression statistics
    status_counts = df['status_category'].value_counts()
    
    return df, status_counts

def analyze_sponsor_patterns(df):
    """
    Analyze patterns in bill sponsorship
    """
    # Count bills by sponsor
    sponsor_counts = df['sponsor_name'].value_counts()
    
    # Calculate average bills per sponsor
    avg_bills_per_sponsor = df.groupby('sponsor_name').size().mean()
    
    # Identify most active sponsors
    top_sponsors = sponsor_counts.head(10)
    
    return sponsor_counts, avg_bills_per_sponsor, top_sponsors

def analyze_legislative_calendar(df):
    """
    Analyze timing patterns in bill introduction and progression
    """
    # Extract year and month from creation date
    df['creation_year'] = df['created_date'].dt.year
    df['creation_month'] = df['created_date'].dt.month
    df['creation_weekday'] = df['created_date'].dt.weekday
    
    # Group by month to see introduction patterns
    monthly_introductions = df.groupby('creation_month').size()
    
    # Analyze seasonal patterns
    weekday_patterns = df.groupby('creation_weekday').size()
    
    return monthly_introductions, weekday_patterns

def visualize_legislative_patterns(df):
    """
    Create visualizations for legislative patterns
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Bill status distribution
    if 'status_category' in df.columns:
        status_counts = df['status_category'].value_counts()
        axes[0, 0].pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%')
        axes[0, 0].set_title('Distribution of Bill Status Categories')
    
    # Bills by month
    monthly_introductions, _ = analyze_legislative_calendar(df)
    axes[0, 1].bar(monthly_introductions.index, monthly_introductions.values)
    axes[0, 1].set_title('Bills Introduced by Month')
    axes[0, 1].set_xlabel('Month')
    axes[0, 1].set_ylabel('Number of Bills')
    
    # Bills by classification
    if 'classification' in df.columns:
        top_classifications = df['classification'].value_counts().head(10)
        axes[1, 0].barh(range(len(top_classifications)), top_classifications.values)
        axes[1, 0].set_yticks(range(len(top_classifications)))
        axes[1, 0].set_yticklabels(top_classifications.index)
        axes[1, 0].set_title('Top 10 Bill Classifications')
        axes[1, 0].set_xlabel('Number of Bills')
    
    # Actions vs. Votes
    if 'actions_count' in df.columns and 'votes_count' in df.columns:
        axes[1, 1].scatter(df['actions_count'], df['votes_count'], alpha=0.6)
        axes[1, 1].set_xlabel('Number of Actions')
        axes[1, 1].set_ylabel('Number of Votes')
        axes[1, 1].set_title('Actions vs. Votes per Bill')
    
    plt.tight_layout()
    plt.show()

def perform_policy_diffusion_analysis(states_data):
    """
    Analyze policy adoption patterns across multiple states (simulated)
    """
    # This would normally compare adoption dates across states
    # For demonstration, we'll create a simulated analysis
    
    print("Policy Diffusion Analysis")
    print("=" * 30)
    
    # Simulate diffusion analysis for each state
    results = {}
    
    for state, data in states_data.items():
        df = load_and_clean_bills_data(data)
        df, status_counts = analyze_bill_progression(df)
        
        # Calculate adoption rate
        if len(status_counts) > 0:
            passed_count = status_counts.get('passed', 0)
            total_count = len(df)
            adoption_rate = passed_count / total_count if total_count > 0 else 0
            
            results[state] = {
                'total_bills': total_count,
                'passed_bills': passed_count,
                'adoption_rate': adoption_rate,
                'status_distribution': status_counts.to_dict()
            }
    
    return results

def content_analysis_preparation(df):
    """
    Prepare data for content analysis of bill text
    """
    # For a real content analysis, you would need the full bill text
    # This function sets up the framework for text analysis
    
    # Create a simplified text corpus from bill titles
    text_corpus = df[['id', 'title', 'subject']].dropna()
    
    # Basic text statistics
    text_stats = {
        'avg_title_length': text_corpus['title'].apply(len).mean(),
        'unique_subjects': len(text_corpus['subject'].unique()),
        'total_documents': len(text_corpus)
    }
    
    return text_corpus, text_stats

def run_sample_analysis():
    """
    Run a sample analysis with example data structure
    """
    print("Sample OpenStates Data Analysis")
    print("=" * 40)
    
    # This would normally load actual data from API
    # For demonstration, we'll show the structure
    
    print("1. Loading and cleaning bill data...")
    print("2. Analyzing bill progression patterns...")
    print("3. Analyzing sponsor patterns...")
    print("4. Examining legislative calendar patterns...")
    print("5. Performing policy diffusion analysis...")
    print("6. Preparing for content analysis...")
    
    print("\nFor actual analysis:")
    print("- Use the OpenStates API to retrieve real bill data")
    print("- Apply the analytical functions to your dataset")
    print("- Use pandas and other libraries for statistical analysis")
    print("- Consider using NLP libraries for text analysis of bill content")

if __name__ == "__main__":
    run_sample_analysis()