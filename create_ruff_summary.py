import json
import os
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple
import urllib.request


GLOSSARY = {
    "E": "pycodestyle errors (PEP8)",
    "W": "pycodestyle warnings",
    "F": "pyflakes (possible bugs: undefined names, unused imports)",
    "I": "isort (import sorting)",
    "B": "flake8-bugbear (common pitfalls, correctness)",
    "UP": "pyupgrade (modernize to newer Python syntax)",
    "SIM": "flake8-simplify (simplify constructs)",
    "C4": "flake8-comprehensions (comprehension best practices)",
    "RUF": "Ruff-specific rules",
}


def summarize(path: Path) -> Dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    c: Counter[str] = Counter()
    for item in data:
        code = item.get("code") or item.get("rule")
        if code:
            c[code] += 1
    return {"total": sum(c.values()), "by_rule": dict(sorted(c.items()))}


def top_n(by_rule: Dict[str, int], n: int = 10) -> List[Tuple[str, int]]:
    return sorted(by_rule.items(), key=lambda kv: kv[1], reverse=True)[:n]


def write_markdown(summary: Dict) -> None:
    enforced = summary.get("enforced", {})
    expanded = summary.get("expanded", {})
    lines: List[str] = []
    lines.append("# Ruff Report\n")
    lines.append("## Totals\n")
    lines.append(f"- Enforced total: {enforced.get('total', 0)}")
    lines.append(f"- Expanded total (B, UP, SIM, C4, RUF): {expanded.get('total', 0)}\n")
    lines.append("## Top 10 Rules (Enforced)\n")
    for code, count in top_n(enforced.get("by_rule", {}), 10):
        family = ''.join([c for c in code if c.isalpha()])
        hint = GLOSSARY.get(family, "")
        lines.append(f"- {code}: {count} {f'({hint})' if hint else ''}")
    lines.append("")
    lines.append("## Top 10 Rules (Expanded)\n")
    for code, count in top_n(expanded.get("by_rule", {}), 10):
        family = ''.join([c for c in code if c.isalpha()])
        hint = GLOSSARY.get(family, "")
        lines.append(f"- {code}: {count} {f'({hint})' if hint else ''}")
    lines.append("")
    lines.append("## Glossary\n")
    for fam, desc in GLOSSARY.items():
        lines.append(f"- {fam}: {desc}")
    Path("ruff-report.md").write_text("\n".join(lines), encoding="utf-8")


def post_slack_webhook(summary: Dict) -> None:
    url = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    event = os.environ.get("GITHUB_EVENT_NAME", "")
    if not url or event != "pull_request":
        return
    enforced = summary.get("enforced", {})
    expanded = summary.get("expanded", {})
    top_enf = ', '.join([f"{c}:{n}" for c, n in top_n(enforced.get("by_rule", {}), 3)]) or "none"
    top_exp = ', '.join([f"{c}:{n}" for c, n in top_n(expanded.get("by_rule", {}), 3)]) or "none"
    text = (
        f"Ruff summary: enforced={enforced.get('total',0)}, expanded={expanded.get('total',0)}\n"
        f"Top enforced: {top_enf}\nTop expanded: {top_exp}"
    )
    payload = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as _:
            pass
    except Exception:
        # Non-fatal if Slack is not reachable
        pass


def main() -> int:
    enforced = summarize(Path("ruff-enforced.json"))
    expanded = summarize(Path("ruff-expanded.json"))
    summary = {"enforced": enforced, "expanded": expanded}
    Path("ruff-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_markdown(summary)
    post_slack_webhook(summary)
    print(json.dumps(summary))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
