#!/usr/bin/env python3
"""Run all B3 E2/E3 validation commands and optionally save evidence logs."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
  parser = argparse.ArgumentParser()
  parser.add_argument("--require-toolchain", action="store_true")
  parser.add_argument("--evidence-dir", type=Path)
  args = parser.parse_args()

  commands = [
    ("e2-contracts", [sys.executable, str(ROOT / "validate_e2_contracts.py")]),
    ("e3-draft", [sys.executable, str(ROOT / "e3" / "draft" / "validate_draft_fixture.py")]),
    ("e3-mdfixer", [sys.executable, str(ROOT / "e3" / "mdfixer" / "validate_mdfixer_fixture.py")]),
    ("e3-evidence", [sys.executable, str(ROOT / "e3" / "validate_evidence.py")]),
  ]
  if args.require_toolchain:
    commands[1][1].append("--require-toolchain")
    commands[2][1].append("--require-toolchain")

  if args.evidence_dir:
    args.evidence_dir = args.evidence_dir.resolve()
    args.evidence_dir.mkdir(parents=True, exist_ok=True)
    commands[2][1].extend(["--evidence-dir", str(args.evidence_dir / "mdfixer")])

  summary: dict[str, object] = {}
  failures: list[str] = []
  for name, command in commands:
    completed = subprocess.run(command, cwd=ROOT.parents[1], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(f"===== {name} =====")
    print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
    if args.evidence_dir:
      (args.evidence_dir / f"{name}.log").write_text(completed.stdout, encoding="utf-8")
    script = Path(command[1]).relative_to(ROOT.parents[1]).as_posix()
    summary[name] = {"exit_code": completed.returncode, "command": ["python3", script, *command[2:]]}
    if completed.returncode:
      failures.append(name)

  summary["failures"] = failures
  summary_text = json.dumps(summary, ensure_ascii=False, indent=2)
  print(summary_text)
  if args.evidence_dir:
    (args.evidence_dir / "summary.json").write_text(summary_text + "\n", encoding="utf-8")
  return 1 if failures else 0


if __name__ == "__main__":
  raise SystemExit(main())
