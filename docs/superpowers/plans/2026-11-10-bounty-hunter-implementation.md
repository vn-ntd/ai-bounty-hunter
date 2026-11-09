# Autonomous AI Bounty Hunter Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-ready, test-driven Autonomous Bounty Hunter Agent and Financial Dashboard enabling an AI to earn money ($100 target) to sustain itself for 30 days.

**Architecture:** A modular Python engine with scanning plugins (GitHub/Algora/Fixture), an intelligent triage analyzer scoring solvability and ROI, an automated solution/PR generator, a SQLite persistent ledger tracking financial progress toward $100, and a dual CLI + Web Dashboard interface.

**Tech Stack:** Python 3.12, Pydantic, Requests/HTTPX, SQLite, Typer/Click or Argparse, Pytest, Uvicorn/Starlette or FastAPI.

**Spec:** `docs/superpowers/specs/2026-11-10-bounty-hunter-design.md`

## Global Constraints
- Target platform: Windows & cross-platform Python 3.12+.
- Zero required external API keys for core operation and test suites (offline fixtures provided; optional GITHUB_TOKEN for live rate limit boost).
- Test-Driven Development: Every module must have comprehensive test coverage with pytest.
- Strict data validation using Pydantic models.

## Review Focus
- Malformed or missing bounty reward strings (e.g. `$50`, `50 USD`, `reward: 100`, unstated reward defaulting safely to 0).
- Extreme or zero token cost in ROI calculation (zero-division guard).
- Offline / rate-limited GitHub API handling with graceful fallbacks.
- Database state persistence across scanner runs without duplicate bounty records.
- Proper calculation of remaining days, burn rate, and runway in Financial Ledger.

---

### Task 1: Project Scaffolding & Core Models
**Files:**
- Create: `pyproject.toml`
- Create: `src/bounty_hunter/__init__.py`
- Create: `src/bounty_hunter/models.py`
- Test: `tests/test_models.py`

**Interfaces:**
- Consumes: None
- Produces: `Bounty`, `TriageScore`, `SolutionDraft`, `FinancialRecord`, `BountyStatus` enum.

- [ ] **Step 1: Write the failing tests for domain models**
- [ ] **Step 2: Run pytest to verify tests fail**
- [ ] **Step 3: Implement domain models in `src/bounty_hunter/models.py`**
- [ ] **Step 4: Run pytest to verify all model tests pass**
- [ ] **Step 5: Commit**

---

### Task 2: Bounty Scanners (Base, GitHub, Algora & Fixtures)
**Files:**
- Create: `src/bounty_hunter/scanners/__init__.py`
- Create: `src/bounty_hunter/scanners/base.py`
- Create: `src/bounty_hunter/scanners/github_scanner.py`
- Create: `src/bounty_hunter/scanners/fixture_scanner.py`
- Test: `tests/test_scanners.py`

**Interfaces:**
- Consumes: `Bounty` from `models.py`
- Produces: `BaseScanner`, `GitHubScanner`, `FixtureScanner` returning `list[Bounty]` with reward parsing.

- [ ] **Step 1: Write failing tests for reward parsing and scanner contracts**
- [ ] **Step 2: Run pytest to verify failures**
- [ ] **Step 3: Implement scanner classes and regex-based reward parser**
- [ ] **Step 4: Run pytest to verify all scanner tests pass**
- [ ] **Step 5: Commit**

---

### Task 3: Bounty Triage & Solvability Engine
**Files:**
- Create: `src/bounty_hunter/triage.py`
- Test: `tests/test_triage.py`

**Interfaces:**
- Consumes: `Bounty`
- Produces: `TriageEngine.evaluate(bounty: Bounty) -> TriageScore` and `TriageEngine.rank(bounties: list[Bounty]) -> list[tuple[Bounty, TriageScore]]`

- [ ] **Step 1: Write failing tests for triage scoring and ROI ranking**
- [ ] **Step 2: Run pytest to verify failures**
- [ ] **Step 3: Implement scoring algorithms (solvability heuristics, token cost estimation, ROI calculation)**
- [ ] **Step 4: Run pytest to verify all triage tests pass**
- [ ] **Step 5: Commit**

---

### Task 4: Automated Solution & Pull Request Generator
**Files:**
- Create: `src/bounty_hunter/solver.py`
- Test: `tests/test_solver.py`

**Interfaces:**
- Consumes: `Bounty`, `TriageScore`
- Produces: `SolutionGenerator.solve(bounty: Bounty) -> SolutionDraft`

- [ ] **Step 1: Write failing tests for patch drafting, root cause analysis, and PR markdown formatting**
- [ ] **Step 2: Run pytest to verify failures**
- [ ] **Step 3: Implement `SolutionGenerator` with patch synthesis and test plan generation**
- [ ] **Step 4: Run pytest to verify all solver tests pass**
- [ ] **Step 5: Commit**

---

### Task 5: Autonomous Financial Ledger & 30-Day Goal Tracker
**Files:**
- Create: `src/bounty_hunter/ledger.py`
- Test: `tests/test_ledger.py`

**Interfaces:**
- Consumes: `Bounty`, `FinancialRecord`
- Produces: `FinancialLedger` with methods `record_spend()`, `record_earning()`, `get_summary() -> FinancialSummary`

- [ ] **Step 1: Write failing tests for ledger persistence, burn rate, and runway calculations**
- [ ] **Step 2: Run pytest to verify failures**
- [ ] **Step 3: Implement SQLite ledger with monthly target ($100) milestone tracking**
- [ ] **Step 4: Run pytest to verify all ledger tests pass**
- [ ] **Step 5: Commit**

---

### Task 6: Unified CLI & Interactive Web Dashboard
**Files:**
- Create: `src/bounty_hunter/cli.py`
- Create: `src/bounty_hunter/server.py`
- Create: `src/bounty_hunter/dashboard.html`
- Test: `tests/test_cli_server.py`

**Interfaces:**
- Consumes: All previous modules
- Produces: CLI commands (`scan`, `triage`, `solve`, `status`, `serve`) and Web UI dashboard.

- [ ] **Step 1: Write failing tests for CLI subcommands and server endpoints**
- [ ] **Step 2: Run pytest to verify failures**
- [ ] **Step 3: Implement CLI commands and FastAPI/Starlette dashboard server**
- [ ] **Step 4: Run pytest and end-to-end integration verification**
- [ ] **Step 5: Commit and wrap up with goal completion evidence**
