from dataclasses import dataclass
from typing import Optional


@dataclass
class SimClock:
    # Prevent pytest from attempting to collect this as a test class
    __test__ = False
    now_sec: float = 0.0

    def now(self) -> float:
        return self.now_sec

    def advance(self, seconds: float) -> None:
        self.now_sec += seconds


class ClaimsProcessorSim:
    """
    Simple simulation of a claims processor to reason about RTO/RPO.

    - last_checkpoint_time: last time state was durably persisted
    - checkpoint_interval_seconds: how often a durable checkpoint occurs
    - recovery_duration_seconds: simulated time to restore and resume
    """

    def __init__(
        self,
    clock: SimClock,
        checkpoint_interval_seconds: float = 300.0,
        recovery_duration_seconds: float = 1.0,
    ) -> None:
        self.clock = clock
        self.checkpoint_interval_seconds = checkpoint_interval_seconds
        self.recovery_duration_seconds = recovery_duration_seconds
        self.last_checkpoint_time: float = 0.0
        self.last_processed_time: float = 0.0

    def process_claim(self) -> None:
        """Process one claim at current time and checkpoint if due."""
        t = self.clock.now()
        self.last_processed_time = t
        if (t - self.last_checkpoint_time) >= self.checkpoint_interval_seconds:
            self.last_checkpoint_time = t

    def simulate_outage(self, outage_duration_seconds: float) -> tuple[float, float]:
        """Advance clock to represent an outage; returns (outage_start, outage_end)."""
        outage_start = self.clock.now()
        self.clock.advance(outage_duration_seconds)
        outage_end = self.clock.now()
        return outage_start, outage_end

    def recover(self, outage_end: float) -> float:
        """Simulate recovery and return RTO (seconds to resume)."""
        # Recovery consumes recovery_duration_seconds
        self.clock.advance(self.recovery_duration_seconds)
        recovery_complete = self.clock.now()
        rto = max(0.0, recovery_complete - outage_end)
        return rto

    def compute_rpo(self, outage_start: float) -> float:
        """Compute RPO as time between outage start and last durable checkpoint."""
        return max(0.0, outage_start - self.last_checkpoint_time)

# Backward-compatibility aliases for tests
TestClock = SimClock
