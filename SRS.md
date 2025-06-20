# Software Requirements Specification (SRS)

## Project: opendiscourse

## Purpose
Define the requirements, microgoals, and measurable criteria for the opendiscourse platform, including agent-driven development and automation.

---

## Functional Requirements

1. **Multi-Agent Orchestration**
   - Integrate Ollama, Agent-Zero, and OpenAI Codex for collaborative development.
   - Criteria: Each agent is set up, documented, and can be assigned tasks.

2. **Microgoal-Driven Task Management**
   - All features and fixes are broken into microgoals with clear, measurable criteria.
   - Criteria: Each microgoal is tracked in `project_tasks.md` and SRS.

3. **Script Automation**
   - Scripts for db migration, health checks, agent orchestration, and backup/restore exist and are documented.
   - Criteria: Scripts run successfully and are referenced in documentation.

4. **Documentation**
   - All new features, scripts, and workflows are documented in `PROJECT_STRUCTURE.md`, `DEVELOPMENT.md`, and `AGENT.md`.
   - Criteria: Docs exist and are up to date.

---

## Microgoals & Measurable Criteria

| Microgoal                                         | Criteria/Definition                                      |
|---------------------------------------------------|---------------------------------------------------------|
| Integrate Ollama for local LLM agent              | Ollama installed, model running, API accessible         |
| Add Agent-Zero for code review/planning           | Agent-Zero app added to repo, PRs reviewed              |
| Set up OpenAI Codex for code generation           | API key configured, script runs, code generated         |
| Automate db migration/health scripts              | Scripts exist, run, and are documented                  |
| Document all new scripts in PROJECT_STRUCTURE.md  | PROJECT_STRUCTURE.md updated with new scripts           |
| Create DEVELOPMENT.md and AGENT.md docs           | Docs exist, describe workflow and agent setup           |
| Create SRS with microgoals and measurable criteria| SRS exists, microgoals listed, criteria defined         |
| Implement Codex delegation workflow                    | Script exists, documented, can send prompt to Codex and save result |
| Implement Ollama delegation workflow                    | Script exists, documented, can send prompt to Ollama and save result |
| Implement Ollama agent API for workload submission         | API endpoint exists, accepts prompt, returns ID                |
| Implement Ollama agent background worker                   | Worker processes prompt, stores result, handles errors          |
| Implement Ollama agent webhook/callback                    | Webhook endpoint exists, receives and logs notifications        |
| Implement Ollama agent result/status API                   | API endpoint returns status/result for given ID                 |

---

## Non-Functional Requirements

- All automation and agent orchestration must be secure and auditable.
- Documentation must be updated with every change.
- Scripts must be cross-platform (Linux/macOS, zsh compatible).

---

## Traceability
- All requirements and microgoals are mapped to tasks in `project_tasks.md` and referenced in documentation.
