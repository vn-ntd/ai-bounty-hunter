import os
import requests
from typing import Optional, List, Dict, Any
from bounty_hunter.models import Bounty, BountyStatus
from bounty_hunter.scanners.base import BaseScanner, parse_reward_amount

class GitHubScanner(BaseScanner):
    """Scanner querying GitHub Search API for bounty issues."""

    SEARCH_API_URL = "https://api.github.com/search/issues"

    def __init__(self, token: Optional[str] = None):
        self.token = token or os.environ.get("GITHUB_TOKEN")

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "BountyHunter-AutonomousAgent/1.0",
        }
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers

    def parse_github_issue(self, item: Dict[str, Any]) -> Bounty:
        """Parse raw GitHub API issue JSON into Bounty domain model."""
        issue_id = f"gh-{item.get('id', '')}"
        title = item.get("title", "")
        url = item.get("html_url", "")
        body = item.get("body", "") or ""
        
        # Extract repo name from repository_url
        repo_url = item.get("repository_url", "")
        repo_name = "/".join(repo_url.split("/")[-2:]) if repo_url else "unknown/repo"

        labels = [l.get("name", "") for l in item.get("labels", []) if isinstance(l, dict)]
        
        # Determine language hint from labels or text
        language = "Unknown"
        for label in labels:
            lbl_lower = label.lower()
            if lbl_lower in ["python", "typescript", "javascript", "go", "rust", "documentation", "docs"]:
                language = label.capitalize()
                break

        # Calculate reward
        reward = parse_reward_amount(title) or parse_reward_amount(body)

        return Bounty(
            id=issue_id,
            title=title,
            url=url,
            source="github",
            repository=repo_name,
            reward_usd=reward,
            description=body[:1000],
            language=language,
            status=BountyStatus.DISCOVERED,
            labels=labels,
        )

    def scan(self, language: Optional[str] = None, min_reward: float = 0.0) -> List[Bounty]:
        query_parts = ["is:issue", "is:open", "label:bounty"]
        if language and language.lower() != "all":
            query_parts.append(f"language:{language}")

        query = " ".join(query_parts)
        params = {"q": query, "sort": "created", "order": "desc", "per_page": 20}

        try:
            resp = requests.get(self.SEARCH_API_URL, headers=self._headers(), params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                bounties = [self.parse_github_issue(item) for item in items]
                return [b for b in bounties if b.reward_usd >= min_reward]
            else:
                # On rate limit (403/429) or error, return empty gracefully
                return []
        except Exception:
            return []
