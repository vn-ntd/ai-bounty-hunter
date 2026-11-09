import pytest
from datetime import datetime, timezone
from bounty_hunter.models import Bounty, BountyStatus, TriageScore, SolutionDraft, FinancialRecord

def test_bounty_creation_and_defaults():
    bounty = Bounty(
        id="gh-101",
        title="Fix NullPointerException in JWT auth filter",
        url="https://github.com/example/auth-service/issues/101",
        source="github",
        repository="example/auth-service",
        reward_usd=50.0,
        description="The filter throws NPE when Authorization header is missing bearer prefix.",
        language="Python",
        created_at=datetime(2026, 11, 10, tzinfo=timezone.utc),
    )
    assert bounty.id == "gh-101"
    assert bounty.reward_usd == 50.0
    assert bounty.status == BountyStatus.DISCOVERED
    assert bounty.language == "Python"

def test_bounty_status_transitions():
    bounty = Bounty(
        id="gh-102",
        title="Doc typo",
        url="https://github.com/example/repo/issues/102",
        source="github",
        repository="example/repo",
        reward_usd=15.0,
    )
    bounty.status = BountyStatus.TRIAGED
    assert bounty.status == BountyStatus.TRIAGED
    bounty.status = BountyStatus.SOLVED
    assert bounty.status == BountyStatus.SOLVED

def test_triage_score_validation():
    score = TriageScore(
        bounty_id="gh-101",
        solvability_score=85,
        estimated_token_cost=0.08,
        difficulty="EASY",
        roi=625.0,
        reasoning="Well-defined NPE with exact stack trace."
    )
    assert score.solvability_score == 85
    assert score.roi == 625.0

def test_solution_draft_structure():
    solution = SolutionDraft(
        bounty_id="gh-101",
        root_cause="Authorization header stripped prematurely",
        patch_diff="--- a/jwt.py\n+++ b/jwt.py\n@@ ...",
        test_code="def test_jwt_auth_no_bearer(): ...",
        pr_title="fix: guard against missing Bearer prefix in JWT header",
        pr_body="## Problem\n...\n## Solution\n..."
    )
    assert "Authorization header" in solution.root_cause
    assert "fix:" in solution.pr_title

def test_financial_record_calculation():
    spend = FinancialRecord(
        record_type="SPEND",
        amount_usd=0.05,
        description="API tokens for analyzing issue #101"
    )
    earn = FinancialRecord(
        record_type="EARN",
        amount_usd=50.0,
        description="Bounty reward paid for PR #102"
    )
    assert spend.amount_usd == 0.05
    assert earn.amount_usd == 50.0
