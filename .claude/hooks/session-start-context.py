#!/usr/bin/env python3
"""
SessionStart Hook: Inject memory context into every conversation
Reads SOUL.md + USER.md + MEMORY.md + recent daily logs → prints to stdout (injected into context)
"""

from paths import VAULT_PATH, DAILY_PATH

def get_recent_daily_logs(n=3):
    """Get the n most recent daily logs."""
    if not DAILY_PATH.exists():
        return []
    logs = sorted(DAILY_PATH.glob("*.md"), reverse=True)
    return logs[:n]

def main():
    outputs = []

    # Load SOUL.md
    soul = VAULT_PATH / "SOUL.md"
    if soul.exists():
        outputs.append(f"\n=== SOUL.md (Agent Personality) ===\n{soul.read_text()}\n")

    # Load USER.md
    user = VAULT_PATH / "USER.md"
    if user.exists():
        outputs.append(f"\n=== USER.md (User Profile) ===\n{user.read_text()}\n")

    # Load MEMORY.md
    memory = VAULT_PATH / "MEMORY.md"
    if memory.exists():
        outputs.append(f"\n=== MEMORY.md (Long-Term Memory) ===\n{memory.read_text()}\n")

    # Load recent daily logs
    recent_logs = get_recent_daily_logs(3)
    if recent_logs:
        outputs.append("\n=== Recent Daily Logs ===\n")
        for log in recent_logs:
            outputs.append(f"\n--- {log.name} ---\n{log.read_text()}\n")

    print("\n".join(outputs))

if __name__ == "__main__":
    main()