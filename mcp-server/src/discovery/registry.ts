import { watch, type FSWatcher } from "node:fs";
import { discoverAll, type DiscoveryResult } from "./scanner.js";
import type { Component, ComponentType, SkillComponent } from "../types.js";

type ChangeListener = (type: ComponentType, slug: string) => void;

/**
 * ComponentRegistry manages a cached view of all components
 * and watches the filesystem for changes.
 */
export class ComponentRegistry {
  private opencodeDir: string;
  private cache: DiscoveryResult | null = null;
  private watcher: FSWatcher | null = null;
  private listeners: ChangeListener[] = [];
  private refreshTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(opencodeDir: string) {
    this.opencodeDir = opencodeDir;
  }

  /**
   * Initialize the registry by scanning all components.
   */
  async init(): Promise<void> {
    this.cache = await discoverAll(this.opencodeDir);
  }

  /**
   * Start watching the opencode directory for filesystem changes.
   * Debounces rescans and notifies listeners.
   */
  startWatching(): void {
    if (this.watcher) return;

    try {
      this.watcher = watch(
        this.opencodeDir,
        { recursive: true },
        (_event, filename) => {
          if (!filename) return;
          // Debounce: wait 300ms after last change before rescanning
          if (this.refreshTimer) clearTimeout(this.refreshTimer);
          this.refreshTimer = setTimeout(() => this.refresh(filename), 300);
        },
      );
    } catch (err) {
      console.error(`[registry] Failed to start file watcher: ${err}`);
    }
  }

  /**
   * Stop watching the filesystem.
   */
  stopWatching(): void {
    if (this.watcher) {
      this.watcher.close();
      this.watcher = null;
    }
    if (this.refreshTimer) {
      clearTimeout(this.refreshTimer);
      this.refreshTimer = null;
    }
  }

  /**
   * Register a listener for component changes.
   */
  onChange(listener: ChangeListener): void {
    this.listeners.push(listener);
  }

  /**
   * Rescan and notify listeners about changes.
   */
  private async refresh(changedFile: string): Promise<void> {
    const oldCache = this.cache;
    this.cache = await discoverAll(this.opencodeDir);

    // Determine what type of component changed based on path
    const componentType = this.inferTypeFromPath(changedFile);
    const slug = this.inferSlugFromPath(changedFile);

    if (componentType && slug) {
      for (const listener of this.listeners) {
        listener(componentType, slug);
      }
    }
  }

  private inferTypeFromPath(filePath: string): ComponentType | null {
    if (filePath.startsWith("agents/subagents/")) return "subagent";
    if (filePath.startsWith("agents/")) return "agent";
    if (filePath.startsWith("skills/")) return "skill";
    if (filePath.startsWith("commands/")) return "command";
    if (filePath.startsWith("mcp-servers/")) return "mcp-server";
    return null;
  }

  private inferSlugFromPath(filePath: string): string | null {
    const parts = filePath.split("/");
    const last = parts[parts.length - 1];
    if (!last) return null;
    // Remove .md extension if present
    return last.endsWith(".md") ? last.slice(0, -3) : last;
  }

  // --- Accessors ---

  getAgents(): Component[] {
    return this.cache?.agents ?? [];
  }

  getSubagents(category?: string): Component[] {
    const all = this.cache?.subagents ?? [];
    if (category) return all.filter((c) => c.category === category);
    return all;
  }

  getSubagentCategories(): string[] {
    const cats = new Set(
      (this.cache?.subagents ?? [])
        .map((c) => c.category)
        .filter(Boolean) as string[],
    );
    return [...cats].sort();
  }

  getSkills(): SkillComponent[] {
    return this.cache?.skills ?? [];
  }

  getCommands(): Component[] {
    return this.cache?.commands ?? [];
  }

  getMcpServers(): Component[] {
    return this.cache?.mcpServers ?? [];
  }

  /**
   * Find a component by type and slug.
   */
  findBySlug(type: ComponentType, slug: string): Component | null {
    const list = this.getByType(type);
    return list.find((c) => c.slug === slug) ?? null;
  }

  /**
   * Find a subagent by category and slug.
   */
  findSubagent(category: string, slug: string): Component | null {
    return (
      (this.cache?.subagents ?? []).find(
        (c) => c.category === category && c.slug === slug,
      ) ?? null
    );
  }

  private getByType(type: ComponentType): Component[] {
    switch (type) {
      case "agent":
        return this.getAgents();
      case "subagent":
        return this.getSubagents();
      case "skill":
        return this.getSkills();
      case "command":
        return this.getCommands();
      case "mcp-server":
        return this.getMcpServers();
    }
  }
}
