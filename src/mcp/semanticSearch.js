const { read_resource } = require('@modelcontextprotocol/client');

const semanticSearchMCP = {
  // Store document analysis results
  async storeDocumentAnalysis(packageId, analyses) {
    try {
      // Store each type of analysis
      for (const analysis of analyses) {
        await read_resource({
          ServerName: 'semantic-search',
          Uri: 'store_analysis',
          Query: {
            packageId,
            analysisType: analysis.type,
            content: analysis.content,
            metadata: analysis.metadata
          }
        });
      }

      // Generate embeddings for the document
      const embeddings = await this.generateDocumentEmbeddings(packageId);
      
      // Store embeddings
      await read_resource({
        ServerName: 'semantic-search',
        Uri: 'store_embeddings',
        Query: {
          packageId,
          embeddings,
          vectorStore: 'legislative_documents'
        }
      });

      return true;
    } catch (error) {
      console.error('Error storing document analysis:', error);
      throw error;
    }
  },

  // Generate document embeddings
  async generateDocumentEmbeddings(packageId) {
    try {
      // Get document content
      const content = await read_resource({
        ServerName: 'semantic-search',
        Uri: 'get_document_content',
        Query: { packageId }
      });

      // Generate embeddings using OpenAI
      const embeddings = await read_resource({
        ServerName: 'openai',
        Uri: 'get_embeddings',
        Query: { text: content }
      });

      return embeddings;
    } catch (error) {
      console.error('Error generating embeddings:', error);
      throw error;
    }
  },

  // Extract entities from document
  async extractEntities(packageId) {
    try {
      // Get document content
      const content = await read_resource({
        ServerName: 'semantic-search',
        Uri: 'get_document_content',
        Query: { packageId }
      });

      // Extract entities using OpenAI
      const entities = await read_resource({
        ServerName: 'openai',
        Uri: 'extract_entities',
        Query: {
          text: content,
          entityTypes: ['person', 'organization', 'location', 'concept']
        }
      });

      // Store entities
      await read_resource({
        ServerName: 'semantic-search',
        Uri: 'store_entities',
        Query: {
          packageId,
          entities
        }
      });

      return entities;
    } catch (error) {
      console.error('Error extracting entities:', error);
      throw error;
    }
  },

  // Analyze document impact
  async analyzeImpact(packageId) {
    try {
      // Get document content
      const content = await read_resource({
        ServerName: 'semantic-search',
        Uri: 'get_document_content',
        Query: { packageId }
      });

      // Analyze impact using OpenAI
      const impactAnalysis = await read_resource({
        ServerName: 'openai',
        Uri: 'analyze_impact',
        Query: {
          text: content,
          analysisTypes: ['economic', 'social', 'legal', 'environmental']
        }
      });

      // Store impact analysis
      await read_resource({
        ServerName: 'semantic-search',
        Uri: 'store_impact_analysis',
        Query: {
          packageId,
          analysis: impactAnalysis
        }
      });

      return impactAnalysis;
    } catch (error) {
      console.error('Error analyzing impact:', error);
      throw error;
    }
  },

  // Search documents by semantic similarity
  async searchDocuments(query, options = {}) {
    try {
      // Generate query embedding
      const queryEmbedding = await read_resource({
        ServerName: 'openai',
        Uri: 'get_embeddings',
        Query: { text: query }
      });

      // Search using vector similarity
      const results = await read_resource({
        ServerName: 'semantic-search',
        Uri: 'search_embeddings',
        Query: {
          vector: queryEmbedding,
          vectorStore: 'legislative_documents',
          topK: options.topK || 10,
          filter: options.filter
        }
      });

      return results;
    } catch (error) {
      console.error('Error searching documents:', error);
      throw error;
    }
  }
};

module.exports = semanticSearchMCP;
