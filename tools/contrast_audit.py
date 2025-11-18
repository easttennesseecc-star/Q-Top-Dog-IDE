"""Contrast Audit Script

Scans a set of foreground/background color pairs and reports WCAG contrast ratios.
Run: python tools/contrast_audit.py
Add additional pairs as needed.
"""
from __future__ import annotations
import re
from typing import Tuple, List

# Define color pairs to test (foreground, background, label)
PAIRS: List[Tuple[str,str,str]] = [
    ("#9ca3af", "#1f2937", "text-gray-400 on bg-gray-800"),
    ("#9ca3af", "#0b0f16", "text-gray-400 on app bg"),
    ("#c2c8d0", "#121827", "--muted on --surface dark"),
    ("#e6edf3", "#0b0f16", "--text on app bg"),
    ("#0ea5e9", "#0b0f16", "accent on dark bg"),
    ("#0b0f16", "#0ea5e9", "dark text on accent (on-accent)"),
]

HEX_RE = re.compile(r"^#([0-9a-fA-F]{6})$")

def _parse(hex_color: str) -> Tuple[float,float,float]:
    m = HEX_RE.match(hex_color)
    if not m:
        raise ValueError(f"Invalid hex: {hex_color}")
    v = m.group(1)
    r = int(v[0:2],16)/255.0
    g = int(v[2:4],16)/255.0
    b = int(v[4:6],16)/255.0
    def _pivot(c: float) -> float:
        return c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    return _pivot(r), _pivot(g), _pivot(b)

def luminance(hex_color: str) -> float:
    r,g,b = _parse(hex_color)
    return 0.2126*r + 0.7152*g + 0.0722*b

def contrast_ratio(fg: str, bg: str) -> float:
    L1 = luminance(fg)
    L2 = luminance(bg)
    lighter = max(L1,L2)
    darker = min(L1,L2)
    return (lighter + 0.05) / (darker + 0.05)

def classify(ratio: float) -> str:
    if ratio >= 7:
        return "AAA normal / AA large"
    if ratio >= 4.5:
        return "AA normal"
    if ratio >= 3:
        return "AA large text only"
    return "Fail (<3)"

def main():
    print("Contrast Audit Results:\n")
    for fg,bg,label in PAIRS:
        ratio = contrast_ratio(fg,bg)
        print(f"{label:40} {fg} / {bg}  ratio={ratio:.2f}  {classify(ratio)}")
    print("\nAdd more pairs by editing PAIRS in tools/contrast_audit.py")

if __name__ == "__main__":
    main()
