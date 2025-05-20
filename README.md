# Comprehensive News Aggregator Platform

A sophisticated news aggregation and analysis platform that combines multiple news sources, social media, TV streams, and financial data with advanced AI capabilities for content analysis and fact-checking.

## Features

- Multi-source news aggregation
- Social media integration (Twitter)
- TV stream transcription and analysis
- Financial news integration
- Advanced NLP and NLG capabilities
- Bias detection and analysis
- Fact-checking system
- User profiles and authentication
- AI-powered content analysis
- Document processing and RAG
- Library of Congress integration

## Tech Stack

- Backend: Node.js with Express
- Database: PostgreSQL
- AI/ML: Various LLMs and NLP models
- Frontend: Modern JavaScript framework
- Authentication: OAuth2/JWT
- Real-time processing: WebSocket/Socket.io
- Caching: Redis
- Queue System: RabbitMQ

## Project Structure

```
src/
├── api/              # API routes and controllers
├── auth/             # Authentication system
├── database/         # Database models and migrations
├── jobs/             # Background job processing
├── services/         # External service integrations
├── ai/               # AI/ML components
├── models/           # Data models and schemas
├── utils/            # Utility functions
└── config/           # Configuration files
```

## Getting Started

1. Clone the repository
2. Install dependencies: `npm install`
3. Set up environment variables
4. Run database migrations
5. Start the development server

## Environment Variables

```
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=news_aggregator
DB_USER=postgres
DB_PASSWORD=your_password

# Authentication
JWT_SECRET=your_jwt_secret

# External Services
TWITTER_API_KEY=your_twitter_api_key
BLOOMBERG_API_KEY=your_bloomberg_api_key

# AI/ML
OPENAI_API_KEY=your_openai_api_key
```

## License

MIT
