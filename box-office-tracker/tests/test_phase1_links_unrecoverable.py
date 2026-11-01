"""A regular leg whose show date has rolled off AMC and that has no linked
film left must end empty, not fail the slot (2026-11-01 07Z MT: 3 retries)."""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import scraper  # noqa: E402


class Phase1LinksUnrecoverableTest(unittest.TestCase):
    def test_true_only_when_every_group_date_has_rolled_off(self):
        rolled = {("MT", "2026-10-31"): False, ("ET", "2026-11-01"): True}
        with mock.patch.object(scraper, "phase1_target_date_is_repairable", lambda tz, d: rolled[(tz, d)]):
            self.assertTrue(scraper.phase1_links_unrecoverable(["MT"], {"MT": "2026-10-31"}))
            self.assertFalse(scraper.phase1_links_unrecoverable(["ET"], {"ET": "2026-11-01"}))
            self.assertFalse(scraper.phase1_links_unrecoverable(["MT", "ET"],
                                                                {"MT": "2026-10-31", "ET": "2026-11-01"}))
        self.assertFalse(scraper.phase1_links_unrecoverable([], {}))
        self.assertFalse(scraper.phase1_links_unrecoverable(["MT"], {}))


if __name__ == "__main__":
    unittest.main()
