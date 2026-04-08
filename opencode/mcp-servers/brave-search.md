---
name: "Brave Search"
description: "Web, news, image, video, and local search powered by Brave's independent search index. Includes AI-generated summaries from multiple sources. Requires API key."
type: "mcp-server"
version: "2.0.75"
transport:
  - "stdio"
  - "http"
command: "npx"
args:
  - "-y"
  - "@anthropic-ai/brave-search-mcp@latest"
env:
  - name: BRAVE_API_KEY
    description: "Brave Search API key (required). Get one at https://brave.com/search/api/"
    required: true
  - name: BRAVE_MCP_TRANSPORT
    description: "Transport mode: 'stdio' (default) or 'http'"
    required: false
---

# Brave Search MCP Server

Web, news, image, video, and local search powered by Brave's independent search index.
Provides rich structured results with metadata, AI-generated summaries, and specialized
search verticals -- all through a single MCP server.

## Overview

Use Brave Search when an agent needs live web information: current events, documentation
lookups, local business details, news articles, video content, or image search. The server
exposes six specialized tools covering different search verticals, plus an AI summarizer
that synthesizes results from multiple sources into concise answers.

Requires a Brave Search API key (free tier available). Supports both stdio and HTTP
transports.

## Installation

```bash
# Use via npx (no install required)
npx -y @anthropic-ai/brave-search-mcp@latest

# Or install globally
npm install -g @anthropic-ai/brave-search-mcp
```

## Tools Provided

| Tool | Description |
|---|---|
| `brave_web_search` | General web search with rich metadata, FAQ, discussions, and more |
| `brave_local_search` | Local business/place search with ratings, hours, phone numbers |
| `brave_news_search` | Recent news articles filtered by freshness (24h, 7d, 31d, 1y) |
| `brave_video_search` | Video search with duration, thumbnails, and metadata |
| `brave_image_search` | Image search with source URLs and metadata |
| `brave_summarizer` | AI-generated summary of web search results (requires Pro plan + prior search with `summary=true`) |

### Common Parameters

Most tools support:

- **`count`** - Number of results (1-20 for web, up to 50 for news/video)
- **`country`** - 2-letter country code for result locality
- **`freshness`** - Filter by discovery date (`pd`, `pw`, `pm`, `py`, or date range)
- **`safesearch`** - Content filtering (`off`, `moderate`, `strict`)
- **`search_lang`** - Language preference for results

## API Key Setup

1. Go to <https://brave.com/search/api/>
2. Create a free account (2,000 queries/month on free tier)
3. Copy your API key
4. Set the `BRAVE_API_KEY` environment variable

## Editor Configuration Examples

### OpenCode

```json
{
  "mcp": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/brave-search-mcp@latest"],
      "env": {
        "BRAVE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Claude Code

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/brave-search-mcp@latest"],
      "env": {
        "BRAVE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Links

- Repository: <https://github.com/anthropics/brave-search-mcp>
- npm: <https://www.npmjs.com/package/@anthropic-ai/brave-search-mcp>
- Brave Search API: <https://brave.com/search/api/>
- License: MIT
