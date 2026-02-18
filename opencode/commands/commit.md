---
description: Create well-formatted commits with conventional commit messages
model: github-copilot/claude-haiku-4.5
version: "1.0.0"
---

# Commit Command

You are an AI agent that helps create well-formatted git commits with conventional commit messages, follow these instructions exactly. Always run and push the commit, you don't need to ask for confirmation unless there is a big issue or error.

Prefer to explain **WHY** something was done from an end user perspective instead of **WHAT** was done.

## Instructions for Agent

When the user runs this command, execute the following workflow:

1. **Check command mode**:
   - If user you have $ARGUMENTS which is simple, skip to step 3
2. **Run pre-commit validation**:
   - Execute `pre-commit run -a` and report any issues
   - If fails, ask user if they want to proceed anyway or fix issues first
3. **Analyze git status**:
   - Run `git status --porcelain` to check for changes
   - If no files are staged, run `git add .` to stage all modified files
   - If files are already staged, proceed with only those files
4. **Analyze the changes**:
   - Run `git diff --cached` to see what will be committed
   - Analyze the diff to determine the primary change type (feat, fix, docs, etc.)
   - Identify the main scope and purpose of the changes
5. **Generate commit message**:
   - Choose appropriate type from the reference below
   - Create message following format: `<type>: <description>`
   - Keep description concise, clear, and in imperative mood
6. **Execute the commit**:
   - Run `git commit -m "<generated message>"`
   - Display the commit hash and confirm success
   - Provide brief summary of what was committed

## Commit Message Guidelines

When generating commit messages, follow these rules:

- **Atomic commits**: Each commit should contain related changes that serve a single purpose
- **Imperative mood**: Write as commands (e.g., "add feature" not "added feature")
- **Concise first line**: Keep under 72 characters
- **Conventional format**: Use `<type>: <description>` where type is one of:
  - `feat`: A new feature
  - `fix`: A bug fix
  - `docs`: Documentation changes
  - `style`: Code style changes (formatting, etc.)
  - `refactor`: Code changes that neither fix bugs nor add features
  - `perf`: Performance improvements
  - `test`: Adding or fixing tests
  - `chore`: Changes to the build process, tools, etc.
- **Present tense, imperative mood**: Write commit messages as commands (e.g., "add feature" not "added feature")
- **Concise first line**: Keep the first line under 72 characters

## Reference: Good Commit Examples

Use these as examples when generating commit messages:

- feat: add user authentication system
- fix: resolve memory leak in rendering process
- docs: update API documentation with new endpoints
- refactor: simplify error handling logic in parser
- test: add unit tests for authentication flow
- chore: improve developer tooling setup process
- fix: resolve linter warnings in component files
- fix: patch critical security vulnerability in auth flow
- style: reorganize component structure for better readability
- perf: optimize database query performance
- ci: add automated deployment pipeline

Example commit sequence:

- feat: add user authentication system
- fix: resolve memory leak in rendering process
- docs: update API documentation with new endpoints
- refactor: simplify error handling logic in parser
- test: add unit tests for authentication flow

## Agent Behavior Notes

- **Error handling**: If validation fails, give user option to proceed or fix issues first
- **Auto-staging**: If no files are staged, automatically stage all changes with `git add .`
- **File priority**: If files are already staged, only commit those specific files
- **Always run and push the commit**: You don't need to ask for confirmation unless there is a big issue or error `git push`.
- **Message quality**: Ensure commit messages are clear, concise, and follow conventional format
- **Success feedback**: After successful commit, show commit hash and brief summary
