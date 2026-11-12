"""A chain's subtitled / foreign-language listing is the same film (audit
2026-11-12: Harkins never read Godzilla Minus Zero, Cinemark lost it in
weekend 2 and every 'en-espanol-' showing)."""
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cinemark_collect as cc  # noqa: E402
import fandango_collect as fc  # noqa: E402
import harkins_collect as H  # noqa: E402

TARGETS = {fc.slugify_title(t): t for t in
           ["Godzilla Minus Zero", "Ebenezer", "The Cat in the Hat", "The Dark", "Scene"]}


class LanguageVariantTest(unittest.TestCase):
    def test_live_variants_resolve(self):
        for listed, want in (
                ("Godzilla Minus Zero [Japanese, subtitled]", "Godzilla Minus Zero"),
                ("godzilla-minus-zero-japanese-with-english-subtitles", "Godzilla Minus Zero"),
                ("en-espanol-ebenezer", "Ebenezer"),
                ("en-espanol-the-cat-in-the-hat", "The Cat in the Hat"),
                ("Scene [Tamil, subtitled]", "Scene"),
                ("Ebenezer", "Ebenezer")):
            self.assertEqual(want, fc.resolve_target_title(listed, TARGETS), listed)

    def test_other_films_do_not_resolve(self):
        for listed in ("In the Dark",                 # filler word only, no language word
                       "Ebenezer 2", "Ebenezer: The Musical",
                       "Godzilla [Japanese, subtitled]",   # 'Godzilla' is not tracked
                       "The Cat in the Hat Double Feature",
                       "Spanish Lessons", ""):
            self.assertIsNone(fc.resolve_target_title(listed, TARGETS), listed)

    def test_two_tracked_titles_fitting_is_no_match(self):
        targets = {"scene": "Scene", "scene-tamil": "Scene Tamil"}
        self.assertEqual("Scene Tamil", fc.resolve_target_title("Scene Tamil", targets))   # exact wins
        self.assertIsNone(fc.language_variant_title("scene-tamil-dubbed-hindi", {"scene-tamil": "A", "scene-hindi": "B"}))

    def test_cinemark_slug_matcher_accepts_variants(self):
        self.assertEqual("Godzilla Minus Zero", cc.match_movie_slug(
            "/movies/godzilla-minus-zero-japanese-with-english-subtitles", TARGETS))
        self.assertEqual("Ebenezer", cc.match_movie_slug("/movies/en-espanol-ebenezer", TARGETS))
        self.assertIsNone(cc.match_movie_slug("/movies/ebenezer-2", TARGETS))

    def test_harkins_reads_the_subtitled_listing_under_the_tracked_title(self):
        day = {"movies": [{"movieId": 15903, "performances": [
            {"showtimeUtc": "11/14/2026 2:35:00 AM", "showtime": "November 13, 2026 7:35 PM",
             "url": "https://harkins.com/ticketing/theatre/16/movie/HO00015903/session/600001/date/2026-11-13 19:35"}]}]}
        picked = H.pick_performances(day, {15903: "Godzilla Minus Zero [Japanese, subtitled]"}, TARGETS,
                                     datetime(2026, 11, 13, 20, 0, tzinfo=timezone.utc), "pre")
        self.assertEqual([("600001", "Godzilla Minus Zero")], [(p["sessionId"], t) for p, t in picked])


if __name__ == "__main__":
    unittest.main()
