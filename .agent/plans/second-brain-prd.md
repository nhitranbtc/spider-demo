# Nhi Tran's Second Brain — Product Requirements Document

**Generated:** 2026-04-13
**Owner:** Nhi Tran — Blockchain & Backend Engineer

---

## Summary

An AI second brain for Nhi that captures code decisions and architectural tradeoffs, surfaces GitHub PRs needing review, maintains Claude Code session continuity, and delivers daily summaries — built on Obsidian vault + Claude hooks + GitHub integration, with an Observer-level proactive stance (notify only, no autonomous actions).

---

## Phase 1: Foundation (Memory Layer)

**What to build:** Set up the Obsidian vault structure for Nhi's Memory directory with personality, user profile, memory index, and daily logging.

**Key files to create:**

| File | Purpose |
|------|---------|
| `Dynamous/Memory/SOUL.md` | Agent personality — precise, technical, security-minded, minimalist |
| `Dynamous/Memory/USER.md` | User profile: Nhi Tran, Blockchain & Backend Engineer, GitHub username, Obsidian path |
| `Dynamous/Memory/MEMORY.md` | Indexed key decisions, lessons learned, active projects (Rust, Substrate, Polkadot-SDK) |
| `Dynamous/Memory/daily/` | Append-only timestamped logs (YYYY-MM-DD.md) |
| `Dynamous/Memory/HEARTBEAT.md` | Checklist for heartbeat monitoring |

**Personalization notes:**
- Vault path: `Dynamous/Memory/` (relative to repo root — in repo at `spider-demo/Dynamous/Memory/`)
- Memory categories: **Project status and progress** (checked), plus code decisions and architectural tradeoffs from the top tasks
- SOUL.md tone: precise, technical, no fluff — matches Nhi's backend/engineer mindset

**Dependencies:** None
**Estimated complexity:** Low

---

## Phase 2: Hooks (Context Persistence)

**What to build:** Three Claude Code lifecycle hooks that inject memory context at session start and persist it at end/compact.

**Key files to create:**

| File | Purpose |
|------|---------|
| `.claude/hooks/session-start-context.py` | On session start: read SOUL.md + USER.md + MEMORY.md + recent daily logs → inject into context |
| `.claude/hooks/pre-compact-flush.py` | Before auto-compaction: extract key decisions/facts from transcript → append to daily log |
| `.claude/hooks/session-end-flush.py` | On session end: save conversation context to daily log |
| `.claude/settings.json` | Register all three hooks |

**Hook configuration (settings.json):**
```json
{
  "hooks": {
    "SessionStart": [{"path": ".claude/hooks/session-start-context.py"}],
    "PreCompact": [{"path": ".claude/hooks/pre-compact-flush.py"}],
    "SessionEnd": [{"path": ".claude/hooks/session-end-flush.py"}]
  }
}
```

**Personalization notes:**
- Observer-level: hooks focus on **capture and notify**, not action
- Daily logs should capture Claude Code session context specifically (since that's a top task)
- PreCompact flush should prioritize code decisions and architecture tradeoffs for Nhi's work

**Dependencies:** Phase 1 (vault must exist)
**Estimated complexity:** Medium

---

## Phase 3: Memory Search (Hybrid RAG)

**What to build:** Chunking + embedding pipeline with SQLite (local) using sqlite-vec + FTS5 for hybrid search.

**Key files to create:**

| File | Purpose |
|------|---------|
| `.claude/scripts/db.py` | SQLite abstraction (sqlite-vec + FTS5) |
| `.claude/scripts/embeddings.py` | FastEmbed ONNX batch embedding (all-MiniLM-L6-v2, 384-dim) |
| `.claude/scripts/memory_index.py` | Incremental indexer — only re-index changed files |
| `.claude/scripts/memory_search.py` | Hybrid merge: 0.7 vector + 0.3 FTS5 keyword |

**Chunking strategy:** ~400 tokens with 50-token overlap, chunk metadata (source file, line range)

**Personalization notes:**
- Index should prioritize code decision files, architecture docs, and daily logs
- Search should handle technical queries well (Rust, Substrate, Polkadot terminology)

**Dependencies:** Phase 1 (vault structure)
**Estimated complexity:** Medium

---

## Phase 4: Integrations (GitHub First)

**What to build:** GitHub integration module for PR review tracking and surfacing.

**GitHub setup requirements:**
- Authentication: Personal Access Token (fine-grained, repo scope)
- SDK: `PyGithub` or `ghapi` for Python
- Key endpoints needed:
  - `GET /repos/{owner}/{repo}/pulls?state=open` — list open PRs
  - `GET /repos/{owner}/{repo}/pulls/{pr}/reviews` — get review history
  - `GET /repos/{owner}/{repo}/pulls/{pr}/reviews?headers=X-GitHub-Api-Version=2022-11-28` — per-review detail
  - `GET /repos/{owner}/{repo}/pulls/{pr}/files` — diff for review context
  - `POST /repos/{owner}/{repo}/pulls/{pr}/reviews` — submit review (Observer mode: read-only)

**Key files to create:**

| File | Purpose |
|------|---------|
| `.claude/scripts/integrations/github.py` | GitHub integration: auth, PR queries, review status |
| `.claude/scripts/integrations/registry.py` | Integration registry (tracks enabled integrations) |
| `.claude/scripts/query.py` | CLI: `query.py github prs-reviewed`, `query.py github prs-pending-review` |
| `~/.claude/.env` | `GITHUB_TOKEN=ghp_...` (never hardcoded) |

**CLI subcommands for GitHub:**
```
query.py github list-repos                # List repos with open PRs
query.py github prs-pending-review        # PRs needing Nhi's review
query.py github prs-reviewed <owner/repo> # Nhi's review history
```

**Personalization notes:**
- Observer mode: read-only, no posting reviews automatically
- Heartbeat checks: open PRs where Nhi is a requested reviewer, surfacing notification
- Review decisions logged to daily/YYYY-MM-DD.md for memory

**Dependencies:** Phase 2 (hooks for logging)
**Estimated complexity:** Medium

---

## Phase 5: Skills (Starter Pack)

**What to build:** Two initial skills — one vault-structure skill and one custom skill for Nhi's top task.

**Key files to create:**

| File | Purpose |
|------|---------|
| `.claude/skills/vault-structure/SKILL.md` | Teaches agent Nhi's vault organization, memory categories, file naming conventions |
| `.claude/skills/vault-structure/references/folder-map.md` | Detailed folder structure reference |
| `.claude/skills/code-decisions/SKILL.md` | Custom skill: capture architectural decisions, tradeoffs, lessons learned |
| `.claude/skills/code-decisions/scripts/capture.py` | CLI to log a code decision with context (type, decision, rationale, project) |

**Skills anatomy:**
- SKILL.md: YAML frontmatter (name, description, triggers) + markdown instructions
- scripts/: executable Python for deterministic tasks
- references/: loaded on demand

**Personalization notes:**
- Top task skill: **code-decisions** — structured capture of architectural choices, tradeoffs, and lessons learned, stored in a format optimized for RAG later (Phase 3)
- Vault structure skill should reference the memory categories: Project status and progress is primary

**Dependencies:** Phase 1 (vault exists)
**Estimated complexity:** Low-Medium

---

## Phase 6: Proactive Systems (Heartbeat + Daily Reflection)

**What to build:** Scheduled heartbeat script and daily reflection — Observer mode (notify only, no drafting/sending).

**Heartbeat behavior (Observer):**
- Gather data from GitHub integration (open PRs needing review)
- Claude reasons over pre-loaded context → surfaces items needing attention
- Notifications via Linux `notify-send` (no Slack/email in Observer mode)
- State diffing: only notify on new/changed items (no spam)

**Key files to create:**

| File | Purpose |
|------|---------|
| `.claude/scripts/heartbeat.py` | Main heartbeat: gather → reason → notify |
| `.claude/scripts/memory_reflect.py` | Daily at 8 AM: promote yesterday's decisions to MEMORY.md |
| `.claude/data/state/heartbeat-state.json` | Snapshot state for diffing |
| `~/.claude/settings.json` | Schedule heartbeat every 30 min during active hours |

**Schedule:** `*/30 * * * *` (every 30 minutes) — OS cron on Linux

**Daily reflection behavior:**
- Read yesterday's daily log
- Identify: code decisions, PR review conclusions, platform activity
- Promote key items to MEMORY.md (keep it concise — max ~50 items)
- Archive daily log to `daily/history/` subfolder

**Personalization notes:**
- Observer mode: no draft emails, no auto-organize, no auto-log (unless session hook creates logs)
- Heartbeat focus: GitHub PR review reminders, daily summary preparation
- Nhi is technical/terminal-comfortable — CLI output is fine for notifications

**Dependencies:** Phase 4 (GitHub integration), Phase 2 (hooks for session logging)
**Estimated complexity:** High

---

## Phase 7: Chat Interface

**What to build:** Not included — Nhi did not select Chat/Messaging in platforms (Slack, Discord, Teams all unchecked).

**Skip this phase.**

---

## Phase 8: Security Hardening

**What to build:** Three-layer defense and command guardrails matching Nhi's security boundaries.

**Nhi's boundaries:**
- ✅ Never modify files outside the memory vault
- ❌ No restriction on sending emails/messages (Observer mode already prevents this)
- ❌ No restriction on social media posting (not selected)
- ❌ No restriction on financial data (not selected)
- ❌ No restriction on deletion (not selected)

**Key files to create:**

| File | Purpose |
|------|---------|
| `.claude/scripts/sanitize.py` | 3-layer: pattern detection → markdown escaping → XML trust boundary |
| `.claude/scripts/shared.py` | Guardrails: deterministic pre-check + LLM evaluation (pass/fail/suspicious) |
| `.claude/scripts/query.py` | Python CLI wrapper — LLM never sees API tokens |

**Guardrail rules (from boundaries):**
```
ALWAYS DENY:
- File write operations outside the vault (Dynamous/Memory/)
- File delete operations (any path)
- File modify operations outside the vault

ALWAYS ALLOW:
- Read operations anywhere
- Claude Code native tool operations in ~/.claude/
- Query.py calls to integrations

REQUIRES EXPLICIT CONFIRMATION:
- Any operation touching files outside Dynamous/Memory/
```

**Dependencies:** Phase 2 (hooks context), Phase 5 (vault structure skill)
**Estimated complexity:** Medium

---

## Phase 9: Deployment

**What to build:** Local Linux deployment with OS scheduler.

**Infrastructure choices:**
- OS: Linux ✅
- Deployment: Local only ✅ (no VPS)
- Existing tools: Comfortable with terminal, Claude Code CLI

**Key setup tasks:**
1. Create `~/.claude/scripts/` directory structure
2. Symlink vault to Obsidian-compatible path
3. Set up cron job for heartbeat (every 30 minutes)
4. Set up cron job for daily reflection (8 AM daily)
5. Configure `.claude/settings.json` with hook registrations and schedules
6. Add `query.py` to PATH or create shell alias

**Cron jobs:**
```cron
*/30 * * * * /home/nhitran/.claude/scripts/heartbeat.py >> /home/nhitran/.claude/logs/heartbeat.log 2>&1
0 8 * * * /home/nhitran/.claude/scripts/memory_reflect.py >> /home/nhitran/.claude/logs/memory_reflect.log 2>&1
```

**Obsidian integration:**
- Vault path: `Dynamous/Memory/` (use Obsidian's "Open folder as vault")
- No additional setup needed — vault is local filesystem

**Dependencies:** Phases 2, 4, 5, 6
**Estimated complexity:** Low (mostly configuration, not code)

---

## Build Order

```
Week 1:
├── Phase 1 (Foundation)     — Day 1: create vault structure
└── Phase 2 (Hooks)         — Day 2-3: session hooks

Week 2:
├── Phase 4 (GitHub)         — Day 4-5: GitHub integration (Phase 2 dependency)
└── Phase 3 (Memory Search) — Day 5-6: RAG pipeline (can parallelize with GitHub)

Week 3:
├── Phase 5 (Skills)         — Day 7-8: vault structure + code-decisions skill
└── Phase 8 (Security)      — Day 8: guardrails (can parallelize with Skills)

Week 4:
└── Phase 6 (Heartbeat)     — Day 9-10: heartbeat + daily reflection

Week 5:
└── Phase 9 (Deployment)    — Day 11: OS scheduler, cron, final wiring
```

**Parallelization opportunities:**
- Phase 3 (Memory Search) can start during Phase 4 (GitHub) — both are independent
- Phase 8 (Security) can run alongside Phase 5 (Skills) — no dependencies

**Total estimated time:** ~5-6 full days of implementation work

---

## Cost Estimate (Observer Mode)

- **Claude Max:** $0/month (Observer mode, no autonomous API calls)
- **Obsidian:** Free (local vault)
- **GitHub API:** Free (personal access token, rate limits: 5,000 req/hr for personal tokens)
- **sqlite-vec + FastEmbed:** Free (local, ~80MB model cache)
- **Total:** ~$0/month for local Observer-mode setup

---

*This PRD was generated from Nhi's requirements at `my-second-brain-requirements.md`. Revisit and update as your system evolves — particularly the proactivity level, which can be escalated from Observer to Advisor/Assistant/Partner as trust grows.*