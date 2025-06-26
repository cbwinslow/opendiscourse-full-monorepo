# Development Workflow Guide

This document describes the recommended development workflow for the opendiscourse project, including multi-agent collaboration, microgoal-driven task management, and automation practices.

## Key Practices

- Use microgoals: Break down features and fixes into small, measurable, attainable tasks.
- Multi-agent workflow: Delegate tasks to AI agents (Ollama, Agent-Zero, OpenAI Codex) for code generation, review, and planning.
- Document all changes: Update documentation and project task lists with every change.
- Use scripts for automation: Scripts are provided for migrations, health checks, and agent orchestration.

## Workflow Steps

1. Define microgoals for each feature or fix in `project_tasks.md` and SRS.
2. Assign microgoals to agents (see `AGENT.md`).
3. Use provided scripts to automate setup, migration, and agent orchestration.
4. Document progress and results in `project_tasks.md` and commit messages.
5. Review and merge changes via PRs, using Agent-Zero for code review if enabled.

## Example Microgoal

- "Implement NIM API health check script"
  - Criteria: Script exists, runs, logs health status, documented in `PROJECT_STRUCTURE.md`.

---

See `AGENT.md` for agent setup and delegation details.
