#!/usr/bin/env python3
"""
Shared path configuration for hooks and scripts.
Single source of truth for vault and repo paths.
"""

from pathlib import Path

# All scripts are in .claude/hooks/ or .claude/scripts/
# .claude/hooks/script.py → 3 parents → repo root
# .claude/scripts/script.py → 3 parents → repo root
_REPO_ROOT = Path(__file__).parent.parent.parent

# Vault path (Dynamous/Memory at repo root)
VAULT_PATH = _REPO_ROOT / "Dynamous" / "Memory"

# Key subdirectories
DAILY_PATH = VAULT_PATH / "daily"
ERRORS_PATH = VAULT_PATH / "errors"
DECISIONS_PATH = VAULT_PATH / "decisions"