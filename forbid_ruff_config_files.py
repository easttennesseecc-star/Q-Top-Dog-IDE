"""Pre-commit hook: fail if stray Ruff config files are present.

We centrally manage Ruff settings in pyproject.toml. This prevents accidental
reintroduction of ruff.toml or .ruff.toml with narrower excludes that could slow
lint execution or create inconsistent results.
"""
from __future__ import annotations
import os
import sys

BAD_FILES = ["ruff.toml", ".ruff.toml"]
found = [f for f in BAD_FILES if os.path.exists(f)]
if found:
    print(
        "Error: Found stray Ruff config file(s): "
        + ", ".join(found)
        + ". Remove them and rely on pyproject.toml only."
    )
    sys.exit(1)

sys.exit(0)
