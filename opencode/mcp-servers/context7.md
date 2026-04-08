---
name: "Context7"
description: "Up-to-date documentation and code examples for any library or framework, pulled directly from official sources. Resolves library IDs and queries versioned docs with code snippets."
type: "mcp-server"
version: "2.1.7"
transport:
  - "stdio"
  - "http"
command: "npx"
args:
  - "-y"
  - "@upstash/context7-mcp"
url: "https://mcp.context7.com/mcp"
env:
  - name: CONTEXT7_API_KEY
    description: "Optional API key for higher rate limits (free tier works without it)"
    required: false
---

# Context7 MCP Server

Up-to-date documentation and code examples for any programming library or framework,
pulled directly from official sources. Stop guessing at outdated APIs -- Context7 resolves
library identifiers and returns versioned, snippet-rich documentation on demand.

## Overview

Use Context7 when an agent needs accurate, current documentation for a library rather than
relying on training data that may be months or years out of date. The workflow is two-step:
first resolve a library name to a Context7-compatible ID, then query that library's docs
with a specific question.

Results include code snippets, source reputation scores, and benchmark quality indicators
so agents can evaluate documentation reliability.

Supports both stdio (local) and hosted HTTP transport (`https://mcp.context7.com/mcp`).
No API key required for basic usage; optional key unlocks higher rate limits.

## Installation

```bash
# Use via npx (no install required)
npx -y @upstash/context7-mcp

# Or install globally
npm install -g @upstash/context7-mcp
```

## Tools Provided

| Tool | Description |
|---|---|
| `resolve-library-id` | Resolve a package/product name to a Context7-compatible library ID. Returns matching libraries with metadata (reputation, snippet count, benchmark score). |
| `query-docs` | Query documentation for a resolved library ID. Returns relevant docs and code examples for a specific question. |

### Typical Workflow

1. Call `resolve-library-id` with the library name (e.g. "next.js", "fastapi")
2. Select the best match from results based on reputation, snippet count, and relevance
3. Call `query-docs` with the library ID and your specific question

## Editor Configuration Examples

### OpenCode

```json
{
  "mcp": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

### OpenCode (HTTP transport)

```json
{
  "mcp": {
    "context7": {
      "url": "https://mcp.context7.com/mcp"
    }
  }
}
```

### Claude Code

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

## Links

- Repository: <https://github.com/upstash/context7>
- npm: <https://www.npmjs.com/package/@upstash/context7-mcp>
- License: MIT
