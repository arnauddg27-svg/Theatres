"""Guard: nothing may read a canonical CSV without also reading its archive.

Settled weekends rotate out of seat-counts.csv / pre-reservation-snapshots.csv
into per-weekend gzip archives so the live files stay under GitHub's 100MB push
limit. A reader that opens the live CSV directly therefore sees only the two
most recent weekends and silently loses all history — no exception, no log.

That is exactly how `load_cross_chain_occupancy` broke: it opened SEAT_CSV
directly, so the day weekend 2026-07-10 rotated, its AMC side vanished, the
per-film cross-chain share fell back to the fleet prior, and the canonical
Thursday backtest drifted 18.1% -> 21.2% MAE undetected for days.

Readers must go through the archive-aware row-source helpers. This test fails
on any NEW direct open so the bug class cannot silently return.
"""
import ast
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CANONICAL = {"SEAT_CSV", "PRE_RESERVATION_CSV"}

# Functions allowed to open a canonical CSV directly, and why.
ALLOWED = {
    # the archive-aware helpers themselves — they yield live + archive readers
    "_seat_row_sources",
    "_pre_reservation_row_sources",
    "_snapshot_readers",
    # "which weekend is newest?" probes: the newest weekend is by definition
    # still live, never archived, so scanning the live file is correct here
    "load_seat_data",
    "load_pre_reservation_data",
}


def _direct_opens(path):
    """[(function_name, lineno)] for open(<CANONICAL>) calls in `path`."""
    tree = ast.parse(path.read_text())
    scopes = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            scopes.append((node.lineno, node.end_lineno or node.lineno, node.name))

    def enclosing(lineno):
        best = None
        for start, end, name in scopes:
            if start <= lineno <= end and (best is None or start > best[0]):
                best = (start, name)
        return best[1] if best else "<module>"

    hits = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "open" and node.args):
            continue
        arg = node.args[0]
        name = (arg.id if isinstance(arg, ast.Name)
                else arg.attr if isinstance(arg, ast.Attribute) else None)
        if name in CANONICAL:
            hits.append((enclosing(node.lineno), node.lineno))
    return hits


class ArchiveAwareReaderTests(unittest.TestCase):
    def _check(self, path):
        offenders = [(fn, ln) for fn, ln in _direct_opens(path)
                     if fn not in ALLOWED]
        self.assertEqual(
            [], offenders,
            f"{path.name} opens a canonical CSV outside the archive-aware "
            f"helpers at {offenders}. Use _seat_row_sources(weekend_of) / "
            f"_pre_reservation_row_sources(...) instead, or add the function "
            f"to ALLOWED with a reason if the live file really is correct.")

    def test_predict_has_no_unsanctioned_direct_reads(self):
        self._check(ROOT / "predict.py")

    def test_analysis_scripts_have_no_unsanctioned_direct_reads(self):
        # scraper.py is excluded on purpose: it WRITES/appends and dedupes
        # against the live file, which is the correct target for collection.
        for script in sorted((ROOT / "scripts").glob("*.py")):
            with self.subTest(script=script.name):
                self._check(script)

    def test_guard_detects_a_planted_offender(self):
        # the guard must actually catch the pattern it claims to catch
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "bad.py"
            bad.write_text("def sneaky():\n    with open(SEAT_CSV) as f:\n        pass\n")
            self.assertEqual([("sneaky", 2)], _direct_opens(bad))


if __name__ == "__main__":
    unittest.main()
