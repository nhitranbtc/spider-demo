# Spider Demo

Web crawling and scraping integration using [Spider](https://github.com/spider-rs/spider) - the fastest web crawler for Rust.

## Project Structure

```
spider-demo/
├── Cargo.toml
├── .env.example
└── src/
    └── main.rs
```

## Setup

1. Get a free API key at https://spider.cloud
2. Copy `.env.example` to `.env` and add your key:
   ```bash
   cp .env.example .env
   ```
3. Run the crawler:
   ```bash
   cargo run
   ```

## Usage

```bash
# Set API key and URL in .env
SPIDER_API_KEY=your_key_here
SPIDER_URL=https://example.com

# Crawl a website (returns Markdown)
cargo run

# Output format: [status_code] URL
#                 ---
#                 markdown_content
```

## Dependencies

- `spider` v2 with `spider_cloud` feature
- `tokio` for async runtime
- `dotenvy` for loading .env files

## Notes

- Requires Spider Cloud API key (free tier available)
- Returns content as Markdown for AI/LLM consumption
- Uses `SpiderCloudMode::Smart` for intelligent crawling

---

# Behavioral Guidelines

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
