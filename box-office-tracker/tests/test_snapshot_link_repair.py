"""The snapshot lane must self-heal stale showtime-links, not strand a weekend.

Phase 1 (collect-links) runs Tue-Thu. If it skips — Polymarket listed the
weekend's market later, which is normal — or fails, showtime-links.json still
points at the PRIOR weekend. Every snapshot slot (3/day x 4 days, i.e. the
entire pre-reservation dataset) then aborted with "run Phase 1 first", and no
scheduled slot remained to fix it. That is how the 2026-08-07 weekend was lost.

The repair path (`repair_snapshot_phase1_links_async`) already rebuilds exactly
the slices a snapshot run needs; it was reachable for a showtime-window-version
mismatch but not for the far more common wrong-weekend state.
"""
import ast
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRAPER = ROOT / "scraper.py"
WORKFLOW = ROOT.parent / ".github" / "workflows" / "box-office-pipeline.yml"


class SnapshotLinkRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = SCRAPER.read_text()

    def test_wrong_weekend_repairs_before_it_can_fail(self):
        """The repair branch must be evaluated ahead of the fail_phase branch."""
        marker = "showtime-links.json is from weekend"
        repair_at = self.src.index("rebuilding the snapshot")
        fail_at = self.src.index(f'fail_phase(f"\\n❌ {marker}')
        self.assertLess(repair_at, fail_at,
                        "the wrong-weekend fail_phase shadows the repair branch")

    def test_repair_branch_is_gated_to_snapshot_runs(self):
        # a REGULAR scrape must still fail loudly — it has no repair budget and
        # its links must genuinely match the weekend being read
        line = next(ln for ln in self.src.splitlines()
                    if "elif links_weekend and" in ln)
        self.assertIn("snapshots_only", line)
        self.assertIn("repair_snapshot_links", line)

    def test_repair_clears_saved_links_so_the_rebuild_runs(self):
        start = self.src.index("rebuilding the snapshot")
        block = self.src[start:start + 400]
        self.assertIn("saved_links = {}", block)

    def test_scraper_still_parses(self):
        ast.parse(self.src)

    def test_workflow_passes_the_repair_flag_to_every_snapshot_run(self):
        wf = WORKFLOW.read_text()
        self.assertIn("--repair-snapshot-links", wf)
        # the flag is set exactly when snapshots_only is true
        block = wf[wf.index('SNAPSHOT_REPAIR_FLAG=""'):]
        block = block[:block.index("python scraper.py")]
        self.assertTrue(re.search(r'snapshots_only\s*}}"?\s*=\s*"true"', block))


if __name__ == "__main__":
    unittest.main()
