#!/usr/bin/env python3
"""Verify archived B3 evidence and its binding to the current DRAFT fixtures."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIXTURE = ROOT / "draft" / "hello"
ARCHIVE = ROOT / "evidence" / "gitlab-job-658805"
LOCAL_WSL = ROOT / "evidence" / "local-wsl-20261002"

EXPECTED = {
  "Dockerfile.broken": "b163b7ab94b5c640d183cbcd01fd9bf6f7c9ee68d9b3cb59e2097bb27f337764",
  "Dockerfile.reference": "3575e975d293ebe472dbfeaa0ce6046d72058185ee8ce51aaf5f02eec217a911",
}


def content_sha256(path: Path) -> str:
  """Hash repository text consistently across LF and CRLF worktrees."""
  normalized = path.read_bytes().replace(b"\r\n", b"\n")
  return hashlib.sha256(normalized).hexdigest()


def main() -> int:
  hashes: dict[str, str] = {}
  for filename, expected in EXPECTED.items():
    current = content_sha256(FIXTURE / filename)
    archived = content_sha256(ARCHIVE / filename)
    if current != expected or archived != expected:
      raise AssertionError(f"{filename} is not bound to Job 658805: current={current}, archived={archived}")
    hashes[filename] = expected

  metadata = dict(
    line.split("=", 1)
    for line in (ARCHIVE / "metadata.env").read_text(encoding="utf-8").splitlines()
    if "=" in line
  )
  assert metadata == {
    "commit": "279853855005de330157d88ff37e5979bc88577f",
    "pipeline": "335666",
    "job": "658805",
    "reference_image": "nju-devops/groupb04/e3-draft-reference:27985385",
  }

  broken_log = (ARCHIVE / "broken-build.log").read_text(encoding="utf-8")
  assert "/bin/sh: 1: make: not found" in broken_log
  assert "exit code: 127" in broken_log

  image_id = (ARCHIVE / "reference-image-id.txt").read_text(encoding="utf-8").strip()
  assert re.fullmatch(r"sha256:[0-9a-f]{64}", image_id)
  assert (ARCHIVE / "reference-verify.log").read_text(encoding="utf-8").strip() == "hello E3"

  local_summary = json.loads((LOCAL_WSL / "summary.json").read_text(encoding="utf-8"))
  assert local_summary["failures"] == []
  assert all(item["exit_code"] == 0 for key, item in local_summary.items() if key != "failures")
  local_contracts = (LOCAL_WSL / "e2-contracts.log").read_text(encoding="utf-8")
  local_draft = (LOCAL_WSL / "e3-draft.log").read_text(encoding="utf-8")
  local_mdfixer = (LOCAL_WSL / "e3-mdfixer.log").read_text(encoding="utf-8")
  assert '"schemas": 7, "examples": 25, "failures": []' in local_contracts
  assert '"toolchain": "PASSED"' in local_draft and '"verify_stdout": "hello E3"' in local_draft
  assert all(marker in local_mdfixer for marker in (
    '"toolchain": "PASSED"',
    '"unrepaired_incremental": "1"',
    '"repaired_incremental": "3"',
    '"invalid_candidate": "REJECTED"',
    '"recovery": "PASSED"',
  ))

  print(json.dumps({
    "pipeline": metadata["pipeline"],
    "job": metadata["job"],
    "fixture_sha256": hashes,
    "broken_candidate": "EXPECTED_FAILURE_127",
    "reference_image_id": image_id,
    "reference_stdout": "hello E3",
    "local_wsl": "CONTRACT_DRAFT_MDFIXER_PASSED",
  }, ensure_ascii=False, indent=2))
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
