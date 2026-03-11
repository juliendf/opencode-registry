---
name: second-opinion
description: Ask another AI model for a second opinion on a question, approach, or draft response.
license: MIT
compatibility: opencode
metadata:
  version: "1.0.0"
---

# Second Opinion

Use this skill when you want an independent take from another model before finalizing an answer, design, or recommendation.

## Workflow

1. Turn the topic into a clear, self-contained request.
2. Ask the secondary model with `opencode run`, using your configured default model.
3. Read the response critically rather than treating it as automatically correct.
4. Summarize the external opinion and your own conclusion for the user.

## Command

```bash
opencode run "<REQUEST>"
```

## Parameters

- `REQUEST`: The concise but complete question or request to send to the other model.

If you want to compare against a specific alternative, pass `-m` with one of your configured models instead of hardcoding a provider/model ID in the skill.

## Output expectations

- Capture the most useful points from the second opinion.
- Call out any disagreements or uncertainty.
- Report back clearly and concisely in your own words.
