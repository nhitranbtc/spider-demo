#!/usr/bin/env python3
"""
Integration registry — tracks available integrations and their status.
"""

from dataclasses import dataclass
from pathlib import Path
import os

# Load .env if present
from dotenv import load_dotenv
REPO_ROOT = Path(__file__).parent.parent.parent.parent
load_dotenv(REPO_ROOT / ".env")


@dataclass
class Integration:
    name: str
    enabled: bool
    auth_method: str  # "token", "oauth", "none"
    env_var: str | None  # e.g., "GITHUB_TOKEN"

    def check_configured(self) -> bool:
        """Check if this integration is properly configured."""
        if not self.enabled:
            return False
        if self.auth_method == "token":
            return bool(os.environ.get(self.env_var or ""))
        return True


INTEGRATIONS = [
    Integration(
        name="github",
        enabled=True,
        auth_method="token",
        env_var="GITHUB_TOKEN"
    ),
    Integration(
        name="gmail",
        enabled=False,
        auth_method="oauth",
        env_var="GMAIL_CLIENT_SECRET"
    ),
    Integration(
        name="obsidian",
        enabled=True,
        auth_method="none",
        env_var=None
    ),
]


def get_enabled_integrations() -> list[Integration]:
    """Return all enabled integrations."""
    return [i for i in INTEGRATIONS if i.enabled]


def get_configured_integrations() -> list[Integration]:
    """Return integrations that are both enabled and properly configured."""
    return [i for i in INTEGRATIONS if i.check_configured()]


def list_integrations() -> str:
    """Format integration status as a string."""
    lines = ["Available integrations:"]
    for i in INTEGRATIONS:
        status = "✅ configured" if i.check_configured() else ("❌ not configured" if i.enabled else "⚪ disabled")
        auth = f" ({i.auth_method})" if i.auth_method != "none" else ""
        lines.append(f"  {i.name}: {status}{auth}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(list_integrations())