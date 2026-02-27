---
name: Shared Agent Configuration
description: Documentation for shared configuration files used by primary agents
type: documentation
mode: subagent
hidden: true
version: "1.0.0"
---

# Shared Agent Configuration

This directory contains shared configuration files referenced by multiple primary agents.

## Files

### `delegation-rules.md`

Centralized routing rules that define when and how primary agents should delegate to specialist subagents.

**Purpose**: Single source of truth for domain keyword detection and subagent invocation patterns.

**Usage**: 
- Primary agents **embed** the critical routing table directly in their instructions (for reliability)
- Full detailed rules are maintained here (100+ keywords, examples, workflows)
- Agents can reference this file for complete documentation

**Benefits**:
- Maintain detailed rules in one place
- Agents work even if file reference fails (embedded routing)
- Easy to add new domains and specialists
- Simple to update trigger keywords

**Note**: When adding new domains/specialists, update both:
1. This file (`delegation-rules.md`) - Complete documentation
2. Primary agent files - Condensed routing tables

## Adding New Shared Files

Place any configuration that should be shared across multiple agents in this directory.

## Installation

The installer automatically copies this directory to `~/.config/opencode/agents/_shared/` during installation.
