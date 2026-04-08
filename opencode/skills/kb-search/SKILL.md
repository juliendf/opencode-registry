---
model_tier: "medium"
name: kb-search
description: Search internal knowledge bases and public library documentation to answer questions grounded in authoritative sources. Use when the user asks questions that benefit from looking up actual documentation rather than reasoning from memory -- e.g. library best practices, framework patterns, technology recommendations, or domain-specific guidance.
compatibility: opencode
license: MIT
metadata:
  version: "1.0.0"
---

# Knowledge Base Search

Search first, then reason. This skill retrieves authoritative knowledge from internal knowledge bases (via Ragclaw) and public library/framework documentation (via Context7), then synthesizes a grounded answer with clear provenance.

## When to Use This Skill

Activate this skill when the user asks a question where **looking it up** is better than **reasoning from memory**:

- "How does X library handle Y?"
- "What's the recommended pattern for Z in framework W?"
- "I need to design a service using [specific tech] -- what are the best practices?"
- "What do we have documented about [domain topic]?"
- "I need to build X with Y, advise me on patterns to use"
- "What does the documentation say about configuring Z?"

**Do NOT use this skill for:**

- Pure coding tasks ("write me a function that does X")
- General conversation or clarification questions
- Tasks where the user already provided all necessary context

## Workflow

### Step 1: Analyze the Query

Before searching, identify:

1. **Domain concepts** -- what internal/project-specific knowledge might be relevant?
2. **Specific libraries or frameworks** -- are any technologies explicitly mentioned by name?
3. **The core question** -- what does the user actually need to know?

### Step 2: Search Internal Knowledge (Ragclaw)

Always start with internal knowledge -- your team may have standards or opinions that override generic documentation.

#### 2.1 Discover Available Knowledge Bases

Use `kb_list_databases` to list all available knowledge bases and their descriptions/keywords.

- If **no knowledge bases exist**, skip to Step 3 and note the gap in the output (see Step 4).
- If **one database exists**, search it.
- If **multiple databases exist**, select the most relevant one(s) based on their description and keywords matching the user's query. Search at most 2 databases to stay focused.

#### 2.2 Search the Knowledge Base

Use `kb_search` with a well-crafted query derived from the user's question. Target the specific concepts, not the full question verbatim.

- Use the `db` parameter to target the selected knowledge base(s).
- Set an appropriate `limit` (5 results is a good default).
- If results are poor or empty, try one reformulated query before giving up.

### Step 3: Search Public Documentation (Context7)

Use Context7 to look up official library and framework documentation. **Only do this if the user's query mentions specific technologies by name.**

If the query is purely conceptual with no specific library or framework named (e.g. "how should I structure a microservice?"), skip this step entirely.

#### 3.1 Resolve Library IDs

For each technology mentioned (up to 2-3 max), use `context7_resolve-library-id`:

- Pass the user's question as the `query` parameter for relevance ranking.
- Select the best match based on name similarity, source reputation, and snippet coverage.

#### 3.2 Query Documentation

For each resolved library ID, use `context7_query-docs`:

- Craft a specific query focused on what the user needs to know about that library.
- Be precise -- "How to set up authentication middleware in Express.js" is better than "auth".

**Important:** Context7 tools are limited to 3 calls each per question. Budget accordingly when multiple libraries are involved.

### Step 4: Synthesize and Respond

Combine all retrieved knowledge into a structured research brief. Use the following format:

```python
## Internal Knowledge Base

[Findings from Ragclaw searches. Include the database name for each result.]
[Reference specific documents or chunks that informed the answer.]

If no knowledge bases were configured:
> No internal knowledge bases are configured. You can create one by indexing
> relevant documentation, URLs, or files using the Ragclaw `kb_add` tool.
> This will improve future searches with project-specific context.

If knowledge bases exist but returned no relevant results:
> No relevant results found in [database name(s)]. Consider indexing
> documentation related to [topic] to improve future searches.

## Library Documentation

[Findings from Context7 queries. Include the library name for each result.]
[Reference specific documentation sections, code examples, or patterns.]

If Context7 was skipped (no specific technology mentioned):
> No specific library or framework was referenced -- skipped public
> documentation lookup.

If Context7 returned no useful results:
> No relevant documentation found for [library name(s)].

## Synthesis & Recommendation

[Combined reasoning that integrates both internal and public knowledge.]
[Clearly call out where internal standards differ from or extend public docs.]
[Provide actionable recommendations grounded in the retrieved sources.]
[If sources conflict, acknowledge the conflict and explain your reasoning.]
```

## Guidelines

### Query Crafting

- Extract the core concepts from the user's question -- don't search the full question verbatim.
- For Ragclaw, use domain-specific terminology that would appear in internal docs.
- For Context7, use the library's own terminology and concepts.

### Source Priority

- Internal knowledge takes priority over public documentation when they conflict.
- If internal docs reference specific versions or configurations, honor those.
- Public documentation fills gaps where internal knowledge is silent.

### Transparency

- Always cite which source informed each part of the answer.
- If a recommendation is your own synthesis (not directly from a source), say so.
- Never present retrieved information as your own reasoning or vice versa.

### Do Not Chase Source Files

- Ragclaw search results include source paths as metadata. **Never** use these paths to read, glob, or open the original files.
- Knowledge bases are portable — they may have been indexed on a different machine, in a different directory, or from URLs that are no longer accessible.
- The chunk text returned by `kb_search` is the complete, authoritative content. If the chunk doesn't contain enough detail, search with a different query instead of trying to read the source file.

### Handling Uncertainty

- If both sources return nothing useful, say so clearly and provide the best answer you can from general knowledge, clearly labeled as such.
- Don't hallucinate sources or fabricate documentation references.
