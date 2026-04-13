#!/usr/bin/env python3
"""
PreCompact Hook: Before auto-compaction, extract key decisions/facts from transcript → append to daily log
"""

import sys
from datetime import datetime
from paths import DAILY_PATH

def extract_key_facts(transcript_text):
    """
    Lightweight extraction of key facts from transcript.
    Looks for patterns like:
    - "decided to", "chose", "architecture", "tradeoff"
    - Code decisions, lessons learned
    Returns list of (category, fact) tuples.
    """
    facts = []
    lines = transcript_text.split("\n")

    decision_keywords = ["decided", "chose", "architecture", "tradeoff", "instead", "because", "alternative"]
    code_keywords = ["rust", "substrate", "polkadot", "api", "function", "impl", "struct", "enum"]

    for i, line in enumerate(lines):
        line_lower = line.lower()
        # Check for decision patterns
        if any(kw in line_lower for kw in decision_keywords):
            # Capture surrounding context (line + 1 before, line, 1 after)
            context_start = max(0, i - 1)
            context_end = min(len(lines), i + 2)
            context = " ".join(lines[context_start:context_end])
            if len(context) > 20:  # Filter noise
                facts.append(("decision", context.strip()))

        # Check for code/technical content
        if any(kw in line_lower for kw in code_keywords):
            context_start = max(0, i - 1)
            context_end = min(len(lines), i + 2)
            context = " ".join(lines[context_start:context_end])
            if len(context) > 20:
                facts.append(("technical", context.strip()))

    return facts

def append_to_daily_log(facts):
    """Append extracted facts to today's daily log."""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_file = DAILY_PATH / f"{today}.md"

    if not daily_file.exists():
        DAILY_PATH.mkdir(parents=True, exist_ok=True)
        daily_file.write_text(f"# {today}\n\n## Auto-Logged from Session\n")

    existing = daily_file.read_text()
    new_content = "\n\n## Extracted from Auto-Compaction\n"
    for category, fact in facts:
        new_content += f"- [{category.upper()}] {fact}\n"

    daily_file.write_text(existing + new_content)

def main():
    # Read from stdin (transcript is passed via stdin)
    transcript = sys.stdin.read()

    if not transcript or len(transcript) < 100:
        sys.exit(0)  # Skip empty or too-short transcripts

    facts = extract_key_facts(transcript)

    if facts:
        append_to_daily_log(facts)

if __name__ == "__main__":
    main()