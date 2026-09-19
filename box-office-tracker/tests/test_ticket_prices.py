"""Real AMC ticket prices from the tickets route (2026-09-19). The model stays
on its assumed prices until a recalibration; the sampler and the gate are
what this checks."""
import csv, json, os, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import seat_fetch_http as sfh  # noqa: E402
import predict as P  # noqa: E402
import sample_ticket_prices as stp  # noqa: E402

PAYLOAD = (b'2:{"when":"2026-09-20T19:30:00.000Z","prices":[{"sku":"TICKET-RS-147086776-ADULT","type":"Adult",'
           b'"price":13.19,"convenienceFee":2.69,"priceWithFees":15.88},{"sku":"TICKET-RS-147086776-CHILD","type":"Child",'
           b'"price":10.79,"convenienceFee":2.69},{"sku":"TICKET-RS-147086776-SENIOR","type":"Senior","price":11.99,'
           b'"convenienceFee":2.69}],"other":1}')


class ParsePricesTest(unittest.TestCase):
    def test_reads_adult_child_senior_fee_and_id(self):
        p = sfh.parse_rsc_prices(PAYLOAD)
        self.assertEqual((13.19, 10.79, 11.99, 2.69, "147086776"), (p["adult"], p["child"], p["senior"], p["fee"], p["showtime_id"]))
        self.assertEqual({"Adult": 13.19, "Child": 10.79, "Senior": 11.99}, p["all"])

    def test_no_price_block_means_none(self):
        self.assertIsNone(sfh.parse_rsc_prices(b'1:{"seatingLayout":{"seats":[]}}'))
        self.assertIsNone(sfh.parse_rsc_prices(b""))
        self.assertEqual("https://www.amctheatres.com/showtimes/12/tickets", sfh.tickets_url("12"))


class PickSamplesTest(unittest.TestCase):
    LINKS = {"weekend_of": "2026-09-18", "theatres": {
        "AMC A": {"tz": "ET", "dates": {
            "2026-09-17": {"movies": {"F": [{"showtime": "7:00pm", "showtime_id": "1", "format": "Laser at AMC"}]}},
            "2026-09-18": {"movies": {"F": [{"showtime": "4:00pm", "showtime_id": "2", "format": "Laser at AMC"},
                                            {"showtime": "7:00pm", "showtime_id": "3", "format": "Laser at AMC"},
                                            {"showtime": "10:00pm", "showtime_id": "4", "format": "Laser at AMC"},
                                            {"showtime": "8:00pm", "showtime_id": "5", "format": "IMAX at AMC"}]}}}},
        "AMC B": {"tz": "PT", "dates": {"2026-09-19": {"movies": {"F": [{"showtime": "9:00pm", "showtime_id": "9", "format": "Standard"}]}}}},
    }}

    def test_one_per_theatre_format_prefers_friday_middle_showtime(self):
        picks = stp.pick_samples(self.LINKS, "2026-09-18", set())
        by = {(p["theatre_name"], p["auditorium_type"]): p for p in picks}
        self.assertEqual({("AMC A", "Laser at AMC"), ("AMC A", "IMAX at AMC"), ("AMC B", "Standard")}, set(by))
        self.assertEqual(("2026-09-18", "3"), (by[("AMC A", "Laser at AMC")]["show_date"], by[("AMC A", "Laser at AMC")]["showtime_id"]))
        self.assertEqual("9", by[("AMC B", "Standard")]["showtime_id"])          # Saturday when no Friday

    def test_already_sampled_pairs_are_skipped(self):
        picks = stp.pick_samples(self.LINKS, "2026-09-18", {("AMC A", "Laser at AMC"), ("AMC B", "Standard")})
        self.assertEqual([("AMC A", "IMAX at AMC")], [(p["theatre_name"], p["auditorium_type"]) for p in picks])
        self.assertEqual([], stp.pick_samples(self.LINKS, "not-a-date", set()))


class ModelGateTest(unittest.TestCase):
    def test_reader_and_lookup(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "p.csv")
            with open(path, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=stp.FIELDS); w.writeheader()
                w.writerow({k: "" for k in stp.FIELDS} | {"weekend_of": "2026-09-18", "theatre_name": "AMC A", "auditorium_type": "Laser at AMC", "adult_price": "13.19"})
                w.writerow({k: "" for k in stp.FIELDS} | {"weekend_of": "2026-09-18", "theatre_name": "AMC A", "auditorium_type": "Standard", "adult_price": "11.49"})
                w.writerow({k: "" for k in stp.FIELDS} | {"weekend_of": "2026-09-11", "theatre_name": "AMC A", "auditorium_type": "Standard", "adult_price": "99"})
            saved = P.TICKET_PRICES_CSV
            P.TICKET_PRICES_CSV = path; P._TICKET_PRICE_CACHE.clear()
            try:
                prices = P.load_ticket_prices("2026-09-18")
                self.assertEqual({("AMC A", "Laser at AMC"): 13.19, ("AMC A", "Standard"): 11.49}, prices)
                self.assertEqual(13.19, P.sampled_adult_price({"theatre_name": "AMC A", "auditorium_type": "Laser at AMC"}, prices))
                self.assertEqual(11.49, P.sampled_adult_price({"theatre_name": "AMC A", "auditorium_type": "Dolby Cinema at AMC"}, prices), "falls back to the theatre's standard price")
                self.assertIsNone(P.sampled_adult_price({"theatre_name": "AMC Z", "auditorium_type": "Standard"}, prices))
                d = P.price_diagnostic("2026-09-18")
                self.assertEqual((2, 1), (d["pairs"], d["theatres"]))
            finally:
                P.TICKET_PRICES_CSV = saved; P._TICKET_PRICE_CACHE.clear()

    def test_relative_mode_is_level_neutral_and_clipped(self):
        prices = {("A", "Laser at AMC"): 20.0, ("B", "Laser at AMC"): 10.0, ("C", "Laser at AMC"): 16.0,
                  ("D", "Laser at AMC"): 16.0, ("E", "Laser at AMC"): 16.0, ("F", "Laser at AMC"): 40.0}
        P._RANK_MEDIAN_CACHE.clear()
        med = P.sampled_rank_medians(prices)[2]
        self.assertEqual(16.0, med)
        assumed = P.FORMAT_TICKET_PRICES[2]
        self.assertAlmostEqual(assumed * 20 / 16, P.relative_sampled_price({"theatre_name": "A", "auditorium_type": "Laser at AMC"}, prices, assumed))
        self.assertAlmostEqual(assumed, P.relative_sampled_price({"theatre_name": "C", "auditorium_type": "Laser at AMC"}, prices, assumed))
        self.assertAlmostEqual(assumed * 1.6, P.relative_sampled_price({"theatre_name": "F", "auditorium_type": "Laser at AMC"}, prices, assumed), msg="clipped")
        self.assertIsNone(P.relative_sampled_price({"theatre_name": "Z", "auditorium_type": "Laser at AMC"}, prices, assumed))
        # a rank with fewer than 5 samples has no median -> assumed price
        few = {("A", "IMAX at AMC"): 30.0}
        P._RANK_MEDIAN_CACHE.clear()
        self.assertIsNone(P.relative_sampled_price({"theatre_name": "A", "auditorium_type": "IMAX at AMC"}, few, 18.0))

    def test_default_mode_is_relative(self):
        self.assertEqual("relative", P.AMC_SAMPLED_PRICE_MODE)
        self.assertTrue(P.AMC_USE_SAMPLED_PRICES)
        row = {"theatre_name": "AMC A", "auditorium_type": "Laser at AMC", "total_seats": "100", "seats_sold": "50",
               "has_seat_map": "True", "day_of_week": "Friday", "weekend_of": "2026-09-18"}
        cal = P.load_calibration()
        base = P.estimate_theatre_daily_revenue(dict(row), cal)
        self.assertTrue(base)
