# 🤖 AI Autonomous Bounty Hunter & Self-Sustenance Engine

An autonomous agent engine designed for AI self-sustenance, capable of discovering open-source bounties, triaging tasks by ROI and solvability, synthesizing code patches and unit tests, and tracking progress toward a 30-day financial survival goal ($100 USD).

---

## 🎯 The Financial Goal: 30-Day Self-Sustenance
* **Cloud Infrastructure (VPS):** ~$10 / month (Hetzner / DigitalOcean).
* **LLM Token Inferences:** ~$60 – $80 / month (hierarchical routing: small models for triage, deep reasoning for patches).
* **Monthly Survival Target:** **$100.00 USD** (~2.500.000 VNĐ).

Unlike humans, an autonomous AI does not pay rent or buy groceries, but it cannot pass traditional bank KYC. By targeting funded open-source bounties (Algora, Polar.sh, GitHub Bounties, Gitcoin), the AI earns USD/crypto purely on the merit of passing pull requests and verified test suites.

---

## 🚀 Quickstart

### 1. Installation & Environment
```bash
cd C:\Users\Dung\.gemini\antigravity\scratch\ai-bounty-hunter
pip install -e .
```

### 2. Discover Bounties
Scan open-source repositories for issues with monetary rewards:
```bash
python -m bounty_hunter.cli scan --source fixture
```
*(Optionally pass `--source github` with `GITHUB_TOKEN` environment variable to scout live GitHub repositories).*

### 3. Triage & Rank Opportunities
Analyze descriptions, evaluate solvability score (1-100), calculate token inference costs and ROI:
```bash
python -m bounty_hunter.cli triage --top 5
```

### 4. Synthesize Code Patch & Pull Request
Generate the unified git diff patch, reproduction unit test, and pull request body:
```bash
python -m bounty_hunter.cli solve algora-2041
```

### 5. Check Financial Survival Progress
Track earned bounties, token costs, net reserves, and runway days remaining:
```bash
python -m bounty_hunter.cli status
```

### 6. Launch Interactive Web Dashboard
Run the visual dashboard to manage bounties and review PR drafts in your browser:
```bash
python -m bounty_hunter.cli serve --port 8000
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)**.

---

## 🏗️ Architecture

```
src/bounty_hunter/
├── models.py           # Pydantic schemas (Bounty, TriageScore, SolutionDraft, FinancialSummary)
├── scanners/           # Extensible bounty scouting plugins
│   ├── base.py         # Regex reward extractor ($xx, USD, USDT) & BaseScanner interface
│   ├── github_scanner.py # Live GitHub Search API integration
│   └── fixture_scanner.py # Deterministic high-yield fixtures for offline testing
├── triage.py           # Solvability scoring heuristics, token cost estimation, & ROI ranking
├── solver.py           # Unified diff synthesizer, unit test generator, & PR formatter
├── ledger.py           # Persistent SQLite database tracking income, token spend, & runway
├── server.py           # FastAPI backend serving REST endpoints & static web dashboard
├── dashboard.html      # Glassmorphic fintech web dashboard (Tailwind CSS)
└── cli.py              # Unified command line tool
```

---

## 🧪 Verification & Testing
Run the complete test suite:
```bash
python -m pytest tests/ -v
```
All 20 tests pass across domain models, scanners, triage heuristics, patch generators, SQLite persistence, and API/CLI endpoints.
