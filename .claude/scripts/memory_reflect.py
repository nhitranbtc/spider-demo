#!/usr/bin/env python3
"""
Daily reflection — promote important items from daily log to MEMORY.md.
Runs daily at 8 AM. Mirrors human memory: short-term → long-term consolidation.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

REPO_ROOT = Path(__file__).parent.parent.parent
VAULT_PATH = REPO_ROOT / "Dynamous" / "Memory"
MEMORY_FILE = VAULT_PATH / "MEMORY.md"


def get_yesterday_log() -> Path | None:
    """Get yesterday's daily log path."""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    log_path = VAULT_PATH / "daily" / f"{yesterday}.md"
    return log_path if log_path.exists() else None


def extract_key_items(log_content: str) -> list[tuple[str, str]]:
    """
    Extract items that should be promoted to MEMORY.md.
    Looks for:
    - Code decisions (marked with [decision], [architecture], [tradeoff])
    - Lessons learned (marked with [lesson])
    - Important facts (marked with [fact])
    - Project updates
    """
    items = []
    lines = log_content.split("\n")

    markers = {
        "[DECISION]": "decision",
        "[ARCHITECTURE]": "architecture",
        "[TRADE]": "tradeoff",
        "[LESSON]": "lesson",
        "[FACT]": "fact",
    }

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("##"):
            continue

        for marker, item_type in markers.items():
            if marker in stripped.upper():
                # Extract the relevant content
                content = stripped.split("]")[1].strip() if "]" in stripped else stripped
                items.append((item_type, content))
                break

    return items


def promote_to_memory(items: list[tuple[str, str]]):
    """
    Add extracted items to MEMORY.md.
    Maintains the MEMORY.md structure: decisions, lessons, facts sections.
    """
    if not items:
        print("No items to promote.")
        return

    # Read current MEMORY.md
    content = MEMORY_FILE.read_text() if MEMORY_FILE.exists() else ""

    # Find insertion point for each item type
    sections = {
        "decision": "## Code Decisions & Architectural Tradeoffs",
        "architecture": "## Code Decisions & Architectural Tradeoffs",
        "tradeoff": "## Code Decisions & Architectural Tradeoffs",
        "lesson": "## Lessons Learned",
        "fact": "## Important Facts"
    }

    # For simplicity, append to the appropriate section
    # In production, you'd want more sophisticated section detection
    new_entries = []
    date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    for item_type, item_content in items:
        new_entries.append(f"- [{item_type.upper()}] {item_content} *(from {date})*")

    if new_entries:
        # Append to MEMORY.md
        new_section = "\n\n## Items Promoted from Daily Log\n"
        new_section += "\n".join(new_entries)

        if "## Items Promoted from Daily Log" in content:
            # Replace existing section
            parts = content.split("## Items Promoted from Daily Log")
            content = parts[0] + new_section + "\n"
        else:
            content += new_section

        MEMORY_FILE.write_text(content)
        print(f"Promoted {len(items)} items to MEMORY.md")


def archive_daily_log(log_path: Path):
    """Archive the daily log to history."""
    history_dir = log_path.parent / "history"
    history_dir.mkdir(exist_ok=True)

    # Move the file
    history_path = history_dir / log_path.name
    log_path.rename(history_path)
    print(f"Archived {log_path.name} → {history_path}")


def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Daily reflection starting...")

    # Get yesterday's log
    yesterday_log = get_yesterday_log()
    if not yesterday_log:
        print("No yesterday's log found — skipping.")
        sys.exit(0)

    # Read log content
    log_content = yesterday_log.read_text()

    # Extract key items
    items = extract_key_items(log_content)

    # Promote to MEMORY.md
    promote_to_memory(items)

    # Archive the log
    archive_daily_log(yesterday_log)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Daily reflection complete.")


if __name__ == "__main__":
    main()