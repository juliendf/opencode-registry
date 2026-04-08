---
model_tier: "medium"
name: web-search
description: Search the live web to answer questions that require up-to-date information. Use when the user asks about current events, recent releases, live data, comparisons of real-world services, or anything where fresh internet results are more reliable than reasoning from memory.
compatibility: opencode
license: MIT
metadata:
  version: "1.0.0"
---

# Web Search

Search the web first, then reason. This skill uses the Brave Search API (via the `brave-search-mcp-server`) to retrieve live web results, then synthesizes a grounded answer with citations. Falls back to `webfetch` if the Brave MCP server is not configured.

## Prerequisites

This skill requires the [Brave Search MCP Server](https://github.com/brave/brave-search-mcp-server) to be installed and configured with a valid `BRAVE_API_KEY` environment variable. If the `brave_web_search` tool is not available, the skill falls back to the built-in `webfetch` tool with reduced capabilities.

## When to Use This Skill

Activate this skill when the user asks a question where **live web information** is better than **reasoning from memory**:

- "What's the latest version of X?"
- "How does service A compare to service B in 2025?"
- "What's the current status of [project/issue/event]?"
- "Find me tutorials on how to do X with Y"
- "What are people saying about [technology/tool]?"
- "Is there a known fix for [error message]?"

**Do NOT use this skill for:**

- Questions answerable from the codebase or local context
- Pure coding tasks ("write me a function that does X")
- Documentation lookups for specific libraries (use `kb-search` instead)
- General conversation or clarification questions

## Workflow

### Step 1: Analyze the Query

Before searching, identify:

1. **The core question** -- what does the user actually need to know?
2. **Time sensitivity** -- does the question require recent results? If so, determine the appropriate `freshness` value (`pd` = past day, `pw` = past week, `pm` = past month, `py` = past year).
3. **Search terms** -- distill the question into concise, effective search keywords. Strip filler words and focus on the specific concepts.

### Step 2: Search the Web

#### 2.1 Primary: Brave Web Search

If `brave_web_search` is available, use it with a well-crafted query.

**Parameter guidance:**

- `query` (required): Concise search terms, not the user's full question verbatim. Max 400 chars, 50 words.
- `count`: Start with 5-10 results. Use fewer for simple factual queries, more for comparison or research questions.
- `freshness`: Set this when recency matters. Omit it for evergreen topics.
- `safesearch`: Leave as default (`moderate`) unless the user's query requires otherwise.
- `summary`: Set to `true` when an AI-generated summary would help synthesize results.

**Example:**

```json
{
  "query": "Next.js 15 server actions breaking changes",
  "count": 5,
  "freshness": "pm",
  "summary": true
}
```

#### 2.2 Fallback: WebFetch

If `brave_web_search` is not available, inform the user that the Brave Search MCP server is not configured and fall back to `webfetch`:

1. Construct a search URL: `https://search.brave.com/search?q=<encoded query>`
2. Fetch the page with `webfetch` in markdown format.
3. Extract relevant results from the rendered content.

Note: The fallback is less structured and may yield fewer results. Recommend the user configure the Brave MCP server for better results.

### Step 3: Evaluate and Refine

After receiving results, evaluate their quality:

- **Sufficient?** If the results clearly answer the user's question, proceed to Step 4.
- **Insufficient?** If results are off-topic, too broad, or missing key information, refine the query and search again. Try:
  - More specific terms
  - Different phrasing or synonyms
  - Adding or removing the `freshness` filter
  - Narrowing with additional context (e.g., add the programming language or framework name)

**Cap: maximum 3 searches per question.** If three attempts don't yield useful results, proceed to Step 4 with whatever you have and clearly state the limitation.

### Step 4: Synthesize and Respond

Combine the retrieved results into a clear, actionable answer:

1. **Lead with the answer** -- don't make the user read through all the search results to find the conclusion.
2. **Cite every claim** -- use inline links: `[Source Title](url)`. Every factual statement derived from search results must have a citation.
3. **Note recency** -- if results have dates, mention them so the user knows how current the information is.
4. **Acknowledge gaps** -- if the search didn't fully answer the question, say so. Don't fill gaps with speculation.

**Response format:**

```markdown
[Direct answer to the user's question, with inline citations.]

[Supporting details, comparisons, or context as needed.]

[If applicable: caveats, conflicting information, or gaps in the results.]
```

## Guidelines

### Query Crafting

- Extract core concepts from the user's question -- don't search the full question verbatim.
- Use specific technical terms, library names, error messages, or version numbers when available.
- For "how to" questions, include the technology stack in the query.
- For error messages, quote the distinctive part of the error.

### Citation Standards

- Always cite sources with inline markdown links: `[Title](url)`.
- If multiple sources agree on a fact, cite the most authoritative one.
- If sources conflict, cite both and explain the discrepancy.
- Never present search results as your own reasoning or vice versa.

### Handling Uncertainty

- If search results are empty or irrelevant after 3 attempts, say so clearly and provide the best answer you can from general knowledge, clearly labeled as such.
- Don't hallucinate URLs or fabricate sources.
- If results are outdated relative to the user's question, flag this explicitly.
