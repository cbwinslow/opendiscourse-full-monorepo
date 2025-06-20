# Project Task Board

This document tracks all current and upcoming tasks, microgoals, and agent assignments for the opendiscourse project.

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
| Implement Codex delegation workflow                    | Script exists, documented, can send prompt to Codex and save result | DONE      | Copilot       |
| Implement Ollama delegation workflow                    | Script exists, documented, can send prompt to Ollama and save result | TODO      | Copilot       |
| Implement Ollama agent API for workload submission         | API endpoint exists, accepts prompt, returns ID                | DONE      | Copilot       |
| Implement Ollama agent background worker                   | Worker processes prompt, stores result, handles errors          | DONE      | Copilot       |
| Implement Ollama agent webhook/callback                    | Webhook endpoint exists, receives and logs notifications        | DONE      | Copilot       |
| Implement Ollama agent result/status API                   | API endpoint returns status/result for given ID                 | DONE      | Copilot       |
| Document MCP server API endpoints                         | API reference exists in docs, endpoints described                | DONE      | Copilot       |
| Integrate MCP server endpoints with UI                    | UI can submit, poll, and display results from MCP server         | TODO      | Copilot       |

---

Update this file as tasks are completed or new microgoals are defined.
