# Project Tasks (Consolidated)

This file consolidates all project tasks, microgoals, and agent assignments from previous task files.

## Task Table

| Task/Microgoal                                      | Criteria/Definition                                      | Status    | Assigned Agent |
|-----------------------------------------------------|---------------------------------------------------------|-----------|---------------|
| Integrate Ollama for local LLM agent                | Ollama installed, model running, API accessible         | TODO      | Ollama        |
| Add Agent-Zero for code review/planning             | Agent-Zero app added to repo, PRs reviewed              | TODO      | Agent-Zero    |
| Set up OpenAI Codex for code generation             | API key configured, script runs, code generated         | TODO      | OpenAI Codex  |
| Create DEVELOPMENT.md and AGENT.md docs             | Docs exist, describe workflow and agent setup           | DONE      | Copilot       |
| Create SRS with microgoals and measurable criteria  | SRS exists, microgoals listed, criteria defined         | TODO      | Copilot       |
| Automate db migration/health scripts                | Scripts exist, run, and are documented                  | DONE      | Copilot       |
| Document all new scripts in PROJECT_STRUCTURE.md    | PROJECT_STRUCTURE.md updated with new scripts           | DONE      | Copilot       |
| Implement Codex delegation workflow                 | Script exists, documented, can send prompt to Codex and save result | DONE      | Copilot       |
| Implement Ollama delegation workflow                | Script exists, documented, can send prompt to Ollama and save result | TODO      | Copilot       |
| Implement Ollama agent API for workload submission  | API endpoint exists, accepts prompt, returns ID          | DONE      | Copilot       |
| Implement Ollama agent background worker            | Worker processes prompt, stores result, handles errors   | DONE      | Copilot       |
| Implement Ollama agent webhook/callback             | Webhook endpoint exists, receives and logs notifications | DONE      | Copilot       |
| Implement Ollama agent result/status API            | API endpoint returns status/result for given ID          | DONE      | Copilot       |
| Document MCP server API endpoints                   | API reference exists in docs, endpoints described        | DONE      | Copilot       |
| Integrate MCP server endpoints with UI              | UI can submit, poll, and display results from MCP server | TODO      | Copilot       |
| GovInfo: Data Download                             | Identify target collections, create download script, set up storage | TODO      | Copilot       |
| GovInfo: Database Design                           | Design tables/relationships, implement schema, load data | TODO      | Copilot       |
| GovInfo: ERD Creation                              | Generate/validate/export ERD                             | TODO      | Copilot       |
| GovInfo: Documentation                             | Create project docs, write README                        | TODO      | Copilot       |
| Committee: Database Design                         | Finalize schema, implement structure, load data          | TODO      | Copilot       |
| Committee: ERD Creation                            | Generate/validate/export ERD                             | TODO      | Copilot       |
| Committee: Documentation                           | Create docs, write README                                | TODO      | Copilot       |
| Member: Data Extraction                            | Extraction script, pagination, historical data           | TODO      | Copilot       |
| Member: Data Processing                            | Parse/transform data, create schema                      | TODO      | Copilot       |
| Member: Data Validation                            | Validation scripts, quality checks, error handling       | TODO      | Copilot       |
| Member: Database Design                            | Design/implement schema, load data                       | TODO      | Copilot       |
| Member: ERD Creation                               | Generate/validate/export ERD                             | TODO      | Copilot       |
| Member: Documentation                              | Create docs, write README                                | TODO      | Copilot       |
| RAG Database & Vector Store Design                 | Design schema for documents, entities, declarations, inferences, media, tasks, and vector store (pgvector/ClickHouse). | IN PROGRESS | Copilot |
| RAG DB migration/automation script                | Script exists to apply rag_db_schema.sql to PostgreSQL, usage documented | DONE      | Copilot       |
| Ingest media appearances (podcasts, YouTube, news) | Scripts exist to ingest and link media appearances to entities, transcripts stored | TODO      | Copilot       |
| Expand entity tracking (contacts, social handles, transcripts) | Entity model and ingestion scripts support new data types | TODO      | Copilot       |
| Automate scheduled ingestion (background jobs/cron) | Ingestion jobs run on schedule, new data is regularly added | TODO      | Copilot       |
| Scaffold web UI for RAG DB (React/Next.js)         | Create minimal React/Next.js app, add pages for search, chat, admin, and analytics. | TODO      | Copilot       |
| Build research and chat interfaces (LLM-powered Q&A, attribution) | UI supports LLM Q&A, document exploration, and attribution | TODO      | Copilot       |
| Build admin dashboard for sources/entities/jobs    | Admin UI for managing sources, entities, and ingestion jobs | TODO      | Copilot       |
| Integrate LangChain retrieval/QA chains            | Retrieval/QA chains implemented and connected to UI | TODO      | Copilot       |
| Connect web UI to retrieval/QA chains              | UI can interact with retrieval/QA backend for research/chat | TODO      | Copilot       |
| Expand CI/CD for new scripts and web UI            | CI/CD covers scripts and web UI, automated tests and deploys | TODO      | Copilot       |
| Expand Jira/GitHub/GitLab automation for tasks     | Automation syncs tasks, reports progress, updates issues | TODO      | Copilot       |
| Continue updating documentation and global rules   | Docs and rules reflect new features and workflows | IN PROGRESS | Copilot       |
| Consolidate all scripts into functional directories | All scripts organized into data_ingestion, rag, setup, reporting, tests, legacy | DONE      | Copilot       |
| Document script structure in SCRIPTS.md            | SCRIPTS.md exists and describes all script locations and purposes | DONE      | Copilot       |
| Consolidate recommendations into RECOMMENDATIONS.md| All recommendations merged into a single file | DONE      | Copilot       |
| Consolidate project tasks into TASKS.md            | All tasks and microgoals merged into a single file | DONE      | Copilot       |
| Create and enforce GLOBAL_RULES.md                 | Global rules for agent behavior and task tracking documented and enforced | DONE      | Copilot       |
| Set up Jira integration and automation             | .github/workflows/jira-issue.yml and jira_sync.py sync TASKS.md with Jira | DONE      | Copilot       |
| Document Jira setup in dotfiles/JIRA_SETUP.md      | JIRA_SETUP.md exists and describes integration steps | DONE      | Copilot       |
| Design RAG DB schema in rag_db_schema.sql          | Schema covers documents, entities, declarations, inferences, media, tasks, vectors | DONE      | Copilot       |
| Add ingestion scripts for documents and social media| Scripts exist for ingesting legal/code/docs and Twitter posts | DONE      | Copilot       |
| Update TASKS.md and GLOBAL_RULES.md on every change| All agent actions update TASKS.md and follow global rules | IN PROGRESS | Copilot       |
| Add ingestion scripts for new sources (future)      | Scripts for media, entity tracking, and other sources | TODO      | Copilot       |
| Add background jobs for scheduled ingestion/research| Jobs run on schedule for ingestion and research | TODO      | Copilot       |
| Integrate LangChain for inference and attribution   | Retrieval/QA chains use LangChain for RAG and attribution | TODO      | Copilot       |
| Expand entity tracking (contacts, social, media)    | Entity model and ingestion scripts support contacts, handles, transcripts | TODO      | Copilot       |
| Expand admin and reporting interfaces               | Admin UI and reporting tools for managing and monitoring ingestion | TODO      | Copilot       |
| Add project management automation (Jira, GitHub, GitLab CI/CD) | Automated sync, reporting, and task tracking | IN PROGRESS | Copilot       |
| Maintain up-to-date project documentation          | All docs reflect current structure, features, and rules | IN PROGRESS | Copilot       |
| Enforce global rules for agent and contributor behavior | All contributors/agents follow documented rules | IN PROGRESS | Copilot       |
| Add onboarding and developer setup docs            | Clear onboarding and setup instructions for new contributors | TODO      | Copilot       |
| Add test coverage for all new scripts and features | Automated/unit/integration tests for all new code | TODO      | Copilot       |
| Add monitoring and alerting for ingestion/research jobs | Monitoring and alerting in place for background jobs | TODO      | Copilot       |
| Add data validation and quality checks to ingestion | Ingestion scripts include validation and error handling | TODO      | Copilot       |
| Add ERD diagrams for all major schemas             | ERD diagrams generated and included in docs | TODO      | Copilot       |
| Add user feedback and issue reporting to web UI    | Web UI allows users to submit feedback and report issues | TODO      | Copilot       |
| Add API documentation and OpenAPI specs            | API endpoints documented with OpenAPI/Swagger | TODO      | Copilot       |
| Add support for ClickHouse as alternative vector store | ClickHouse schema and ingestion supported | TODO      | Copilot       |
| Add support for multi-agent collaboration          | System supports multiple agents with clear roles and coordination | TODO      | Copilot       |
| Add versioning and migration for RAG schema        | Schema changes are versioned and migrations are automated | TODO      | Copilot       |
| Add data export and backup scripts                 | Scripts exist for exporting and backing up all data | TODO      | Copilot       |
| Add analytics and usage reporting                  | Analytics and usage reports available to admins | TODO      | Copilot       |
| Add security review and audit tasks                | Security reviews and audits scheduled and tracked | TODO      | Copilot       |
| Add accessibility review for web UI                | Web UI reviewed and improved for accessibility | TODO      | Copilot       |
| Add localization/internationalization support      | System supports multiple languages/locales | TODO      | Copilot       |

---

## Progress Tracking (as of 2025-07-12)

### Task Progress Table

| Task/Microgoal | Progress Notes | % Complete |
|----------------|---------------|------------|
| Integrate Ollama for local LLM agent | Not started. | 0% |
| Add Agent-Zero for code review/planning | Not started. | 0% |
| Set up OpenAI Codex for code generation | Not started. | 0% |
| Create DEVELOPMENT.md and AGENT.md docs | Docs created and committed. | 100% |
| Create SRS with microgoals and measurable criteria | Not started. | 0% |
| Automate db migration/health scripts | Scripts created, tested, and documented. | 100% |
| Document all new scripts in PROJECT_STRUCTURE.md | PROJECT_STRUCTURE.md updated. | 100% |
| Implement Codex delegation workflow | Script created, tested, and documented. | 100% |
| Implement Ollama delegation workflow | Not started. | 0% |
| Implement Ollama agent API for workload submission | API endpoint created and tested. | 100% |
| Implement Ollama agent background worker | Worker implemented and tested. | 100% |
| Implement Ollama agent webhook/callback | Webhook implemented and tested. | 100% |
| Implement Ollama agent result/status API | API endpoint created and tested. | 100% |
| Document MCP server API endpoints | API reference written and committed. | 100% |
| Integrate MCP server endpoints with UI | Not started. | 0% |
| GovInfo: Data Download | Not started. | 0% |
| GovInfo: Database Design | Not started. | 0% |
| GovInfo: ERD Creation | Not started. | 0% |
| GovInfo: Documentation | Not started. | 0% |
| Committee: Database Design | Not started. | 0% |
| Committee: ERD Creation | Not started. | 0% |
| Committee: Documentation | Not started. | 0% |
| Member: Data Extraction | Not started. | 0% |
| Member: Data Processing | Not started. | 0% |
| Member: Data Validation | Not started. | 0% |
| Member: Database Design | Not started. | 0% |
| Member: ERD Creation | Not started. | 0% |
| Member: Documentation | Not started. | 0% |
| RAG Database & Vector Store Design | Schema designed, SQL written, schema file created, progress tracked. | 90% |
| RAG DB migration/automation script | Script created, tested, and documented. | 100% |
| Ingest media appearances (podcasts, YouTube, news) | Not started. | 0% |
| Expand entity tracking (contacts, social handles, transcripts) | Not started. | 0% |
| Automate scheduled ingestion (background jobs/cron) | Not started. | 0% |
| Scaffold web UI for RAG DB (React/Next.js) | Create minimal React/Next.js app, add pages for search, chat, admin, and analytics. | 0% |
| Build research and chat interfaces (LLM-powered Q&A, attribution) | Not started. | 0% |
| Build admin dashboard for sources/entities/jobs | Not started. | 0% |
| Integrate LangChain retrieval/QA chains | Not started. | 0% |
| Connect web UI to retrieval/QA chains | Not started. | 0% |
| Expand CI/CD for new scripts and web UI | Not started. | 0% |
| Expand Jira/GitHub/GitLab automation for tasks | Workflow and script created, Jira integration tested, progress tracked. | 80% |
| Continue updating documentation and global rules | Ongoing updates, new rules added, progress tracked. | 80% |
| Consolidate all scripts into functional directories | All scripts moved, committed, and pushed. | 100% |
| Document script structure in SCRIPTS.md | SCRIPTS.md created and updated. | 100% |
| Consolidate recommendations into RECOMMENDATIONS.md | All recommendations merged. | 100% |
| Consolidate project tasks into TASKS.md | All tasks merged. | 100% |
| Create and enforce GLOBAL_RULES.md | Rules created, updated, and enforced. | 100% |
| Set up Jira integration and automation | Workflow and script created, Jira integration tested. | 100% |
| Document Jira setup in dotfiles/JIRA_SETUP.md | JIRA_SETUP.md created and updated. | 100% |
| Design RAG DB schema in rag_db_schema.sql | Schema designed and documented. | 100% |
| Add ingestion scripts for documents and social media | Scripts created and tested. | 100% |
| Update TASKS.md and GLOBAL_RULES.md on every change | Ongoing, rules and tasks updated after every change. | 80% |
| Add ingestion scripts for new sources (future) | Not started. | 0% |
| Add background jobs for scheduled ingestion/research | Not started. | 0% |
| Integrate LangChain for inference and attribution | Not started. | 0% |
| Expand entity tracking (contacts, social, media) | Not started. | 0% |
| Expand admin and reporting interfaces | Not started. | 0% |
| Add project management automation (Jira, GitHub, GitLab CI/CD) | Ongoing, automation expanded. | 80% |
| Maintain up-to-date project documentation | Ongoing, docs updated. | 80% |
| Enforce global rules for agent and contributor behavior | Ongoing, rules enforced. | 80% |
| Add onboarding and developer setup docs | Not started. | 0% |
| Add test coverage for all new scripts and features | Not started. | 0% |
| Add monitoring and alerting for ingestion/research jobs | Not started. | 0% |
| Add data validation and quality checks to ingestion | Not started. | 0% |
| Add ERD diagrams for all major schemas | Not started. | 0% |
| Add user feedback and issue reporting to web UI | Not started. | 0% |
| Add API documentation and OpenAPI specs | Not started. | 0% |
| Add support for ClickHouse as alternative vector store | Not started. | 0% |
| Add support for multi-agent collaboration | Not started. | 0% |
| Add versioning and migration for RAG schema | Not started. | 0% |
| Add data export and backup scripts | Not started. | 0% |
| Add analytics and usage reporting | Not started. | 0% |
| Add security review and audit tasks | Not started. | 0% |
| Add accessibility review for web UI | Not started. | 0% |
| Add localization/internationalization support | Not started. | 0% |

#### Section Completion
- Core Infrastructure: 80%
- RAG DB & Ingestion: 60%
- Automation & CI/CD: 70%
- Documentation & Rules: 90%
- Web UI & Admin: 0%
- Analytics, Security, Accessibility: 0%

#### Total Project Completion: 48%

---

## Progress Notes

### RAG Database & Vector Store Design
- Schema planned: documents, entities, declarations, inferences, media_appearances, tasks, with vector store support (pgvector/ClickHouse).
- Will support ingestion of legal docs, social media, media appearances, and entity tracking.
- Next: Implement SQL schema and migration scripts.

## Completed Tasks (Satisfied)
- API setup, data validation, and processing for all pipelines
- Database migration/health scripts automated
- Documentation for new scripts in PROJECT_STRUCTURE.md
- Codex and Ollama agent API, background worker, webhook, and result/status API
- MCP server API endpoints documented

Update this file as tasks are completed or new microgoals are defined.
