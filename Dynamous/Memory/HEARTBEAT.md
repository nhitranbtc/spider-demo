# HEARTBEAT.md — Heartbeat Checklist

> Heartbeat runs every 30 minutes during active hours. Observer mode: notify only, no autonomous actions.

## Monitoring Checklist

### GitHub PR Reviews
- [ ] Check open PRs where Nhi is a requested reviewer
- [ ] Flag PRs that have been waiting > 48 hours
- [ ] Log review activity to daily log

### Daily Summary
- [ ] Collect activity from last 30 minutes
- [ ] If significant: prepare notification
- [ ] Update heartbeat state (diff against previous)

## Notification Rules

- **Only notify on new/changed items** — no spam for unchanged state
- **Format:** concise, actionable, technical
- **Delivery:** Linux `notify-send` via CLI

## State Management

- Snapshot stored at: `.claude/data/state/heartbeat-state.json`
- Diff against previous snapshot before notifying
- Only alert on deltas

## Observer Mode Constraints

- ❌ Do NOT draft messages or emails
- ❌ Do NOT post to any platform
- ❌ Do NOT auto-organize files
- ✅ DO: Surface information, log activity, prepare notifications

## Active Hours

<!-- Configure: e.g., 9 AM - 6 PM local time -->
<!-- Use cron expression: 0 9-18 * * 1-5 for weekdays 9 AM - 6 PM -->