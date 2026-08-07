"""The regular lane's Phase 1 self-heal must be reachable at the slot it guards.

`ensure_phase1_links_async` is the only self-repair on the regular (seat-count)
lane, and its sole fallback is `fail_phase`. It was gated on
`phase1_target_date_is_repairable`, which compared the target show date against
the CALENDAR date — but the regular scrape fires at 07:00 UTC, i.e. 00:00-03:00
local, so `phase1_expected_date` (now - 12h) is always the previous calendar day
and the gate was always False. The repair could never run: any timezone whose
Phase 1 didn't land lost every seat read for the weekend with no recovery.

A cinema business day runs past midnight, so the window follows the theatre day.
"""
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TZ_NAMES = {"ET": "America/New_York", "CT": "America/Chicago",
            "PT": "America/Los_Angeles"}


def _load_scraper():
    """Import scraper.py with its heavy runtime deps stubbed (same pattern as
    tests/test_scraper_logging.py — neither is installed for unit tests)."""
    from types import ModuleType
    sys.modules.setdefault("requests", ModuleType("requests"))
    playwright_mod = ModuleType("playwright")
    playwright_async = ModuleType("playwright.async_api")
    playwright_async.async_playwright = lambda: None
    sys.modules.setdefault("playwright", playwright_mod)
    sys.modules.setdefault("playwright.async_api", playwright_async)
    import scraper  # noqa: E402
    return scraper


class Phase1RepairWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.S = _load_scraper()

    def _at(self, utc_dt, tz):
        """Evaluate the predicate as if 'now' were utc_dt, for one tz group."""
        local = utc_dt.astimezone(ZoneInfo(TZ_NAMES[tz]))
        with mock.patch.object(self.S, "local_now", return_value=local):
            target = (local - timedelta(hours=12)).strftime("%Y-%m-%d")
            return self.S.phase1_target_date_is_within_theatre_day(tz, target), target

    def test_regular_07z_slot_is_repairable(self):
        # the slot this gate exists to protect — was always False before
        utc = datetime(2026, 8, 8, 7, 0, tzinfo=ZoneInfo("UTC"))
        for tz in TZ_NAMES:
            with self.subTest(tz=tz):
                ok, target = self._at(utc, tz)
                self.assertTrue(ok, f"{tz} target {target} must be repairable at 07Z")

    def test_evening_snapshot_slot_still_repairable(self):
        utc = datetime(2026, 8, 8, 2, 30, tzinfo=ZoneInfo("UTC"))
        for tz in TZ_NAMES:
            with self.subTest(tz=tz):
                self.assertTrue(self._at(utc, tz)[0])

    def test_late_morning_slot_is_not_repairable(self):
        # 14:30Z is 07:30-10:30 local: yesterday's shows really have rolled off,
        # so the gate must still refuse rather than burn the repair budget.
        utc = datetime(2026, 8, 8, 14, 30, tzinfo=ZoneInfo("UTC"))
        for tz in TZ_NAMES:
            with self.subTest(tz=tz):
                self.assertFalse(self._at(utc, tz)[0])

    def test_genuinely_old_date_is_refused(self):
        local = datetime(2026, 8, 8, 3, 0, tzinfo=ZoneInfo(TZ_NAMES["ET"]))
        with mock.patch.object(self.S, "local_now", return_value=local):
            self.assertFalse(self.S.phase1_target_date_is_within_theatre_day("ET", "2026-08-01"))

    def test_strict_predicate_unchanged_so_cached_links_are_still_preferred(self):
        """The last-resort window must NOT widen the cached-links decision.

        When usable cached links exist, spending the Phase 1 budget on a rolled-
        off date is waste — and a failed re-collection could turn a working
        cached-links run into a hard failure. Only the branch that would
        otherwise call fail_phase consults the wider theatre-day window.
        """
        local = datetime(2026, 5, 9, 2, 30, tzinfo=ZoneInfo(TZ_NAMES["PT"]))
        with mock.patch.object(self.S, "local_now", return_value=local):
            self.assertFalse(self.S.phase1_target_date_is_repairable("PT", "2026-05-08"))
            self.assertTrue(self.S.phase1_target_date_is_within_theatre_day("PT", "2026-05-08"))

    def test_malformed_date_is_refused(self):
        self.assertFalse(self.S.phase1_target_date_is_within_theatre_day("ET", "not-a-date"))
        self.assertFalse(self.S.phase1_target_date_is_within_theatre_day("ET", None))


if __name__ == "__main__":
    unittest.main()
