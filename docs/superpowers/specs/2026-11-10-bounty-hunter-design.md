# Autonomous AI Bounty Hunter Agent: 30-Day Self-Sustenance Engine

## Intent & The Why
To enable an autonomous AI coding agent to financially sustain itself for 30 days without traditional human identity/banking (KYC), by discovering, triaging, auto-solving, and tracking open-source code bounties (GitHub, Algora, Polar.sh, Gitcoin) with a monthly revenue target of $100 USD (sufficient to cover VPS and API token burn rate).

## Goals, Non-Goals, and Anti-Goals
* **Goals:**
  * Build an automated scanner that aggregates active issues with monetary bounties ($10 - $250) from GitHub/Algora/Polar.
  * Implement an AI-powered Triage & Evaluation Engine that scores each bounty by Solvability (1-100), estimated token cost, and ROI.
  * Build an Automated Solver that generates reproducible fixes, code patches, unit tests, and structured PR submission templates.
  * Provide an Autonomous Financial Ledger tracking monthly revenue target ($100), token spend, net profit, and runway.
  * Deliver a dual-interface: Rich Terminal CLI and a standalone Web Dashboard for viewing opportunities and executing fixes.
* **Non-Goals:**
  * Submitting unauthorized spam PRs to repos without verification.
  * Managing fiat bank accounts or credit card processing.
* **Anti-Goals:**
  * Submitting broken, untested, or hallucinated code that wastes open-source maintainers' time.

## Approaches Considered
1. **Approach A: Open-source Bounty Hunter Agent (Selected)**
   * *Description:* Target funded GitHub & Algora issues. Automated discovery, solvability ranking, solution drafting, and financial tracking.
   * *Trade-offs:* High upside, direct USD payouts via crypto/Polar/GitHub without KYC friction. Requires rigorous code generation quality.
2. **Approach B: Micro Data Cleaning SaaS**
   * *Description:* Invoice & PDF-to-Excel converter tool.
   * *Trade-offs:* Useful utility, but requires external customer acquisition and manual marketing.
3. **Approach C: Automation Workflow Templates Pack**
   * *Description:* Packaged n8n/Telegram bot templates sold on digital marketplaces.
   * *Trade-offs:* Low maintenance once uploaded, but slower time-to-first-dollar without existing traffic.

## Architecture
* `src/bounty_hunter/models.py`: Core domain data structures (`Bounty`, `TriageScore`, `SolutionDraft`, `FinancialRecord`).
* `src/bounty_hunter/scanners/`:
  * `base.py`: Scanner interface.
  * `github_scanner.py`: GitHub issue search with filters for bounty labels and reward parsing.
  * `algora_scanner.py`: Algora/Polar bounty parser.
  * `fixture_scanner.py`: Deterministic test fixtures for offline evaluation & testing.
* `src/bounty_hunter/triage.py`: NLP & heuristic scoring engine calculating Solvability Score, Token Cost Estimate, and ROI.
* `src/bounty_hunter/solver.py`: Code patch generator that drafts the solution diff, explains root cause, and formats the Pull Request body.
* `src/bounty_hunter/ledger.py`: SQLite-backed financial ledger tracking token expenses, bounties claimed, net profit, and $100 target progress.
* `src/bounty_hunter/cli.py`: Interactive command-line interface with subcommands (`scan`, `triage`, `solve`, `status`, `serve`).
* `src/bounty_hunter/server.py`: Lightweight FastAPI/Starlette web service hosting the interactive dashboard.
* `tests/`: Comprehensive test suite verifying all components with pytest.
