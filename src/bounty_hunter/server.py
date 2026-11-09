import os
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from bounty_hunter.models import Bounty, BountyStatus, FinancialSummary, SolutionDraft
from bounty_hunter.ledger import FinancialLedger
from bounty_hunter.scanners.fixture_scanner import FixtureScanner
from bounty_hunter.scanners.github_scanner import GitHubScanner
from bounty_hunter.triage import TriageEngine
from bounty_hunter.solver import SolutionGenerator

def create_app(ledger: Optional[FinancialLedger] = None) -> FastAPI:
    app = FastAPI(title="AI Bounty Hunter Agent API", version="0.1.0")
    active_ledger = ledger if ledger is not None else FinancialLedger()
    triage_engine = TriageEngine()
    solver = SolutionGenerator()

    html_file = Path(__file__).parent / "dashboard.html"

    @app.get("/", response_class=HTMLResponse)
    def index():
        if html_file.exists():
            return html_file.read_text(encoding="utf-8")
        return "<h1>AI Bounty Hunter Dashboard</h1>"

    @app.get("/api/summary", response_model=FinancialSummary)
    def get_summary(days_elapsed: int = 1):
        return active_ledger.get_summary(days_elapsed=days_elapsed)

    @app.get("/api/bounties", response_model=List[Bounty])
    def get_bounties():
        return active_ledger.get_bounties()

    @app.post("/api/scan", response_model=List[Bounty])
    def scan_bounties(
        source: str = Query("fixture"),
        language: Optional[str] = None,
        min_reward: float = 0.0
    ):
        if source == "github":
            scanner = GitHubScanner()
            bounties = scanner.scan(language=language, min_reward=min_reward)
            # If github returned 0 due to rate limit/offline, fallback to fixture
            if not bounties:
                bounties = FixtureScanner().scan(language=language, min_reward=min_reward)
        else:
            scanner = FixtureScanner()
            bounties = scanner.scan(language=language, min_reward=min_reward)

        for b in bounties:
            active_ledger.save_bounty(b)

        return active_ledger.get_bounties()

    @app.post("/api/solve/{bounty_id}", response_model=SolutionDraft)
    def solve_bounty(bounty_id: str):
        bounties = active_ledger.get_bounties()
        match = next((b for b in bounties if b.id == bounty_id), None)
        if not match:
            raise HTTPException(status_code=404, detail=f"Bounty {bounty_id} not found in database.")

        score = triage_engine.evaluate(match)
        # Log small token spend for solver
        active_ledger.record_spend(
            amount_usd=score.estimated_token_cost,
            description=f"Inference token spend to draft PR for {bounty_id}",
            bounty_id=bounty_id
        )

        draft = solver.solve(match, score)
        active_ledger.update_bounty_status(bounty_id, BountyStatus.SOLVED)
        return draft

    @app.post("/api/payout/{bounty_id}")
    def claim_payout(bounty_id: str, amount: float = Query(...)):
        bounties = active_ledger.get_bounties()
        match = next((b for b in bounties if b.id == bounty_id), None)
        if not match:
            raise HTTPException(status_code=404, detail=f"Bounty {bounty_id} not found in database.")

        active_ledger.update_bounty_status(bounty_id, BountyStatus.PAID)
        record = active_ledger.record_earning(
            amount_usd=amount,
            description=f"Bounty reward received for merged PR on {bounty_id}",
            bounty_id=bounty_id
        )
        return {"status": "SUCCESS", "record_id": record.id, "amount_usd": amount}

    return app
