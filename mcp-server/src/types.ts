/**
 * Component types supported by the registry.
 */
export const COMPONENT_TYPES = [
  "agent",
  "subagent",
  "skill",
  "command",
  "mcp-server",
] as const;

export type ComponentType = (typeof COMPONENT_TYPES)[number];

/**
 * Parsed frontmatter metadata common to all component types.
 */
export interface ComponentMeta {
  name: string;
  slug: string;
  type: ComponentType;
  description: string;
  version?: string;
  model_tier?: string;
  /** Subagent category directory (e.g. "01-core") */
  category?: string;
  /** Relative path from the opencode directory root */
  relativePath: string;
  /** Absolute path on disk */
  absolutePath: string;
  /** All raw frontmatter fields */
  frontmatter: Record<string, unknown>;
}

/**
 * Full component including parsed metadata and raw content.
 */
export interface Component extends ComponentMeta {
  /** Full markdown content including frontmatter */
  rawContent: string;
  /** Markdown body without frontmatter */
  body: string;
}

export type McpTransport = "stdio" | "http";

/**
 * MCP server definition extends base component with connection details.
 * A server can support one or both transports.
 */
export interface McpServerMeta extends ComponentMeta {
  type: "mcp-server";
  /** Supported transports — single value or array */
  transport: McpTransport[];
  /** Command to launch the server (stdio transport) */
  command?: string;
  /** Command arguments (stdio transport) */
  args?: string[];
  /** Required/optional environment variables */
  env?: Array<{ name: string; description: string; required: boolean }>;
  /** Endpoint URL (http transport) */
  url?: string;
}

/**
 * Skill component with additional file listing.
 */
export interface SkillComponent extends Component {
  type: "skill";
  /** Other files in the skill directory besides SKILL.md */
  files: string[];
}
