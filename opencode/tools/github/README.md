# GitHub Tool for OpenCode

Safe wrappers around the `gh` CLI for common GitHub operations.

## Prerequisites

- [GitHub CLI (`gh`)](https://cli.github.com/) installed
- Authenticated: `gh auth login`

## Tools

This package exports multiple tools:

| Tool | Description |
|------|-------------|
| `github_issue` | Manage issues (list, view, create, comment, close, reopen, edit) |
| `github_pr` | Manage pull requests (list, view, create, checkout, diff, checks, review, merge) |
| `github_repo` | Repository operations (view, list, clone, fork) |
| `github_api` | Direct API access (REST and GraphQL) |
| `github_auth` | Check authentication status |

## Safety Features

### Confirmation Required

Destructive actions require explicit `confirmed=true`:

- Closing issues/PRs
- Merging PRs
- DELETE API requests

### Blocked Operations

Some dangerous API endpoints are blocked:

- Deleting repositories
- Deleting organizations
- Deleting user accounts

Use the GitHub web interface for these operations.

### Input Sanitization

All inputs are sanitized to prevent shell injection.

## Examples

### List open issues assigned to me

```text
github_issue(action: "list", state: "open", assignee: "@me")
```

### Create a new issue

```text
github_issue(action: "create", repo: "owner/repo", title: "Bug: X doesn't work", body: "Description...", labels: "bug")
```

### View PR details

```text
github_pr(action: "view", number: 123)
```

### Approve a PR

```text
github_pr(action: "review", number: 123, reviewDecision: "approve", body: "LGTM!")
```

### Merge a PR (with confirmation)

```text
github_pr(action: "merge", number: 123, mergeMethod: "squash", confirmed: true)
```

### Check CI status

```text
github_pr(action: "checks", number: 123)
```

### GraphQL query

```text
github_api(endpoint: "graphql", query: "{ viewer { login } }")
```

## Installation

This tool is part of the opencode-registry. Install via:

```bash
opencode-config install github
# or
opencode-config install --group advanced
```

The tool files will be copied to `~/.config/opencode/tools/github/`.

## License

MIT
