import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fandango_collect as F  # noqa: E402


class RegalPriorityOrderTest(unittest.TestCase):
    def setUp(self):
        self.pool = [{"name": f"T{i}"} for i in range(10)]
        self.scores = {f"T{i}": float(i) for i in range(10)}      # T9 busiest

    def test_half_and_half_every_theatre_once(self):
        out = F.priority_order(self.pool, 0.5, self.scores, rng=random.Random(1))
        self.assertEqual(sorted(t["name"] for t in self.pool), sorted(t["name"] for t in out))
        first6 = out[:6]
        self.assertEqual(3, sum(t["_pick_mode"] == "priority" for t in first6))
        pri = [t["name"] for t in out if t["_pick_mode"] == "priority"]
        self.assertEqual("T9", pri[0])                            # busiest spent first
        self.assertEqual(sorted(pri, key=lambda n: -self.scores[n]), pri)

    def test_share_zero_or_no_history_is_all_random(self):
        self.assertTrue(all(t["_pick_mode"] == "random" for t in F.priority_order(self.pool, 0, self.scores)))
        self.assertTrue(all(t["_pick_mode"] == "random" for t in F.priority_order(self.pool, 0.5, {})))

    def test_unscored_pool_still_fills_with_random(self):
        out = F.priority_order(self.pool, 0.5, {"T3": 5.0}, rng=random.Random(2))
        self.assertEqual(10, len(out))
        self.assertEqual(["T3"], [t["name"] for t in out if t["_pick_mode"] == "priority"])


if __name__ == "__main__":
    unittest.main()
