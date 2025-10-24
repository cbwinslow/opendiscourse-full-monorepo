# OpenDiscourse Project

Welcome to the OpenDiscourse project - a comprehensive platform for collecting, processing, and analyzing government data with AI-powered insights.

## 📋 Project Overview

OpenDiscourse is an ambitious initiative to aggregate legislative data from multiple government sources and provide sophisticated analysis capabilities through AI/ML techniques. The project focuses on US federal and state government data, with a particular emphasis on legislative activities, voting records, and political discourse.

**Repository Note:** This is the consolidated monorepo version of the OpenDiscourse project, integrating all components into a single repository at [https://github.com/cbwinslow/opendiscourse-full-monorepo](https://github.com/cbwinslow/opendiscourse-full-monorepo).

## 🏗️ Architecture

This project follows a monorepo structure with the following key components:

- **Data Collection** (`packages/data-collector/`) - Tools for collecting data from Congress.gov, GovInfo, OpenStates, and other government APIs
- **API Services** (`packages/api/`, `apps/api-server/`) - Backend services providing REST APIs for data access
- **AI/ML Engine** (`packages/rag-engine/`) - Retrieval Augmented Generation system for contextual analysis
- **Web Interface** (`apps/web-client/`, `apps/web-client-next/`) - Frontend applications for browsing and analyzing data
- **Infrastructure** (`infrastructure/`) - Deployment configurations and DevOps tools
- **External Sources** (`external-sources/`) - Reference implementations and integrations with external projects

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   npm install
   pip install -r requirements.txt
   ```

2. **Run Development Server**:
   ```bash
   npm run dev
   ```

3. **Access Services**:
   - Web Interface: http://localhost:3000
   - API Server: http://localhost:8000

## 📚 Documentation

The project includes extensive documentation to help you understand and contribute:

- [`PROJECT_SUMMARY.md`](PROJECT_SUMMARY.md) - High-level overview of the project
- [`KNOWLEDGE_BASE.md`](KNOWLEDGE_BASE.md) - Comprehensive context for AI assistants
- [`FEATURES.md`](FEATURES.md) - Feature roadmap and specifications
- [`TODO.md`](TODO.md) - Current tasks and development priorities
- [`AGENT_SETUP_GUIDE.md`](AGENT_SETUP_GUIDE.md) - Setup guide for AI agents

## 🛠️ Development Helper

For an interactive guide to navigating this project, run:

```bash
./opendiscourse_dev_helper.sh
```

This script provides:
- Project overview and structure
- Available services and components
- Development commands and workflows
- AI assistance information
- Recommended next steps

## 🎯 Key Features

- **Multi-source Data Collection**: Aggregates data from federal and state government sources
- **AI-Powered Analysis**: Uses LLMs for contextual understanding of legislative content
- **Scalable Architecture**: Designed for horizontal scaling and high availability
- **Extensible Design**: Modular structure allows for easy addition of new data sources
- **Comprehensive Documentation**: Extensive research, API specs, and development guides

## 🤝 Contributing

We welcome contributions from the community! Please see our documentation for guidelines on:

1. Setting up your development environment
2. Understanding the codebase structure
3. Contributing new features or improvements
4. Reporting issues or suggesting enhancements

## 📞 Support

For questions about the project or to discuss potential collaborations, please reach out to the maintainers.

---

*This project represents a significant effort to increase government transparency and provide powerful tools for analyzing political discourse and legislative activities.*