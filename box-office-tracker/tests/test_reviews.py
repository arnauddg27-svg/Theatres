import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import predict as P  # noqa: E402


class ReviewWeekendFactorTests(unittest.TestCase):
    def test_no_score_is_neutral(self):
        self.assertEqual(P.review_weekend_factor(None), 1.0)
        self.assertEqual(P.review_weekend_factor(0), 1.0)

    def test_imdb_is_the_default_scale(self):
        # default column is imdb_rating (0-10): low rating trims, high boosts.
        bad = P.review_weekend_factor(4.5)
        good = P.review_weekend_factor(8.0)
        self.assertLess(bad, 1.0)          # weak WOM → trim the weekend
        self.assertGreater(good, 1.0)      # strong WOM → small boost
        self.assertLess(bad, good)         # monotonic in score

    def test_imdb_mean_is_about_neutral(self):
        # the comp-mean IMDb rating maps to ~1.0 (no shift at the average)
        mean_imdb = P._review_sunday_regression("imdb_rating")[2]
        self.assertAlmostEqual(P.review_weekend_factor(mean_imdb), 1.0, delta=0.01)

    def test_rt_audience_scale_still_supported_as_fallback(self):
        bad = P.review_weekend_factor(50, "rt_audience_score")
        good = P.review_weekend_factor(95, "rt_audience_score")
        self.assertLess(bad, good)
        self.assertAlmostEqual(
            P.review_weekend_factor(82, "rt_audience_score"), 1.0, delta=0.02)

    def test_factor_is_bounded_on_both_scales(self):
        for col, scores in (("imdb_rating", (0.5, 2, 5, 7, 10, 20, -3)),
                            ("rt_audience_score", (1, 5, 30, 70, 100, 200, -5))):
            for score in scores:
                f = P.review_weekend_factor(score, col)
                self.assertGreaterEqual(f, P.REVIEW_FACTOR_FLOOR)
                self.assertLessEqual(f, P.REVIEW_FACTOR_CAP)

    def test_effect_is_small(self):
        # reviews affect the Sunday hold only — even an awful IMDb score moves
        # the weekend total by no more than the floor (~6%).
        self.assertGreaterEqual(P.review_weekend_factor(2.0), 0.93)


class LoadReviewsDataTests(unittest.TestCase):
    def _write(self, path, rows):
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=[
                "weekend_of", "as_of_date", "movie_title", "rt_audience_score",
                "rt_critic_score", "imdb_rating", "source", "notes"])
            w.writeheader()
            w.writerows(rows)

    def test_latest_row_per_movie_and_through_date_filter(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "reviews.csv"
            self._write(path, [
                {"weekend_of": "2026-06-26", "as_of_date": "2026-06-25",
                 "movie_title": "Supergirl", "rt_audience_score": "60"},
                {"weekend_of": "2026-06-26", "as_of_date": "2026-06-26",
                 "movie_title": "Supergirl", "rt_audience_score": "65"},   # newer → wins
            ])
            orig = P.REVIEWS_CSV
            try:
                P.REVIEWS_CSV = str(path)
                # no through_date → latest row (65)
                data = P.load_reviews_data(weekend_of="2026-06-26")
                self.assertEqual(data["Supergirl"]["rt_audience_score"], "65")
                # through Thursday → the newer (Friday) row is excluded → 60
                data2 = P.load_reviews_data(weekend_of="2026-06-26", through_date="2026-06-25")
                self.assertEqual(data2["Supergirl"]["rt_audience_score"], "60")
            finally:
                P.REVIEWS_CSV = orig

    def test_absent_file_is_empty(self):
        orig = P.REVIEWS_CSV
        try:
            P.REVIEWS_CSV = "/nonexistent/reviews.csv"
            self.assertEqual(P.load_reviews_data(), {})
        finally:
            P.REVIEWS_CSV = orig


if __name__ == "__main__":
    unittest.main()
