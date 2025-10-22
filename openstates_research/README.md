# OpenStates Dataset Research Guide

This repository contains resources for conducting research using the OpenStates legislative dataset. OpenStates provides comprehensive legislative data across all 50 U.S. states, making it an invaluable resource for political science, public policy, and legislative research.

## Table of Contents

1. [OpenStates Research Methods](openstates_research_methods.md) - Comprehensive overview of research methodologies
2. [Example Python Code](openstates_example.py) - Practical code for accessing OpenStates API
3. [Data Analysis Functions](openstates_analysis.py) - Common analytical functions for legislative research
4. [Getting Started Guide](#getting-started) - How to begin your research
5. [Research Applications](#research-applications) - Common research uses of OpenStates data

## Getting Started

### Prerequisites

- Python 3.7+
- Basic knowledge of data analysis with pandas
- Understanding of legislative processes (helpful but not required)

### Required Libraries

```bash
pip install requests pandas numpy matplotlib seaborn
```

### Getting an API Key

To access OpenStates data, you'll need an API key:

1. Visit [OpenStates API Signup](https://openstates.org/api/signup)
2. Register for an account
3. Generate your API key
4. Use the key in your research code

## Research Applications

### 1. Policy Diffusion Research

How policies spread across states over time. Use the `perform_policy_diffusion_analysis()` function in `openstates_analysis.py` to examine adoption patterns.

### 2. Legislative Behavior Analysis

Understanding voting patterns, bill sponsorship, and legislative productivity. The `analyze_sponsor_patterns()` function provides insights into sponsor behavior.

### 3. Content Analysis of Legislation

Using natural language processing to analyze bill content. The framework in `openstates_analysis.py` provides a starting point for text analysis.

### 4. Comparative State Politics

Comparing political processes and outcomes across states. Use the multi-state analysis functions to conduct comparative research.

## Code Structure

### openstates_example.py
Demonstrates how to access OpenStates API and set up a research workflow. Shows:
- API authentication
- Data retrieval methods
- Basic data structures

### openstates_analysis.py
Contains analytical functions for:
- Data cleaning and preparation
- Statistical analysis of legislative patterns
- Visualization functions
- Policy diffusion analysis
- Content analysis preparation

### openstates_research_methods.md
Comprehensive guide covering:
- Research methodologies
- Data structure and content
- Common applications
- Tools and approaches
- Future research directions

## Research Workflow

1. **Define your research question** - What legislative phenomenon are you studying?
2. **Obtain API access** - Get your OpenStates API key
3. **Retrieve data** - Use the example code to access relevant data
4. **Clean and process** - Apply cleaning functions from `openstates_analysis.py`
5. **Analyze** - Use appropriate analytical methods based on your research question
6. **Visualize** - Create charts and graphs to understand patterns
7. **Interpret** - Draw conclusions from your analysis

## Common Research Questions Addressed with OpenStates Data

- How do policies spread across states?
- What predicts bill success or failure?
- How do legislator characteristics affect behavior?
- How do state institutions affect policy outcomes?
- What factors influence legislative agenda-setting?
- How does partisanship influence legislative behavior?

## Best Practices

1. **Respect API rate limits** - Don't overload the servers with requests
2. **Cache data locally** - Download and store data to reduce API calls
3. **Validate your data** - Check for inconsistencies and missing values
4. **Document your methods** - Keep detailed records of your analysis
5. **Cite appropriately** - Acknowledge OpenStates as your data source

## Advanced Topics

### Natural Language Processing
For content analysis of bill text, consider integrating with:
- NLTK: Natural language toolkit
- spaCy: Advanced NLP library
- scikit-learn: Machine learning for text classification
- Gensim: Topic modeling and document similarity

### Network Analysis
For relationship analysis, consider:
- NetworkX: Graph analysis and network creation
- igraph: Network analysis tools
- community detection algorithms for legislative collaboration

### Statistical Modeling
For advanced statistical analysis:
- Statsmodels: Traditional statistical models
- scikit-learn: Machine learning algorithms
- PyMC: Bayesian statistical modeling
- lifelines: Survival/event history analysis

## Contributing

If you develop additional analytical tools or methods for working with OpenStates data, please consider contributing back to the research community by sharing your code and approaches.

## References

- OpenStates API documentation: https://api.openstates.org/
- Open Civic Data project: https://github.com/opencivicdata/
- Legislative research methodology papers in political science journals

## Support

For questions about using OpenStates data for research:
- Check the OpenStates documentation
- Review the legislative research literature
- Contact academic colleagues working in state politics