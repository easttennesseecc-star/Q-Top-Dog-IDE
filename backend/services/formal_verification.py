"""
Formal Verification Service

Treats reasoning as a typed program expressed as structured predicates.
Provides minimal, deterministic checks for simple inference rules
(e.g., modus ponens, transitivity). This is deliberately conservative
and dependency-light; for stronger guarantees, integrate a real prover
(e.g., Z3, Lean 4) behind the same interface.

Data model (JSON-friendly):
{
  "assumptions": ["A", "A->B"],
  "goals": ["B"],
  "steps": [
    {"rule": "assume", "out": "A"},
    {"rule": "assume", "out": "A->B"},
    {"rule": "modus_ponens", "in": ["A", "A->B"], "out": "B"}
  ]
}

Predicates are strings in a tiny propositional logic subset using "->"
for implication and "/\" for conjunction (optional). No quantifiers.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Set, Tuple


@dataclass
class VerificationResult:
    ok: bool
    proved: List[str]
    missing_goals: List[str]
    steps_checked: int
    errors: List[str]


class FormalVerificationService:
    def __init__(self) -> None:
        pass

    def verify(self, trace: Dict[str, Any]) -> VerificationResult:
        assumptions: List[str] = list(map(self._norm, trace.get("assumptions", [])))
        goals: List[str] = list(map(self._norm, trace.get("goals", [])))
        steps: List[Dict[str, Any]] = trace.get("steps", [])

        errors: List[str] = []
        proved: Set[str] = set()
        known: Set[str] = set(assumptions)
        steps_checked = 0

        # Assumptions are trivially proved
        for a in assumptions:
            proved.add(a)

        for s in steps:
            try:
                rule = (s.get("rule") or "").strip().lower()
                if rule == "assume":
                    out = self._norm(s.get("out"))
                    if out:
                        known.add(out)
                        proved.add(out)
                elif rule == "modus_ponens":
                    ins = [self._norm(x) for x in (s.get("in") or [])]
                    out = self._norm(s.get("out"))
                    if len(ins) != 2 or not out:
                        errors.append("invalid modus_ponens step")
                    else:
                        a, imp = ins
                        if a in known and self._is_implication_of(imp, a, out):
                            known.add(out)
                            proved.add(out)
                        else:
                            errors.append("modus_ponens premises not satisfied")
                elif rule == "transitivity":
                    ins = [self._norm(x) for x in (s.get("in") or [])]
                    out = self._norm(s.get("out"))
                    if len(ins) != 2 or not out:
                        errors.append("invalid transitivity step")
                    else:
                        imp1, imp2 = ins
                        # If imp1 is X->Y and imp2 is Y->Z, then out should be X->Z
                        x_y = self._split_implication(imp1)
                        y_z = self._split_implication(imp2)
                        out_imp = self._split_implication(out)
                        if x_y and y_z and out_imp and x_y[1] == y_z[0] and out_imp == (x_y[0], y_z[1]):
                            known.add(out)
                            proved.add(out)
                        else:
                            errors.append("transitivity premises not satisfied")
                else:
                    errors.append(f"unknown rule: {rule}")
                steps_checked += 1
            except Exception as e:
                errors.append(f"step error: {e}")

        missing_goals = [g for g in goals if g not in proved]
        ok = len(missing_goals) == 0 and all(g in known for g in goals)
        return VerificationResult(
            ok=ok,
            proved=sorted(proved),
            missing_goals=missing_goals,
            steps_checked=steps_checked,
            errors=errors,
        )

    def _norm(self, s: Any) -> str:
        if not isinstance(s, str):
            return ""
        return "".join(s.split()).lower()

    def _split_implication(self, s: str) -> Tuple[str, str] | None:
        if "->" not in s:
            return None
        a, b = s.split("->", 1)
        return a, b

    def _is_implication_of(self, imp: str, premise: str, conclusion: str) -> bool:
        parts = self._split_implication(imp)
        if not parts:
            return False
        a, b = parts
        return a == premise and b == conclusion
