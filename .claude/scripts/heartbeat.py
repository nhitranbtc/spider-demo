#!/usr/bin/env python3
"""
Heartbeat — Observer mode proactive monitoring.
Runs every 30 minutes, gathers data from integrations, surfaces notifications.

Observer mode: notify only, never act autonomously.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent
VAULT_PATH = REPO_ROOT / "Dynamous" / "Memory"
STATE_DIR = REPO_ROOT / ".claude" / "data" / "state"
STATE_FILE = STATE_DIR / "heartbeat-state.json"
LOG_DIR = REPO_ROOT / ".claude" / "logs"

# Load .env if present
from dotenv import load_dotenv
load_dotenv(REPO_ROOT / ".env")


def ensure_dirs():
    """Ensure required directories exist."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def load_state() -> dict:
    """Load previous heartbeat state."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {"last_prs": [], "last_check": None, "last_summary": None}


def save_state(state: dict):
    """Save current heartbeat state."""
    STATE_FILE.write_text(json.dumps(state, indent=2))


def build_snapshot() -> dict:
    """
    Gather current state from all integrations.
    Returns a snapshot dict.
    """
    snapshot = {
        "timestamp": datetime.now().isoformat(),
        "pending_prs": [],
        "summary": None
    }

    # Get GitHub username from USER.md
    user_file = VAULT_PATH / "USER.md"
    github_username = None
    if user_file.exists():
        content = user_file.read_text()
        for line in content.split("\n"):
            if "github.com/" in line.lower():
                # Extract username from URL or text
                parts = line.split("github.com/")
                if len(parts) > 1:
                    github_username = parts[1].strip().split("/")[0]
                    break
        # Also check for explicit username field
        for line in content.split("\n"):
            if line.strip().startswith("- **Username:**"):
                github_username = line.split("**")[-1].strip()
                break

    if not github_username:
        github_username = os.environ.get("GITHUB_USERNAME", "your-github-username")

    # Check for GITHUB_TOKEN
    if not os.environ.get("GITHUB_TOKEN"):
        snapshot["error"] = "GITHUB_TOKEN not set"
        return snapshot

    # Query GitHub for pending PRs
    try:
        script_path = REPO_ROOT / ".claude" / "scripts" / "integrations" / "github.py"
        result = subprocess.run(
            ["python3", str(script_path), "pending-review", "-u", github_username, "--max-age", "168"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0 and result.stdout.strip():
            snapshot["pending_prs"] = result.stdout.strip().split("\n\n")
            snapshot["pending_pr_count"] = len(snapshot["pending_prs"])
        elif "No PRs pending" in result.stdout:
            snapshot["pending_pr_count"] = 0
    except Exception as e:
        snapshot["error"] = str(e)

    # Generate summary
    if snapshot.get("pending_pr_count", 0) > 0:
        snapshot["summary"] = f"{snapshot['pending_pr_count']} PR(s) need your review"
    else:
        snapshot["summary"] = "No action items"

    return snapshot


def diff_snapshot(prev: dict, curr: dict) -> list[str]:
    """
    Compare snapshots, return list of new/changed items to notify about.
    Only notifies on actual changes.
    """
    notifications = []

    # Check for new pending PRs
    prev_prs = set()
    if "pending_prs" in prev:
        for pr in prev.get("pending_prs", []):
            # Extract PR identifier (repo + number) from notification text
            if "PR #" in pr:
                prev_prs.add(pr.split("PR #")[1].split(":")[0] if "PR #" in pr else "")

    new_prs = []
    for pr in curr.get("pending_prs", []):
        if "PR #" in pr:
            pr_id = pr.split("PR #")[1].split(":")[0]
            if pr_id not in prev_prs:
                new_prs.append(pr)

    if new_prs:
        notifications.append(f"🆕 {len(new_prs)} new PR(s) need your review:")
        for pr in new_prs[:5]:  # Limit to 5
            notifications.append(f"   {pr.split('[')[1].split(']')[0] if '[' in pr else 'unknown'}: {pr.split(':')[1].strip() if ':' in pr else pr}")

    # Check for summary changes
    if prev.get("summary") != curr.get("summary") and curr.get("summary"):
        # Only notify if there's an actual action item
        if "need your review" in curr.get("summary", ""):
            notifications.append(f"📋 {curr['summary']}")

    return notifications


def notify(message: str):
    """Send notification via Linux notify-send."""
    try:
        subprocess.run(
            ["notify-send", "-a", "Second Brain", "Heartbeat", message],
            capture_output=True,
            timeout=5
        )
    except Exception:
        # Fallback: just print
        print(f"[Heartbeat] {message}")


def main():
    ensure_dirs()

    # Load previous state
    prev_state = load_state()

    # Build current snapshot
    curr_snapshot = build_snapshot()

    # Check for errors
    if "error" in curr_snapshot:
        print(f"Heartbeat error: {curr_snapshot['error']}")
        # Still save state so we don't keep erroring
        save_state(curr_snapshot)
        sys.exit(0)

    # Diff against previous
    if prev_state.get("last_check"):
        changes = diff_snapshot(prev_state, curr_snapshot)
        if changes:
            notify("\n".join(changes))
        else:
            print(f"[{datetime.now().strftime('%H:%M')}] No changes detected")
    else:
        # First run — just report current state
        if curr_snapshot.get("pending_pr_count", 0) > 0:
            notify(f"📋 {curr_snapshot['pending_pr_count']} PR(s) need your review")

    # Save state
    save_state({
        "last_prs": curr_snapshot.get("pending_prs", []),
        "last_check": curr_snapshot["timestamp"],
        "last_summary": curr_snapshot.get("summary"),
        "pending_count": curr_snapshot.get("pending_pr_count", 0)
    })

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Heartbeat complete — {curr_snapshot.get('summary', 'unknown')}")


if __name__ == "__main__":
    main()