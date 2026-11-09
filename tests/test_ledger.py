import pytest
import os
import tempfile
from datetime import datetime, timezone
from bounty_hunter.models import Bounty, BountyStatus, FinancialRecord, FinancialSummary
from bounty_hunter.ledger import FinancialLedger

@pytest.fixture
def temp_ledger(tmp_path):
    db_file = tmp_path / "test_bounty.db"
    ledger = FinancialLedger(db_path=str(db_file))
    return ledger

def test_ledger_initialization_and_summary_defaults(temp_ledger):
    summary = temp_ledger.get_summary()
    assert isinstance(summary, FinancialSummary)
    assert summary.total_earned_usd == 0.0
    assert summary.total_spent_usd == 0.0
    assert summary.net_profit_usd == 0.0
    assert summary.target_progress_percent == 0.0
    assert summary.runway_days_remaining == 29

def test_record_spend_and_earning(temp_ledger):
    temp_ledger.record_spend(0.15, "API tokens for evaluating bounty #101", bounty_id="gh-101")
    temp_ledger.record_spend(0.05, "Cloud VPS runtime 1 hour")
    temp_ledger.record_earning(50.0, "Merged PR #45 payout", bounty_id="gh-101")

    records = temp_ledger.get_records()
    assert len(records) == 3

    summary = temp_ledger.get_summary(days_elapsed=2)
    assert summary.total_spent_usd == 0.20
    assert summary.total_earned_usd == 50.0
    assert summary.net_profit_usd == 49.80
    assert summary.target_progress_percent == 50.0
    assert summary.runway_days_remaining == 28

def test_save_and_retrieve_bounties(temp_ledger):
    bounty = Bounty(
        id="gh-2041",
        title="Add exponential backoff",
        url="https://github.com/example/repo/issues/2041",
        source="github",
        repository="example/repo",
        reward_usd=45.0,
        description="Need backoff logic",
        language="Python",
    )
    temp_ledger.save_bounty(bounty)
    
    bounties = temp_ledger.get_bounties()
    assert len(bounties) == 1
    assert bounties[0].id == "gh-2041"
    assert bounties[0].reward_usd == 45.0

    # Updating status
    temp_ledger.update_bounty_status("gh-2041", BountyStatus.PAID)
    updated = temp_ledger.get_bounties()
    assert updated[0].status == BountyStatus.PAID

    summary = temp_ledger.get_summary()
    assert summary.bounties_solved_count == 1
