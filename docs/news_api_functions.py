from newsapi import NewsApiClient
from datetime import datetime, timedelta

# --- Initialize NewsAPI client ---
NEWSAPI_KEY = '367abe65b21647b69c54bfb8da20f27d' # Replace with your actual NewsAPI.org API key

# --- Utility Functions (using the client library) ---

def get_top_headlines_client(newsapi, country='us', category=None, sources=None, query=None, page_size=20):
    """Fetches top headlines using the NewsAPI client."""
    try:
        if sources:
            top_headlines_data = newsapi.get_top_headlines(q=query,
                                                           sources=sources,
                                                           page_size=page_size)
        elif category:
             top_headlines_data = newsapi.get_top_headlines(q=query,
                                                           category=category,
                                                           country=country,
                                                           page_size=page_size)
        else:
            top_headlines_data = newsapi.get_top_headlines(q=query,
                                                           country=country,
                                                           page_size=page_size)

        return top_headlines_data.get('articles', [])
    except Exception as e: # The client library might raise specific exceptions.
        print(f"An error occurred with NewsAPI client: {e}")
        return []


def search_articles_client(newsapi, query, sources=None, domains=None, from_param=None,
                           to_param=None, language='en', sort_by='publishedAt', page_size=20):
    """Searches for articles using the NewsAPI client."""
    if not query:
        print("Search query cannot be empty.")
        return []
    try:
        all_articles_data = newsapi.get_everything(q=query,
                                                   sources=sources,
                                                   domains=domains,
                                                   from_param=from_param, # Note: param name is from_param
                                                   to=to_param,
                                                   language=language,
                                                   sort_by=sort_by,
                                                   page_size=page_size)
        return all_articles_data.get('articles', [])
    except Exception as e:
        print(f"An error occurred with NewsAPI client: {e}")
        return []

# display_articles function remains the same as in the requests example.
def display_articles(articles, max_articles=5):
    """
    Prints article details in a readable format.
    Args:
        articles (list): A list of article dictionaries.
        max_articles (int): Maximum number of articles to display.
    """
    if not articles:
        print("No articles to display.")
        return

    print(f"\n--- Displaying up to {max_articles} Articles ---")
    for i, article in enumerate(articles[:max_articles]):
        title = article.get('title', 'N/A')
        source_name = article.get('source', {}).get('name', 'N/A')
        published_at = article.get('publishedAt', 'N/A')
        description = article.get('description', 'N/A')
        url = article.get('url', '#')

        print(f"\nArticle {i+1}:")
        print(f"  Title: {title}")
        print(f"  Source: {source_name}")
        print(f"  Published: {published_at}")
        print(f"  Description: {description}")
        print(f"  URL: {url}")
    print("--------------------------------------")


# --- Example Usage (Client Library) ---
if __name__ == "__main__":
    if NEWSAPI_KEY == 'YOUR_API_KEY':
        print("Please replace 'YOUR_API_KEY' with your actual NewsAPI.org API key.")
    else:
        newsapi = NewsApiClient(api_key=NEWSAPI_KEY)

        # Example 1: Get top headlines from US for 'business'
        print("Fetching top business headlines from US (client lib)...")
        business_headlines_client = get_top_headlines_client(newsapi, category='business', page_size=3)
        display_articles(business_headlines_client)

        # Example 2: Search for "global economy" articles
        print("\nSearching for 'global economy' articles (client lib)...")
        # For 'everything' endpoint, free plan usually searches articles from past month.
        # `from_param` can be a datetime object or an ISO format string.
        # from_date_iso = (datetime.now() - timedelta(days=7)).isoformat()
        economy_articles_client = search_articles_client(newsapi,
                                                         query="global economy",
                                                         # from_param=from_date_iso,
                                                         language='en',
                                                         sort_by='relevancy',
                                                         page_size=3)
        display_articles(economy_articles_client)
