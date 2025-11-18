import argparse
import json
import os
import sys
import urllib.request


def post_with_bot(token: str, channel: str, text: str, thread_ts: str | None = None) -> str:
    url = "https://slack.com/api/chat.postMessage"
    payload = {"channel": channel, "text": text}
    if thread_ts:
        payload["thread_ts"] = thread_ts
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": f"Bearer {token}",
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read().decode("utf-8", errors="ignore")
    try:
        obj = json.loads(body)
    except Exception:
        return ""
    return str(obj.get("ts", ""))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--bot-token", dest="token")
    p.add_argument("--channel", required=True)
    p.add_argument("--text", required=True)
    p.add_argument("--thread-ts")
    args = p.parse_args()

    if not args.token:
        return 0
    ts = post_with_bot(args.token, args.channel, args.text, args.thread_ts)
    if ts:
        sys.stdout.write(ts)
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
