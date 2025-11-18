#!/usr/bin/env python3
"""
Parse a pytest JUnit XML file and write a concise markdown summary with
- totals (tests/failures/errors/skips)
- top failing tests (up to 10) with brief messages

Usage:
  python tools/parse_junit.py <input_junit.xml> --out <output_summary.md>
"""
from __future__ import annotations
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("input", type=Path, help="Path to junit.xml")
    p.add_argument("--out", type=Path, required=True, help="Path to output markdown summary")
    return p.parse_args()


def summarize(junit_path: Path) -> str:
    if not junit_path.exists():
        return "No junit.xml found."
    try:
        tree = ET.parse(junit_path)
        root = tree.getroot()
    except Exception as e:  # noqa: BLE001
        return f"Failed to parse junit.xml: {e}"

    # Support either single testsuite or multiple nested testsuites
    if root.tag == "testsuite":
        suites = [root]
    else:
        suites = root.findall(".//testsuite") or []

    total = fails = errors = skips = 0
    cases: list[tuple[str, str, str, str, str, str]] = []

    for s in suites:
        total += int(s.attrib.get("tests", 0) or 0)
        fails += int(s.attrib.get("failures", 0) or 0)
        errors += int(s.attrib.get("errors", 0) or 0)
        skips += int(s.attrib.get("skipped", 0) or 0)
        for tc in s.findall("testcase"):
            name = tc.attrib.get("name", "")
            classname = tc.attrib.get("classname", "")
            file = tc.attrib.get("file", "") or tc.attrib.get("filename", "") or ""
            duration = tc.attrib.get("time", "")
            status = "ok"
            detail = ""
            f = tc.find("failure") or tc.find("error")
            if f is not None:
                status = f.tag
                detail = (f.attrib.get("message") or "").strip()
                if not detail:
                    detail = (f.text or "").strip().splitlines()[0] if (f.text or "") else ""
            cases.append((status, classname, name, file, duration, detail))

    lines: list[str] = []
    lines.append("# Pytest Summary")
    lines.append("")
    lines.append(f"- Total: {total}  Failures: {fails}  Errors: {errors}  Skips: {skips}")
    lines.append("")
    failing = [c for c in cases if c[0] in ("failure", "error")]
    if failing:
        lines.append("## Top failing tests")
        for i, (status, classname, name, file, duration, detail) in enumerate(failing[:10], 1):
            ident = f"{classname}::{name}" if classname else name
            loc = f" ({file})" if file else ""
            lines.append(f"{i}. [{status}] {ident}{loc}")
            if detail:
                d = detail.replace("\n", " ").strip()
                if len(d) > 300:
                    d = d[:300] + "…"
                lines.append(f"   - {d}")
    else:
        lines.append("No failing tests found.")

    return "\n".join(lines)


def main() -> int:
    ns = parse_args()
    out_text = summarize(ns.input)
    ns.out.parent.mkdir(parents=True, exist_ok=True)
    ns.out.write_text(out_text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
