# Contributing to Nexus AI

Developer are more than welcome to contribute to Nexus AI! This guide will help you get started with our development standards and contribution process.

## Our Philosophy
Nexus AI is built on the pillars of **autonomy**, **resilience**, and **simplicity**. We strive for:
- World-class documentation.
- Clean, self-documenting code.
- Robust error handling.
- Optimized performance.

## Getting Started
1. **Fork the Repository**: Create your own copy of the project.
2. **Issue Registry**: Check the Issues page for bugs or feature requests. 
3. **Branching Strategy**: 
   - `feature/your-feature-name` for new features.
   - `fix/your-fix-name` for bug fixes.
   - `docs/description` for documentation improvements.

## Code Standards
### Python (Backend)
- Follow **PEP 8** style guidelines.
- Use **Google-style docstrings** for all public modules, classes, and functions.
- Ensure all functions have **Type Hints**.
- Run `pytest` before submitting a PR.

### JavaScript (Frontend)
- Use **React Functional Components** with Hooks.
- Document components using **JSDoc**.
- Keep components focused and reusable.
- Follow the established design system (standard colors, shadows).

## Submission Process
1. **Sync with Main**: Ensure your branch is up to date with the `main` branch.
2. **Comprehensive PRs**: Your PR description should explain *what* changed and *why*.
3. **Review**: All PRs require at least one approval from a maintainer.
4. **Verification**: Include instructions on how to verify your changes.

## Developing New Agents
If you want to add a new type of agent:
1. Inherit from `BaseAgent` in `backend/agents/base_agent.py`.
2. Define a specialized system prompt.
3. Register the agent in `backend/agents/agent_registry.py`.
4. (Optional) Add custom tools in `backend/tools/`.

## Reporting Issues
Please provide as much detail as possible:
- Steps to reproduce.
- Expected behavior vs. actual behavior.
- Browser/OS versions.
- Log snippets from `backend/backend.log`.

Thank you for helping us build the future of autonomous AI workspaces!
