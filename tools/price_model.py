from dataclasses import dataclass
from typing import Dict, Tuple

@dataclass
class Tier:
    name: str
    price_monthly: float
    storage_gb: float
    infra_cost: float
    support_cost: float
    bandwidth_cost: float
    regulated_uplift: float = 0.0

STRIPE_PCT = 0.029
STRIPE_FIXED = 0.30
RESERVE_RATE = 0.01  # refunds/churn reserve
STORAGE_COST_PER_GB = 0.03  # effective with overhead


def seat_cost(t: Tier) -> Tuple[float, Dict[str, float]]:
    stripe_fees = t.price_monthly * STRIPE_PCT + STRIPE_FIXED
    storage_cost = t.storage_gb * STORAGE_COST_PER_GB
    reserve = t.price_monthly * RESERVE_RATE
    total = stripe_fees + t.infra_cost + storage_cost + t.bandwidth_cost + t.support_cost + t.regulated_uplift + reserve
    breakdown = {
        "stripe_fees": round(stripe_fees, 2),
        "infra": round(t.infra_cost, 2),
        "storage": round(storage_cost, 2),
        "bandwidth": round(t.bandwidth_cost, 2),
        "support": round(t.support_cost + t.regulated_uplift, 2),
        "reserve": round(reserve, 2),
    }
    return total, breakdown


def margin(t: Tier) -> Tuple[float, float, Dict[str, float]]:
    cost, breakdown = seat_cost(t)
    revenue = t.price_monthly
    m = (revenue - cost) / revenue if revenue > 0 else 0.0
    return revenue, cost, breakdown | {"margin_pct": round(m * 100, 2)}


def default_tiers() -> Dict[str, Tier]:
    return {
        # Dev
        "dev_pro": Tier("Dev Pro", 29, storage_gb=5, infra_cost=1.5, support_cost=1.0, bandwidth_cost=0.2),
        "dev_pro_plus": Tier("Dev Pro Plus", 49, storage_gb=15, infra_cost=1.5, support_cost=2.0, bandwidth_cost=0.3),
        "dev_teams": Tier("Dev Teams", 39, storage_gb=10, infra_cost=2.0, support_cost=3.0, bandwidth_cost=0.3),
        "dev_enterprise": Tier("Dev Enterprise", 79, storage_gb=50, infra_cost=3.0, support_cost=8.0, bandwidth_cost=0.4),
        # Regulated — Med
        "med_pro": Tier("Med Pro", 89, storage_gb=10, infra_cost=2.5, support_cost=3.0, bandwidth_cost=0.45, regulated_uplift=0.0),
        "med_teams": Tier("Med Teams", 129, storage_gb=25, infra_cost=3.0, support_cost=7.0, bandwidth_cost=0.55, regulated_uplift=0.0),
        "med_enterprise": Tier("Med Enterprise", 199, storage_gb=75, infra_cost=4.0, support_cost=18.0, bandwidth_cost=0.7, regulated_uplift=0.0),
        # Regulated — Sci
        "sci_pro": Tier("Sci Pro", 69, storage_gb=8, infra_cost=2.0, support_cost=3.0, bandwidth_cost=0.35, regulated_uplift=0.0),
        "sci_teams": Tier("Sci Teams", 99, storage_gb=20, infra_cost=2.5, support_cost=6.0, bandwidth_cost=0.45, regulated_uplift=0.0),
        "sci_enterprise": Tier("Sci Enterprise", 149, storage_gb=60, infra_cost=3.5, support_cost=12.0, bandwidth_cost=0.6, regulated_uplift=0.0),
    }


def summarize():
    tiers = default_tiers()
    print("Tier, Revenue, Cost, Margin% | breakdown")
    for key, t in tiers.items():
        revenue, cost, info = margin(t)
        print(f"{t.name}, ${revenue:.2f}, ${cost:.2f}, {info['margin_pct']:.2f}% | {info}")


if __name__ == "__main__":
    summarize()
