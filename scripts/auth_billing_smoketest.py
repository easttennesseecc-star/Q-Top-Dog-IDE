"""Smoketest for password auth + health + billing subscription.

Runs directly against the FastAPI app using TestClient so we don't need
to keep a uvicorn server process alive in this environment.

Steps:
1. Set env vars for temporary password provisioning.
2. Attempt login; if fails, register then login.
3. Change password to a stronger temporary value.
4. Hit /health.
5. Hit /api/billing/subscription with X-User-ID header.
Print JSON results for each step.
"""

import os
import sys
from pathlib import Path
from pprint import pprint

os.environ.setdefault("TEMP_PASSWORD_EMAIL", "paul@quellum")
os.environ.setdefault("TEMP_PASSWORD_PLAIN", "jesus")
os.environ.setdefault("ADMIN_TOKEN", "TEMP_ADMIN_TOKEN_123")
os.environ.setdefault("LOG_TO_STDOUT_ONLY", "true")

from fastapi.testclient import TestClient

# Ensure project root is on sys.path for `backend` package import
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.main import app  # triggers import-time provisioning  # noqa: E402

def main():
    results = {}
    with TestClient(app) as client:
        email = os.environ["TEMP_PASSWORD_EMAIL"]
        weak_pass = os.environ["TEMP_PASSWORD_PLAIN"]
        strong_pass = "StrongerPass123!$"  # demo only; choose a better one later

        # 1. Login attempt (may fail if not yet provisioned)
        r = client.post("/auth/password/login", json={"email": email, "password": weak_pass})
        if r.status_code != 200:
            # 2. Register then retry login
            reg = client.post(
                "/auth/password/register",
                json={"email": email, "password": weak_pass, "admin_token": os.environ.get("ADMIN_TOKEN")},
            )
            results["register"] = {"status_code": reg.status_code, "body": reg.json() if reg.content else None}
            r = client.post("/auth/password/login", json={"email": email, "password": weak_pass})
        results["login"] = {"status_code": r.status_code, "body": r.json() if r.content else None}
        # session id not needed for current smoketest

        # 3. Change password
        ch = client.post(
            "/auth/password/change",
            json={"email": email, "old_password": weak_pass, "new_password": strong_pass},
        )
        results["change_password"] = {"status_code": ch.status_code, "body": ch.json() if ch.content else None}

        # 4. Health check
        h = client.get("/health")
        results["health"] = {"status_code": h.status_code, "body": h.json() if h.content else None}

        # 5. Billing subscription (X-User-ID header consumed by get_current_user)
        b = client.get("/api/billing/subscription", headers={"X-User-ID": email})
        try:
            b_json = b.json()
        except Exception:
            b_json = b.text
        results["billing_subscription"] = {"status_code": b.status_code, "body": b_json}

    print("\n=== Smoketest Results ===")
    for k, v in results.items():
        print(f"\n-- {k} --")
        pprint(v)
    # Provide quick summary line
    print("\nSummary:")
    print(
        f"login={results['login']['status_code']} change={results['change_password']['status_code']} "
        f"health={results['health']['status_code']} billing={results['billing_subscription']['status_code']}"
    )


if __name__ == "__main__":
    main()
