import pinecone
import os
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings

def search(query, top_k=5):
    """Search for documents similar to the given query.
    
    Args:
        query (str): Search query
        top_k (int): Number of results to return
        
    Returns:
        list: List of search results with scores and metadata
    """
    # Load environment variables
    load_dotenv()
    
    # Initialize Pinecone
    pinecone.init(
        api_key=os.getenv('PINECONE_API_KEY'),
        environment=os.getenv('PINECONE_ENVIRONMENT')
    )
    
    # Initialize OpenAI embeddings
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )
    
    # Get the Pinecone index
    index = pinecone.Index("opendiscourse-docs")
    
    # Get query embedding
    query_embedding = embeddings.embed_query(query)
    
    # Search for similar documents
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    
    # Format results
    formatted_results = []
    for match in results.matches:
        formatted_results.append({
            'score': match.score,
            'title': match.metadata.get('title', ''),
            'content': match.metadata.get('content', ''),
            'document_id': match.metadata.get('document_id', '')
        })
    
    return formatted_results

if __name__ == "__main__":
    # Example usage
    query = "What is the main topic of this document?"
    results = search(query)
    for i, result in enumerate(results, 1):
        print(f"\nResult {i} (Score: {result['score']:.3f})")
        print(f"Title: {result['title']}")
        print(f"Content: {result['content']}")
