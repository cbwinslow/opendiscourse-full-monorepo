const { read_resource } = require('@modelcontextprotocol/client');
const { govinfoService } = require('../govinfoService');
const { createJob } = require('../jobs');

const DOCUMENT_ANALYSIS_TYPES = {
  LEGAL: 'legal_analysis',
  IMPACT: 'impact_analysis',
  ENTITY_EXTRACTION: 'entity_extraction',
  SEMANTIC: 'semantic_analysis'
};

const DocumentAnalyzer = {
  async analyzeDocument(packageId) {
    try {
      // Get document content
      const content = await govinfoService.getPackageContent(packageId);
      
      // Create analysis jobs
      const analysisJobs = [
        this.createLegalAnalysisJob(content),
        this.createImpactAnalysisJob(content),
        this.createEntityExtractionJob(content),
        this.createSemanticAnalysisJob(content)
      ];

      // Process jobs in parallel
      const results = await Promise.all(analysisJobs);
      
      // Store analysis results
      await this.storeAnalysisResults(packageId, results);
      
      return results;
    } catch (error) {
      console.error('Error analyzing document:', error);
      throw error;
    }
  },

  createLegalAnalysisJob(content) {
    return createJob({
      type: DOCUMENT_ANALYSIS_TYPES.LEGAL,
      payload: {
        content,
        analysisType: 'legal'
      }
    });
  },

  createImpactAnalysisJob(content) {
    return createJob({
      type: DOCUMENT_ANALYSIS_TYPES.IMPACT,
      payload: {
        content,
        analysisType: 'impact'
      }
    });
  },

  createEntityExtractionJob(content) {
    return createJob({
      type: DOCUMENT_ANALYSIS_TYPES.ENTITY_EXTRACTION,
      payload: {
        content,
        analysisType: 'entity_extraction'
      }
    });
  },

  createSemanticAnalysisJob(content) {
    return createJob({
      type: DOCUMENT_ANALYSIS_TYPES.SEMANTIC,
      payload: {
        content,
        analysisType: 'semantic'
      }
    });
  },

  async storeAnalysisResults(packageId, results) {
    try {
      // Store in our database
      await read_resource({
        ServerName: 'semantic-search',
        Uri: 'store_document_analysis',
        Query: {
          packageId,
          analyses: results
        }
      });
    } catch (error) {
      console.error('Error storing analysis results:', error);
      throw error;
    }
  },

  async monitorGovInfo() {
    try {
      // Get collections we want to monitor
      const collections = await govinfoService.getCollections();
      
      // For each collection, get updates
      for (const collection of collections) {
        const updates = await govinfoService.getCollectionUpdates(
          collection.collectionCode,
          new Date(Date.now() - 24 * 60 * 60 * 1000) // Last 24 hours
        );

        if (updates && updates.packageList) {
          // Process each new/updated document
          for (const packageId of updates.packageList) {
            await this.analyzeDocument(packageId);
          }
        }
      }
    } catch (error) {
      console.error('Error monitoring GovInfo:', error);
      throw error;
    }
  }
};

module.exports = DocumentAnalyzer;
