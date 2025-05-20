const express = require('express');
const { validate } = require('express-validation');
const { govinfoService } = require('../services/govinfoService');

const router = express.Router();

// Request validation schemas
const searchValidation = {
  body: {
    query: {
      type: 'string',
      required: true,
      minLength: 1,
      maxLength: 1000
    },
    options: {
      type: 'object',
      properties: {
        collection: { type: 'string' },
        dateRange: {
          type: 'object',
          properties: {
            startDate: { type: 'string', format: 'date' },
            endDate: { type: 'string', format: 'date' }
          }
        },
        pageSize: { type: 'integer', minimum: 1, maximum: 1000 },
        sort: { type: 'string', enum: ['RELEVANCY', 'DATE_NEW_TO_OLD', 'DATE_OLD_TO_NEW', 'TITLE_A_TO_Z', 'TITLE_Z_TO_A'] }
      }
    }
  }
};

const relatedValidation = {
  params: {
    packageId: {
      type: 'string',
      required: true,
      pattern: /^[A-Z]+-[0-9]+$/
    }
  },
  query: {
    limit: { type: 'integer', minimum: 1, maximum: 100 },
    sort: { type: 'string', enum: ['RELEVANCY', 'DATE_NEW_TO_OLD', 'DATE_OLD_TO_NEW', 'TITLE_A_TO_Z', 'TITLE_Z_TO_A'] }
  }
};

// Routes
router.get('/collections', async (req, res) => {
  try {
    const collections = await govinfoService.getCollections();
    res.json(collections);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/collections/updates', async (req, res) => {
  try {
    const { collectionCode, startDate, endDate, pageSize } = req.query;
    const updates = await govinfoService.getCollectionUpdates(collectionCode, startDate, endDate, pageSize);
    res.json(updates);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/search', validate(searchValidation), async (req, res) => {
  try {
    const { query, options } = req.body;
    const results = await govinfoService.searchDocuments(query, options);
    res.json(results);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/related/:packageId', validate(relatedValidation), async (req, res) => {
  try {
    const { packageId } = req.params;
    const { limit, sort } = req.query;
    const relatedDocs = await govinfoService.getRelatedDocuments(packageId, { limit, sort });
    res.json(relatedDocs);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/process', validate({
  body: {
    packageId: {
      type: 'string',
      required: true,
      pattern: /^[A-Z]+-[0-9]+$/
    }
  }
}), async (req, res) => {
  try {
    const { packageId } = req.body;
    const processedDoc = await govinfoService.processDocument(packageId);
    res.json(processedDoc);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
