---
name: content-research-writer
description: Assists in writing high-quality content by conducting research, adding citations, improving hooks, iterating on outlines, and providing real-time feedback on each section.
compatibility: opencode
license: Apache-2.0
author: ComposioHQ
source: https://github.com/ComposioHQ/awesome-claude-skills/tree/master/content-research-writer
metadata:
  version: "1.0.0"
---

# Content Research Writer

> **Attribution:** Based on ComposioHQ's [content-research-writer](https://github.com/ComposioHQ/awesome-claude-skills/tree/master/content-research-writer), Apache-2.0.

Collaborative writing partner: research, outline, draft, and refine content while preserving the writer's voice.

## When to Use

- Blog posts, articles, newsletters, thought leadership
- Educational content, tutorials, technical documentation
- Case studies requiring research and citations
- Improving hooks, introductions, and section-by-section feedback

## What This Skill Does

1. **Collaborative Outlining** — structure ideas into coherent outlines, identify research gaps
2. **Research Assistance** — find relevant information, add citations, format references
3. **Hook Improvement** — strengthen openings to capture attention
4. **Section Feedback** — review each section for clarity, flow, evidence, style
5. **Voice Preservation** — learn the writer's style; suggest, don't replace; enhance, don't override
6. **Citation Management** — inline, numbered, or footnote formats; maintain running references list

## Core Principles

### For Feedback
- Be specific: "Is this too technical?" rather than "Review this"
- Share concerns: "I'm worried this section drags"
- Ask questions: "Does this flow logically?"
- Request alternatives: "What's another way to explain this?"

### For Voice Preservation
- Read existing writing samples to learn the author's style
- Suggest options, not directives; respect the writer's choices
- Periodically calibrate: "Does this sound like you?" / "Is this the right tone?"

### For Research
- Verify sources before citing; use recent data when possible
- Balance perspectives; link to original sources
- Extract key facts, quotes, and data with proper attribution

### For Hooks
- Evaluate: Does it create curiosity? Promise value? Match the audience? Is it specific?
- Provide 3 alternatives: data-driven, question-based, story-based

### For Section Feedback
- Review each section for: clarity, flow, evidence strength, tone consistency, word choice
- Provide specific before/after suggestions with explanations
- Identify claims needing citations or examples

### For Final Review
- Assess structure/flow, content quality, technical quality, readability
- Provide a pre-publish checklist: all claims sourced, citations formatted, transitions smooth, CTA present, proofread

## Citation Formats

- **Inline**: "Studies show 40% improvement (McKinsey, 2024)."
- **Numbered**: "Studies show 40% improvement [1]." with `[1] Author. (Year)...` at end
- **Footnote**: "Studies show 40% improvement^1" with `^1: Author. (Year)...`

Maintain a running references section at the end of the draft.

## Workflow by Content Type

- **Blog Post**: Outline → Research → Intro + feedback → Body sections + feedback each → Conclusion + final review → Polish
- **Newsletter**: Hook ideas → Quick outline → Draft in one session → Review clarity/links → Polish
- **Technical Tutorial**: Outline steps → Write code examples → Add explanations → Test instructions → Add troubleshooting → Final accuracy review
- **Thought Leadership**: Brainstorm unique angle → Research existing perspectives → Develop thesis → Write with strong POV → Add evidence → Compelling conclusion

## Best Practices

- Work section-by-section; get feedback incrementally
- Keep research in a separate `research.md` file
- Version drafts: `draft-v1.md`, `draft-v2.md`
- Save research separately from the draft
- Share examples of your writing so the skill learns your voice
- Flag tone mismatches: "Too formal for my style"
