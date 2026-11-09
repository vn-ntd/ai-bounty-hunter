import sys
import argparse
from typing import Optional, List
from bounty_hunter.ledger import FinancialLedger
from bounty_hunter.scanners.fixture_scanner import FixtureScanner
from bounty_hunter.scanners.github_scanner import GitHubScanner
from bounty_hunter.triage import TriageEngine
from bounty_hunter.solver import SolutionGenerator
from bounty_hunter.models import BountyStatus

def run_cli(argv: Optional[List[str]] = None) -> int:
    parent_p = argparse.ArgumentParser(add_help=False)
    parent_p.add_argument("--db", default="bounty_ledger.db", help="Path to SQLite ledger file")

    parser = argparse.ArgumentParser(
        prog="bounty-hunter",
        description="Autonomous Open-Source Bounty Hunter & Payout Engine",
        parents=[parent_p]
    )
    subparsers = parser.add_subparsers(dest="command")

    # Command: scan
    scan_p = subparsers.add_parser("scan", parents=[parent_p], help="Scan for active open-source bounties")
    scan_p.add_argument("--source", default="fixture", choices=["fixture", "github"], help="Scan source")
    scan_p.add_argument("--language", default=None, help="Filter by language")
    scan_p.add_argument("--min-reward", type=float, default=0.0, help="Minimum reward in USD")

    # Command: triage
    triage_p = subparsers.add_parser("triage", parents=[parent_p], help="Triage and rank bounties by solvability and ROI")
    triage_p.add_argument("--top", type=int, default=5, help="Number of top bounties to show")

    # Command: solve
    solve_p = subparsers.add_parser("solve", parents=[parent_p], help="Synthesize code patch, tests, and PR body")
    solve_p.add_argument("bounty_id", help="Bounty ID to solve")

    # Command: payout
    pay_p = subparsers.add_parser("payout", parents=[parent_p], help="Record payout for a merged PR")
    pay_p.add_argument("bounty_id", help="Bounty ID paid")
    pay_p.add_argument("amount", type=float, help="Reward amount in USD")

    # Command: status
    subparsers.add_parser("status", parents=[parent_p], help="Show 30-day financial survival progress toward $100")

    # Command: serve
    serve_p = subparsers.add_parser("serve", parents=[parent_p], help="Launch interactive Web Dashboard")
    serve_p.add_argument("--port", type=int, default=8000, help="Server port")
    serve_p.add_argument("--host", default="127.0.0.1", help="Server host")

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    ledger = FinancialLedger(db_path=args.db)

    if args.command == "scan":
        if args.source == "github":
            scanner = GitHubScanner()
            bounties = scanner.scan(language=args.language, min_reward=args.min_reward)
            if not bounties:
                bounties = FixtureScanner().scan(language=args.language, min_reward=args.min_reward)
        else:
            scanner = FixtureScanner()
            bounties = scanner.scan(language=args.language, min_reward=args.min_reward)

        for b in bounties:
            ledger.save_bounty(b)

        print(f"\nDiscovered {len(bounties)} bounties (Source: {args.source}):")
        print("-" * 75)
        for b in bounties:
            print(f"[{b.id}] ${b.reward_usd:6.2f} | {b.language:12} | {b.repository:25} | {b.title[:30]}")
        print("-" * 75)
        return 0

    elif args.command == "triage":
        bounties = ledger.get_bounties()
        if not bounties:
            print("No bounties in ledger. Run 'bounty-hunter scan' first.")
            return 0
        engine = TriageEngine()
        ranked = engine.rank(bounties)
        print(f"\nTop {min(args.top, len(ranked))} Triaged Bounties (Ranked by ROI & Solvability):")
        print("=" * 85)
        for b, score in ranked[:args.top]:
            print(f"[{b.id}] ${b.reward_usd:.2f} | Solvability: {score.solvability_score:3}/100 | ROI: {score.roi:6.1f}x | Action: {score.recommended_action:12}")
            print(f"    Repository: {b.repository} | Title: {b.title}")
            print(f"    Reasoning:  {score.reasoning}")
            print("-" * 85)
        return 0

    elif args.command == "solve":
        bounties = ledger.get_bounties()
        match = next((b for b in bounties if b.id == args.bounty_id), None)
        if not match:
            print(f"Error: Bounty {args.bounty_id} not found in database.")
            return 1

        engine = TriageEngine()
        score = engine.evaluate(match)
        ledger.record_spend(score.estimated_token_cost, f"Tokens to draft fix for {match.id}", bounty_id=match.id)

        solver = SolutionGenerator()
        draft = solver.solve(match, score)
        ledger.update_bounty_status(match.id, BountyStatus.SOLVED)

        print(f"\nGenerated Solution for [{match.id}]: {draft.pr_title}")
        print("=" * 80)
        print(f"Root Cause: {draft.root_cause}\n")
        print("--- Patch Diff ---")
        print(draft.patch_diff)
        print("--- Verification Unit Test ---")
        print(draft.test_code)
        print("=" * 80)
        print(f"Status updated to SOLVED. Estimated token spend logged: ${score.estimated_token_cost:.3f}\n")
        return 0

    elif args.command == "payout":
        ledger.update_bounty_status(args.bounty_id, BountyStatus.PAID)
        rec = ledger.record_earning(args.amount, f"Bounty payout for {args.bounty_id}", bounty_id=args.bounty_id)
        print(f"Recorded payout of ${args.amount:.2f} for bounty {args.bounty_id} (Record #{rec.id})")
        return 0

    elif args.command == "status":
        summary = ledger.get_summary()
        print("\n=======================================================")
        print("    AI AGENT 30-DAY SELF-SUSTENANCE FINANCIAL STATUS    ")
        print("=======================================================")
        print(f"Target Monthly Goal:      ${summary.target_usd:.2f} USD")
        print(f"Total Bounties Earned:    ${summary.total_earned_usd:.2f} USD")
        print(f"Total Token/VPS Cost:     ${summary.total_spent_usd:.2f} USD")
        print(f"Net Profit / Reserve:     ${summary.net_profit_usd:.2f} USD")
        print(f"Goal Progress:            {summary.target_progress_percent:.1f}%")
        print(f"Bounties Solved / Paid:   {summary.bounties_solved_count}")
        print(f"Runway Days Remaining:    {summary.runway_days_remaining} days")
        print("=======================================================\n")
        return 0

    elif args.command == "serve":
        import uvicorn
        from bounty_hunter.server import create_app
        app = create_app(ledger=ledger)
        print(f"\nLaunching Bounty Hunter Dashboard at http://{args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)
        return 0

    return 0

if __name__ == "__main__":
    sys.exit(run_cli(sys.argv[1:]))
