"""Black-box C1/C2/C4 validation for the AgentRQ adapter."""

from __future__ import annotations

import unittest

from agentrq_blackbox import run_black_box


class AgentRQAdapterBlackBoxTests(unittest.TestCase):
    def test_c1_c2_c4_adapter_gates_pass_with_product_owned_semantics(self) -> None:
        report = run_black_box()
        self.assertEqual([scenario["status"] for scenario in report["scenarios"]], ["PASS", "PASS", "PASS"])
        self.assertEqual(report["surface"], ["createTask", "getTask", "updateTaskStatus", "reply"])
        self.assertIn("no AgentRQ claim operation", report["native_surface_boundary"]["c2"])
        self.assertIn("no AgentRQ reviewer state", report["native_surface_boundary"]["c4"])


if __name__ == "__main__":
    unittest.main()
