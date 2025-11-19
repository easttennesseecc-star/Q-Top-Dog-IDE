"""Admin password reset utility.

Usage (PowerShell):
  python scripts/reset_password_user.py --email paul@quellum --new "TopDogStrong!2025" --admin-token $env:ADMIN_TOKEN

If --admin-token omitted, will use ADMIN_TOKEN from environment.
Exits with code 0 on success, 1 on failure.
"""

import argparse
import os
import sys
from pathlib import Path
from json import dumps

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.auth import admin_reset_password_user  # type: ignore  # noqa: E402


def parse_args():
    p = argparse.ArgumentParser(description="Admin reset of password user")
    p.add_argument("--email", required=True, help="Email/user id")
    p.add_argument("--new", required=True, help="New password value")
    p.add_argument("--admin-token", required=False, help="Admin token (defaults to env ADMIN_TOKEN)")
    return p.parse_args()


def main():
    args = parse_args()
    token = args.admin_token or os.getenv("ADMIN_TOKEN") or ""
    ok = admin_reset_password_user(args.email, args.new, token)
    result = {"status": "ok" if ok else "error", "email": args.email}
    print(dumps(result))
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
