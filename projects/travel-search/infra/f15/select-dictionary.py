#!/usr/bin/env python3
"""Select a local dictionary file; loading it requires restarting the F15 node."""
import pathlib
import sys
HERE = pathlib.Path(__file__).resolve().parent
choice = sys.argv[1] if len(sys.argv) == 2 else ""
if choice not in {"empty", "travel"}:
    raise SystemExit("Usage: python3 infra/f15/select-dictionary.py empty|travel")
runtime = HERE / ".runtime"
runtime.mkdir(exist_ok=True)
(runtime / "words.dic").write_bytes((HERE / "dictionaries" / (choice + ".dic")).read_bytes())
print("Selected", choice, "on disk; restart the F15 node, then verify _analyze")
