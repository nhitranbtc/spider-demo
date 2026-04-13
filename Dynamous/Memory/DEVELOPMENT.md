# Second Brain — Development Document

**Project:** spider-demo Second Brain
**Created:** 2026-04-13
**Owner:** Nhi Tran
**Status:** Phase 1-6 implemented, Phase 7 skipped, Phase 8-9 partial

---

## Overview

An AI second brain built on Claude Code hooks and local file storage. Captures code decisions, tracks GitHub PRs, maintains session continuity, and surfaces notifications via heartbeat.

**Proactivity Level:** Observer — notify only, never act autonomously.

---

## Architecture

```
spider-demo/
├── .claude/
│   ├── hooks/                    # Claude Code lifecycle hooks
│   │   ├── paths.py             # Shared path configuration
│   │   ├── session-start-context.py
│   │   ├── pre-compact-flush.py
│   │   └── session-end-flush.py
│   ├── scripts/                  # Automation scripts
│   │   ├── db.py                 # SQLite + FTS5 abstraction
│   │   ├── embeddings.py          # FastEmbed ONNX batch embedding
│   │   ├── memory_index.py        # Incremental vault indexer
│   │   ├── memory_search.py       # Hybrid vector + keyword search
│   │   ├── heartbeat.py           # Observer-mode heartbeat
│   │   ├── memory_reflect.py     # Daily reflection
│   │   ├── query.py              # Unified CLI
│   │   └── integrations/
│   │       ├── github.py          # GitHub PR review tracking
│   │       └── registry.py        # Integration status
│   ├── skills/                   # Claude Code skills
│   │   ├── vault-structure/       # Vault organization skill
│   │   ├── code-decisions/       # Decision capture skill
│   │   └── error-capture/        # Error logging skill
│   └── settings.json             # Hook registrations
├── Dynamous/Memory/              # Vault (Obsidian-compatible)
│   ├── SOUL.md                   # Agent personality
│   ├── USER.md                   # User profile + config
│   ├── MEMORY.md                 # Long-term memory index
│   ├── HEARTBEAT.md              # Heartbeat checklist
│   ├── daily/                    # Append-only timestamped logs
│   ├── errors/                   # Error tracking
│   ├── decisions/                # Code decisions
│   └── drafts/                   # Draft management
└── .env                          # API tokens (not committed)
```

---

## Vault Path Convention

All vault files are relative to repo root: `Dynamous/Memory/`

| Path | Purpose |
|------|---------|
| `Dynamous/Memory/` | Vault root |
| `Dynamous/Memory/daily/` | Daily logs (YYYY-MM-DD.md) |
| `Dynamous/Memory/errors/` | Error logs |
| `Dynamous/Memory/decisions/` | Code decisions |
| `Dynamous/Memory/drafts/` | Draft management |

**Hard Rule:** Never modify files outside `Dynamous/Memory/`

---

## Hooks

### SessionStart (`session-start-context.py`)
- Reads: SOUL.md, USER.md, MEMORY.md, last 3 daily logs
- Injects context into every Claude Code session

### PreCompact (`pre-compact-flush.py`)
- Extracts decisions and technical content from transcript
- Appends to daily log before auto-compaction

### SessionEnd (`session-end-flush.py`)
- Saves session summary and key points to daily log
- Runs on session exit

### Path Configuration (`paths.py`)
```python
_REPO_ROOT = Path(__file__).parent.parent.parent  # 3 levels = repo root
VAULT_PATH = _REPO_ROOT / "Dynamous" / "Memory"
DAILY_PATH = VAULT_PATH / "daily"
ERRORS_PATH = VAULT_PATH / "errors"
DECISIONS_PATH = VAULT_PATH / "decisions"
```

---

## Scripts

### heartbeat.py
Observer-mode proactive monitoring.
- Runs every 30 minutes (via cron)
- Gathers GitHub PR data
- Only notifies on new/changed items
- Uses state diffing to avoid spam

### memory_index.py
Incremental vault indexer.
- Only re-indexes changed files
- Uses FastEmbed (all-MiniLM-L6-v2, 384-dim)
- Stores in SQLite with FTS5

### memory_search.py
Hybrid search: 0.7 keyword + 0.3 vector.
```bash
~/.venv/bin/python .claude/scripts/memory_search.py "query"
```

### query.py
Unified CLI for integrations.
```bash
python3 .claude/scripts/query.py github pending-review -u <username>
python3 .claude/scripts/query.py integrations
```

---

## Skills

### vault-structure
Teaches Claude Code vault organization, file naming, folder structure.

### code-decisions
Capture and retrieve architectural decisions.
```bash
python3 .claude/skills/code-decisions/scripts/capture.py \
  --type architecture --project myproject --title "Chose X over Y"
```

### error-capture
Log and track errors.
```bash
python3 .claude/skills/error-capture/scripts/log.py \
  -m "Build failed" -s high -t build
```

---

## .env Configuration

```bash
# GitHub Integration
GITHUB_TOKEN=ghp_your_token_here
GITHUB_USERNAME=your_username

# Spider (spider-demo project)
SPIDER_API_KEY=your_key
SPIDER_URL=https://example.com
```

**Never commit .env** — it's in `.gitignore`.

---

## Cron Setup

```bash
# Heartbeat every 30 minutes
*/30 * * * * /usr/bin/python3 /path/to/.claude/scripts/heartbeat.py >> /path/to/.claude/logs/heartbeat.log 2>&1

# Daily reflection at 8 AM
0 8 * * * /usr/bin/python3 /path/to/.claude/scripts/memory_reflect.py >> /path/to/.claude/logs/memory_reflect.log 2>&1
```

---

## Error Tracking

Errors are logged to `Dynamous/Memory/errors/` with YAML frontmatter:

| Field | Description |
|-------|-------------|
| `type` | runtime, build, script, integration, security |
| `severity` | low, medium, high, critical |
| `timestamp` | YYYY-MM-DD HH:MM:SS |
| `project` | Project name or "general" |
| `command` | Command that failed |

---

## Known Issues (Resolved)

| # | Error | Resolution |
|---|-------|-----------|
| 1 | Hooks settings.json wrong format | Use `{"hooks": [{"type": "command"...}]}` |
| 2 | REPO_ROOT 3 vs 5 levels | Skill paths need 5 parent levels |
| 3 | dotenv not in venv | `pip install python-dotenv` |
| 4 | github.py missing main() | Added explicit main() function |
| 5 | Registry not loading .env | Added `load_dotenv()` at top |
| 6 | Hooks hardcoded paths | Created shared `paths.py` |

---

## Verification Commands

```bash
# Test hooks
python3 .claude/hooks/session-start-context.py | head

# Test integrations
python3 .claude/scripts/integrations/registry.py

# Test memory search
~/.venv/bin/python .claude/scripts/memory_search.py "query"

# Test heartbeat
python3 .claude/scripts/heartbeat.py

# Test error capture
python3 .claude/skills/error-capture/scripts/log.py -m "Test" -s low -t script
```

---

## Dependencies

```bash
# Core (system Python)
pip install python-dotenv pygithub

# Memory/embedding (venv)
~/.venv/bin/pip install fastembed python-dotenv
```

---

## File Naming Conventions

| Type | Format |
|------|--------|
| Daily log | `YYYY-MM-DD.md` |
| Error | `YYYY-MM-DD_<slug>.md` |
| Decision | `YYYY-MM-DD_<slug>.md` |
| Draft | `YYYY-MM-DD_<type>_<slug>.md` |

---

## Memory Categories (Priority Order)

1. Project status and progress
2. Code decisions and architectural tradeoffs
3. GitHub PR review status
4. Claude Code session context

---

## Observer Mode Constraints

- ✅ Notify on PRs needing review
- ✅ Log decisions and errors
- ❌ Never send messages/email
- ❌ Never post to social media
- ❌ Never delete anything
- ❌ Never modify files outside vault