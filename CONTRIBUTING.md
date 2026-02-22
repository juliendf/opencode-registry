# Contributing to OpenCode Registry

Thank you for your interest in contributing to OpenCode Registry! This document provides guidelines for contributing.

## 🌟 Ways to Contribute

1. **Add New Components** - Share your agents, skills, or commands
2. **Improve Existing Components** - Enhance documentation or functionality
3. **Report Bugs** - Help us identify and fix issues
4. **Suggest Features** - Share ideas for improvements
5. **Improve Documentation** - Fix typos, add examples, clarify instructions

## 🚀 Quick Start

1. Fork the repository
2. Clone your fork:
   ```bash
git clone https://github.com/juliendf/opencode-registry.git
cd opencode-registry
   ```
3. Create a branch for your changes:
   ```bash
   git checkout -b feature/my-new-agent
   ```
4. Make your changes
5. Test your changes
6. Commit and push
7. Open a Pull Request

## 📦 Adding Components

### Directory Structure

Components go in these directories:
- **Agents:** `opencode/agents/`
- **Subagents:** `opencode/agents/subagents/<category>/`
- **Skills:** `opencode/skills/<skill-name>/`
- **Commands:** `opencode/commands/`

### Component Template

All components should have YAML frontmatter with metadata:

```markdown
---
name: "Component Name"
description: "Brief description"
type: "agent|subagent|skill|command"
version: "1.0.0"
author: "Your Name"
tags: ["tag1", "tag2"]
---

# Component Name

Component content here...
```

### Categories for Subagents

When adding subagents, use these categories:
- `01-core` - Backend, API, microservices, GraphQL, fullstack
- `02-languages` - Python, TypeScript, Go, React, Bash, SQL, Vue
- `03-infrastructure` - Kubernetes, Terraform, AWS, GCP, Azure, GitOps
- `04-quality-and-security` - Testing, security, performance, debugging
- `05-data-ai` - ML, data engineering, AI, database optimization
- `06-developer-experience` - CLI development, MCP, DX optimization
- `07-specialized-domains` - Mobile, payments, technical writing
- `09-meta-orchestration` - Workflow orchestration, context management

## 🧪 Testing Your Changes

Before submitting:

```bash
# Install the CLI in development mode
cd installer
pip install -e .

# Test your component appears
opencode-config list

# Test installation
opencode-config install --group basic --dry-run

# Verify your component info
opencode-config info your-component-id
```

## 📝 Commit Guidelines

- Use clear, descriptive commit messages
- Start with a verb: "Add", "Fix", "Update", "Remove"
- Reference issues when applicable: "Fix #123"

Examples:
```
Add kubernetes-expert subagent
Fix typo in README
Update install command to support dry-run
```

## 🔍 Code Review Process

1. All PRs require at least one review
2. CI checks must pass (when implemented)
3. Documentation must be updated if needed
4. Components must include proper frontmatter

## 🐛 Reporting Bugs

When reporting bugs, include:
- Operating system
- Python version
- Steps to reproduce
- Expected behavior
- Actual behavior
- Error messages (if any)

## 💡 Suggesting Features

When suggesting features:
- Explain the use case
- Describe the expected behavior
- Consider how it fits with existing features
- Provide examples if possible

## 📋 Pull Request Template

Your PR description should include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] New component (agent/skill/command)
- [ ] Bug fix
- [ ] Feature enhancement
- [ ] Documentation update

## Testing
- [ ] Tested locally with `opencode-config list`
- [ ] Verified component installs correctly
- [ ] Updated documentation if needed

## Checklist
- [ ] Component has proper frontmatter
- [ ] Commit messages are clear
- [ ] No personal/sensitive information included
```

## 🎯 Component Quality Guidelines

### Good Components Have:
- Clear, descriptive names
- Comprehensive documentation
- Proper YAML frontmatter
- Examples of usage
- Appropriate categorization

### Avoid:
- Hardcoded personal paths
- Sensitive information (API keys, tokens, etc.)
- Overly specific configurations
- Duplicate functionality

## 🏷️ Versioning

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible changes
- **MINOR** version for backward-compatible functionality
- **PATCH** version for backward-compatible bug fixes

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes (for significant contributions)
- Project acknowledgments

## 💬 Getting Help

- Open a GitHub Issue for bugs or feature requests
- Start a Discussion for questions
- Check existing issues before creating new ones

## 🎨 Style Guide

### Markdown
- Use ATX-style headers (`#` not underlines)
- Include blank lines between sections
- Use code fences with language identifiers

### Python Code
- Follow PEP 8
- Use type hints where appropriate
- Include docstrings for functions/classes
- Maximum line length: 100 characters

### YAML
- Use 2-space indentation
- Quote strings with special characters
- Keep it simple and readable

## 🚦 Component Review Criteria

Before accepting a component, we check:
1. **Functionality** - Does it work as described?
2. **Quality** - Is it well-documented and tested?
3. **Originality** - Does it duplicate existing components?
4. **Scope** - Is it generally useful to the community?
5. **Safety** - Does it follow security best practices?

## 📞 Contact

- GitHub Issues: For bugs and features
- GitHub Discussions: For questions and ideas
- Pull Requests: For contributions

---

Thank you for contributing to OpenCode Registry! 🎉
