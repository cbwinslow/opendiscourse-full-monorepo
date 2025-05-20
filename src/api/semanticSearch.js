const express = require('express');
const router = express.Router();
const semanticSearchService = require('../services/semanticSearchService');
const { validate } = require('express-validator');

// Validate search query
const validateSearch = [
  validate('query').isString().trim().notEmpty(),
  validate('limit').optional().isInt({ min: 1, max: 100 })
];

// Validate article ID
const validateArticleId = [
  validate('articleId').isInt().toInt()
];

// Semantic search endpoint
router.post('/search', validateSearch, async (req, res) => {
  try {
    const { query, limit = 10 } = req.body;
    const results = await semanticSearchService.search(query, limit);
    
    // Add article metadata from our database
    const articlesWithMetadata = await Promise.all(
      results.map(async (result) => {
        const article = await req.db.articles.findByPk(result.id);
        return {
          ...result,
          title: article.title,
          content: article.content,
          source: article.source,
          publishedAt: article.publishedAt
        };
      })
    );

    res.json({ results: articlesWithMetadata });
  } catch (error) {
    console.error('Error in semantic search:', error);
    res.status(500).json({ error: 'Failed to perform semantic search' });
  }
});

// Get related articles endpoint
router.get('/related/:articleId', validateArticleId, async (req, res) => {
  try {
    const { articleId } = req.params;
    const relatedArticles = await semanticSearchService.getRelatedArticles(articleId);
    
    // Add article metadata
    const articlesWithMetadata = await Promise.all(
      relatedArticles.map(async (article) => {
        const dbArticle = await req.db.articles.findByPk(article.id);
        return {
          ...article,
          title: dbArticle.title,
          content: dbArticle.content,
          source: dbArticle.source,
          publishedAt: dbArticle.publishedAt
        };
      })
    );

    res.json({ relatedArticles: articlesWithMetadata });
  } catch (error) {
    console.error('Error getting related articles:', error);
    res.status(500).json({ error: 'Failed to get related articles' });
  }
});

module.exports = router;
