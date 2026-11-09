from typing import Optional, List
from datetime import datetime, timezone
from bounty_hunter.models import Bounty, BountyStatus
from bounty_hunter.scanners.base import BaseScanner

FIXTURE_BOUNTIES = [
    Bounty(
        id="algora-2041",
        title="Add exponential backoff retry to webhook dispatcher ($45)",
        url="https://github.com/fast-event-hub/dispatcher/issues/2041",
        source="algora",
        repository="fast-event-hub/dispatcher",
        reward_usd=45.0,
        description="When webhooks fail with 5xx or timeout, we currently drop them. Need a 3-retry exponential backoff with jitter.",
        language="Python",
        status=BountyStatus.DISCOVERED,
        labels=["bounty", "algora", "python", "backend"],
        created_at=datetime.now(timezone.utc)
    ),
    Bounty(
        id="polar-1082",
        title="Sanitize SVG uploads to prevent XSS vulnerability ($120)",
        url="https://github.com/open-media-store/core/issues/1082",
        source="polar",
        repository="open-media-store/core",
        reward_usd=120.0,
        description="Users can upload SVGs containing malicious `<script>` tags. We need to parse and strip script, onload, and iframe elements using defusedxml or clean parser.",
        language="Python",
        status=BountyStatus.DISCOVERED,
        labels=["bounty", "security", "polar", "python"],
        created_at=datetime.now(timezone.utc)
    ),
    Bounty(
        id="gh-7840",
        title="Add TypeScript types and validation for payment webhook payloads ($70)",
        url="https://github.com/merchant-dock/sdk-js/issues/7840",
        source="github",
        repository="merchant-dock/sdk-js",
        reward_usd=70.0,
        description="Currently webhook payloads are typed as `any`. Define Zod schemas and TypeScript interfaces for InvoiceCreated and InvoicePaid events.",
        language="TypeScript",
        status=BountyStatus.DISCOVERED,
        labels=["bounty", "typescript", "good-first-issue"],
        created_at=datetime.now(timezone.utc)
    ),
    Bounty(
        id="gh-3319",
        title="Fix pagination offset calculation when page size is larger than total count ($25)",
        url="https://github.com/data-query/fast-sql/issues/3319",
        source="github",
        repository="data-query/fast-sql",
        reward_usd=25.0,
        description="When limit > count, the next_page token returns a negative offset causing an IndexError in slice.",
        language="Python",
        status=BountyStatus.DISCOVERED,
        labels=["bounty", "bug", "python"],
        created_at=datetime.now(timezone.utc)
    ),
    Bounty(
        id="gh-5502",
        title="Write API documentation and OpenAPI 3.1 specification for Auth endpoints ($50)",
        url="https://github.com/auth-mesh/proxy/issues/5502",
        source="github",
        repository="auth-mesh/proxy",
        reward_usd=50.0,
        description="Missing OpenAPI specs for /v1/oauth/token and /v1/oauth/introspect. Need yaml docs and response schema.",
        language="Documentation",
        status=BountyStatus.DISCOVERED,
        labels=["bounty", "docs", "good-first-issue"],
        created_at=datetime.now(timezone.utc)
    )
]

class FixtureScanner(BaseScanner):
    """Scanner providing deterministic fixtures for offline operation, testing and simulation."""

    def __init__(self, fixtures: Optional[List[Bounty]] = None):
        self.fixtures = fixtures if fixtures is not None else list(FIXTURE_BOUNTIES)

    def scan(self, language: Optional[str] = None, min_reward: float = 0.0) -> List[Bounty]:
        results = []
        for b in self.fixtures:
            if language and b.language and language.lower() not in b.language.lower():
                continue
            if b.reward_usd < min_reward:
                continue
            results.append(b)
        return results
