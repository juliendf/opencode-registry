---
name: mcp-builder
description: Guide for creating high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services through well-designed tools. Use when building MCP servers to integrate external APIs or services, whether in Python (FastMCP) or Node/TypeScript (MCP SDK).
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
---

# MCP Server Development Guide

To create high-quality MCP (Model Context Protocol) servers that enable LLMs to effectively interact with external services. Quality is measured by how well LLMs accomplish real-world tasks using the tools provided.

---

# Process

## Phase 1: Deep Research and Planning

### Agent-Centric Design Principles

- **Build for workflows, not API endpoints** — consolidate related operations; design tools that enable complete tasks, not individual API calls
- **Optimize for limited context** — return high-signal information; offer concise vs detailed response formats; use human-readable identifiers; treat context budget as scarce
- **Design actionable error messages** — guide agents toward correct usage; suggest next steps; make errors educational
- **Follow natural task subdivisions** — tool names should reflect how humans think about tasks; group with consistent prefixes
- **Use evaluation-driven development** — create realistic eval scenarios early; let agent feedback drive improvements

### Research

- Fetch MCP protocol spec: `https://modelcontextprotocol.io/llms-full.txt`
- Load reference files: [MCP Best Practices](./reference/mcp_best_practices.md)
- **Python**: Fetch Python SDK README + [Python Implementation Guide](./reference/python_mcp_server.md)
- **Node/TypeScript**: Fetch TypeScript SDK README + [TypeScript Implementation Guide](./reference/node_mcp_server.md)
- Exhaustively study the target API: auth, rate limits, pagination, endpoints, data models, error responses

### Implementation Plan

- **Tool selection**: Prioritize most valuable endpoints; consider which tools combine for complex workflows
- **Shared utilities**: Common API patterns, pagination helpers, filtering/formatting, error handling
- **Input/Output design**: Pydantic v2 / Zod schemas; consistent response formats (JSON/Markdown); configurable detail levels; character limits (~25K tokens)
- **Error handling**: Graceful failures; LLM-friendly natural language messages that prompt next action

---

## Phase 2: Implementation

### Project Setup

- **Python**: Single `.py` file or modules for complex servers; MCP Python SDK + Pydantic v2 with `model_config`; type hints; async/await; module-level constants (`CHARACTER_LIMIT`, `API_BASE_URL`)
- **Node/TypeScript**: Proper project structure with `package.json`, `tsconfig.json`; MCP TypeScript SDK; Zod `.strict()`; strict mode; no `any`; explicit `Promise<T>` returns; build process

### Core Infrastructure First

Build shared utilities before individual tools: API request helpers, error handling, response formatting (JSON + Markdown), pagination, auth/token management.

### Tool Implementation Checklist

For each tool:
- **Input schema**: Pydantic/Zod with constraints; clear field descriptions with examples
- **Docstrings/descriptions**: one-line summary; detailed purpose; parameter types with examples; return type schema; usage examples (when to use, when NOT); error handling guidance
- **Logic**: Use shared utilities; async/await for I/O; proper error handling; support JSON + Markdown; respect pagination; enforce character limits
- **Annotations**: `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`

---

## Phase 3: Review and Refine

### Code Quality Review
- DRY: no duplicated code between tools
- Composability: shared logic extracted to functions
- Consistency: similar operations return similar formats
- Full type coverage and comprehensive docstrings
- All external calls have error handling

### Testing
MCP servers are long-running processes. Safe test methods:
- Use evaluation harness (Phase 4) — recommended
- Run server in tmux to isolate from main process
- Python: `python -m py_compile your_server.py`
- Node/TypeScript: `npm run build` — verify output

### Quality Checklist
See language-specific guide: [Python Guide](./reference/python_mcp_server.md) or [TypeScript Guide](./reference/node_mcp_server.md).

---

## Phase 4: Evaluations

Load [Evaluation Guide](./reference/evaluation.md) for full instructions.

Create 10 evaluation questions testing whether LLMs can use the server to answer realistic, complex questions. Each question must be: independent, read-only, complex (multi-tool), realistic, verifiable by string comparison, and stable over time.

### Output Format

```xml
<evaluation>
  <qa_pair>
    <question>Find discussions about AI model launches with animal codenames. One model needed a specific safety designation that uses the format ASL-X. What number X was being determined for the model named after a spotted wild cat?</question>
    <answer>3</answer>
  </qa_pair>
</evaluation>
```
