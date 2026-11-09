import pytest
from datetime import datetime, timezone
from bounty_hunter.models import Bounty
from bounty_hunter.triage import TriageEngine

@pytest.fixture
def sample_bounties():
    return [
        Bounty(
            id="test-easy",
            title="Fix typo in README and add docstring to Client.connect ($15)",
            url="https://github.com/example/lib/issues/1",
            source="github",
            repository="example/lib",
            reward_usd=15.0,
            description="Fix minor typo in quickstart and document connect() params.",
            language="Python",
        ),
        Bounty(
            id="test-medium",
            title="Add exponential backoff retry to webhook dispatcher ($45)",
            url="https://github.com/example/dispatcher/issues/2",
            source="github",
            repository="example/dispatcher",
            reward_usd=45.0,
            description="When webhooks fail with 5xx or timeout, retry with backoff.",
            language="Python",
        ),
        Bounty(
            id="test-vague-hard",
            title="Rewrite entire database storage engine in Rust ($200)",
            url="https://github.com/example/db/issues/3",
            source="github",
            repository="example/db",
            reward_usd=200.0,
            description="We should rethink our entire storage layer architecture.",
            language="Rust",
        ),
        Bounty(
            id="test-zero-reward",
            title="General question about installation",
            url="https://github.com/example/db/issues/4",
            source="github",
            repository="example/db",
            reward_usd=0.0,
            description="How do I run this on Windows 11?",
            language="Unknown",
        )
    ]

def test_triage_evaluation_solvability_and_difficulty(sample_bounties):
    engine = TriageEngine()
    
    score_easy = engine.evaluate(sample_bounties[0])
    assert score_easy.difficulty == "EASY"
    assert score_easy.solvability_score >= 80
    assert score_easy.recommended_action == "PROCEED"
    assert score_easy.roi > 100.0

    score_hard = engine.evaluate(sample_bounties[2])
    assert score_hard.difficulty == "HARD"
    assert score_hard.solvability_score < 60
    assert score_hard.recommended_action in ["REVIEW_MANUALLY", "SKIP"]

def test_triage_handles_zero_reward_and_costs(sample_bounties):
    engine = TriageEngine()
    score_zero = engine.evaluate(sample_bounties[3])
    # Zero reward shouldn't crash with division by zero
    assert score_zero.roi <= 0.0
    assert score_zero.recommended_action == "SKIP"

def test_triage_ranking(sample_bounties):
    engine = TriageEngine()
    ranked = engine.rank(sample_bounties)
    
    assert len(ranked) == len(sample_bounties)
    # The first one should have high solvability & high ROI
    top_bounty, top_score = ranked[0]
    assert top_score.recommended_action == "PROCEED"
    # Zero reward should be at or near the bottom
    bottom_bounty, bottom_score = ranked[-1]
    assert bottom_bounty.reward_usd == 0.0
