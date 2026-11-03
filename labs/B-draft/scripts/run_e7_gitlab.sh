#!/usr/bin/env bash
# Run from labs/B-draft on a dedicated shell Runner with a local Docker daemon.
set -euo pipefail
: "${CI_COMMIT_SHA:?Run in GitLab CI}"
: "${CI_JOB_ID:?Run in GitLab CI}"
out="work/ci-e7-${CI_JOB_ID}"
mkdir -p work
mkdir "$out"
printf '%s\n' "$CI_COMMIT_SHA" > "$out/commit.txt"
printf '%s\n' "${CI_PIPELINE_URL:-}" "${CI_JOB_URL:-}" > "$out/urls.txt"
run_stage() {
  local name="$1" code=0
  shift
  printf '%q ' "$@" > "$out/$name.command.txt"
  "$@" > "$out/$name.stdout.log" 2> "$out/$name.stderr.log" || code=$?
  printf '%s\n' "$code" > "$out/$name.exit-code.txt"
  cat "$out/$name.stdout.log" "$out/$name.stderr.log"
  return "$code"
}
run_stage revision bash -c 'test "$(git rev-parse HEAD)" = "$CI_COMMIT_SHA"'
run_stage socket test -S /var/run/docker.sock
run_stage docker docker version
run_stage syntax python3 -m compileall -q services/draft/draft scripts
run_stage source-scan python3 scripts/secret_scan.py . --history
candidate="fixtures/ci-candidates/e6-241830086/Dockerfile"
cp "$candidate" "$out/candidate.Dockerfile"
cp fixtures/ci-candidates/e6-241830086/provenance.json "$out/provenance.json"
run_stage candidate-hash bash -c 'printf "%s  %s\n" 33aa956254b0615a333f341a0105ac57fb837214ba9a4fc769899912431c6765 "$1" | sha256sum -c -' _ "$candidate"
image="course1020-draft:e7-${CI_JOB_ID}"
run_stage build python3 scripts/lab_cloud.py build --image "$image" --out "$out/service-build" --build-timeout 1200
run_stage image-scan python3 scripts/secret_scan.py . --image "$image"
run_stage toolchain docker run --rm --network none "$image" cat /opt/toolchain.lock
run_stage gate python3 scripts/lab_cloud.py gate --image "$image" --candidate "$candidate" --out "$out/full-gate" --build-timeout 600
