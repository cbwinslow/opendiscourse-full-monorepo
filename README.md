# OpenDiscourse

OpenDiscourse is a comprehensive platform for analyzing and processing government documents and legislative data.

## Project Structure

```text
opendiscourse/
├── config/                    # Configuration files
│   └── environments/         # Environment-specific settings
│       ├── development.toml  # Development settings
│       ├── production.toml   # Production settings
│       └── testing.toml      # Testing settings
├── data/                     # Data files (not version controlled)
│   ├── raw/                  # Raw data
│   └── processed/            # Processed data
├── docs/                     # Documentation
│   ├── api/                  # API documentation
│   └── guides/               # Development guides
├── infrastructure/           # Infrastructure as code
│   ├── database/             # Database configurations
│   ├── middleware/           # Middleware configurations
│   └── networking/           # Network configurations
├── opendiscourse/            # Main Python package
│   ├── api/                  # API endpoints
│   │   ├── v1/               # API version 1
│   │   └── v2/               # API version 2
│   ├── core/                 # Core functionality
│   ├── db/                   # Database models and migrations
│   ├── services/             # Business logic services
│   │   ├── scraping/         # Web scraping services
│   │   ├── search/           # Search functionality
│   │   └── storage/          # Data storage services
│   └── utils/                # Utility functions
├── scripts/                  # Utility scripts
│   ├── checks/               # System health checks
│   ├── database/             # Database maintenance
│   ├── deployment/           # Deployment scripts
│   └── setup/                # Setup and installation
└── tests/                    # Test suite
    ├── integration/          # Integration tests
    └── unit/                 # Unit tests
        ├── data/             # Test data
        └── mocks/            # Test mocks
```

## Development Setup

1. Clone the repository

2. Install dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```

3. Set up environment variables:

   ```bash
   cp config/environments/.env.example config/environments/.env
   # Edit the .env file with your configuration
   ```

4. Run the development server:

   ```bash
   python -m opendiscourse
   ```

## Testing

Run the test suite:

```bash
pytest tests/
```

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests and linters
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
