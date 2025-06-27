import json

import requests

NEWSAPI_KEY = "YOUR_API_KEY"  # Replace with your actual NewsAPI.org API key
NEWSAPI_BASE_URL = "https://newsapi.org/v2/"

# --- Utility Functions ---


def make_api_request(endpoint, params=None):
    """
    Makes a request to the NewsAPI.
    Args:
        endpoint (str): The API endpoint (e.g., 'top-headlines', 'everything').
        params (dict, optional): Dictionary of query parameters.
    Returns:
        dict: JSON response from the API, or None if an error occurs.
    """
    if params is None:
        params = {}
    params["apiKey"] = NEWSAPI_KEY
    url = NEWSAPI_BASE_URL + endpoint

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {response.content.decode()}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except json.JSONDecodeError:
        print("Failed to decode JSON response.")
    return None


def get_top_headlines(
    country="us", category=None, sources=None, query=None, page_size=20
):
    """
    Fetches top headlines.
    Args:
        country (str, optional): 2-letter ISO 3166-1 code of the country.
        category (str, optional): Category (e.g., 'business', 'technology').
                                  Cannot be mixed with 'sources' param.
        sources (str, optional): Comma-separated string of identifiers for news sources.
                                Cannot be mixed with 'country' or 'category'.
        query (str, optional): Keywords or a phrase to search for.
        page_size (int, optional): Number of results to return per page. Max 100.
    Returns:
        list: A list of articles, or an empty list if an error occurs or no articles are found.
    """
    params = {"pageSize": page_size}
    if sources:
        params["sources"] = sources
    elif category:
        params["category"] = category
        params["country"] = country  # Category requires country
    else:
        params["country"] = country  # Default to country if no sources/category

    if query:
        params["q"] = query

    data = make_api_request("top-headlines", params)
    return data.get("articles", []) if data else []


def search_articles(
    query,
    sources=None,
    domains=None,
    from_date=None,
    to_date=None,
    language="en",
    sort_by="publishedAt",
    page_size=20,
):
    """
    Searches for articles across a wide range of sources.
    Args:
        query (str): Keywords or phrase to search for.
        sources (str, optional): Comma-separated string of identifiers for news sources.
        domains (str, optional): Comma-separated string of domains to restrict search to.
        from_date (str, optional): Start date for search (YYYY-MM-DD or ISO format).
        to_date (str, optional): End date for search (YYYY-MM-DD or ISO format).
        language (str, optional): 2-letter ISO 639-1 code of the language.
        sort_by (str, optional): How to sort results ('relevancy', 'popularity', 'publishedAt').
        page_size (int, optional): Number of results. Max 100.
    Returns:
        list: A list of articles, or an empty list if an error occurs or no articles are found.
    """
    if not query:
        print("Search query cannot be empty.")
        return []

    params = {
        "q": query,
        "language": language,
        "sortBy": sort_by,
        "pageSize": page_size,
    }
    if sources:
        params["sources"] = sources
    if domains:
        params["domains"] = domains
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date

    data = make_api_request("everything", params)
    return data.get("articles", []) if data else []


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
        title = article.get("title", "N/A")
        source_name = article.get("source", {}).get("name", "N/A")
        published_at = article.get("publishedAt", "N/A")
        description = article.get("description", "N/A")
        url = article.get("url", "#")

        print(f"\nArticle {i+1}:")
        print(f"  Title: {title}")
        print(f"  Source: {source_name}")
        print(f"  Published: {published_at}")
        print(f"  Description: {description}")
        print(f"  URL: {url}")
    print("--------------------------------------")


# --- Example Usage ---
if __name__ == "__main__":
    if NEWSAPI_KEY == "YOUR_API_KEY":
        print("Please replace 'YOUR_API_KEY' with your actual NewsAPI.org API key.")
    else:
        # Example 1: Get top headlines from the US for 'technology'
        print("Fetching top technology headlines from US...")
        top_tech_headlines = get_top_headlines(
            country="us", category="technology", page_size=5
        )
        display_articles(top_tech_headlines)

        # Example 2: Search for articles about "artificial intelligence"
        print("\nSearching for articles about 'artificial intelligence'...")
        # Default from_date is 1 month ago for 'everything' endpoint on free plan.
        # Let's specify a recent range if your plan allows or for testing.
        # yesterday_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')
        ai_articles = search_articles(
            query="artificial intelligence", sort_by="popularity", page_size=3
        )  # from_date=yesterday_str
        display_articles(ai_articles)

        # Example 3: Get top headlines from a specific source (e.g., 'bbc-news')
        print("\nFetching top headlines from BBC News...")
        bbc_headlines = get_top_headlines(sources="bbc-news", page_size=3)
        display_articles(bbc_headlines)
