#!/usr/bin/env python3
"""Validate fixed MD input, accepted repair, rejection, and recovery."""

from __future__ import annotations

import argparse
from datetime import datetime
from functools import partial
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_FILES = ("Makefile", "config.h", "main.c")
COMMIT = re.compile(r"^[0-9a-f]{40}$")
GIT_ENV = {
  "GIT_AUTHOR_NAME": "B3 E3 Fixture",
  "GIT_AUTHOR_EMAIL": "b3-e3@example.invalid",
  "GIT_COMMITTER_NAME": "B3 E3 Fixture",
  "GIT_COMMITTER_EMAIL": "b3-e3@example.invalid",
  "GIT_AUTHOR_DATE": "2026-09-28T00:10:00+0000",
  "GIT_COMMITTER_DATE": "2026-09-28T00:10:00+0000",
}


def write_json(path: Path, value: object) -> None:
  path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(args: list[str], cwd: Path, *, check: bool = True, evidence_dir: Path | None = None) -> subprocess.CompletedProcess[str]:
  env = os.environ.copy()
  env.update(GIT_ENV)
  completed = subprocess.run(args, cwd=cwd, env=env, check=False, text=True, capture_output=True)
  if evidence_dir:
    path = evidence_dir / "commands.json"
    records = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    records.append({"command": args, "cwd": str(cwd), "exit_code": completed.returncode,
                    "stdout": completed.stdout, "stderr": completed.stderr})
    write_json(path, records)
    logs = evidence_dir / "commands"
    logs.mkdir(exist_ok=True)
    for stream in ("stdout", "stderr"):
      (logs / f"{len(records):03}.{stream}.txt").write_text(getattr(completed, stream), encoding="utf-8")
  if check:
    completed.check_returncode()
  return completed


def snapshot(repo: Path, name: str, evidence_dir: Path | None) -> None:
  if evidence_dir:
    destination = evidence_dir / "snapshots" / name
    destination.mkdir(parents=True)
    for filename in SOURCE_FILES:
      shutil.copy2(repo / filename, destination / filename)


def static_checks() -> dict[str, str]:
  report = json.loads((ROOT / "fixed-md-report.template.json").read_text(encoding="utf-8").replace("${SOURCE_COMMIT}", "a" * 40))
  assert report["provenance"] == "INSTRUCTOR_ORACLE"
  assert report["commit"] == "a" * 40
  finding = report["findings"][0]
  assert {key: value for key, value in finding.items() if key != "location"} == {
    "type": "MISSING",
    "target": "main.o",
    "dependency": "config.h",
    "evidence": "main.c includes config.h, but Makefile omits config.h from main.o prerequisites",
  }
  assert len(report["findings"]) == 1
  assert set(finding["location"]) == {"source", "declaration"}
  for location in finding["location"].values():
    lines = (ROOT / location["file"]).read_text(encoding="utf-8").splitlines()
    assert 1 <= location["line"] <= len(lines)
    assert lines[location["line"] - 1] == location["text"], "reported location differs from fixture source"
  makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
  reference = (ROOT / "reference.patch").read_text(encoding="utf-8")
  invalid = (ROOT / "invalid-candidate.patch").read_text(encoding="utf-8")
  assert "main.o: main.c\n" in makefile.replace("\r\n", "\n")
  assert "+main.o: main.c config.h" in reference and "missing.h" not in reference
  assert "+main.o: main.c config.h missing.h" in invalid
  return {"fixed_report": "MISSING main.o -> config.h", "reference_patch": "expected accepted", "invalid_candidate": "expected rejected: missing.h"}


def fresh_repo(parent: Path, name: str, execute=run) -> Path:
  repo = parent / name
  repo.mkdir()
  for filename in SOURCE_FILES:
    shutil.copy2(ROOT / filename, repo / filename)
  execute(["git", "init", "--quiet"], repo)
  execute(["git", "add", "."], repo)
  execute(["git", "commit", "--quiet", "-m", "fixed MD fixture"], repo)
  return repo


def executable(repo: Path) -> Path:
  return repo / ("app.exe" if sys.platform == "win32" else "app")


def build_output(repo: Path, make: str, *, clean: bool = False, execute=run) -> str:
  if clean:
    execute([make, "clean"], repo)
  execute([make], repo)
  return execute([str(executable(repo))], repo).stdout.strip()


def dynamic_checks(required: bool, evidence_dir: Path | None = None) -> dict[str, str]:
  execute = partial(run, evidence_dir=evidence_dir)
  build = partial(build_output, execute=execute)
  make = shutil.which("make")
  compiler = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
  git = shutil.which("git")
  if not make or not compiler or not git:
    if required:
      raise RuntimeError("--require-toolchain needs git, make, and a C compiler")
    return {"toolchain": "SKIPPED: git, make, or C compiler unavailable"}

  if evidence_dir:
    write_json(evidence_dir / "environment.json", {
      "time": datetime.now().astimezone().isoformat(), "platform": platform.platform(),
      "architecture": platform.machine(), "python": sys.version,
      "tool_versions": {name: execute([tool, "--version"], ROOT).stdout for name, tool in
                        (("git", git), ("make", make), ("compiler", compiler))},
    })
    for filename in ("reference.patch", "invalid-candidate.patch"):
      shutil.copy2(ROOT / filename, evidence_dir / filename)

  with tempfile.TemporaryDirectory(prefix="b3-e3-mdfixer-") as temp:
    root = Path(temp)
    repaired = fresh_repo(root, "repaired", execute)
    snapshot(repaired, "before", evidence_dir)
    source_commit = execute([git, "rev-parse", "HEAD"], repaired).stdout.strip()
    if not COMMIT.fullmatch(source_commit):
      raise AssertionError("fixture commit is not a full SHA")
    report = json.loads((ROOT / "fixed-md-report.template.json").read_text(encoding="utf-8").replace("${SOURCE_COMMIT}", source_commit))
    assert report["commit"] == source_commit and report["findings"][0]["type"] == "MISSING"
    if evidence_dir:
      write_json(evidence_dir / "fixed-md-report.json", report)

    initial = build(repaired, make, clean=True)
    assert initial == "1"
    time.sleep(1.1)
    (repaired / "config.h").write_text("#define VALUE 2\n", encoding="utf-8")
    stale = build(repaired, make)
    snapshot(repaired, "unrepaired-incremental", evidence_dir)
    assert stale == "1", "unrepaired sample must retain stale output"

    execute([git, "apply", "--check", str(ROOT / "reference.patch")], repaired)
    execute([git, "apply", str(ROOT / "reference.patch")], repaired)
    clean_result = build(repaired, make, clean=True)
    assert clean_result == "2"
    time.sleep(1.1)
    (repaired / "config.h").write_text("#define VALUE 3\n", encoding="utf-8")
    incremental = build(repaired, make)
    snapshot(repaired, "repaired", evidence_dir)
    assert incremental == "3", "repair must trigger incremental rebuild"
    if evidence_dir:
      (evidence_dir / "applied.patch").write_text(execute([git, "diff", "--", "Makefile"], repaired).stdout, encoding="utf-8")

    rejected = fresh_repo(root, "rejected", execute)
    execute([git, "apply", "--check", str(ROOT / "invalid-candidate.patch")], rejected)
    execute([git, "apply", str(ROOT / "invalid-candidate.patch")], rejected)
    failed = execute([make], rejected, check=False)
    snapshot(rejected, "rejected", evidence_dir)
    assert failed.returncode != 0 and "missing.h" in failed.stdout + failed.stderr

    recovered = fresh_repo(root, "recovered", execute)
    recovery = build(recovered, make, clean=True)
    snapshot(recovered, "recovered", evidence_dir)
    assert recovery == "1"

  return {
    "toolchain": "PASSED",
    "source_commit": source_commit,
    "unrepaired_incremental": stale,
    "repaired_incremental": incremental,
    "invalid_candidate": "REJECTED",
    "recovery": "PASSED",
  }


def main() -> int:
  parser = argparse.ArgumentParser()
  parser.add_argument("--require-toolchain", action="store_true")
  parser.add_argument("--evidence-dir", type=Path)
  args = parser.parse_args()
  if args.evidence_dir:
    args.evidence_dir = args.evidence_dir.resolve()
    args.evidence_dir.mkdir(parents=True, exist_ok=False)
  report = {}
  try:
    report["static"] = static_checks()
    report["dynamic"] = dynamic_checks(args.require_toolchain, args.evidence_dir)
  except (AssertionError, OSError, RuntimeError, subprocess.CalledProcessError) as error:
    report["error"] = str(error)
    raise
  finally:
    if args.evidence_dir:
      write_json(args.evidence_dir / "observations.json", report)
  print(json.dumps(report, ensure_ascii=False, indent=2))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
