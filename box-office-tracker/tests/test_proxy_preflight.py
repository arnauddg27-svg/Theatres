"""Proxy preflight: seconds before the lock instead of minutes holding it."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import proxy_preflight as pp  # noqa: E402


class PreflightVerdictTest(unittest.TestCase):
    def test_any_response_means_reachable(self):
        self.assertTrue(pp.verdict(["response"]))
        self.assertTrue(pp.verdict(["error", "error", "response"]))
        self.assertFalse(pp.verdict(["error", "error", "error"]))
        self.assertFalse(pp.verdict([]))

    def test_no_proxy_configured_is_a_pass(self):
        import os
        saved = os.environ.pop("AMC_SEAT_PROXY_URL", None)
        try:
            self.assertEqual(0, pp.main())
        finally:
            if saved is not None:
                os.environ["AMC_SEAT_PROXY_URL"] = saved

    def test_budget_is_seconds_not_minutes(self):
        self.assertLessEqual(pp.ATTEMPTS * pp.TIMEOUT_SEC, 60)
