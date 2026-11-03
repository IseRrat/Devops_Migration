"""E7 regression: timeout cleanup must target the actual runtime container.

Uses the existing deterministic workflow harness; real daemon cleanup remains
part of the full runtime-timeout gate and cannot be proven by this unit test.
"""
import unittest
import test_workflow_failures as harness


class E7CleanupTests(unittest.TestCase):
    def test_timeout_removes_exact_runtime_container_once(self):
        flow = harness.WorkflowFailureTests()
        report = flow.exercise("verify-timeout")
        self.assertEqual(report["status"], "TIMED_OUT")
        runtime = next(i for i, command in enumerate(flow.calls) if command[1] == "run")
        removals = [(i, command) for i, command in enumerate(flow.calls) if command[1] == "rm"]
        self.assertEqual(len(removals), 1)
        self.assertGreater(removals[0][0], runtime)
        self.assertEqual(removals[0][1], ["docker", "rm", "-f", "c" * 64])
