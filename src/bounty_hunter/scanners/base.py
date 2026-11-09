import re
from abc import ABC, abstractmethod
from typing import Optional, List
from bounty_hunter.models import Bounty

REWARD_PATTERNS = [
    re.compile(r'\$\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?)', re.IGNORECASE),
    re.compile(r'([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?)\s*(?:usd|usdt|usdc)', re.IGNORECASE),
    re.compile(r'(?:bounty|reward):\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?)', re.IGNORECASE),
]

def parse_reward_amount(text: str) -> float:
    """Extract dollar reward amount from title, labels or body text."""
    if not text:
        return 0.0
    for pattern in REWARD_PATTERNS:
        match = pattern.search(text)
        if match:
            clean_str = match.group(1).replace(",", "")
            try:
                val = float(clean_str)
                if val > 0:
                    return val
            except ValueError:
                continue
    return 0.0

class BaseScanner(ABC):
    """Abstract interface for bounty scanners."""

    @abstractmethod
    def scan(self, language: Optional[str] = None, min_reward: float = 0.0) -> List[Bounty]:
        """Scan and return a list of active bounties matching filters."""
        pass
