import re
from typing import List, Tuple
from bounty_hunter.models import Bounty, TriageScore

EASY_PATTERNS = [
    r'\btypo\b', r'\bdocs?\b', r'\breadme\b', r'\bdocstring\b', r'\blint\b',
    r'\bformat\b', r'\bcomment\b', r'\bminor\b', r'\bsmall\b', r'\bunit\s*test\b'
]
MEDIUM_PATTERNS = [
    r'\bfix\b', r'\bbug\b', r'\bretry\b', r'\bbackoff\b', r'\btimeout\b',
    r'\bsanitize\b', r'\bvalidation\b', r'\bschema\b', r'\btypes?\b', r'\bnull\b',
    r'\boffset\b', r'\bindexerror\b', r'\bexception\b'
]
HARD_PATTERNS = [
    r'\brewrite\b', r'\barchitecture\b', r'\brethink\b', r'\boverhaul\b',
    r'\bentire\b', r'\bkernel\b', r'\bdistributed\b', r'\bconsensus\b', r'\brfc\b'
]

class TriageEngine:
    """AI evaluation engine to rank and triage bounties by solvability and ROI."""

    def evaluate(self, bounty: Bounty) -> TriageScore:
        text = f"{bounty.title} {bounty.description}".lower()
        
        # Check hard indicators first
        hard_hits = sum(1 for p in HARD_PATTERNS if re.search(p, text))
        easy_hits = sum(1 for p in EASY_PATTERNS if re.search(p, text))
        medium_hits = sum(1 for p in MEDIUM_PATTERNS if re.search(p, text))

        if hard_hits > 0:
            difficulty = "HARD"
            estimated_cost = 0.50
            base_score = 45 - (hard_hits * 10)
        elif easy_hits > 0 and hard_hits == 0:
            difficulty = "EASY"
            estimated_cost = 0.03
            base_score = 85 + min(easy_hits * 3, 10)
        else:
            difficulty = "MEDIUM"
            estimated_cost = 0.10
            base_score = 70 + min(medium_hits * 3, 15)

        # Penalize if description is very brief or missing
        if len(bounty.description.strip()) < 30:
            base_score -= 20
        elif len(bounty.description.strip()) > 100:
            base_score += 5

        solvability = max(5, min(100, base_score))

        # ROI Calculation: Guard against division by zero
        if bounty.reward_usd <= 0:
            roi = 0.0
            recommended = "SKIP"
            reasoning = "No monetary reward attached or zero bounty value."
        else:
            roi = round((bounty.reward_usd - estimated_cost) / max(estimated_cost, 0.001), 2)
            if solvability >= 70:
                recommended = "PROCEED"
                reasoning = f"High solvability ({solvability}/100) and attractive ROI ({roi}x) in {bounty.language}."
            elif solvability >= 50:
                recommended = "REVIEW_MANUALLY"
                reasoning = f"Moderate solvability ({solvability}/100). Requires human check before committing compute."
            else:
                recommended = "SKIP"
                reasoning = f"Low solvability ({solvability}/100) or high architectural complexity ({difficulty})."

        return TriageScore(
            bounty_id=bounty.id,
            solvability_score=solvability,
            estimated_token_cost=estimated_cost,
            difficulty=difficulty,
            roi=roi,
            reasoning=reasoning,
            recommended_action=recommended
        )

    def rank(self, bounties: List[Bounty]) -> List[Tuple[Bounty, TriageScore]]:
        """Rank bounties by solvability and ROI descending."""
        scored = [(b, self.evaluate(b)) for b in bounties]

        def sort_key(item: Tuple[Bounty, TriageScore]):
            bounty, score = item
            if bounty.reward_usd <= 0:
                return (0, 0, 0.0)
            # Prioritize PROCEED > REVIEW_MANUALLY > SKIP
            status_priority = {"PROCEED": 3, "REVIEW_MANUALLY": 2, "SKIP": 1}.get(score.recommended_action, 0)
            return (status_priority, score.solvability_score, score.roi)

        scored.sort(key=sort_key, reverse=True)
        return scored
