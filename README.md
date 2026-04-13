# Spider Demo

Web crawler using [Spider](https://github.com/spider-rs/spider) — the fastest web crawler for Rust. Returns content as Markdown for AI/LLM consumption.

## Setup

```bash
# Get free API key at https://spider.cloud
cp .env.example .env
# Add SPIDER_API_KEY and SPIDER_URL to .env

cargo run
```

## Usage

```bash
# Set in .env or pass URL as argument
SPIDER_API_KEY=your_key SPIDER_URL=https://example.com cargo run

# Output format: [status_code] URL
#                 ---
#                 markdown_content
```

## Project Structure

```
spider-demo/
├── src/main.rs           # Spider crawler implementation
├── Cargo.toml            # Dependencies: spider, tokio, dotenvy
├── .env                  # API keys (not committed)
├── .env.example          # Template
├── CLAUDE.md             # Project instructions
├── Dynamous/Memory/      # Second Brain vault
│   ├── SOUL.md          # Agent personality
│   ├── USER.md          # User profile
│   ├── MEMORY.md        # Long-term memory
│   ├── daily/           # Daily logs
│   └── errors/           # Error tracking
├── .claude/             # Second Brain implementation
│   ├── hooks/           # Claude Code lifecycle hooks
│   ├── scripts/          # Automation (heartbeat, memory, etc.)
│   └── skills/          # Claude Code skills
└── .agent/plans/        # PRD and planning docs
```

## Second Brain

This project includes a full AI second brain implementation (Phases 1-6):

- **Hooks**: Session start/end context injection, pre-compact flushing
- **Memory**: Hybrid search with FastEmbed embeddings + FTS5
- **GitHub**: PR review tracking integration
- **Skills**: vault-structure, code-decisions, error-capture

See `Dynamous/Memory/DEVELOPMENT.md` for details.

## Dependencies

- `spider` v2 with `spider_cloud` feature
- `tokio` async runtime
- `dotenvy` for .env loading