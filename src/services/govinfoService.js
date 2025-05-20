const axios = require('axios');
const { read_resource } = require('@modelcontextprotocol/client');

const GOVINFO_API_BASE = 'https://api.govinfo.gov';
const SEARCH_API_ENDPOINT = `${GOVINFO_API_BASE}/search`;
const RELATED_DOC_API_ENDPOINT = `${GOVINFO_API_BASE}/related`;

// Sort options for search results
const SORT_OPTIONS = {
  RELEVANCY: { field: 'score', sortOrder: 'DESC' },
  DATE_NEW_TO_OLD: { field: 'publishdate', sortOrder: 'DESC' },
  DATE_OLD_TO_NEW: { field: 'publishdate', sortOrder: 'ASC' },
  TITLE_A_TO_Z: { field: 'title', sortOrder: 'ASC' },
  TITLE_Z_TO_A: { field: 'title', sortOrder: 'DESC' },
  LAST_MODIFIED_DESC: { field: 'lastModified', sortOrder: 'DESC' },
  LAST_MODIFIED_ASC: { field: 'lastModified', sortOrder: 'ASC' }
};
const COLLECTIONS = {
  BILLS: 'BILLS',      // Congressional Bills
  STATUTE: 'STATUTE',  // Statutes at Large
  PLAW: 'PLAW',        // Public Laws
  CRPT: 'CRPT',        // Congressional Reports
  CREC: 'CREC',        // Congressional Record
  USCOURTS: 'USCOURTS' // United States Court Opinions
};

// Constants for API parameters
const DEFAULT_PAGE_SIZE = 100;
const MAX_PAGE_SIZE = 1000;

const govinfoService = {
  // Get document metadata
  async getDocumentMetadata(packageId) {
    try {
      const apiKey = process.env.GOVINFO_API_KEY;
      const response = await axios.get(`${GOVINFO_API_BASE}/packages/${packageId}/metadata`, {
        params: {
          api_key: apiKey
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching package metadata:', error);
      throw error;
    }
  },

  // Get package content
  async getPackageContent(packageId, format = 'xml') {
    try {
      const apiKey = process.env.GOVINFO_API_KEY;
      const response = await axios.get(`${GOVINFO_API_BASE}/packages/${packageId}/content`, {
        params: {
          api_key: apiKey,
          contentFormat: format
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching package content:', error);
      throw error;
    }
  },

  // Get package granules
  async getPackageGranules(packageId) {
    try {
      const apiKey = process.env.GOVINFO_API_KEY;
      const response = await axios.get(`${GOVINFO_API_BASE}/packages/${packageId}/granules`, {
        params: {
          api_key: apiKey
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching package granules:', error);
      throw error;
    }
  },

  // Get granule content
  async getGranuleContent(packageId, granuleId, format = 'xml') {
    try {
      const apiKey = process.env.GOVINFO_API_KEY;
      const response = await axios.get(`${GOVINFO_API_BASE}/packages/${packageId}/granules/${granuleId}/content`, {
        params: {
          api_key: apiKey,
          contentFormat: format
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching granule content:', error);
      throw error;
    }
  },

  // Process document and analyze content
  async processDocument(packageId) {
    try {
      // Get package metadata
      const metadata = await this.getPackageMetadata(packageId);
      
      // Get package content
      const content = await this.getPackageContent(packageId);
      
      // Use semantic search MCP to generate embeddings and analyze content
      const analysis = await read_resource({
        ServerName: 'semantic-search',
        Uri: 'analyze_document',
        Query: {
          content,
          metadata: {
            packageId,
            collection: metadata.collection,
            title: metadata.title,
            dateIssued: metadata.dateIssued,
            source: 'govinfo'
          }
        }
      });

      // Extract key information from the analysis
      const processedData = {
        packageId,
        collection: metadata.collection,
        title: metadata.title,
        dateIssued: metadata.dateIssued,
        summary: analysis.summary,
        keyPoints: analysis.keyPoints,
        relatedTopics: analysis.relatedTopics,
        sentiment: analysis.sentiment,
        entities: analysis.entities,
        legalAnalysis: analysis.legalAnalysis,
        impactAnalysis: analysis.impactAnalysis
      };

      return processedData;
    } catch (error) {
      console.error('Error processing document:', error);
      throw error;
    }
  },

  // Sync collection updates
  async syncCollection(collectionCode, startDate, endDate = null) {
    try {
      // Get collection updates
      const updates = await this.getCollectionUpdates(collectionCode, startDate, endDate);
      
      if (!updates || !updates.packageList) return;

      // Process each package
      for (const packageId of updates.packageList) {
        try {
          const processedDoc = await this.processDocument(packageId);
          await this.storeProcessedDocument(processedDoc);
        } catch (error) {
          console.error(`Error processing package ${packageId}:`, error);
          // Continue with next package even if one fails
        }
      }
    } catch (error) {
      console.error('Error syncing collection:', error);
      throw error;
    }
  },

  // Store processed document in our database
  async storeProcessedDocument(processedDoc) {
    try {
      // Store in our database
      await read_resource({
        ServerName: 'semantic-search',
        Uri: 'store_document',
        Query: {
          id: processedDoc.packageId,
          content: processedDoc,
          vectorStore: 'legislative_documents'
        }
      });
    } catch (error) {
      console.error('Error storing processed document:', error);
      throw error;
    }
  },

  async getCollections() {
    try {
      const apiKey = process.env.GOVINFO_API_KEY;
      const response = await axios.get(`${GOVINFO_API_BASE}/collections`, {
        params: {
          api_key: apiKey
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Error fetching collections:', error);
      throw error;
    }
  },

  async getCollectionUpdates(collectionCode, startDate, endDate = null, pageSize = DEFAULT_PAGE_SIZE) {
    try {
      if (!collectionCode) throw new Error('Collection code is required');
      if (!startDate) throw new Error('Start date is required');
      
      const apiKey = process.env.GOVINFO_API_KEY;
      const endpoint = endDate 
        ? `${GOVINFO_API_BASE}/collections/${collectionCode}/${startDate}/${endDate}`
        : `${GOVINFO_API_BASE}/collections/${collectionCode}/${startDate}`;

      const response = await axios.get(endpoint, {
        params: {
          api_key: apiKey,
          pageSize,
          offsetMark: '*'
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Error fetching collection updates:', error);
      throw error;
    }
  },

  async getPackageMetadata(packageId) {
    try {
      const apiKey = process.env.GOVINFO_API_KEY;
      const response = await axios.get(`${GOVINFO_API_BASE}/packages/${packageId}/metadata`, {
        params: {
          api_key: apiKey
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Error fetching package metadata:', error);
      throw error;
    }
  },

  async getPackageContent(packageId, format = 'xml') {
    try {
      const apiKey = process.env.GOVINFO_API_KEY;
      const response = await axios.get(`${GOVINFO_API_BASE}/packages/${packageId}/content`, {
        params: {
          api_key: apiKey,
          contentFormat: format
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Error fetching package content:', error);
      throw error;
    }
  },

  async getPackageGranules(packageId) {
    try {
      const apiKey = process.env.GOVINFO_API_KEY;
      const response = await axios.get(`${GOVINFO_API_BASE}/packages/${packageId}/granules`, {
        params: {
          api_key: apiKey
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Error fetching package granules:', error);
      throw error;
    }
  },

  async getGranuleContent(packageId, granuleId, format = 'xml') {
    try {
      const apiKey = process.env.GOVINFO_API_KEY;
      const response = await axios.get(`${GOVINFO_API_BASE}/packages/${packageId}/granules/${granuleId}/content`, {
        params: {
          api_key: apiKey,
          contentFormat: format
        }
      });
      
      return response.data;
    } catch (error) {
      console.error('Error fetching granule content:', error);
      throw error;
    }
  },

  async processDocument(packageId) {
    try {
      // Get package metadata
      const metadata = await this.getPackageMetadata(packageId);
      
      // Get package content
      const content = await this.getPackageContent(packageId);
      
      // Use semantic search MCP to generate embeddings and analyze content
      const analysis = await read_resource({
        ServerName: 'semantic-search',
        Uri: 'analyze_document',
        Query: {
          content,
          metadata: {
            packageId,
            collection: metadata.collection,
            title: metadata.title,
            dateIssued: metadata.dateIssued,
            source: 'govinfo'
          }
        }
      });

      // Extract key information from the analysis
      const processedData = {
        packageId,
        collection: metadata.collection,
        title: metadata.title,
        dateIssued: metadata.dateIssued,
        summary: analysis.summary,
        keyPoints: analysis.keyPoints,
        relatedTopics: analysis.relatedTopics,
        sentiment: analysis.sentiment,
        entities: analysis.entities,
        legalAnalysis: analysis.legalAnalysis,
        impactAnalysis: analysis.impactAnalysis
      };

      return processedData;
    } catch (error) {
      console.error('Error processing document:', error);
      throw error;
    }
  },

  async syncCollection(collectionCode, startDate, endDate = null) {
    try {
      // Get collection updates
      const updates = await this.getCollectionUpdates(collectionCode, startDate, endDate);
      
      if (!updates || !updates.packageList) return;

      // Process each package
      for (const packageId of updates.packageList) {
        try {
          const processedDoc = await this.processDocument(packageId);
          await this.storeProcessedDocument(processedDoc);
        } catch (error) {
          console.error(`Error processing package ${packageId}:`, error);
          // Continue with next package even if one fails
        }
      }
    } catch (error) {
      console.error('Error syncing collection:', error);
      throw error;
    }
  },

  async storeProcessedDocument(processedDoc) {
    try {
      // Store in our database
      await read_resource({
        ServerName: 'semantic-search',
        Uri: 'store_document',
        Query: {
          id: processedDoc.packageId,
          content: processedDoc,
          vectorStore: 'legislative_documents'
        }
      });
    } catch (error) {
      console.error('Error storing processed document:', error);
      throw error;
    }
  }
};

module.exports = govinfoService;
