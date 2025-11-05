#!/usr/bin/env python3
"""
pythonrto: quick RTO/RPO simulation for claims processing.

Usage:
  python tools/pythonrto.py

Env vars:
  CLAIMS_RTO_TARGET_SECONDS (default 2)
  CLAIMS_RPO_TARGET_SECONDS (default 120)
  CHECKPOINT_INTERVAL_SECONDS (default 60)
  RECOVERY_DURATION_SECONDS (default 1)
  OUTAGE_DURATION_SECONDS (default 5)
  WARMUP_SECONDS (default 900)  # simulate steady processing before outage
"""
import os
from backend.services.claims_rto_rpo_sim import TestClock, ClaimsProcessorSim


def main() -> int:
    rto_target = float(os.getenv("CLAIMS_RTO_TARGET_SECONDS", "2"))
    rpo_target = float(os.getenv("CLAIMS_RPO_TARGET_SECONDS", "120"))
    checkpoint_interval = float(os.getenv("CHECKPOINT_INTERVAL_SECONDS", "60"))
    recovery_duration = float(os.getenv("RECOVERY_DURATION_SECONDS", "1"))
    outage_duration = float(os.getenv("OUTAGE_DURATION_SECONDS", "5"))
    warmup_seconds = float(os.getenv("WARMUP_SECONDS", "900"))

    clock = TestClock(0.0)
    sim = ClaimsProcessorSim(clock, checkpoint_interval, recovery_duration)

    # Warmup
    steps = int(warmup_seconds)
    for _ in range(steps):
        sim.process_claim()
        clock.advance(1.0)

    # Outage + recovery
    outage_start, outage_end = sim.simulate_outage(outage_duration)
    rto = sim.recover(outage_end)
    rpo = sim.compute_rpo(outage_start)

    print(f"RTO: {rto:.2f}s (target <= {rto_target:.2f}s)")
    print(f"RPO: {rpo:.2f}s (target <= {rpo_target:.2f}s)")

    ok = (rto <= rto_target) and (rpo <= rpo_target)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
