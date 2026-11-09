from enum import Enum
from datetime import datetime, timezone
from typing import Optional, List
from pydantic import BaseModel, Field

class BountyStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    TRIAGED = "TRIAGED"
    SOLVED = "SOLVED"
    PR_SUBMITTED = "PR_SUBMITTED"
    MERGED = "MERGED"
    PAID = "PAID"
    REJECTED = "REJECTED"

class Bounty(BaseModel):
    id: str
    title: str
    url: str
    source: str = "github"
    repository: str
    reward_usd: float = 0.0
    description: str = ""
    language: Optional[str] = "Unknown"
    status: BountyStatus = BountyStatus.DISCOVERED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    labels: List[str] = Field(default_factory=list)

class TriageScore(BaseModel):
    bounty_id: str
    solvability_score: int  # 0 to 100
    estimated_token_cost: float  # USD
    difficulty: str  # EASY, MEDIUM, HARD
    roi: float  # (reward - cost) / max(cost, 0.001) or reward / cost
    reasoning: str
    recommended_action: str = "PROCEED"

class SolutionDraft(BaseModel):
    bounty_id: str
    root_cause: str
    patch_diff: str
    test_code: str
    pr_title: str
    pr_body: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FinancialRecord(BaseModel):
    id: Optional[int] = None
    record_type: str  # SPEND, EARN
    amount_usd: float
    description: str
    bounty_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class FinancialSummary(BaseModel):
    total_earned_usd: float
    total_spent_usd: float
    net_profit_usd: float
    target_usd: float = 100.0
    target_progress_percent: float
    runway_days_remaining: int
    bounties_solved_count: int
