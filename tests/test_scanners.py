import pytest
from bounty_hunter.scanners.base import parse_reward_amount, BaseScanner
from bounty_hunter.scanners.fixture_scanner import FixtureScanner
from bounty_hunter.scanners.github_scanner import GitHubScanner
from bounty_hunter.models import Bounty

def test_parse_reward_amount():
    assert parse_reward_amount("Bounty: $50") == 50.0
    assert parse_reward_amount("Fix auth bug - $120.50 reward") == 120.50
    assert parse_reward_amount("250 USD on merge") == 250.0
    assert parse_reward_amount("bounty: 75 usd") == 75.0
    assert parse_reward_amount("Reward: $1,000") == 1000.0
    assert parse_reward_amount("Just a regular bug fix") == 0.0
    assert parse_reward_amount("") == 0.0

def test_fixture_scanner_returns_bounties():
    scanner = FixtureScanner()
    bounties = scanner.scan()
    assert len(bounties) > 0
    assert all(isinstance(b, Bounty) for b in bounties)
    
    # Check language filter
    py_bounties = scanner.scan(language="Python")
    assert all(b.language == "Python" for b in py_bounties)
    assert len(py_bounties) > 0

    # Check min_reward filter
    high_value = scanner.scan(min_reward=80.0)
    assert all(b.reward_usd >= 80.0 for b in high_value)

def test_github_scanner_parser_and_offline_fallback():
    scanner = GitHubScanner(token=None)
    # When offline or without network, scanner should fallback or mock cleanly
    mock_item = {
        "id": 987654321,
        "title": "Add retry logic to webhook client ($60)",
        "html_url": "https://github.com/example-org/fast-webhooks/issues/42",
        "body": "We need exponential backoff. Bounty: $60 USD upon merge.",
        "labels": [{"name": "bounty"}, {"name": "python"}],
        "repository_url": "https://api.github.com/repos/example-org/fast-webhooks"
    }
    bounty = scanner.parse_github_issue(mock_item)
    assert bounty.id == "gh-987654321"
    assert bounty.reward_usd == 60.0
    assert bounty.repository == "example-org/fast-webhooks"
    assert "bounty" in bounty.labels
