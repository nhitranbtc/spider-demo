#!/usr/bin/env python3
"""
Query CLI — unified interface for all integrations.
Usage: query.py <integration> <action> [args]

Examples:
    query.py github pending-review -u myuser
    query.py github review-history -u myuser --repo owner/repo
    query.py integrations list
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / ".claude" / "scripts"))

# Load .env if present
from dotenv import load_dotenv
load_dotenv(REPO_ROOT / ".env")

from integrations import registry


def main():
    if len(sys.argv) < 2:
        print("Usage: query.py <integration> <action> [args]")
        print("\nIntegrations:")
        print(registry.list_integrations())
        sys.exit(1)

    integration = sys.argv[1]

    if integration == "integrations":
        print(registry.list_integrations())
        sys.exit(0)

    # Import and delegate to specific integration
    if integration == "github":
        from integrations.github import main as github_main
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        github_main()
    else:
        print(f"Unknown integration: {integration}")
        print(f"Available: {', '.join([i.name for i in registry.INTEGRATIONS])}")
        sys.exit(1)


if __name__ == "__main__":
    main()