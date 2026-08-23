"""Phase 1 partial-link preservation (audit 2026-08-23).

The per-date 90% coverage gate was all-or-nothing: one 85% show date made
fail_phase discard the ENTIRE merged link cache — every fully-covered date
included — before the save. Worse, two nested rebuild callers in the regular
lane let that SystemExit kill the whole leg with 0 rows on a night whose
post-showtime seat reads can never be re-collected.

The fix, in four locked-together parts (each pinned here):
  1. run_collect_links_async saves the merged cache (atomic, with a
     link_coverage/degraded marker) BEFORE the coverage gate; the gate still
     fails the job red so retry slots keep firing.
  2. The two regular-lane nested callers catch SystemExit; the preflight
     proceeds on a partial cache down to REGULAR_PHASE2_PARTIAL_LINK_FLOOR
     (a wall profile below that still hard-fails).
  3. collect_links_dedup_guard never skips a slot on a degraded cache
     (otherwise partial links between the guard's bar and the scraper's bar
     stop retries and the partial becomes quietly permanent).
  4. The workflow commits links on failed runs too (not cancels) and the
     dedup step validates at the scraper's own 0.90 bar.
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SRC = (ROOT / "scraper.py").read_text()
YML = (ROOT.parent / ".github" / "workflows" / "box-office-pipeline.yml").read_text()


def _func_src(name):
    i = SRC.index(f"def {name}")
    j = SRC.find("\ndef ", i + 1)
    k = SRC.find("\nasync def ", i + 1)
    ends = [x for x in (j, k) if x != -1]
    return SRC[i:min(ends)] if ends else SRC[i:]


class SaveBeforeGateTests(unittest.TestCase):
    def test_links_saved_before_coverage_gate(self):
        body = _func_src("run_collect_links_async")
        save = body.index("os.replace(_tmp_links, LINKS_JSON)")
        gate = body.index("require_phase1_coverage(fresh_report")
        self.assertLess(save, gate,
                        "the merged cache must reach disk before the gate can discard it")

    def test_save_is_atomic(self):
        body = _func_src("run_collect_links_async")
        self.assertIn('.json.tmp', body)
        self.assertIn("os.replace(", body)

    def test_degraded_marker_embedded(self):
        body = _func_src("run_collect_links_async")
        self.assertIn('links["link_coverage"]', body)
        self.assertIn('"degraded": _degraded', body)

    def test_only_one_link_save_remains(self):
        # the old post-gate save was removed; a second dump would resurrect
        # the discard-on-fail behaviour for whichever write came last
        self.assertEqual(1, SRC.count('os.replace(_tmp_links, LINKS_JSON)'))
        self.assertEqual(0, SRC.count('with open(LINKS_JSON, "w")'))


class NestedCallerGuardTests(unittest.TestCase):
    def test_ensure_preflight_catches_gate_exit(self):
        body = _func_src("ensure_phase1_links_async")
        self.assertIn("except SystemExit", body)
        self.assertIn("REGULAR_PHASE2_PARTIAL_LINK_FLOOR", body)

    def test_partial_floor_still_fails_wall_profiles(self):
        body = _func_src("ensure_phase1_links_async")
        i = body.index("REGULAR_PHASE2_PARTIAL_LINK_FLOOR:")
        self.assertIn("fail_phase", body[i:i + 600],
                      "below the floor the leg must still die loudly")

    def test_partial_proceed_is_loud(self):
        body = _func_src("ensure_phase1_links_async")
        self.assertIn("::warning::", body)

    def test_fallback_repair_catches_gate_exit(self):
        body = _func_src("repair_regular_snapshot_preserved_fallbacks_async")
        self.assertIn("except SystemExit", body)

    def test_floor_below_threshold(self):
        import re
        m = re.search(r'REGULAR_PHASE2_PARTIAL_LINK_FLOOR = _env_float\("REGULAR_PHASE2_PARTIAL_LINK_FLOOR", ([0-9.]+)', SRC)
        self.assertIsNotNone(m)
        self.assertLess(float(m.group(1)), 0.90)
        self.assertGreaterEqual(float(m.group(1)), 0.25,
                                "floor at wall-profile levels would defeat the sparse-data protections")


class DedupGuardDegradedTests(unittest.TestCase):
    def _repo(self, tmpdir, degraded):
        root = Path(tmpdir)
        data = root / "box-office-tracker" / "data"
        data.mkdir(parents=True)
        (data / "theatres-all.json").write_text(json.dumps({
            "ET": [{"name": "AMC Test 1", "slug": "amc-test-1"},
                   {"name": "AMC Test 2", "slug": "amc-test-2"}]}))
        (data / "showtime-links.json").write_text(json.dumps({
            "link_coverage": {"ratio": 0.85, "min_ratio": 0.9, "degraded": degraded},
            "theatres": {
                "AMC Test 1": {"tz": "ET", "dates": {"2026-08-21": {"links": ["x"]}}},
                "AMC Test 2": {"tz": "ET", "dates": {"2026-08-21": {"links": ["x"]}}},
            }}))
        return root

    def test_degraded_cache_never_skips(self):
        from scripts import collect_links_dedup_guard as G
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, degraded=True)
            self.assertFalse(G._fresh_theatre_link_coverage_ok(
                root, "ET", ["2026-08-21"], 0.5))

    def test_healthy_cache_can_still_skip(self):
        from scripts import collect_links_dedup_guard as G
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d, degraded=False)
            # min_ratio 0.0 isolates the degraded check from date-entry shape
            self.assertTrue(G._fresh_theatre_link_coverage_ok(
                root, "ET", ["2026-08-21"], 0.0))


class WorkflowWiringTests(unittest.TestCase):
    def test_fatal_marker_is_uploaded(self):
        # the merge-side fatal drop reads this file from the artifact; without
        # this line the whole mechanism is a production no-op
        self.assertIn(
            "box-office-tracker/data/scrape-manifest/${{ matrix.tz }}-snapshot-fatal.marker",
            YML)

    def test_links_committed_on_failure_not_cancel(self):
        i = YML.index("- name: Commit showtime links")
        block = YML[i:i + 1500]
        self.assertIn("!cancelled()", block)
        self.assertNotIn("if: success()", block)

    def test_dedup_step_uses_live_ratio_bar(self):
        i = YML.index("collect_links_dedup_guard.py")
        block = YML[max(0, i - 800):i]
        self.assertIn("PHASE1_MIN_FRESH_LINK_RATIO: '0.90'", block)


class WatchdogGuardTests(unittest.TestCase):
    WD = (ROOT / "scripts" / "capture_completeness.py").read_text()

    def test_same_day_advisory_excludes_amc_seat(self):
        # amc_seat rows for day D only ever arrive via D+1's 07Z regular
        # scrape; the first production run fired SILENT TODAY on a healthy
        # Sunday because of it
        i = self.WD.index("SILENT TODAY")
        head = self.WD[:i]
        self.assertIn('if lane == "amc_seat":', head[head.index("cap_day == today"):])

    def test_drift_guard_present(self):
        self.assertIn("capture DRIFT", self.WD)

    def test_ghost_film_guard_present(self):
        self.assertIn("ABSENT from every capture", self.WD)


class StalenessNoticeTests(unittest.TestCase):
    def test_blank_git_log_gets_a_label(self):
        # git log -1 -- <path> with no commit in the shallow window exits 0
        # with EMPTY output, so the || arm never ran and the notice was blank
        # exactly in the long-outage case it exists for
        self.assertIn('last_pred="unknown (no regeneration within the shallow fetch window)"', YML)


if __name__ == "__main__":
    unittest.main()
