#!/usr/bin/env python3
"""Validate B3 E2 examples with JSON Schema plus cross-field semantics."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Callable

try:
  from jsonschema import Draft202012Validator, FormatChecker, RefResolver
except ModuleNotFoundError as error:
  raise SystemExit(
    "jsonschema is required; run: python -m pip install -r "
    "E1-E3/GroupB04/validation-requirements.in"
  ) from error

ROOT = Path(__file__).resolve().parent
EXAMPLES = ROOT / "examples"
SCHEMAS = ROOT / "schemas"
PUBLIC_SCHEMAS = ROOT.parent / "schemas"
COMMIT = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
IMAGE_ID = re.compile(r"^sha256:[0-9a-f]{64}$")
ERROR_CODE = re.compile(r"^(VALIDATION|ENV|EXEC|ANALYSIS|CANCEL)_[0-9]{4}$")


def load(path: Path) -> dict[str, Any]:
  with path.open(encoding="utf-8") as handle:
    value = json.load(handle)
  if not isinstance(value, dict):
    raise ValueError(f"{path} must contain a JSON object")
  return value


def schema_validators() -> tuple[dict[str, dict[str, Any]], dict[str, Draft202012Validator]]:
  schemas = {
    path.name: load(path)
    for directory in (PUBLIC_SCHEMAS, SCHEMAS)
    for path in sorted(directory.glob("*.schema.json"))
  }
  store = {schema["$id"]: schema for schema in schemas.values()}
  validators: dict[str, Draft202012Validator] = {}
  for name, schema in schemas.items():
    Draft202012Validator.check_schema(schema)
    validators[name] = Draft202012Validator(
      schema,
      resolver=RefResolver.from_schema(schema, store=store),
      format_checker=FormatChecker(),
    )
  return schemas, validators


def passes_schema(validator: Draft202012Validator, value: object) -> bool:
  return next(validator.iter_errors(value), None) is None


def nonempty(value: object) -> bool:
  return isinstance(value, str) and bool(value)


def exact_keys(data: dict[str, Any], allowed: set[str]) -> bool:
  return set(data) <= allowed


def valid_artifact(value: object) -> bool:
  allowed = {"artifact_id", "type", "uri", "media_type", "sha256", "producer_job_id", "source_commit"}
  return (
    isinstance(value, dict)
    and {"uri", "sha256"} <= set(value)
    and set(value) <= allowed
    and isinstance(value.get("uri"), str)
    and value["uri"].startswith("artifact://")
    and isinstance(value.get("sha256"), str)
    and bool(SHA256.fullmatch(value["sha256"]))
    and all(nonempty(value[key]) for key in ("artifact_id", "type", "media_type", "producer_job_id") if key in value)
    and (
      "source_commit" not in value
      or (isinstance(value["source_commit"], str) and bool(COMMIT.fullmatch(value["source_commit"])))
    )
  )


def validate_job(data: dict[str, Any]) -> str | None:
  allowed = {"schema_version", "job_id", "job_type", "trace_id", "status", "input", "output", "error"}
  if not exact_keys(data, allowed):
    return "JOB_ADDITIONAL_PROPERTY"
  if data.get("schema_version") != "1.0" or data.get("job_type") not in {"DRAFT", "FULL_CHECK", "INCREMENTAL_CHECK", "REPAIR"}:
    return "JOB_INVALID"
  if not nonempty(data.get("job_id")) or not nonempty(data.get("trace_id")):
    return "JOB_INVALID"
  status = data.get("status")
  if status not in {"QUEUED", "RUNNING", "SUCCEEDED", "FAILED", "TIMED_OUT", "CANCELLED"}:
    return "JOB_INVALID"
  if status in {"QUEUED", "RUNNING"} and ("output" in data or "error" in data):
    return "JOB_TERMINAL_CONFLICT"
  if status == "SUCCEEDED" and (not isinstance(data.get("output"), dict) or "error" in data):
    return "JOB_TERMINAL_CONFLICT"
  if status in {"FAILED", "TIMED_OUT", "CANCELLED"}:
    error = data.get("error")
    if (
      "output" in data
      or not isinstance(error, dict)
      or not {"code", "message"} <= set(error)
      or not set(error) <= {"code", "message", "field"}
    ):
      return "JOB_TERMINAL_CONFLICT"
    if not isinstance(error.get("code"), str) or not ERROR_CODE.fullmatch(error["code"]) or not nonempty(error.get("message")):
      return "JOB_TERMINAL_CONFLICT"
  return None


def validate_draft_request(data: dict[str, Any]) -> str | None:
  allowed = {"schema_version", "job_type", "trace_id", "repository", "context_files", "build_command", "verify_command", "expected_stdout", "max_iterations", "timeout_seconds"}
  required = allowed - {"expected_stdout"}
  if not exact_keys(data, allowed) or not required <= set(data):
    return "VALIDATION_1200"
  if data.get("schema_version") != "1.0" or data.get("job_type") != "DRAFT" or not nonempty(data.get("trace_id")):
    return "VALIDATION_1200"
  repository = data.get("repository")
  if (
    not isinstance(repository, dict)
    or set(repository) != {"url", "commit"}
    or not nonempty(repository.get("url"))
    or not str(repository["url"]).startswith("https://")
  ):
    return "VALIDATION_1201"
  if not isinstance(repository.get("commit"), str) or not COMMIT.fullmatch(repository["commit"]):
    return "VALIDATION_1201"
  context_files = data.get("context_files")
  if not isinstance(context_files, list) or not 1 <= len(context_files) <= 2 or len(set(context_files)) != len(context_files):
    return "VALIDATION_1202"
  if not all(
    nonempty(item)
    and not str(item).startswith("/")
    and not re.match(r"^[A-Za-z]:", str(item))
    and "\\" not in str(item)
    and ".." not in str(item).split("/")
    for item in context_files
  ):
    return "VALIDATION_1202"
  if not nonempty(data.get("build_command")) or not nonempty(data.get("verify_command")):
    return "VALIDATION_1203"
  if "expected_stdout" in data and not isinstance(data["expected_stdout"], str):
    return "VALIDATION_1203"
  if isinstance(data.get("max_iterations"), bool) or not isinstance(data.get("max_iterations"), int) or not 1 <= data["max_iterations"] <= 30:
    return "VALIDATION_1204"
  if isinstance(data.get("timeout_seconds"), bool) or not isinstance(data.get("timeout_seconds"), int) or not 1 <= data["timeout_seconds"] <= 1800:
    return "VALIDATION_1205"
  return None


def validate_draft_output(data: dict[str, Any]) -> str | None:
  required = {"repository_commit", "dockerfile", "image", "build_log", "verify_log", "iterations"}
  if set(data) != required:
    return "DRAFT_OUTPUT_INVALID"
  if not isinstance(data.get("repository_commit"), str) or not COMMIT.fullmatch(data["repository_commit"]):
    return "DRAFT_OUTPUT_INVALID"
  if not all(valid_artifact(data.get(key)) for key in ("dockerfile", "build_log", "verify_log")):
    return "DRAFT_OUTPUT_INVALID"
  image = data.get("image")
  if not isinstance(image, dict) or not {"reference", "image_id", "platform"} <= set(image) or not set(image) <= {"reference", "image_id", "digest", "platform"}:
    return "DRAFT_OUTPUT_INVALID"
  if not nonempty(image.get("reference")) or not isinstance(image.get("image_id"), str) or not IMAGE_ID.fullmatch(image["image_id"]) or image.get("platform") != "linux/amd64":
    return "DRAFT_OUTPUT_INVALID"
  iterations = data.get("iterations")
  if not isinstance(iterations, list) or not iterations:
    return "DRAFT_OUTPUT_INVALID"
  for item in iterations:
    if not isinstance(item, dict) or set(item) != {"number", "dockerfile_uri", "result", "selection_reason"}:
      return "DRAFT_OUTPUT_INVALID"
    if not isinstance(item["number"], int) or item["number"] < 1 or not str(item["dockerfile_uri"]).startswith("artifact://"):
      return "DRAFT_OUTPUT_INVALID"
    if item["result"] not in {"ACCEPTED", "REJECTED"} or not nonempty(item["selection_reason"]):
      return "DRAFT_OUTPUT_INVALID"
  return None


def validate_repair_request(data: dict[str, Any]) -> str | None:
  allowed = {"schema_version", "job_type", "trace_id", "repository", "missing_report", "makefile_path", "build_command", "verify_command", "expected_stdout", "max_candidates", "timeout_seconds"}
  required = allowed - {"expected_stdout"}
  if not exact_keys(data, allowed) or not required <= set(data):
    return "VALIDATION_1300"
  if data.get("schema_version") != "1.0" or data.get("job_type") != "REPAIR" or not nonempty(data.get("trace_id")):
    return "VALIDATION_1300"
  repository = data.get("repository")
  if not isinstance(repository, dict) or set(repository) != {"url", "commit"}:
    return "VALIDATION_1301"
  if (
    not nonempty(repository.get("url"))
    or not str(repository["url"]).startswith("https://")
    or not isinstance(repository.get("commit"), str)
    or not COMMIT.fullmatch(repository["commit"])
  ):
    return "VALIDATION_1301"
  report = data.get("missing_report")
  if not isinstance(report, dict) or set(report) != {"uri", "sha256", "report_commit", "finding_type"}:
    return "VALIDATION_1302"
  if not isinstance(report.get("uri"), str) or not report["uri"].startswith("artifact://"):
    return "VALIDATION_1302"
  if not isinstance(report.get("sha256"), str) or not SHA256.fullmatch(report["sha256"]):
    return "VALIDATION_1302"
  if report.get("finding_type") != "MISSING" or report.get("report_commit") != repository["commit"]:
    return "VALIDATION_1302"
  path = data.get("makefile_path")
  if (
    not nonempty(path)
    or str(path).startswith("/")
    or re.match(r"^[A-Za-z]:", str(path))
    or "\\" in str(path)
    or ".." in str(path).split("/")
  ):
    return "VALIDATION_1303"
  if not nonempty(data.get("build_command")) or not nonempty(data.get("verify_command")):
    return "VALIDATION_1304"
  if isinstance(data.get("max_candidates"), bool) or not isinstance(data.get("max_candidates"), int) or not 1 <= data["max_candidates"] <= 30:
    return "VALIDATION_1305"
  if isinstance(data.get("timeout_seconds"), bool) or not isinstance(data.get("timeout_seconds"), int) or not 1 <= data["timeout_seconds"] <= 1800:
    return "VALIDATION_1306"
  return None


def validate_repair_output(data: dict[str, Any]) -> str | None:
  required = {"repository_commit", "patch", "repair_report", "build_log", "verify_log", "recheck_report", "candidate_summary"}
  if set(data) != required:
    return "REPAIR_OUTPUT_INVALID"
  if not isinstance(data.get("repository_commit"), str) or not COMMIT.fullmatch(data["repository_commit"]):
    return "REPAIR_OUTPUT_INVALID"
  if not all(valid_artifact(data.get(key)) for key in ("patch", "repair_report", "build_log", "verify_log", "recheck_report")):
    return "REPAIR_OUTPUT_INVALID"
  candidates = data.get("candidate_summary")
  if not isinstance(candidates, list) or not candidates:
    return "REPAIR_OUTPUT_INVALID"
  for item in candidates:
    if not isinstance(item, dict) or set(item) != {"candidate_id", "result", "reason"}:
      return "REPAIR_OUTPUT_INVALID"
    if not nonempty(item["candidate_id"]) or item["result"] not in {"ACCEPTED", "REJECTED"} or not nonempty(item["reason"]):
      return "REPAIR_OUTPUT_INVALID"
  return None


def validate_repair_report(data: dict[str, Any]) -> str | None:
  required = {"schema_version", "source_commit", "finding", "accepted_candidate", "candidates", "verification"}
  if set(data) != required or data.get("schema_version") != "1.0":
    return "REPAIR_REPORT_INVALID"
  if not isinstance(data.get("source_commit"), str) or not COMMIT.fullmatch(data["source_commit"]):
    return "REPAIR_REPORT_INVALID"
  finding = data.get("finding")
  if not isinstance(finding, dict) or set(finding) != {"type", "target", "dependency"} or finding.get("type") != "MISSING":
    return "REPAIR_REPORT_INVALID"
  if not nonempty(finding.get("target")) or not nonempty(finding.get("dependency")):
    return "REPAIR_REPORT_INVALID"
  candidates = data.get("candidates")
  accepted = data.get("accepted_candidate")
  if not isinstance(candidates, list) or not candidates or not nonempty(accepted):
    return "REPAIR_REPORT_INVALID"
  candidate_ids = [item.get("candidate_id") for item in candidates if isinstance(item, dict)]
  accepted_ids = [item.get("candidate_id") for item in candidates if isinstance(item, dict) and item.get("result") == "ACCEPTED"]
  if len(candidate_ids) != len(set(candidate_ids)) or accepted_ids != [accepted]:
    return "REPAIR_REPORT_INVALID"
  verification = data.get("verification")
  if not isinstance(verification, dict) or set(verification) != {"patch_applied", "build_passed", "functional_test_passed", "recheck_passed"}:
    return "REPAIR_REPORT_INVALID"
  if any(value is not True for value in verification.values()):
    return "REPAIR_REPORT_INVALID"
  return None


def main() -> int:
  failures: list[str] = []
  schemas, validators = schema_validators()
  for name in sorted(schemas):
    print(f"PASS Draft 2020-12 schema: {name}")

  cases: list[tuple[str, str, bool, Callable[[dict[str, Any]], str | None], str | None]] = [
    ("job-succeeded-valid.json", "job.schema.json", True, validate_job, None),
    ("job-failed-valid.json", "job.schema.json", True, validate_job, None),
    ("job-succeeded-with-error-invalid.json", "job.schema.json", False, validate_job, "JOB_TERMINAL_CONFLICT"),
    ("job-running-with-output-invalid.json", "job.schema.json", False, validate_job, "JOB_TERMINAL_CONFLICT"),
    ("job-cancelled-without-error-invalid.json", "job.schema.json", False, validate_job, "JOB_TERMINAL_CONFLICT"),
    ("job-cancelled-valid.json", "job.schema.json", True, validate_job, None),
    ("draft-request-valid.json", "draft-request.schema.json", True, validate_draft_request, None),
    ("draft-request-job-type-invalid.json", "draft-request.schema.json", False, validate_draft_request, "VALIDATION_1200"),
    ("draft-request-commit-invalid.json", "draft-request.schema.json", False, validate_draft_request, "VALIDATION_1201"),
    ("draft-request-context-invalid.json", "draft-request.schema.json", False, validate_draft_request, "VALIDATION_1202"),
    ("draft-request-url-invalid.json", "draft-request.schema.json", False, validate_draft_request, "VALIDATION_1201"),
    ("draft-request-windows-path-invalid.json", "draft-request.schema.json", False, validate_draft_request, "VALIDATION_1202"),
    ("draft-request-bool-iterations-invalid.json", "draft-request.schema.json", False, validate_draft_request, "VALIDATION_1204"),
    ("draft-output-valid.json", "draft-output.schema.json", True, validate_draft_output, None),
    ("draft-output-verify-log-invalid.json", "draft-output.schema.json", False, validate_draft_output, "DRAFT_OUTPUT_INVALID"),
    ("repair-request-valid.json", "repair-request.schema.json", True, validate_repair_request, None),
    ("repair-request-job-type-invalid.json", "repair-request.schema.json", False, validate_repair_request, "VALIDATION_1300"),
    ("repair-request-redundant-invalid.json", "repair-request.schema.json", False, validate_repair_request, "VALIDATION_1302"),
    ("repair-request-commit-invalid.json", "repair-request.schema.json", True, validate_repair_request, "VALIDATION_1302"),
    ("repair-request-uri-invalid.json", "repair-request.schema.json", False, validate_repair_request, "VALIDATION_1302"),
    ("repair-output-valid.json", "repair-output.schema.json", True, validate_repair_output, None),
    ("repair-output-recheck-invalid.json", "repair-output.schema.json", False, validate_repair_output, "REPAIR_OUTPUT_INVALID"),
    ("repair-report-valid.json", "repair-report.schema.json", True, validate_repair_report, None),
    ("repair-report-malformed-candidate-invalid.json", "repair-report.schema.json", False, validate_repair_report, "REPAIR_REPORT_INVALID"),
    ("repair-report-two-accepted-invalid.json", "repair-report.schema.json", False, validate_repair_report, "REPAIR_REPORT_INVALID"),
  ]

  for filename, schema_name, expected_schema, validator, expected in cases:
    value = load(EXAMPLES / filename)
    schema_result = passes_schema(validators[schema_name], value)
    actual = validator(value)
    result = "PASS" if schema_result == expected_schema and actual == expected else "FAIL"
    print(
      f"{result} {filename}: schema expected {expected_schema}, got {schema_result}; "
      f"semantic expected {expected}, got {actual}"
    )
    if result == "FAIL":
      failures.append(filename)

  succeeded = load(EXAMPLES / "job-succeeded-valid.json")
  output_valid = passes_schema(validators["draft-output.schema.json"], succeeded["output"])
  print(f"{'PASS' if output_valid else 'FAIL'} job-succeeded-valid.json: DRAFT output schema")
  if not output_valid:
    failures.append("job-succeeded-valid.json#output")

  print(json.dumps({"schemas": len(schemas), "examples": len(cases), "failures": failures}, ensure_ascii=False))
  return 1 if failures else 0


if __name__ == "__main__":
  sys.exit(main())
