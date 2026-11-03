#!/usr/bin/env python3
"""Validate B1 DRAFT fixtures for B3, with optional real toolchain checks."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HELLO = ROOT / "hello"
B1_DOCKERFILE = ROOT.parents[1] / "Dockerfile"


def run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
  return subprocess.run(args, cwd=cwd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def static_checks() -> dict[str, str]:
  broken = (HELLO / "Dockerfile.broken").read_text(encoding="utf-8")
  reference = (HELLO / "Dockerfile.reference").read_text(encoding="utf-8")
  makefile = (HELLO / "Makefile").read_text(encoding="utf-8")
  b1 = B1_DOCKERFILE.read_text(encoding="utf-8")

  assert "RUN make" in broken and "apt-get install" not in broken
  assert all(token in reference for token in ("gcc", "make", "libc6-dev", "RUN make", 'CMD ["./hello"]'))
  assert "hello: main.o" in makefile and "main.o: main.c" in makefile
  assert b1.count("FROM ") >= 2, "B1 Dockerfile must use a builder and a runtime stage"
  assert all(token in b1 for token in ("pip wheel", "pip install", "VCS_REF", "tinygrad-ok"))
  return {"broken_candidate": "expected failure: toolchain absent", "reference_candidate": "static requirements passed", "b1_dockerfile": "multi-stage and verification command present"}


def toolchain_checks(required: bool) -> dict[str, str]:
  make = shutil.which("make")
  compiler = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
  if not make or not compiler:
    if required:
      raise RuntimeError("--require-toolchain needs make and a C compiler")
    return {"toolchain": "SKIPPED: make or C compiler unavailable"}

  with tempfile.TemporaryDirectory(prefix="b3-e3-draft-") as temp:
    work = Path(temp) / "hello"
    shutil.copytree(HELLO, work, ignore=shutil.ignore_patterns("Dockerfile.*", "README.md"))
    run([make], work)
    executable = work / ("hello.exe" if sys.platform == "win32" else "hello")
    observed = run([str(executable)], work).stdout.strip()
    if observed != "hello E3":
      raise AssertionError(f"expected hello E3, got {observed!r}")
    run([make, "clean"], work)
    if executable.exists() or (work / "main.o").exists():
      raise AssertionError("make clean left build outputs")
  return {"toolchain": "PASSED", "verify_stdout": "hello E3", "cleanup": "PASSED"}


def main() -> int:
  parser = argparse.ArgumentParser()
  parser.add_argument("--require-toolchain", action="store_true")
  args = parser.parse_args()
  report = {"static": static_checks(), "dynamic": toolchain_checks(args.require_toolchain)}
  print(json.dumps(report, ensure_ascii=False, indent=2))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
