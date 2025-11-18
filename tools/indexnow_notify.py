#!/usr/bin/env python3
"""Simple IndexNow notifier.

Call after successful production deployment to notify search engines of updated URLs.
Usage:
  python tools/indexnow_notify.py --host topdog-ide.com --urls https://topdog-ide.com/ https://topdog-ide.com/features

Generates a key if one not present and submits to the IndexNow endpoint.
"""
import argparse
import os
import hashlib
import time
import json
import textwrap
from pathlib import Path
import urllib.request

INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
KEY_FILE = Path("indexnow.key")

def ensure_key() -> str:
    if KEY_FILE.exists():
        return KEY_FILE.read_text().strip()
    # Generate deterministic-ish key
    seed = f"{time.time()}-{os.getenv('CANONICAL_HOST','topdog-ide.com')}"
    key = hashlib.sha256(seed.encode()).hexdigest()
    KEY_FILE.write_text(key)
    return key

def submit(host: str, urls: list[str], key: str):
    payload = {
        "host": host,
        "key": key,
        "keyLocation": f"https://{host}/{key}.txt",
        "urlList": urls,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(INDEXNOW_ENDPOINT, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            print("IndexNow response:", body)
    except Exception as e:
        print("IndexNow submission failed:", e)


def main():
    ap = argparse.ArgumentParser(description="Notify IndexNow of updated URLs")
    ap.add_argument("--host", required=True)
    ap.add_argument("--urls", nargs="+", required=True)
    args = ap.parse_args()
    key = ensure_key()
    submit(args.host, args.urls, key)
    # Optionally write key file for verification
    key_txt = Path(f"{key}.txt")
    if not key_txt.exists():
        key_txt.write_text(textwrap.dedent(f"""IndexNow key file\nKey: {key}\nHost: {args.host}\n"""))

if __name__ == "__main__":
    main()
