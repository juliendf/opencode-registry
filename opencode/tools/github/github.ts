/**
 * GitHub CLI Tool for OpenCode
 * 
 * Provides safe wrappers around `gh` CLI for common GitHub operations.
 * Requires `gh` CLI to be installed and authenticated.
 */

import { tool } from "@opencode-ai/plugin";
import { z } from "zod";

// =============================================================================
// Shared utilities
// =============================================================================

const ALLOWED_ISSUE_ACTIONS = ["list", "view", "create", "comment", "close", "reopen", "edit"] as const;
const ALLOWED_PR_ACTIONS = ["list", "view", "create", "checkout", "diff", "checks", "review", "merge", "ready", "close"] as const;
const ALLOWED_REPO_ACTIONS = ["view", "clone", "fork", "list"] as const;

// Destructive actions that require confirmation
const DESTRUCTIVE_ACTIONS = ["close", "merge", "delete"];

/**
 * Sanitize string input to prevent shell injection
 */
function sanitize(input: string): string {
  // Remove shell metacharacters, allow common punctuation
  return input.replace(/[`$\\;&|<>]/g, "");
}

/**
 * Execute gh CLI command safely
 */
async function execGh(args: string[]): Promise<{ stdout: string; stderr: string; exitCode: number }> {
  const sanitizedArgs = args.map(sanitize);
  const proc = Bun.spawn(["gh", ...sanitizedArgs], {
    stdout: "pipe",
    stderr: "pipe",
  });
  
  const stdout = await new Response(proc.stdout).text();
  const stderr = await new Response(proc.stderr).text();
  const exitCode = await proc.exited;
  
  return { stdout: stdout.trim(), stderr: stderr.trim(), exitCode };
}

/**
 * Format error response
 */
function formatError(stderr: string, exitCode: number): string {
  return `Error (exit code ${exitCode}): ${stderr}`;
}

// =============================================================================
// github_issue - Issue management
// =============================================================================

export const issue = tool({
  description: `Manage GitHub issues. Actions: ${ALLOWED_ISSUE_ACTIONS.join(", ")}. 
Use 'list' to find issues, 'view' for details, 'create' to open new issues, 
'comment' to add comments, 'close/reopen' to change state, 'edit' to modify.`,
  
  args: {
    action: tool.schema.enum(ALLOWED_ISSUE_ACTIONS).describe("Action to perform"),
    repo: tool.schema.string().optional().describe("Repository (owner/repo). Uses current repo if not specified"),
    number: tool.schema.number().optional().describe("Issue number (required for view, comment, close, reopen, edit)"),
    title: tool.schema.string().optional().describe("Issue title (for create)"),
    body: tool.schema.string().optional().describe("Issue body or comment text"),
    labels: tool.schema.string().optional().describe("Comma-separated labels (for create, edit)"),
    assignee: tool.schema.string().optional().describe("Assignee username (for create, edit)"),
    state: tool.schema.enum(["open", "closed", "all"]).optional().describe("Filter by state (for list)"),
    limit: tool.schema.number().optional().describe("Max results (for list, default: 30)"),
    confirmed: tool.schema.boolean().optional().describe("Confirm destructive action (required for close)"),
  },
  
  async execute(args) {
    const { action, repo, number, title, body, labels, assignee, state, limit, confirmed } = args;
    const repoArgs = repo ? ["-R", repo] : [];
    
    // Check confirmation for destructive actions
    if (DESTRUCTIVE_ACTIONS.includes(action) && !confirmed) {
      return `⚠️ Action '${action}' requires confirmation. Set confirmed=true to proceed.`;
    }
    
    let cmdArgs: string[] = ["issue"];
    
    switch (action) {
      case "list":
        cmdArgs.push("list", ...repoArgs);
        if (state) cmdArgs.push("--state", state);
        if (labels) cmdArgs.push("--label", labels);
        if (assignee) cmdArgs.push("--assignee", assignee);
        if (limit) cmdArgs.push("--limit", String(limit));
        cmdArgs.push("--json", "number,title,state,author,labels,createdAt");
        break;
        
      case "view":
        if (!number) return "Error: 'number' is required for view action";
        cmdArgs.push("view", String(number), ...repoArgs);
        cmdArgs.push("--json", "number,title,body,state,author,labels,assignees,comments,createdAt,updatedAt");
        break;
        
      case "create":
        if (!title) return "Error: 'title' is required for create action";
        cmdArgs.push("create", ...repoArgs, "--title", title);
        if (body) cmdArgs.push("--body", body);
        if (labels) cmdArgs.push("--label", labels);
        if (assignee) cmdArgs.push("--assignee", assignee);
        break;
        
      case "comment":
        if (!number) return "Error: 'number' is required for comment action";
        if (!body) return "Error: 'body' is required for comment action";
        cmdArgs.push("comment", String(number), ...repoArgs, "--body", body);
        break;
        
      case "close":
        if (!number) return "Error: 'number' is required for close action";
        cmdArgs.push("close", String(number), ...repoArgs);
        if (body) cmdArgs.push("--comment", body);
        break;
        
      case "reopen":
        if (!number) return "Error: 'number' is required for reopen action";
        cmdArgs.push("reopen", String(number), ...repoArgs);
        break;
        
      case "edit":
        if (!number) return "Error: 'number' is required for edit action";
        cmdArgs.push("edit", String(number), ...repoArgs);
        if (title) cmdArgs.push("--title", title);
        if (body) cmdArgs.push("--body", body);
        if (labels) cmdArgs.push("--add-label", labels);
        if (assignee) cmdArgs.push("--add-assignee", assignee);
        break;
        
      default:
        return `Unknown action: ${action}`;
    }
    
    const result = await execGh(cmdArgs);
    
    if (result.exitCode !== 0) {
      return formatError(result.stderr, result.exitCode);
    }
    
    return result.stdout || "Success";
  },
});

// =============================================================================
// github_pr - Pull Request management
// =============================================================================

export const pr = tool({
  description: `Manage GitHub pull requests. Actions: ${ALLOWED_PR_ACTIONS.join(", ")}.
Use 'list' to find PRs, 'view' for details, 'create' to open new PRs,
'checkout' to switch to PR branch, 'diff' to see changes, 'checks' for CI status,
'review' to approve/request changes, 'merge' to merge, 'ready' to mark ready.`,
  
  args: {
    action: tool.schema.enum(ALLOWED_PR_ACTIONS).describe("Action to perform"),
    repo: tool.schema.string().optional().describe("Repository (owner/repo). Uses current repo if not specified"),
    number: tool.schema.number().optional().describe("PR number (required for most actions)"),
    title: tool.schema.string().optional().describe("PR title (for create)"),
    body: tool.schema.string().optional().describe("PR body or review comment"),
    base: tool.schema.string().optional().describe("Base branch (for create, default: main)"),
    head: tool.schema.string().optional().describe("Head branch (for create, default: current branch)"),
    draft: tool.schema.boolean().optional().describe("Create as draft PR"),
    reviewDecision: tool.schema.enum(["approve", "request-changes", "comment"]).optional().describe("Review decision (for review)"),
    mergeMethod: tool.schema.enum(["merge", "squash", "rebase"]).optional().describe("Merge method (for merge)"),
    state: tool.schema.enum(["open", "closed", "merged", "all"]).optional().describe("Filter by state (for list)"),
    limit: tool.schema.number().optional().describe("Max results (for list, default: 30)"),
    confirmed: tool.schema.boolean().optional().describe("Confirm destructive action (required for merge, close)"),
  },
  
  async execute(args) {
    const { action, repo, number, title, body, base, head, draft, reviewDecision, mergeMethod, state, limit, confirmed } = args;
    const repoArgs = repo ? ["-R", repo] : [];
    
    // Check confirmation for destructive actions
    if (DESTRUCTIVE_ACTIONS.includes(action) && !confirmed) {
      return `⚠️ Action '${action}' requires confirmation. Set confirmed=true to proceed.`;
    }
    
    let cmdArgs: string[] = ["pr"];
    
    switch (action) {
      case "list":
        cmdArgs.push("list", ...repoArgs);
        if (state) cmdArgs.push("--state", state);
        if (limit) cmdArgs.push("--limit", String(limit));
        cmdArgs.push("--json", "number,title,state,author,headRefName,baseRefName,isDraft,createdAt");
        break;
        
      case "view":
        if (!number) return "Error: 'number' is required for view action";
        cmdArgs.push("view", String(number), ...repoArgs);
        cmdArgs.push("--json", "number,title,body,state,author,headRefName,baseRefName,isDraft,mergeable,reviewDecision,commits,comments,reviews,createdAt,updatedAt");
        break;
        
      case "create":
        if (!title) return "Error: 'title' is required for create action";
        cmdArgs.push("create", ...repoArgs, "--title", title);
        if (body) cmdArgs.push("--body", body);
        if (base) cmdArgs.push("--base", base);
        if (head) cmdArgs.push("--head", head);
        if (draft) cmdArgs.push("--draft");
        break;
        
      case "checkout":
        if (!number) return "Error: 'number' is required for checkout action";
        cmdArgs.push("checkout", String(number), ...repoArgs);
        break;
        
      case "diff":
        if (!number) return "Error: 'number' is required for diff action";
        cmdArgs.push("diff", String(number), ...repoArgs);
        break;
        
      case "checks":
        if (!number) return "Error: 'number' is required for checks action";
        cmdArgs.push("checks", String(number), ...repoArgs);
        break;
        
      case "review":
        if (!number) return "Error: 'number' is required for review action";
        if (!reviewDecision) return "Error: 'reviewDecision' is required for review action";
        cmdArgs.push("review", String(number), ...repoArgs);
        if (reviewDecision === "approve") cmdArgs.push("--approve");
        else if (reviewDecision === "request-changes") cmdArgs.push("--request-changes");
        else cmdArgs.push("--comment");
        if (body) cmdArgs.push("--body", body);
        break;
        
      case "merge":
        if (!number) return "Error: 'number' is required for merge action";
        cmdArgs.push("merge", String(number), ...repoArgs);
        if (mergeMethod === "squash") cmdArgs.push("--squash");
        else if (mergeMethod === "rebase") cmdArgs.push("--rebase");
        else cmdArgs.push("--merge");
        break;
        
      case "ready":
        if (!number) return "Error: 'number' is required for ready action";
        cmdArgs.push("ready", String(number), ...repoArgs);
        break;
        
      case "close":
        if (!number) return "Error: 'number' is required for close action";
        cmdArgs.push("close", String(number), ...repoArgs);
        break;
        
      default:
        return `Unknown action: ${action}`;
    }
    
    const result = await execGh(cmdArgs);
    
    if (result.exitCode !== 0) {
      return formatError(result.stderr, result.exitCode);
    }
    
    return result.stdout || "Success";
  },
});

// =============================================================================
// github_repo - Repository operations
// =============================================================================

export const repo = tool({
  description: `Repository operations. Actions: ${ALLOWED_REPO_ACTIONS.join(", ")}.
Use 'view' for repo info, 'list' to list your repos, 'clone' to clone,
'fork' to create a fork.`,
  
  args: {
    action: tool.schema.enum(ALLOWED_REPO_ACTIONS).describe("Action to perform"),
    repo: tool.schema.string().optional().describe("Repository (owner/repo)"),
    limit: tool.schema.number().optional().describe("Max results (for list, default: 30)"),
    visibility: tool.schema.enum(["public", "private", "all"]).optional().describe("Filter by visibility (for list)"),
  },
  
  async execute(args) {
    const { action, repo, limit, visibility } = args;
    
    let cmdArgs: string[] = ["repo"];
    
    switch (action) {
      case "view":
        cmdArgs.push("view");
        if (repo) cmdArgs.push(repo);
        cmdArgs.push("--json", "name,owner,description,url,sshUrl,defaultBranch,visibility,isFork,stargazerCount,forkCount,createdAt,updatedAt");
        break;
        
      case "list":
        cmdArgs.push("list");
        if (limit) cmdArgs.push("--limit", String(limit));
        if (visibility && visibility !== "all") cmdArgs.push(`--${visibility}`);
        cmdArgs.push("--json", "nameWithOwner,description,visibility,updatedAt");
        break;
        
      case "clone":
        if (!repo) return "Error: 'repo' is required for clone action";
        cmdArgs.push("clone", repo);
        break;
        
      case "fork":
        if (!repo) return "Error: 'repo' is required for fork action";
        cmdArgs.push("fork", repo, "--clone=false");
        break;
        
      default:
        return `Unknown action: ${action}`;
    }
    
    const result = await execGh(cmdArgs);
    
    if (result.exitCode !== 0) {
      return formatError(result.stderr, result.exitCode);
    }
    
    return result.stdout || "Success";
  },
});

// =============================================================================
// github_api - Direct API access (with safety limits)
// =============================================================================

export const api = tool({
  description: `Make authenticated GitHub API requests. Supports REST and GraphQL.
Use for advanced operations not covered by other tools.
⚠️ Be careful: this provides direct API access.`,
  
  args: {
    endpoint: tool.schema.string().describe("API endpoint (e.g., 'repos/{owner}/{repo}/issues' or 'graphql')"),
    method: tool.schema.enum(["GET", "POST", "PATCH", "PUT", "DELETE"]).optional().describe("HTTP method (default: GET)"),
    body: tool.schema.string().optional().describe("JSON request body (for POST/PATCH/PUT)"),
    query: tool.schema.string().optional().describe("GraphQL query (for graphql endpoint)"),
    jq: tool.schema.string().optional().describe("jq filter to apply to response"),
    paginate: tool.schema.boolean().optional().describe("Paginate through all results"),
    confirmed: tool.schema.boolean().optional().describe("Confirm destructive action (required for DELETE)"),
  },
  
  async execute(args) {
    const { endpoint, method = "GET", body, query, jq, paginate, confirmed } = args;
    
    // Block DELETE without confirmation
    if (method === "DELETE" && !confirmed) {
      return "⚠️ DELETE requests require confirmation. Set confirmed=true to proceed.";
    }
    
    // Block dangerous endpoints
    const dangerousPatterns = [
      /\/repos\/[^/]+\/[^/]+$/,  // DELETE repo
      /\/orgs\/[^/]+$/,          // DELETE org
      /\/user$/,                  // DELETE user
    ];
    
    if (method === "DELETE") {
      for (const pattern of dangerousPatterns) {
        if (pattern.test(endpoint)) {
          return "⛔ This endpoint is blocked for safety. Use the GitHub web interface for this operation.";
        }
      }
    }
    
    let cmdArgs: string[] = ["api"];
    
    // Handle GraphQL
    if (endpoint === "graphql" || query) {
      cmdArgs.push("graphql");
      if (query) cmdArgs.push("-f", `query=${query}`);
    } else {
      if (method !== "GET") cmdArgs.push("-X", method);
      cmdArgs.push(endpoint);
    }
    
    if (body) cmdArgs.push("--input", "-");
    if (jq) cmdArgs.push("--jq", jq);
    if (paginate) cmdArgs.push("--paginate");
    
    // For body, we need to pipe it
    let result;
    if (body) {
      const proc = Bun.spawn(["gh", ...cmdArgs.map(sanitize)], {
        stdin: new Response(body).body,
        stdout: "pipe",
        stderr: "pipe",
      });
      const stdout = await new Response(proc.stdout).text();
      const stderr = await new Response(proc.stderr).text();
      const exitCode = await proc.exited;
      result = { stdout: stdout.trim(), stderr: stderr.trim(), exitCode };
    } else {
      result = await execGh(cmdArgs);
    }
    
    if (result.exitCode !== 0) {
      return formatError(result.stderr, result.exitCode);
    }
    
    return result.stdout || "Success";
  },
});

// =============================================================================
// github_auth - Authentication status
// =============================================================================

export const auth = tool({
  description: "Check GitHub CLI authentication status and available scopes.",
  
  args: {},
  
  async execute() {
    const result = await execGh(["auth", "status"]);
    
    if (result.exitCode !== 0) {
      return `Not authenticated. Run 'gh auth login' to authenticate.\n${result.stderr}`;
    }
    
    return result.stdout || result.stderr;
  },
});
