const { read_resource } = require('@modelcontextprotocol/client');

const semanticSearchService = {
  async search(query, limit = 10) {
    try {
      // Use the semantic search MCP server
      const searchResults = await read_resource({
        ServerName: 'semantic-search',
        Uri: 'search',
        Query: {
          query,
          limit,
          // We'll need to map our article embeddings to the vector store
          // This will be implemented in the database models
          vectorStore: 'news_articles'
        }
      });

      return searchResults;
    } catch (error) {
      console.error('Error in semantic search:', error);
      throw error;
    }
  },

  async getRelatedArticles(articleId, limit = 5) {
    try {
      // Get the article's embedding
      const articleEmbedding = await read_resource({
        ServerName: 'semantic-search',
        Uri: 'get_embedding',
        Query: {
          id: articleId,
          vectorStore: 'news_articles'
        }
      });

      // Find related articles
      const relatedArticles = await read_resource({
        ServerName: 'semantic-search',
        Uri: 'find_similar',
        Query: {
          embedding: articleEmbedding,
          limit,
          vectorStore: 'news_articles'
        }
      });

      return relatedArticles;
    } catch (error) {
      console.error('Error getting related articles:', error);
      throw error;
    }
  }
};

module.exports = semanticSearchService;
