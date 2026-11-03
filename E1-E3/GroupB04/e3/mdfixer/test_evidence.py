"""Verify real command recording and fixture artifact provenance."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import validate_mdfixer_fixture as fixture


class EvidenceTests(unittest.TestCase):
  def test_failed_command_is_saved_before_exception(self):
    with tempfile.TemporaryDirectory() as directory:
      output = Path(directory)
      with self.assertRaises(subprocess.CalledProcessError):
        fixture.run([sys.executable, "-c", "import sys; print('actual output'); print('actual error', file=sys.stderr); sys.exit(7)"], output, evidence_dir=output)
      commands = json.loads((output / "commands.json").read_text())
      self.assertEqual(commands[0]["exit_code"], 7)
      self.assertEqual(commands[0]["stdout"], "actual output\n")
      self.assertEqual(commands[0]["stderr"], "actual error\n")

  def test_cli_archives_report_patch_snapshots_and_observations(self):
    with tempfile.TemporaryDirectory() as directory:
      output = Path(directory) / "evidence"
      result = subprocess.run([sys.executable, str(Path(fixture.__file__)), "--require-toolchain", "--evidence-dir", str(output)], capture_output=True, text=True)
      self.assertEqual(result.returncode, 0, result.stderr)
      observations = json.loads((output / "observations.json").read_text())
      report = json.loads((output / "fixed-md-report.json").read_text())
      self.assertEqual(report["commit"], observations["dynamic"]["source_commit"])
      self.assertNotIn("${SOURCE_COMMIT}", (output / "fixed-md-report.json").read_text())
      locations = report["findings"][0]["location"]
      self.assertEqual(locations["source"]["file"], "main.c")
      self.assertEqual(locations["declaration"]["file"], "Makefile")
      for location in locations.values():
        lines = (output / "snapshots/before" / location["file"]).read_text().splitlines()
        self.assertEqual(lines[location["line"] - 1], location["text"])
      self.assertEqual((output / "reference.patch").read_bytes(), (fixture.ROOT / "reference.patch").read_bytes())
      self.assertIn("main.o: main.c config.h", (output / "snapshots/repaired/Makefile").read_text())
      self.assertNotIn("config.h", (output / "snapshots/before/Makefile").read_text())
      commands = json.loads((output / "commands.json").read_text())
      failure = next(item for item in commands if item["exit_code"] != 0)
      self.assertIn("missing.h", failure["stderr"])
      self.assertTrue(any(item["stdout"].strip() == "3" for item in commands))
      self.assertTrue((output / "snapshots/recovered/Makefile").is_file())


if __name__ == "__main__":
  unittest.main()
