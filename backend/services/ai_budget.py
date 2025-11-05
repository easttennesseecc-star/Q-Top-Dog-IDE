"""
Compute-aware AI budgets: track and enforce request-level complexity budgets.

- Budget can model token limits, depth of tool calls, or time slice per tick.
- Expose counters and helpers to adapt algorithmic complexity dynamically.
"""
from __future__ import annotations
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional


@dataclass
class Budget:
    max_tokens: int = 4000
    max_tools: int = 3
    max_seconds: float = 2.0


class BudgetTracker:
    def __init__(self, budget: Budget):
        self.budget = budget
        self.tokens = 0
        self.tools = 0
        self._start = time.time()

    def add_tokens(self, n: int):
        self.tokens += int(n)

    def add_tool(self):
        self.tools += 1

    @property
    def seconds(self) -> float:
        return max(0.0, time.time() - self._start)

    def within_limits(self) -> bool:
        return (
            self.tokens <= self.budget.max_tokens
            and self.tools <= self.budget.max_tools
            and self.seconds <= self.budget.max_seconds
        )


@contextmanager
def compute_budget(budget: Optional[Budget] = None):
    bt = BudgetTracker(budget or Budget())
    try:
        yield bt
    finally:
        pass
