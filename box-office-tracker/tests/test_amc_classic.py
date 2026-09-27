import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import amc_classic  # noqa: E402
import scraper  # noqa: E402


class AmcClassicAllowListTest(unittest.TestCase):
    def test_general_admission_classic_excluded_reserved_classic_kept(self):
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "a.json")
            json.dump({"reserved": ["AMC CLASSIC Brazos Mall 14"]}, open(p, "w"))
            self.assertFalse(amc_classic.excluded("AMC CLASSIC Brazos Mall 14", path=p))
            self.assertTrue(amc_classic.excluded("AMC CLASSIC Quincy 6", path=p))
            self.assertFalse(amc_classic.excluded("AMC Empire 25", path=p))
            self.assertTrue(amc_classic.excluded("", "amc-classic-galesburg-8", path=p))
            self.assertTrue(amc_classic.excluded("AMC CLASSIC X", path=os.path.join(td, "missing.json")))

    def test_shipped_list_is_wired_into_the_theatre_loader(self):
        names = {t["name"] for g in scraper.load_theatres().values() for t in g}
        for n in amc_classic.reserved_names():
            self.assertIn(n.upper(), {x.upper() for x in names})
        self.assertNotIn("AMC CLASSIC Quincy 6", names)
