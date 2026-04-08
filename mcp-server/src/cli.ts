#!/usr/bin/env bun

import { Command } from "commander";
import { resolve } from "node:path";
import { ComponentRegistry } from "./discovery/registry.js";
import { createMcpServer } from "./server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { createServer } from "node:http";

const program = new Command();

program
  .name("opencode-registry-mcp")
  .description(
    "MCP server for autodiscovery and management of OpenCode registry components",
  )
  .version("0.1.0");

/**
 * Resolve the opencode directory from --dir flag or CWD.
 * Looks for an `opencode/` subdirectory at the resolved path.
 */
function resolveOpencodeDir(dir?: string): string {
  const base = dir ? resolve(dir) : process.cwd();
  // If the path itself ends with /opencode, use it directly
  if (base.endsWith("/opencode")) return base;
  // Otherwise look for opencode/ subdirectory
  return resolve(base, "opencode");
}

// --- serve command with stdio/http subcommands ---

const serve = program
  .command("serve")
  .description("Start the MCP server");

// --- serve stdio ---

serve
  .command("stdio")
  .description("Start MCP server with stdio transport")
  .option(
    "-d, --dir <path>",
    "Directory containing the opencode/ folder (defaults to CWD)",
  )
  .action(async (options: { dir?: string }) => {
    const opencodeDir = resolveOpencodeDir(options.dir);

    const registry = new ComponentRegistry(opencodeDir);
    await registry.init();
    registry.startWatching();

    const server = createMcpServer(registry, opencodeDir);

    // Wire up file watcher -> MCP resource notifications
    wireResourceNotifications(registry, server);

    const transport = new StdioServerTransport();
    await server.connect(transport);

    // Cleanup on exit
    process.on("SIGINT", () => {
      registry.stopWatching();
      process.exit(0);
    });
    process.on("SIGTERM", () => {
      registry.stopWatching();
      process.exit(0);
    });
  });

// --- serve http ---

serve
  .command("http")
  .description("Start MCP server with Streamable HTTP transport")
  .option(
    "-d, --dir <path>",
    "Directory containing the opencode/ folder (defaults to CWD)",
  )
  .option("-p, --port <number>", "Port to listen on", "3000")
  .option("--host <address>", "Host address to bind to", "127.0.0.1")
  .action(
    async (options: { dir?: string; port: string; host: string }) => {
      const opencodeDir = resolveOpencodeDir(options.dir);
      const port = parseInt(options.port, 10);
      const host = options.host;

      const registry = new ComponentRegistry(opencodeDir);
      await registry.init();
      registry.startWatching();

      // Track active transports for session management
      const transports = new Map<string, StreamableHTTPServerTransport>();

      const httpServer = createServer(async (req, res) => {
        const url = new URL(req.url ?? "/", `http://${host}:${port}`);

        // Health check endpoint
        if (url.pathname === "/health" && req.method === "GET") {
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(
            JSON.stringify({
              status: "ok",
              version: "0.1.0",
              opencodeDir,
            }),
          );
          return;
        }

        // MCP endpoint
        if (url.pathname === "/mcp") {
          // Check for existing session
          const sessionId = req.headers["mcp-session-id"] as
            | string
            | undefined;

          if (sessionId && transports.has(sessionId)) {
            // Reuse existing transport for this session
            const transport = transports.get(sessionId)!;
            await transport.handleRequest(req, res);
            return;
          }

          // New session: create a fresh McpServer + transport pair.
          // The high-level McpServer wraps a single Server that can only
          // be connected to one transport, so each session needs its own.
          const sessionServer = createMcpServer(registry, opencodeDir);
          wireResourceNotifications(registry, sessionServer);

          const transport = new StreamableHTTPServerTransport({
            sessionIdGenerator: () => crypto.randomUUID(),
            onsessioninitialized: (id) => {
              transports.set(id, transport);
            },
          });

          // Clean up on close
          transport.onclose = () => {
            const id = [...transports.entries()].find(
              ([, t]) => t === transport,
            )?.[0];
            if (id) transports.delete(id);
          };

          await sessionServer.connect(transport);
          await transport.handleRequest(req, res);
          return;
        }

        // 404 for everything else
        res.writeHead(404, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "Not found" }));
      });

      httpServer.listen(port, host, () => {
        console.log(
          `OpenCode Registry MCP server listening on http://${host}:${port}`,
        );
        console.log(`  MCP endpoint: http://${host}:${port}/mcp`);
        console.log(`  Health check: http://${host}:${port}/health`);
        console.log(`  OpenCode dir: ${opencodeDir}`);
      });

      // Cleanup on exit
      const shutdown = () => {
        registry.stopWatching();
        httpServer.close();
        process.exit(0);
      };
      process.on("SIGINT", shutdown);
      process.on("SIGTERM", shutdown);
    },
  );

/**
 * Wire the registry file watcher to emit MCP resource-change notifications.
 */
function wireResourceNotifications(
  registry: ComponentRegistry,
  server: ReturnType<typeof createMcpServer>,
): void {
  registry.onChange((type, slug) => {
    // The McpServer from the SDK handles notification delivery
    // to all connected transports that have subscribed.
    // We trigger a re-scan (already done in registry.refresh),
    // and the next listResources/readResource call will return fresh data.
    //
    // For proactive notifications, we'd need access to the low-level
    // server.notification() API. With the high-level McpServer API,
    // the resource template's list callback is re-invoked on each request,
    // so clients that poll will see updates immediately.
    //
    // Log for observability:
    console.error(`[watcher] Component changed: ${type}/${slug}`);
  });
}

program.parse();
