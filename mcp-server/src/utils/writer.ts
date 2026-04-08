import { mkdir, rm, stat, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import type { ComponentType } from "../types.js";
import { slugify } from "../discovery/scanner.js";

/**
 * Resolve the target file path for a component.
 */
export function resolveComponentPath(
  opencodeDir: string,
  type: ComponentType,
  slug: string,
  category?: string,
): string {
  switch (type) {
    case "agent":
      return join(opencodeDir, "agents", `${slug}.md`);
    case "subagent":
      if (!category) throw new Error("category is required for subagents");
      return join(opencodeDir, "agents", "subagents", category, `${slug}.md`);
    case "skill":
      return join(opencodeDir, "skills", slug, "SKILL.md");
    case "command":
      return join(opencodeDir, "commands", `${slug}.md`);
    case "mcp-server":
      return join(opencodeDir, "mcp-servers", `${slug}.md`);
  }
}

/**
 * Check if a file already exists at the target path.
 */
async function exists(path: string): Promise<boolean> {
  try {
    await stat(path);
    return true;
  } catch {
    return false;
  }
}

/**
 * Write a component to disk. Fails if file already exists.
 */
export async function writeComponent(
  opencodeDir: string,
  type: ComponentType,
  slug: string,
  content: string,
  category?: string,
): Promise<string> {
  const targetPath = resolveComponentPath(opencodeDir, type, slug, category);

  if (await exists(targetPath)) {
    throw new Error(`Component already exists at: ${targetPath}`);
  }

  // Ensure parent directory exists
  await mkdir(dirname(targetPath), { recursive: true });
  await writeFile(targetPath, content, "utf-8");

  return targetPath;
}

/**
 * Delete a component from disk.
 * For skills, deletes the entire skill directory.
 */
export async function deleteComponent(
  opencodeDir: string,
  type: ComponentType,
  slug: string,
  category?: string,
): Promise<string> {
  const targetPath = resolveComponentPath(opencodeDir, type, slug, category);

  if (!(await exists(targetPath))) {
    throw new Error(`Component not found at: ${targetPath}`);
  }

  if (type === "skill") {
    // Delete the entire skill directory
    const skillDir = dirname(targetPath);
    await rm(skillDir, { recursive: true, force: true });
    return skillDir;
  } else {
    await rm(targetPath);
    return targetPath;
  }
}
