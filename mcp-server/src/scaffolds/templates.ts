import type { ComponentType } from "../types.js";

/**
 * Generate scaffold content for a new component.
 */
export function generateScaffold(
  type: ComponentType,
  name: string,
  description: string,
  options?: Record<string, unknown>,
): string {
  switch (type) {
    case "agent":
      return agentScaffold(name, description, options);
    case "subagent":
      return subagentScaffold(name, description, options);
    case "skill":
      return skillScaffold(name, description, options);
    case "command":
      return commandScaffold(name, description, options);
    case "mcp-server":
      return mcpServerScaffold(name, description, options);
  }
}

function agentScaffold(
  name: string,
  description: string,
  options?: Record<string, unknown>,
): string {
  const modelTier = (options?.model_tier as string) ?? "medium";
  return `---
description: "${escapeYaml(description)}"
mode: primary
model_tier: "${modelTier}"
temperature: 0.2
tools:
  bash: true
  edit: true
  write: true
  read: true
  grep: true
  glob: true
  list: true
  patch: true
  todowrite: true
  todoread: true
  webfetch: true
---

# ${name}

${description}

## Instructions

<!-- Add your agent instructions here -->
`;
}

function subagentScaffold(
  name: string,
  description: string,
  options?: Record<string, unknown>,
): string {
  const modelTier = (options?.model_tier as string) ?? "high";
  return `---
description: "${escapeYaml(description)}"
mode: subagent
model_tier: "${modelTier}"
temperature: 0.3
tools:
  bash: true
  edit: true
  glob: true
  grep: true
  list: true
  patch: true
  read: true
  todoread: true
  todowrite: true
  webfetch: true
  write: true
---

# ${name}

${description}

## Expertise

<!-- Describe this subagent's area of expertise -->

## Instructions

<!-- Add your subagent instructions here -->
`;
}

function skillScaffold(
  name: string,
  description: string,
  options?: Record<string, unknown>,
): string {
  const modelTier = (options?.model_tier as string) ?? "medium";
  return `---
model_tier: "${modelTier}"
name: "${escapeYaml(name)}"
description: "${escapeYaml(description)}"
metadata:
  version: "1.0.0"
---

# ${name}

${description}

<!-- Add your skill instructions here -->
`;
}

function commandScaffold(
  name: string,
  description: string,
  options?: Record<string, unknown>,
): string {
  const modelTier = (options?.model_tier as string) ?? "free";
  return `---
description: "${escapeYaml(description)}"
model_tier: "${modelTier}"
version: "1.0.0"
---

# ${name}

${description}

## Instructions for Agent

When the user runs this command, execute the following workflow:

1. <!-- Step 1 -->
2. <!-- Step 2 -->
3. <!-- Step 3 -->
`;
}

function mcpServerScaffold(
  name: string,
  description: string,
  options?: Record<string, unknown>,
): string {
  // Normalize transport to array
  const rawTransport = options?.transport;
  let transports: string[];
  if (Array.isArray(rawTransport)) {
    transports = rawTransport.filter((t) => t === "stdio" || t === "http");
  } else if (rawTransport === "stdio" || rawTransport === "http") {
    transports = [rawTransport];
  } else {
    transports = ["stdio"];
  }

  const command = (options?.command as string) ?? "";
  const args = (options?.args as string[]) ?? [];
  const url = (options?.url as string) ?? "";

  // Build YAML transport array
  const transportYaml = `transport:\n${transports.map((t) => `  - "${t}"`).join("\n")}`;

  // Build connection fields based on which transports are included
  const connectionParts: string[] = [];
  if (transports.includes("stdio")) {
    connectionParts.push(`command: "${escapeYaml(command)}"`);
    const argsYaml =
      args.length > 0
        ? `args: [${args.map((a) => `"${escapeYaml(a)}"`).join(", ")}]`
        : "args: []";
    connectionParts.push(argsYaml);
  }
  if (transports.includes("http")) {
    connectionParts.push(`url: "${escapeYaml(url)}"`);
  }

  const connectionFields = connectionParts.join("\n");

  return `---
name: "${escapeYaml(name)}"
description: "${escapeYaml(description)}"
type: "mcp-server"
version: "1.0.0"
${transportYaml}
${connectionFields}
env: []
---

# ${name}

${description}

## Overview

<!-- Describe what this MCP server does -->

## Tools Provided

<!-- List the tools this server exposes -->

## Setup

<!-- Installation and configuration instructions -->
`;
}

function escapeYaml(s: string): string {
  return s.replace(/"/g, '\\"');
}
