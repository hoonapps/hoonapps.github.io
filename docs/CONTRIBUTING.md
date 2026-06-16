# Contributing

Hoonapps Lab is a personal engineering lab. Contributions are reviewed through the same lens as published posts: technical depth, reproducibility, and clear operational judgment.

## Content Changes

- Prefer Korean for new public posts.
- Keep English archive posts intact unless fixing a factual or rendering issue.
- Every technical claim should be backed by source links, runnable examples, code, diagrams, or explicit assumptions.
- AI Radar posts should separate observation, hands-on result, and production-readiness judgment.
- Backend deep dives should include failure modes, tradeoffs, and operational checks, not only definitions.

## Code Changes

- Keep changes scoped to the blog system, publishing workflow, or supporting tools.
- Run `bundle exec jekyll build` before shipping site changes.
- Run `python3 -m py_compile tools/ai_radar.py` after editing AI Radar automation.
- Do not commit generated `_site` output.

## Review Standard

A change is ready when a reader can understand what changed, why it matters, and how to reproduce or verify the result.
