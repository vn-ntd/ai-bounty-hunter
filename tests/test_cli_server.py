import pytest
from starlette.testclient import TestClient
from bounty_hunter.ledger import FinancialLedger
from bounty_hunter.server import create_app
from bounty_hunter.cli import run_cli

@pytest.fixture
def app_client(tmp_path):
    db_path = str(tmp_path / "test_api.db")
    ledger = FinancialLedger(db_path=db_path)
    app = create_app(ledger=ledger)
    client = TestClient(app)
    return client, ledger

def test_api_summary_and_empty_bounties(app_client):
    client, ledger = app_client
    resp = client.get("/api/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["target_usd"] == 100.0
    assert data["net_profit_usd"] == 0.0

    bounties_resp = client.get("/api/bounties")
    assert bounties_resp.status_code == 200
    assert isinstance(bounties_resp.json(), list)

def test_api_scan_and_solve(app_client):
    client, ledger = app_client
    # Trigger scan
    scan_resp = client.post("/api/scan?source=fixture")
    assert scan_resp.status_code == 200
    items = scan_resp.json()
    assert len(items) > 0
    bounty_id = items[0]["id"]

    # Solve the bounty
    solve_resp = client.post(f"/api/solve/{bounty_id}")
    assert solve_resp.status_code == 200
    solution = solve_resp.json()
    assert solution["bounty_id"] == bounty_id
    assert "diff --git" in solution["patch_diff"]

    # Check payout
    pay_resp = client.post(f"/api/payout/{bounty_id}?amount=45.0")
    assert pay_resp.status_code == 200
    summary = client.get("/api/summary").json()
    assert summary["total_earned_usd"] == 45.0

def test_cli_execution_commands(tmp_path, capsys):
    db_path = str(tmp_path / "cli_test.db")
    # Test scan command
    exit_code = run_cli(["scan", "--source", "fixture", "--db", db_path])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Discovered" in captured.out or "bounties" in captured.out.lower()

    # Test status command
    exit_code_status = run_cli(["status", "--db", db_path])
    assert exit_code_status == 0
    captured_status = capsys.readouterr()
    assert "Financial Status" in captured_status.out or "Target" in captured_status.out
