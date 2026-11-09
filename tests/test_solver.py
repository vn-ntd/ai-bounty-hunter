import pytest
from bounty_hunter.models import Bounty, BountyStatus, SolutionDraft
from bounty_hunter.solver import SolutionGenerator

def test_solver_generates_python_patch_and_pr():
    bounty = Bounty(
        id="gh-2041",
        title="Add exponential backoff retry to webhook dispatcher ($45)",
        url="https://github.com/fast-event-hub/dispatcher/issues/2041",
        source="github",
        repository="fast-event-hub/dispatcher",
        reward_usd=45.0,
        description="When webhooks fail with 5xx or timeout, we drop them. Need a 3-retry exponential backoff.",
        language="Python",
    )
    generator = SolutionGenerator()
    solution = generator.solve(bounty)

    assert isinstance(solution, SolutionDraft)
    assert solution.bounty_id == "gh-2041"
    assert "retry" in solution.root_cause.lower() or "backoff" in solution.root_cause.lower()
    assert "diff --git" in solution.patch_diff
    assert "def test_" in solution.test_code
    assert solution.pr_title.startswith("fix") or solution.pr_title.startswith("feat")
    assert "## Summary" in solution.pr_body
    assert "## Verification" in solution.pr_body
    assert bounty.url in solution.pr_body or "2041" in solution.pr_body

def test_solver_generates_security_fix():
    bounty = Bounty(
        id="polar-1082",
        title="Sanitize SVG uploads to prevent XSS vulnerability ($120)",
        url="https://github.com/open-media-store/core/issues/1082",
        source="polar",
        repository="open-media-store/core",
        reward_usd=120.0,
        description="Users can upload SVGs containing malicious <script> tags. Strip script elements.",
        language="Python",
    )
    generator = SolutionGenerator()
    solution = generator.solve(bounty)

    assert "xss" in solution.root_cause.lower() or "script" in solution.root_cause.lower()
    assert "sanitize" in solution.patch_diff.lower() or "strip" in solution.patch_diff.lower()
    assert "assert" in solution.test_code

def test_solver_generates_typescript_types():
    bounty = Bounty(
        id="gh-7840",
        title="Add TypeScript types and validation for payment webhook payloads ($70)",
        url="https://github.com/merchant-dock/sdk-js/issues/7840",
        source="github",
        repository="merchant-dock/sdk-js",
        reward_usd=70.0,
        description="Currently webhook payloads are typed as any. Define Zod schemas and TypeScript interfaces.",
        language="TypeScript",
    )
    generator = SolutionGenerator()
    solution = generator.solve(bounty)

    assert "type" in solution.root_cause.lower() or "interface" in solution.root_cause.lower()
    assert "interface" in solution.patch_diff or "type" in solution.patch_diff or "export" in solution.patch_diff
