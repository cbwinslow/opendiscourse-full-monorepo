# Onboarding Guide

Welcome to the OpenDiscourse project! This short guide will help new contributors get started quickly.

## Steps

1. **Read `docs/README.md`** for an overview of the project structure and documentation.
2. **Follow the [Development Setup Guide](guides/DEVELOPMENT_SETUP.md)** to configure Python, PostgreSQL, and Node.js.
3. **Run the tests** to verify your environment:
   ```bash
   pip install -r requirements-dev.txt --break-system-packages
   pytest -q
   ```
4. **Create a new branch** for your work and ensure tasks are tracked in `TASKS.md`.
5. **Submit Pull Requests** following the contribution guidelines in `CONTRIBUTING.md` if available.

Happy hacking!
