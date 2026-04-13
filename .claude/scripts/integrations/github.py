#!/usr/bin/env python3
"""
GitHub integration for Nhi's Second Brain
Handles PR review tracking and surfacing (Observer mode: read-only)
"""

import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Load .env if present
from dotenv import load_dotenv
REPO_ROOT = Path(__file__).parent.parent.parent.parent
load_dotenv(REPO_ROOT / ".env")

try:
    from github import Github
except ImportError:
    print("Error: PyGithub not installed. Run: pip install pygithub")
    sys.exit(1)


@dataclass
class PullRequest:
    repo: str
    number: int
    title: str
    author: str
    url: str
    state: str
    created_at: datetime
    requested_reviewers: list
    labels: list

    def age_hours(self) -> int:
        return int((datetime.now() - self.created_at).total_seconds() / 3600)

    def is_pending_review(self, username: str) -> bool:
        return username in self.requested_reviewers


@dataclass
class ReviewDecision:
    repo: str
    pr_number: int
    pr_title: str
    review_state: str  # APPROVED, CHANGES_REQUESTED, COMMENTED, PENDING
    submitted_at: datetime
    body: Optional[str] = None


def get_github_client() -> Github:
    """Create GitHub client with token from environment."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")
    return Github(token)


def get_pending_prs_for_user(username: str, max_age_hours: int = 168) -> list[PullRequest]:
    """
    Get open PRs where user is a requested reviewer.
    max_age_hours: filter out PRs older than this (default: 7 days)
    """
    g = get_github_client()
    user = g.get_user(username)
    pending = []

    # Get repos the user has access to
    # Note: This is a simplified approach. For full coverage, you may want to
    # configure specific repos in USER.md
    for repo in user.get_repos(type="all", sort="updated", direction="desc")[:50]:
        try:
            # Skip forks and private repos unless user is a collaborator
            if repo.fork:
                continue

            # Get PRs where user is a requested reviewer
            prs = repo.get_pulls(state="open", sort="updated", direction="desc")

            for pr in prs[:20]:
                reviewers = [r.login for r in pr.get_review_requests()[0]]
                if username in reviewers:
                    age = (datetime.now() - pr.created_at).total_seconds() / 3600
                    if age <= max_age_hours:
                        pending.append(PullRequest(
                            repo=repo.full_name,
                            number=pr.number,
                            title=pr.title,
                            author=pr.user.login,
                            url=pr.html_url,
                            state=pr.state,
                            created_at=pr.created_at,
                            requested_reviewers=reviewers,
                            labels=[l.name for l in pr.get_labels()]
                        ))
        except Exception as e:
            # Skip repos we don't have access to
            continue

    return pending


def get_review_history(username: str, repo_name: Optional[str] = None, limit: int = 20) -> list[ReviewDecision]:
    """
    Get user's review history across repos or for a specific repo.
    """
    g = get_github_client()

    if repo_name:
        repos = [g.get_repo(repo_name)]
    else:
        user = g.get_user(username)
        repos = user.get_repos(type="all", sort="updated", direction="desc")[:30]

    history = []

    for repo in repos:
        try:
            # Get user's activity for this repo
            events = list(repo.get_events()[:100])

            for event in events:
                if event.type == "PullRequestReviewEvent" and event.actor.login == username:
                    pr = event.payload.get("review", {}).get("pull_request")
                    if pr:
                        review = event.payload.get("review", {})
                        history.append(ReviewDecision(
                            repo=repo.full_name,
                            pr_number=pr.get("number"),
                            pr_title=pr.get("title"),
                            review_state=review.get("state"),
                            submitted_at=event.created_at,
                            body=review.get("body")
                        ))
                        if len(history) >= limit:
                            return history
        except Exception:
            continue

    return history


def format_pr_notification(pr: PullRequest) -> str:
    """Format a PR for notification."""
    age = pr.age_hours()
    age_str = f"{age}h" if age < 24 else f"{age // 24}d"

    lines = [
        f"[{pr.repo}] PR #{pr.number}: {pr.title}",
        f"  Author: @{pr.author} | Age: {age_str} | Labels: {', '.join(pr.labels) or 'none'}",
        f"  URL: {pr.url}"
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GitHub integration CLI")
    parser.add_argument("action", choices=["pending-review", "review-history"])
    parser.add_argument("--username", "-u", required=True, help="GitHub username")
    parser.add_argument("--repo", "-r", help="Specific repo (for review-history)")
    parser.add_argument("--max-age", type=int, default=168, help="Max age in hours (default: 168 = 7 days)")

    args = parser.parse_args()

    if args.action == "pending-review":
        try:
            prs = get_pending_prs_for_user(args.username, args.max_age)
            if prs:
                print(f"Found {len(prs)} PRs pending your review:\n")
                for pr in sorted(prs, key=lambda x: x.created_at):
                    print(format_pr_notification(pr))
                    print()
            else:
                print("No PRs pending your review.")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.action == "review-history":
        history = get_review_history(args.username, args.repo)
        if history:
            print(f"Recent review activity:\n")
            for r in history[:10]:
                print(f"[{r.repo}] #{r.pr_number}: {r.pr_title} — {r.review_state} at {r.submitted_at.strftime('%Y-%m-%d %H:%M')}")
        else:
            print("No review history found.")


def main():
    """Entry point for query.py integration."""
    import argparse

    parser = argparse.ArgumentParser(description="GitHub integration CLI")
    parser.add_argument("action", choices=["pending-review", "review-history"])
    parser.add_argument("--username", "-u", required=True, help="GitHub username")
    parser.add_argument("--repo", "-r", help="Specific repo (for review-history)")
    parser.add_argument("--max-age", type=int, default=168, help="Max age in hours (default: 168 = 7 days)")

    args = parser.parse_args()

    if args.action == "pending-review":
        try:
            prs = get_pending_prs_for_user(args.username, args.max_age)
            if prs:
                print(f"Found {len(prs)} PRs pending your review:\n")
                for pr in sorted(prs, key=lambda x: x.created_at):
                    print(format_pr_notification(pr))
                    print()
            else:
                print("No PRs pending your review.")
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)

    elif args.action == "review-history":
        history = get_review_history(args.username, args.repo)
        if history:
            print(f"Recent review activity:\n")
            for r in history[:10]:
                print(f"[{r.repo}] #{r.pr_number}: {r.pr_title} — {r.review_state} at {r.submitted_at.strftime('%Y-%m-%d %H:%M')}")
        else:
            print("No review history found.")