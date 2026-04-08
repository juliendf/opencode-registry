import matter from "gray-matter";
import { readdir, readFile, stat } from "node:fs/promises";
import { basename, join, relative } from "node:path";
import type {
  Component,
  ComponentMeta,
  ComponentType,
  McpServerMeta,
  McpTransport,
  SkillComponent,
} from "../types.js";

/**
 * Slugify a string for use as a filename.
 * Converts to lowercase, replaces spaces/underscores with hyphens,
 * strips non-alphanumeric characters (except hyphens).
 */
export function slugify(input: string): string {
  return input
    .toLowerCase()
    .replace(/[\s_]+/g, "-")
    .replace(/[^a-z0-9-]/g, "")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

/**
 * Parse a markdown file and extract frontmatter + body.
 */
function parseMarkdown(
  raw: string,
  filePath: string,
): { frontmatter: Record<string, unknown>; body: string } | null {
  try {
    const parsed = matter(raw);
    return {
      frontmatter: parsed.data as Record<string, unknown>,
      body: parsed.content,
    };
  } catch {
    // Lenient on read: skip malformed files
    console.error(`[discovery] Failed to parse frontmatter: ${filePath}`);
    return null;
  }
}

/**
 * Build ComponentMeta from parsed frontmatter and file path info.
 */
function buildMeta(
  frontmatter: Record<string, unknown>,
  type: ComponentType,
  slug: string,
  relativePath: string,
  absolutePath: string,
  category?: string,
): ComponentMeta {
  return {
    name: (frontmatter.name as string) ?? slug,
    slug,
    type,
    description: (frontmatter.description as string) ?? "",
    version: frontmatter.version as string | undefined,
    model_tier: frontmatter.model_tier as string | undefined,
    category,
    relativePath,
    absolutePath,
    frontmatter,
  };
}

/**
 * Check if a directory exists.
 */
async function dirExists(path: string): Promise<boolean> {
  try {
    const s = await stat(path);
    return s.isDirectory();
  } catch {
    return false;
  }
}

/**
 * Check if a file exists.
 */
async function fileExists(path: string): Promise<boolean> {
  try {
    const s = await stat(path);
    return s.isFile();
  } catch {
    return false;
  }
}

/**
 * Scan a flat directory of .md files and return components.
 */
async function scanFlatDir(
  dir: string,
  type: ComponentType,
  opencodeDir: string,
): Promise<Component[]> {
  if (!(await dirExists(dir))) return [];

  const entries = await readdir(dir);
  const components: Component[] = [];

  for (const entry of entries) {
    if (!entry.endsWith(".md")) continue;
    // Skip directories and hidden files
    const filePath = join(dir, entry);
    if (!(await fileExists(filePath))) continue;

    const raw = await readFile(filePath, "utf-8");
    const parsed = parseMarkdown(raw, filePath);
    if (!parsed) continue;

    const slug = basename(entry, ".md");
    const relPath = relative(opencodeDir, filePath);

    components.push({
      ...buildMeta(parsed.frontmatter, type, slug, relPath, filePath),
      rawContent: raw,
      body: parsed.body,
    });
  }

  return components;
}

/**
 * Scan agents directory (top-level .md files, mode=primary).
 */
async function scanAgents(opencodeDir: string): Promise<Component[]> {
  const agentsDir = join(opencodeDir, "agents");
  return scanFlatDir(agentsDir, "agent", opencodeDir);
}

/**
 * Scan subagents across all category directories.
 */
async function scanSubagents(opencodeDir: string): Promise<Component[]> {
  const subagentsDir = join(opencodeDir, "agents", "subagents");
  if (!(await dirExists(subagentsDir))) return [];

  const categories = await readdir(subagentsDir);
  const components: Component[] = [];

  for (const category of categories) {
    const categoryDir = join(subagentsDir, category);
    if (!(await dirExists(categoryDir))) continue;

    const entries = await readdir(categoryDir);
    for (const entry of entries) {
      if (!entry.endsWith(".md")) continue;
      const filePath = join(categoryDir, entry);
      if (!(await fileExists(filePath))) continue;

      const raw = await readFile(filePath, "utf-8");
      const parsed = parseMarkdown(raw, filePath);
      if (!parsed) continue;

      const slug = basename(entry, ".md");
      const relPath = relative(opencodeDir, filePath);

      components.push({
        ...buildMeta(
          parsed.frontmatter,
          "subagent",
          slug,
          relPath,
          filePath,
          category,
        ),
        rawContent: raw,
        body: parsed.body,
      });
    }
  }

  return components;
}

/**
 * Scan skills directories (each skill is a dir with SKILL.md).
 */
async function scanSkills(opencodeDir: string): Promise<SkillComponent[]> {
  const skillsDir = join(opencodeDir, "skills");
  if (!(await dirExists(skillsDir))) return [];

  const entries = await readdir(skillsDir);
  const components: SkillComponent[] = [];

  for (const entry of entries) {
    const skillDir = join(skillsDir, entry);
    if (!(await dirExists(skillDir))) continue;

    const skillFile = join(skillDir, "SKILL.md");
    if (!(await fileExists(skillFile))) continue;

    const raw = await readFile(skillFile, "utf-8");
    const parsed = parseMarkdown(raw, skillFile);
    if (!parsed) continue;

    const slug = entry;
    const relPath = relative(opencodeDir, skillFile);

    // List all files in the skill directory
    const allFiles = await readdir(skillDir, { recursive: true });
    const otherFiles = (allFiles as string[])
      .filter((f) => f !== "SKILL.md");

    const meta = buildMeta(parsed.frontmatter, "skill", slug, relPath, skillFile);
    const skillComponent: SkillComponent = {
      ...meta,
      type: "skill" as const,
      rawContent: raw,
      body: parsed.body,
      files: otherFiles,
    };
    components.push(skillComponent);
  }

  return components;
}

/**
 * Scan commands directory.
 */
async function scanCommands(opencodeDir: string): Promise<Component[]> {
  const commandsDir = join(opencodeDir, "commands");
  return scanFlatDir(commandsDir, "command", opencodeDir);
}

/**
 * Scan MCP server definitions.
 */
async function scanMcpServers(opencodeDir: string): Promise<Component[]> {
  const serversDir = join(opencodeDir, "mcp-servers");
  return scanFlatDir(serversDir, "mcp-server", opencodeDir);
}

/**
 * Normalize a transport field from frontmatter into a string array.
 * Accepts: "stdio", "http", ["stdio", "http"], or missing (defaults to ["stdio"]).
 */
function normalizeTransport(raw: unknown): McpTransport[] {
  if (Array.isArray(raw)) {
    return raw.filter(
      (t): t is McpTransport => t === "stdio" || t === "http",
    );
  }
  if (raw === "stdio" || raw === "http") return [raw];
  return ["stdio"];
}

/**
 * Extract MCP server-specific metadata from a component.
 */
export function toMcpServerMeta(component: Component): McpServerMeta {
  const fm = component.frontmatter;
  return {
    ...component,
    type: "mcp-server",
    transport: normalizeTransport(fm.transport),
    command: fm.command as string | undefined,
    args: fm.args as string[] | undefined,
    env: fm.env as
      | Array<{ name: string; description: string; required: boolean }>
      | undefined,
    url: fm.url as string | undefined,
  };
}

/**
 * Result of a full discovery scan.
 */
export interface DiscoveryResult {
  agents: Component[];
  subagents: Component[];
  skills: SkillComponent[];
  commands: Component[];
  mcpServers: Component[];
}

/**
 * Discover all components in an opencode directory.
 */
export async function discoverAll(
  opencodeDir: string,
): Promise<DiscoveryResult> {
  const [agents, subagents, skills, commands, mcpServers] = await Promise.all([
    scanAgents(opencodeDir),
    scanSubagents(opencodeDir),
    scanSkills(opencodeDir),
    scanCommands(opencodeDir),
    scanMcpServers(opencodeDir),
  ]);

  return { agents, subagents, skills, commands, mcpServers };
}

export { dirExists, fileExists };
