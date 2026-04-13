#!/usr/bin/env python3
"""
SessionEnd Hook: On session end, save conversation context to daily log
"""

import sys
from datetime import datetime
from paths import DAILY_PATH

def extract_session_summary(transcript_text):
    """
    Extract a brief summary from the session transcript.
    Returns: (topic_summary, key_points) tuple.
    """
    lines = transcript_text.split("\n")

    # Skip very short transcripts
    if len(lines) < 5:
        return None, []

    # Get last 50 lines for summary (recent context matters most)
    recent = lines[-50:] if len(lines) > 50 else lines

    # Extract lines that look like decisions, conclusions, or important notes
    important = []
    for line in recent:
        stripped = line.strip()
        if not stripped or len(stripped) < 10:
            continue
        # Look for assistant messages (start with ## or are paragraphs)
        if stripped.startswith("##") or (len(stripped) > 30 and not stripped.startswith("User")):
            important.append(stripped[:200])  # Cap at 200 chars

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for item in important:
        if item not in seen:
            seen.add(item)
            unique.append(item)

    summary = " | ".join(unique[:5]) if unique else None
    return summary, unique[-10:] if unique else []  # Last 10 key points

def append_to_daily_log(session_summary, key_points):
    """Append session summary to today's daily log."""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = DAILY_PATH / f"{today}.md"

    if not daily_file.exists():
        DAILY_PATH.mkdir(parents=True, exist_ok=True)
        daily_file.write_text(f"# {today}\n\n## Session End\n")

    existing = daily_file.read_text()

    timestamp = datetime.now().strftime("%H:%M:%S")
    new_content = f"\n\n## Session End ({timestamp})\n"
    if session_summary:
        new_content += f"**Summary:** {session_summary}\n"
    if key_points:
        new_content += "\n**Key points from session:**\n"
        for point in key_points:
            new_content += f"- {point}\n"

    daily_file.write_text(existing + new_content)

def main():
    # Read from stdin (transcript is passed via stdin)
    transcript = sys.stdin.read()

    if not transcript or len(transcript) < 50:
        sys.exit(0)

    summary, key_points = extract_session_summary(transcript)

    if summary:
        append_to_daily_log(summary, key_points)

if __name__ == "__main__":
    main()