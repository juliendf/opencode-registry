import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import { ComponentRegistry } from "../discovery/registry.js";
import { toMcpServerMeta } from "../discovery/scanner.js";
import { generateScaffold } from "../scaffolds/templates.js";
import { validateForWrite } from "../utils/validation.js";
import { writeComponent, deleteComponent } from "../utils/writer.js";
import type { Component, SkillComponent } from "../types.js";
import { readFile } from "node:fs/promises";
import { join, dirname } from "node:path";

/**
 * Create and configure the MCP server with all tools and resources.
 */
export function createMcpServer(registry: ComponentRegistry, opencodeDir: string): McpServer {
  const server = new McpServer(
    {
      name: "opencode-registry",
      version: "0.1.0",
    },
    {
      capabilities: {
        logging: {},
        resources: { subscribe: true },
      },
    },
  );

  registerAgentTools(server, registry, opencodeDir);
  registerSubagentTools(server, registry, opencodeDir);
  registerSkillTools(server, registry, opencodeDir);
  registerCommandTools(server, registry, opencodeDir);
  registerMcpServerTools(server, registry, opencodeDir);
  registerResources(server, registry);

  return server;
}

// ---------------------------------------------------------------------------
// Helper: format component metadata for list responses
// ---------------------------------------------------------------------------

function metaSummary(c: Component): Record<string, unknown> {
  return {
    name: c.name,
    slug: c.slug,
    type: c.type,
    description: c.description,
    version: c.version,
    model_tier: c.model_tier,
    ...(c.category ? { category: c.category } : {}),
  };
}

function fullComponentResponse(c: Component): Record<string, unknown> {
  return {
    ...metaSummary(c),
    frontmatter: c.frontmatter,
    body: c.body,
    relativePath: c.relativePath,
  };
}

function textResult(data: unknown): { content: Array<{ type: "text"; text: string }> } {
  return { content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }] };
}

function errorResult(msg: string): { content: Array<{ type: "text"; text: string }>; isError: true } {
  return { content: [{ type: "text" as const, text: msg }], isError: true };
}

// ---------------------------------------------------------------------------
// Agent Tools
// ---------------------------------------------------------------------------

function registerAgentTools(
  server: McpServer,
  registry: ComponentRegistry,
  opencodeDir: string,
): void {
  server.tool("list_agents", "List all primary agents with metadata", {}, async () => {
    return textResult(registry.getAgents().map(metaSummary));
  });

  server.tool(
    "get_agent",
    "Get full content and metadata for an agent by slug",
    { slug: z.string().describe("Agent slug (filename without .md)") },
    async ({ slug }) => {
      const agent = registry.findBySlug("agent", slug);
      if (!agent) return errorResult(`Agent not found: ${slug}`);
      return textResult(fullComponentResponse(agent));
    },
  );

  server.tool(
    "create_agent",
    "Create a new primary agent. Provide full content or get a scaffold.",
    {
      name: z.string().describe("Display name for the agent"),
      slug: z.string().describe("Filename slug (e.g. 'my-agent')"),
      description: z.string().describe("Brief description of what the agent does"),
      content: z
        .string()
        .optional()
        .describe("Full markdown content. If omitted, a scaffold is generated."),
      model_tier: z
        .enum(["free", "low", "medium", "high"])
        .optional()
        .describe("Model tier (defaults to medium)"),
    },
    async ({ name, slug, description, content, model_tier }) => {
      const body = content ?? generateScaffold("agent", name, description, { model_tier });
      try {
        const path = await writeComponent(opencodeDir, "agent", slug, body);
        await registry.init(); // refresh cache
        return textResult({ created: true, path });
      } catch (err) {
        return errorResult(`Failed to create agent: ${(err as Error).message}`);
      }
    },
  );

  server.tool(
    "delete_agent",
    "Delete an agent by slug",
    {
      slug: z.string().describe("Agent slug to delete"),
      confirm: z.boolean().describe("Must be true to confirm deletion"),
    },
    async ({ slug, confirm }) => {
      if (!confirm) return errorResult("Deletion requires confirm: true");
      try {
        const path = await deleteComponent(opencodeDir, "agent", slug);
        await registry.init();
        return textResult({ deleted: true, path });
      } catch (err) {
        return errorResult(`Failed to delete agent: ${(err as Error).message}`);
      }
    },
  );
}

// ---------------------------------------------------------------------------
// Subagent Tools
// ---------------------------------------------------------------------------

function registerSubagentTools(
  server: McpServer,
  registry: ComponentRegistry,
  opencodeDir: string,
): void {
  server.tool(
    "list_subagents",
    "List all subagents, optionally filtered by category",
    {
      category: z
        .string()
        .optional()
        .describe("Filter by category (e.g. '01-core', '02-languages')"),
    },
    async ({ category }) => {
      const subagents = registry.getSubagents(category);
      return textResult({
        categories: registry.getSubagentCategories(),
        subagents: subagents.map(metaSummary),
      });
    },
  );

  server.tool(
    "get_subagent",
    "Get full content and metadata for a subagent",
    {
      category: z.string().describe("Category directory (e.g. '01-core')"),
      slug: z.string().describe("Subagent slug"),
    },
    async ({ category, slug }) => {
      const subagent = registry.findSubagent(category, slug);
      if (!subagent) return errorResult(`Subagent not found: ${category}/${slug}`);
      return textResult(fullComponentResponse(subagent));
    },
  );

  server.tool(
    "create_subagent",
    "Create a new subagent in a category directory",
    {
      name: z.string().describe("Display name"),
      slug: z.string().describe("Filename slug"),
      category: z.string().describe("Category directory (e.g. '01-core')"),
      description: z.string().describe("Brief description"),
      content: z.string().optional().describe("Full markdown content or omit for scaffold"),
      model_tier: z.enum(["free", "low", "medium", "high"]).optional(),
    },
    async ({ name, slug, category, description, content, model_tier }) => {
      const body = content ?? generateScaffold("subagent", name, description, { model_tier });
      try {
        const path = await writeComponent(opencodeDir, "subagent", slug, body, category);
        await registry.init();
        return textResult({ created: true, path });
      } catch (err) {
        return errorResult(`Failed to create subagent: ${(err as Error).message}`);
      }
    },
  );

  server.tool(
    "delete_subagent",
    "Delete a subagent",
    {
      category: z.string().describe("Category directory"),
      slug: z.string().describe("Subagent slug to delete"),
      confirm: z.boolean().describe("Must be true to confirm deletion"),
    },
    async ({ category, slug, confirm }) => {
      if (!confirm) return errorResult("Deletion requires confirm: true");
      try {
        const path = await deleteComponent(opencodeDir, "subagent", slug, category);
        await registry.init();
        return textResult({ deleted: true, path });
      } catch (err) {
        return errorResult(`Failed to delete subagent: ${(err as Error).message}`);
      }
    },
  );
}

// ---------------------------------------------------------------------------
// Skill Tools
// ---------------------------------------------------------------------------

function registerSkillTools(
  server: McpServer,
  registry: ComponentRegistry,
  opencodeDir: string,
): void {
  server.tool("list_skills", "List all skills with metadata", {}, async () => {
    return textResult(
      registry.getSkills().map((s) => ({
        ...metaSummary(s),
        files: (s as SkillComponent).files,
      })),
    );
  });

  server.tool(
    "get_skill",
    "Get full content and metadata for a skill, including directory file listing",
    { slug: z.string().describe("Skill slug (directory name)") },
    async ({ slug }) => {
      const skill = registry.findBySlug("skill", slug) as SkillComponent | null;
      if (!skill) return errorResult(`Skill not found: ${slug}`);
      return textResult({
        ...fullComponentResponse(skill),
        files: skill.files,
      });
    },
  );

  server.tool(
    "create_skill",
    "Create a new skill (creates directory with SKILL.md)",
    {
      name: z.string().describe("Display name"),
      slug: z.string().describe("Directory name slug"),
      description: z.string().describe("Brief description"),
      content: z.string().optional().describe("Full SKILL.md content or omit for scaffold"),
      model_tier: z.enum(["free", "low", "medium", "high"]).optional(),
    },
    async ({ name, slug, description, content, model_tier }) => {
      const body = content ?? generateScaffold("skill", name, description, { model_tier });
      try {
        const path = await writeComponent(opencodeDir, "skill", slug, body);
        await registry.init();
        return textResult({ created: true, path });
      } catch (err) {
        return errorResult(`Failed to create skill: ${(err as Error).message}`);
      }
    },
  );

  server.tool(
    "delete_skill",
    "Delete a skill (removes entire skill directory)",
    {
      slug: z.string().describe("Skill slug to delete"),
      confirm: z.boolean().describe("Must be true to confirm deletion"),
    },
    async ({ slug, confirm }) => {
      if (!confirm) return errorResult("Deletion requires confirm: true");
      try {
        const path = await deleteComponent(opencodeDir, "skill", slug);
        await registry.init();
        return textResult({ deleted: true, path });
      } catch (err) {
        return errorResult(`Failed to delete skill: ${(err as Error).message}`);
      }
    },
  );
}

// ---------------------------------------------------------------------------
// Command Tools
// ---------------------------------------------------------------------------

function registerCommandTools(
  server: McpServer,
  registry: ComponentRegistry,
  opencodeDir: string,
): void {
  server.tool("list_commands", "List all commands with metadata", {}, async () => {
    return textResult(registry.getCommands().map(metaSummary));
  });

  server.tool(
    "get_command",
    "Get full content and metadata for a command",
    { slug: z.string().describe("Command slug") },
    async ({ slug }) => {
      const cmd = registry.findBySlug("command", slug);
      if (!cmd) return errorResult(`Command not found: ${slug}`);
      return textResult(fullComponentResponse(cmd));
    },
  );

  server.tool(
    "create_command",
    "Create a new command",
    {
      name: z.string().describe("Display name"),
      slug: z.string().describe("Filename slug"),
      description: z.string().describe("Brief description"),
      content: z.string().optional().describe("Full markdown content or omit for scaffold"),
      model_tier: z.enum(["free", "low", "medium", "high"]).optional(),
    },
    async ({ name, slug, description, content, model_tier }) => {
      const body = content ?? generateScaffold("command", name, description, { model_tier });
      try {
        const path = await writeComponent(opencodeDir, "command", slug, body);
        await registry.init();
        return textResult({ created: true, path });
      } catch (err) {
        return errorResult(`Failed to create command: ${(err as Error).message}`);
      }
    },
  );

  server.tool(
    "delete_command",
    "Delete a command",
    {
      slug: z.string().describe("Command slug to delete"),
      confirm: z.boolean().describe("Must be true to confirm deletion"),
    },
    async ({ slug, confirm }) => {
      if (!confirm) return errorResult("Deletion requires confirm: true");
      try {
        const path = await deleteComponent(opencodeDir, "command", slug);
        await registry.init();
        return textResult({ deleted: true, path });
      } catch (err) {
        return errorResult(`Failed to delete command: ${(err as Error).message}`);
      }
    },
  );
}

// ---------------------------------------------------------------------------
// MCP Server Tools
// ---------------------------------------------------------------------------

function registerMcpServerTools(
  server: McpServer,
  registry: ComponentRegistry,
  opencodeDir: string,
): void {
  server.tool("list_mcp_servers", "List all MCP server definitions", {}, async () => {
    return textResult(
      registry.getMcpServers().map((c) => {
        const meta = toMcpServerMeta(c);
        return {
          ...metaSummary(c),
          transport: meta.transport,
          command: meta.command,
          url: meta.url,
        };
      }),
    );
  });

  server.tool(
    "get_mcp_server",
    "Get full MCP server definition including connection details",
    { slug: z.string().describe("MCP server slug") },
    async ({ slug }) => {
      const comp = registry.findBySlug("mcp-server", slug);
      if (!comp) return errorResult(`MCP server not found: ${slug}`);
      const meta = toMcpServerMeta(comp);
      return textResult({
        ...fullComponentResponse(comp),
        transport: meta.transport,
        command: meta.command,
        args: meta.args,
        env: meta.env,
        url: meta.url,
      });
    },
  );

  server.tool(
    "create_mcp_server",
    "Create a new MCP server definition",
    {
      name: z.string().describe("Display name"),
      slug: z.string().describe("Filename slug"),
      description: z.string().describe("Brief description"),
      transport: z
        .union([z.enum(["stdio", "http"]), z.array(z.enum(["stdio", "http"]))])
        .describe('Transport type(s) — "stdio", "http", or ["stdio", "http"]'),
      command: z.string().optional().describe("Command to launch (for stdio)"),
      args: z.array(z.string()).optional().describe("Command arguments (for stdio)"),
      url: z.string().optional().describe("Endpoint URL (for http)"),
      content: z.string().optional().describe("Full markdown content or omit for scaffold"),
    },
    async ({ name, slug, description, transport, command, args, url, content }) => {
      const errors = validateForWrite("mcp-server", {
        description,
        transport,
        command,
        url,
      });
      if (errors.length > 0) {
        return errorResult(`Validation errors: ${JSON.stringify(errors)}`);
      }

      const body =
        content ??
        generateScaffold("mcp-server", name, description, {
          transport,
          command,
          args,
          url,
        });
      try {
        const path = await writeComponent(opencodeDir, "mcp-server", slug, body);
        await registry.init();
        return textResult({ created: true, path });
      } catch (err) {
        return errorResult(`Failed to create MCP server: ${(err as Error).message}`);
      }
    },
  );

  server.tool(
    "delete_mcp_server",
    "Delete an MCP server definition",
    {
      slug: z.string().describe("MCP server slug to delete"),
      confirm: z.boolean().describe("Must be true to confirm deletion"),
    },
    async ({ slug, confirm }) => {
      if (!confirm) return errorResult("Deletion requires confirm: true");
      try {
        const path = await deleteComponent(opencodeDir, "mcp-server", slug);
        await registry.init();
        return textResult({ deleted: true, path });
      } catch (err) {
        return errorResult(`Failed to delete MCP server: ${(err as Error).message}`);
      }
    },
  );
}

// ---------------------------------------------------------------------------
// Resources
// ---------------------------------------------------------------------------

function registerResources(server: McpServer, registry: ComponentRegistry): void {
  // Agents
  server.resource(
    "agent",
    new ResourceTemplate("opencode://agents/{slug}", { list: undefined }),
    {
      description: "Agent component content",
      mimeType: "text/markdown",
    },
    async (uri, { slug }) => {
      const agent = registry.findBySlug("agent", slug as string);
      if (!agent) return { contents: [] };
      return {
        contents: [{ uri: uri.href, mimeType: "text/markdown", text: agent.rawContent }],
      };
    },
  );

  // Subagents
  server.resource(
    "subagent",
    new ResourceTemplate("opencode://subagents/{category}/{slug}", { list: undefined }),
    {
      description: "Subagent component content",
      mimeType: "text/markdown",
    },
    async (uri, { category, slug }) => {
      const subagent = registry.findSubagent(category as string, slug as string);
      if (!subagent) return { contents: [] };
      return {
        contents: [{ uri: uri.href, mimeType: "text/markdown", text: subagent.rawContent }],
      };
    },
  );

  // Skills
  server.resource(
    "skill",
    new ResourceTemplate("opencode://skills/{slug}", { list: undefined }),
    {
      description: "Skill component content (SKILL.md + file listing)",
      mimeType: "text/markdown",
    },
    async (uri, { slug }) => {
      const skill = registry.findBySlug("skill", slug as string) as SkillComponent | null;
      if (!skill) return { contents: [] };

      const contents: Array<{ uri: string; mimeType: string; text: string }> = [
        { uri: uri.href, mimeType: "text/markdown", text: skill.rawContent },
      ];

      // Include other files in the skill directory
      if (skill.files.length > 0) {
        const skillDir = dirname(skill.absolutePath);
        for (const file of skill.files) {
          try {
            const filePath = join(skillDir, file);
            const fileContent = await readFile(filePath, "utf-8");
            contents.push({
              uri: `${uri.href}/${file}`,
              mimeType: "text/plain",
              text: fileContent,
            });
          } catch {
            // Skip unreadable files
          }
        }
      }

      return { contents };
    },
  );

  // Commands
  server.resource(
    "command",
    new ResourceTemplate("opencode://commands/{slug}", { list: undefined }),
    {
      description: "Command component content",
      mimeType: "text/markdown",
    },
    async (uri, { slug }) => {
      const cmd = registry.findBySlug("command", slug as string);
      if (!cmd) return { contents: [] };
      return {
        contents: [{ uri: uri.href, mimeType: "text/markdown", text: cmd.rawContent }],
      };
    },
  );

  // MCP Servers
  server.resource(
    "mcp-server",
    new ResourceTemplate("opencode://mcp-servers/{slug}", { list: undefined }),
    {
      description: "MCP server definition content",
      mimeType: "text/markdown",
    },
    async (uri, { slug }) => {
      const comp = registry.findBySlug("mcp-server", slug as string);
      if (!comp) return { contents: [] };
      return {
        contents: [{ uri: uri.href, mimeType: "text/markdown", text: comp.rawContent }],
      };
    },
  );
}
