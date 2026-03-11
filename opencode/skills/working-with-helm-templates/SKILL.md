---
name: working-with-helm-templates
description: Work with Helm templates locally for development, rendering, and debugging before any deployment.
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
---

# Working with Helm Templates

Use this skill when debugging or developing Helm charts locally.

## Workflow

1. Run `helm dependency update` first so dependencies are up to date.
2. Use `helm template` to render manifests locally without deploying.
3. Combine values files as needed, for example:

```bash
helm template -f values.yaml -f values-staging.yaml .
```

4. Save rendered output to a temporary file prefixed with `tmp`, for example:

```bash
helm template -f values.yaml . > tmp-output.yaml
```

5. Validate rendered manifests locally to catch syntax errors or missing values before deployment.
6. If rendering fails, inspect the `charts/` directory and the relevant templates and values files to identify the issue.
7. When finished, ask the user before deleting any generated `tmp` files.
