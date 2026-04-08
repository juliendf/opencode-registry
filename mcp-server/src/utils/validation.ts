import type { ComponentType, McpTransport } from "../types.js";

export interface ValidationError {
  field: string;
  message: string;
}

/**
 * Normalize a transport value to an array for validation.
 * Accepts a single string or an array of strings.
 */
function normalizeTransportInput(raw: unknown): string[] {
  if (Array.isArray(raw)) return raw;
  if (typeof raw === "string") return [raw];
  return [];
}

const VALID_TRANSPORTS: ReadonlySet<string> = new Set(["stdio", "http"]);

/**
 * Validate frontmatter for a component being created (strict mode).
 * Returns an array of validation errors (empty = valid).
 */
export function validateForWrite(
  type: ComponentType,
  frontmatter: Record<string, unknown>,
): ValidationError[] {
  const errors: ValidationError[] = [];

  // Common required fields
  if (!frontmatter.description || typeof frontmatter.description !== "string") {
    errors.push({
      field: "description",
      message: "description is required and must be a string",
    });
  }

  // Type-specific validation
  if (type === "mcp-server") {
    const transports = normalizeTransportInput(frontmatter.transport);

    if (transports.length === 0) {
      errors.push({
        field: "transport",
        message: 'transport is required — provide "stdio", "http", or an array of both',
      });
    }

    const invalid = transports.filter((t) => !VALID_TRANSPORTS.has(t));
    if (invalid.length > 0) {
      errors.push({
        field: "transport",
        message: `Invalid transport value(s): ${invalid.join(", ")}. Must be "stdio" or "http"`,
      });
    }

    const validTransports = transports.filter((t): t is McpTransport =>
      VALID_TRANSPORTS.has(t),
    );

    if (validTransports.includes("stdio")) {
      if (!frontmatter.command || typeof frontmatter.command !== "string") {
        errors.push({
          field: "command",
          message: "command is required when transport includes stdio",
        });
      }
    }

    if (validTransports.includes("http")) {
      if (!frontmatter.url || typeof frontmatter.url !== "string") {
        errors.push({
          field: "url",
          message: "url is required when transport includes http",
        });
      }
    }
  }

  // Validate model_tier if provided
  if (frontmatter.model_tier) {
    const validTiers = ["free", "low", "medium", "high"];
    if (!validTiers.includes(frontmatter.model_tier as string)) {
      errors.push({
        field: "model_tier",
        message: `model_tier must be one of: ${validTiers.join(", ")}`,
      });
    }
  }

  return errors;
}
