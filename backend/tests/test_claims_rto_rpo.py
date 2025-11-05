import os
from backend.services.claims_rto_rpo_sim import TestClock, ClaimsProcessorSim


def test_claims_rto_rpo_targets():
    # Targets can be configured via env; defaults keep test fast and strict
    rto_target = float(os.getenv("CLAIMS_RTO_TARGET_SECONDS", "2"))
    rpo_target = float(os.getenv("CLAIMS_RPO_TARGET_SECONDS", "120"))

    clock = TestClock(0.0)
    # Checkpoint every 60s to keep RPO low in this test;
    # Recovery takes 1s to keep RTO under 2s target.
    sim = ClaimsProcessorSim(clock, checkpoint_interval_seconds=60.0, recovery_duration_seconds=1.0)

    # Simulate steady processing for 15 minutes; checkpoint every 60s
    for _ in range(15 * 60):
        sim.process_claim()
        clock.advance(1.0)

    # Induce an outage of 5 seconds
    outage_start, outage_end = sim.simulate_outage(5.0)

    # Recover and compute RTO/RPO
    rto = sim.recover(outage_end)
    rpo = sim.compute_rpo(outage_start)

    assert rto <= rto_target, f"RTO {rto:.2f}s exceeds target {rto_target:.2f}s"
    assert rpo <= rpo_target, f"RPO {rpo:.2f}s exceeds target {rpo_target:.2f}s"
