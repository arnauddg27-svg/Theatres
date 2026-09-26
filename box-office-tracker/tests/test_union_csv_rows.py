import csv
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import union_csv_rows as U  # noqa: E402


def _write(path, fields, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)


def _read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


class UnionCsvRowsTest(unittest.TestCase):
    def test_parallel_runner_rows_survive_and_retries_do_not_duplicate(self):
        with tempfile.TemporaryDirectory() as td:
            base = [{"id": "1", "v": "a"}]
            main = os.path.join(td, "main.csv"); ours = os.path.join(td, "ours.csv")
            _write(main, ["id", "v"], base + [{"id": "2", "v": "other-runner"}])
            _write(ours, ["id", "v"], base + [{"id": "3", "v": "ours"}])
            self.assertEqual(1, U.union_rows(ours, main))
            self.assertEqual(["1", "2", "3"], [r["id"] for r in _read(main)])
            self.assertEqual(0, U.union_rows(ours, main))          # idempotent retry
            self.assertEqual(3, len(_read(main)))

    def test_new_columns_widen_the_target(self):
        with tempfile.TemporaryDirectory() as td:
            main = os.path.join(td, "main.csv"); ours = os.path.join(td, "ours.csv")
            _write(main, ["id"], [{"id": "1"}])
            _write(ours, ["id", "extra"], [{"id": "2", "extra": "x"}])
            self.assertEqual(1, U.union_rows(ours, main))
            rows = _read(main)
            self.assertEqual({"id": "2", "extra": "x"}, rows[-1])
            self.assertEqual("", rows[0]["extra"])


if __name__ == "__main__":
    unittest.main()
