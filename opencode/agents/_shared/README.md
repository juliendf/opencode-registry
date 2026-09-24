---
name: Shared Agent Configuration
description: Documentation for shared configuration files used by primary agents
type: documentation
mode: subagent
hidden: true
---

# Shared Agent Configuration

This directory contains shared configuration files referenced by multiple primary agents.

## Files

### `delegation-rules.md`

Centralized decision rules for when to load a skill vs invoke a subagent.

**Purpose**: Clear decision table. Prefer skills for knowledge, subagents for tool execution.

**Usage**: 
- Code agents (`build`, `debug`) reference this for skill/subagent routing
- Planning agents (`plan`) reference this for READ-ONLY delegation
- General agent (`ask-me-anything`) references this for research workflow

## Adding New Shared Files

Place any configuration that should be shared across multiple agents in this directory.

## Installation

The installer automatically copies this directory to `~/.config/opencode/agents/_shared/` during installation.
