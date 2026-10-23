#!/usr/bin/env python3
"""Regenerate F13 static diagrams with official D2 v0.9.0; never edit SVGs."""
import datetime
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
CLI = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else pathlib.Path("d2")
version = subprocess.check_output([str(CLI), "--version"], text=True).strip()
if version != "v0.9.0":
    raise SystemExit(f"Expected official D2 v0.9.0, got {version}")
record = {
    "recorded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "scope": "F13 analysis chains and Chinese recall teaching diagrams; ES evidence recorded separately",
    "generator": version, "layout": "dagre", "themes": {"light": 4, "dark": 201},
    "pad": 24, "commands": [], "checks": [], "sha256": {},
    "artifact_edits": "D2 sources only; generated SVG files not manually edited",
    "browser_review": "recorded separately in docs/framework-review/20261023-f13-analysis",
}
if CLI.is_file():
    record["cli_sha256"] = hashlib.sha256(CLI.read_bytes()).hexdigest()
for slug in ["analyzer", "recall"]:
    source = f"framework/diagrams/f13/{slug}.d2"
    operations = [["fmt", "--check", source], ["validate", source]]
    for theme, number in record["themes"].items():
        operations.append(["--layout=dagre", f"--theme={number}", "--pad=24", "--timeout=30",
                           source, f"framework/diagrams/f13/{slug}-{theme}.svg"])
    for args in operations:
        subprocess.run([str(CLI), *args], cwd=ROOT, check=True)
        command = "d2 " + " ".join(args)
        record["commands"].append(command)
        record["checks"].append({"command": command, "status": "passed"})
for path in (ROOT / "framework/diagrams/f13").iterdir():
    if path.suffix in {".d2", ".svg"}:
        record["sha256"][str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
(ROOT / "framework/diagrams/f13/generation.json").write_text(
    json.dumps(record, ensure_ascii=False, indent=2) + "\n")
