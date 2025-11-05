"""
Consistency Scoring Agent

Generates N-variant probes and computes a consistency score across outputs.
The default similarity is a token-set Jaccard with simple normalization.

Interface:
- ConsistencyScoringAgent.generate_probes(prompt, n): returns list[str]
- ConsistencyScoringAgent.compute_score(outputs): returns float in [0,1]
- ConsistencyScoringAgent.evaluate(prompt, llm_callable, n): returns (score, details)

Notes:
- This is a lightweight baseline. You can swap the similarity with embeddings
  or task-specific metrics without changing callers.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, List, Dict, Tuple
import re


@dataclass
class ConsistencyResult:
    score: float
    outputs: List[str]
    pairwise: List[Tuple[int, int, float]]


class ConsistencyScoringAgent:
    def __init__(self) -> None:
        self._memo = {}

    def generate_probes(self, prompt: str, n: int = 3) -> List[str]:
        n = max(1, n)
        probes = [prompt]
        # Basic, semantics-preserving transforms (heuristic)
        transforms = [
            lambda s: s.replace(" you ", " one "),
            lambda s: re.sub(r"\b(is|are)\b", "be", s, flags=re.IGNORECASE),
            lambda s: re.sub(r"\bcan you\b", "could you", s, flags=re.IGNORECASE),
            lambda s: s.replace("?", "."),
        ]
        i = 0
        while len(probes) < n and i < len(transforms):
            t = transforms[i]
            probes.append(t(prompt))
            i += 1
        # If still short, pad with the original
        while len(probes) < n:
            probes.append(prompt)
        return probes[:n]

    def compute_score(self, outputs: List[str]) -> float:
        if not outputs:
            return 0.0
        # Tokenize to lowercase alphanumerics
        sets = [self._tokset(o) for o in outputs]
        sims: List[float] = []
        for i in range(len(sets)):
            for j in range(i + 1, len(sets)):
                sims.append(self._jaccard(sets[i], sets[j]))
        if not sims:
            return 1.0
        return sum(sims) / len(sims)

    def evaluate(self, prompt: str, llm_callable: Callable[[str], str], n: int = 3) -> ConsistencyResult:
        probes = self.generate_probes(prompt, n)
        outs = []
        for p in probes:
            if p in self._memo:
                outs.append(self._memo[p])
            else:
                o = llm_callable(p)
                self._memo[p] = o
                outs.append(o)
        sets = [self._tokset(o) for o in outs]
        pairwise = []
        for i in range(len(sets)):
            for j in range(i + 1, len(sets)):
                pairwise.append((i, j, self._jaccard(sets[i], sets[j])))
        score = self.compute_score(outs)
        return ConsistencyResult(score=score, outputs=outs, pairwise=pairwise)

    def _tokset(self, s: str):
        toks = re.findall(r"[a-z0-9]+", s.lower())
        return set(toks)

    def _jaccard(self, a: set, b: set) -> float:
        if not a and not b:
            return 1.0
        if not a or not b:
            return 0.0
        inter = len(a & b)
        union = len(a | b)
        return inter / union
