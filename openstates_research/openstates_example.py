#!/usr/bin/env python3
"""
Example Python script to access and analyze OpenStates data
This demonstrates how researchers typically work with the OpenStates dataset
"""

import requests
import pandas as pd
import json
from datetime import datetime
import time

class OpenStatesResearcher:
    """
    A class to demonstrate research methods using OpenStates data
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the researcher with API key
        You need to get an API key from https://openstates.org/api/signup
        """
        self.api_key = api_key
        self.base_url = "https://api.openstates.org/v3"
        self.headers = {
            "X-Api-Key": api_key
        } if api_key else {}
        
    def get_bills(self, state, session=None, bill_type=None, sponsor=None, **kwargs):
        """
        Retrieve bills from OpenStates API
        """
        params = {
            'state': state,
            'page': 0,
            'per_page': 20
        }
        
        if session:
            params['session'] = session
        if bill_type:
            params['bill_type'] = bill_type
        if sponsor:
            params['sponsor'] = sponsor
            
        # Add any other parameters
        params.update(kwargs)
        
        response = requests.get(f"{self.base_url}/bills/", headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error retrieving bills: {response.status_code}")
            return None
    
    def get_legislators(self, state, chamber=None):
        """
        Retrieve legislators for a specific state
        """
        params = {'state': state}
        if chamber:
            params['chamber'] = chamber
            
        response = requests.get(f"{self.base_url}/people/", headers=self.headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error retrieving legislators: {response.status_code}")
            return None
    
    def analyze_policy_diffusion(self, states, policy_topic, date_range):
        """
        Example research method: Analyze policy diffusion across states
        """
        # This would involve collecting bill data across multiple states
        # and analyzing adoption patterns over time
        diffusion_data = []
        
        for state in states:
            bills = self.get_bills(state, query=policy_topic, **date_range)
            if bills:
                for bill in bills.get('results', []):
                    diffusion_data.append({
                        'state': state,
                        'bill_id': bill.get('id'),
                        'title': bill.get('title'),
                        'created_date': bill.get('created_date'),
                        'classification': bill.get('classification'),
                        'actions': bill.get('actions')
                    })
        
        return diffusion_data
    
    def extract_bill_text_analysis(self, bills):
        """
        Example of text analysis approach using bill content
        """
        # In practice, you would use NLP libraries like NLTK or spaCy here
        analysis_results = []
        
        for bill in bills:
            # Process bill text for analysis
            bill_data = {
                'id': bill.get('id'),
                'title': bill.get('title'),
                'state': bill.get('state', {}).get('name'),
                'text': bill.get('title'),  # Simplified - would use full text in practice
                'sponsor': bill.get('sponsor'),
                'actions': len(bill.get('actions', [])),
                'subjects': bill.get('subject', [])
            }
            analysis_results.append(bill_data)
        
        return analysis_results

def example_research_workflow():
    """
    Example of a typical research workflow using OpenStates data
    """
    print("OpenStates Research Workflow Example")
    print("=" * 50)
    
    # Initialize researcher (without API key, this won't work but shows the structure)
    researcher = OpenStatesResearcher(api_key="YOUR_API_KEY_HERE")
    
    print("1. Retrieving bills for analysis...")
    # Example: Get all education-related bills from California in the last session
    # bills = researcher.get_bills(state='CA', query='education')
    
    print("2. Analyzing legislative patterns...")
    # researcher.analyze_policy_diffusion(['CA', 'NY', 'TX'], 'education', {})
    
    print("3. Performing text analysis...")
    # researcher.extract_bill_text_analysis(bills)
    
    print("\nResearch workflow completed!")
    print("\nTo run this code with real data:")
    print("- Get an API key from https://openstates.org/api/signup")
    print("- Replace 'YOUR_API_KEY_HERE' with your actual API key")
    print("- Install required packages: pip install requests pandas")

def main():
    """
    Main function to demonstrate the research capabilities
    """
    example_research_workflow()

if __name__ == "__main__":
    main()