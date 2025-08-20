from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Tuple
import re
import math

# lightweight string similarity
def _norm(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[_\-\s]+", " ", s)
    return s

def token_jaccard(a: str, b: str) -> float:
    A = set(_norm(a).split())
    B = set(_norm(b).split())
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)

def substr_score(a: str, b: str) -> float:
    aN, bN = _norm(a), _norm(b)
    if aN in bN or bN in aN:
        return 1.0
    return 0.0

def prefix_hints(name: str) -> List[str]:
    """Heuristic hints from block name conventions."""
    n = name.upper()
    hints = []
    if "SUSPEND" in n: hints.append("Suspended Light")
    if "CONCEALED" in n: hints.append("Concealed Light")
    if "DOWN" in n or n == "LED": hints.append("down light")
    if n.startswith("FAN") or n.endswith("_FAN"): hints.append("Fan Point")
    if "SPOT" in n or n in {"SP"}: hints.append("Button Spot Light")
    if n.startswith("SW") or "SWITCH" in n: hints.append("Switch Board")
    if "PENDANT" in n or "PENDENT" in n: hints.append("pendant light")
    return hints

@dataclass
class LinkResult:
    legend_item: str
    best_block: str | None
    score: float
    candidates: List[Tuple[str, float]]

def link_legend_to_blocks(legend_items: List[str], block_counts: Dict[str, int]) -> List[LinkResult]:
    names = list(block_counts.keys())

    results: List[LinkResult] = []
    for item in legend_items:
        # try rule-based hints first
        scored: List[Tuple[str, float]] = []
        for n in names:
            s1 = token_jaccard(item, n)
            s2 = substr_score(item, n)
            s3 = 0.15 if item in prefix_hints(n) else 0.0
            # small count prior: if many occurrences, likely a true symbol
            prior = min(0.2, math.log10(max(block_counts[n],1)+1) * 0.05)
            score = max(s1, s2) + s3 + prior
            if score > 0:
                scored.append((n, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[0] if scored else (None, 0.0)

        # confidence guardrail: require a margin & a minimum
        best, best_score = top
        if best is not None:
            next_best = scored[1][1] if len(scored) > 1 else 0.0
            margin = best_score - next_best
            if best_score < 0.55 or margin < 0.08:
                best = None  # mark as unresolved; will be reviewed manually
        results.append(LinkResult(item, best, best_score if best else 0.0, scored[:5]))
    return results
