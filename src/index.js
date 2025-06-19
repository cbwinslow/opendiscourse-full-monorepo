require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const { Sequelize } = require('sequelize');
const { initializeModels } = require('./database/models');
const authRoutes = require('./api/auth');
const newsRoutes = require('./api/news');
const aiRoutes = require('./api/ai');
const jobsRoutes = require('./api/jobs');
const semanticSearchRoutes = require('./api/semanticSearch');
const govinfoRoutes = require('./api/govinfo');
const path = require('path');

const app = express();

// Middleware
app.use(cors());
app.use(helmet());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Database connection
const sequelize = new Sequelize(process.env.DB_NAME, process.env.DB_USER, process.env.DB_PASSWORD, {
  host: process.env.DB_HOST,
  port: process.env.DB_PORT,
  dialect: 'postgres'
});

// Initialize models
initializeModels(sequelize);

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/news', newsRoutes);
app.use('/api/ai', aiRoutes);
app.use('/api/jobs', jobsRoutes);
app.use('/api/search', semanticSearchRoutes);
app.use('/api/govinfo', govinfoRoutes);
app.use('/web', express.static(path.join(__dirname, '../web')));

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
