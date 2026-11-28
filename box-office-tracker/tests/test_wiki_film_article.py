import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

import wiki_film_article as A  # noqa: E402


def fact(title, film=True, years=(), us=True, imdb=()):
    return {"item": "Q1", "title": title, "film": film, "us": us,
            "years": list(years), "imdb": list(imdb)}


def binding(item, title, film="true", us="true", date=None, imdb=None):
    b = {"item": {"value": f"http://www.wikidata.org/entity/{item}"},
         "title": {"value": title}, "film": {"value": film}, "us": {"value": us}}
    if date:
        b["date"] = {"value": date}
    if imdb:
        b["imdb"] = {"value": imdb}
    return b


class NameTests(unittest.TestCase):
    def test_imdb_id_from_a_link(self):
        self.assertEqual("tt8332922", A.imdb_id("https://www.imdb.com/title/tt8332922/"))
        self.assertEqual("", A.imdb_id("https://www.rottentomatoes.com/m/beast_2022"))
        self.assertEqual("", A.imdb_id(None))

    def test_base_title_drops_only_the_disambiguator(self):
        self.assertEqual("Beast", A.base_title("Beast (2022 American film)"))
        self.assertEqual("Moana", A.base_title("Moana (2026)"))
        self.assertEqual("Thunderbolts*", A.base_title("Thunderbolts*"))
        self.assertEqual([2022], A.disambiguator_years("Smile (2022 film)"))
        self.assertEqual([], A.disambiguator_years("28 Years Later"))
        self.assertEqual([], A.disambiguator_years("2012 (film)"))


class ImdbArticleTests(unittest.TestCase):
    def test_the_item_holding_the_id_decides(self):
        facts = {"tt13223398": [fact("Beast (2022 American film)")]}
        self.assertEqual("Beast (2022 American film)", A.article_for_imdb("tt13223398", facts))

    def test_series_page_sharing_the_id_is_not_the_film(self):
        facts = {"tt17505010": [fact("Horizon: An American Saga", film=False),
                                fact("Horizon: An American Saga – Chapter 1")]}
        self.assertEqual("Horizon: An American Saga – Chapter 1",
                         A.article_for_imdb("tt17505010", facts))

    def test_unknown_or_ambiguous_id_gives_nothing(self):
        self.assertIsNone(A.article_for_imdb("tt15679400", {}))
        two = {"tt1": [fact("A (2020 film)"), fact("A (2021 film)")]}
        self.assertIsNone(A.article_for_imdb("tt1", two))

    def test_a_wrong_id_cannot_bring_in_another_film(self):
        # reviews.csv, 2026-11: the id matched for "Ramayana: Rise of A Legend".
        facts = {"tt27920880": [fact("Villeneuve: The Rise of a Legend", years=[2026])]}
        self.assertIsNone(A.article_for_imdb("tt27920880", facts, "Ramayana: Rise of A Legend", 2026))
        old = {"tt0052271": [fact("No Time to Die (1958 film)", years=[1958])]}
        self.assertIsNone(A.article_for_imdb("tt0052271", old, "No Time to Die", 2021))

    def test_a_right_id_survives_a_differently_worded_title(self):
        for ours, theirs, year in (
                ("F9: The Fast Saga", "F9 (film)", 2021),
                ("F1: The Movie", "F1 (film)", 2025),
                ("Joker: Folie a Deux", "Joker: Folie à Deux", 2024),
                ("Guardians of the Galaxy Vol 3", "Guardians of the Galaxy Vol. 3", 2023),
                ("Runner", "Runner (2026 American film)", 2026),
                ("Talk to Me", "Talk to Me (2022 film)", 2023)):
            facts = {"tt1": [fact(theirs, years=[year])]}
            self.assertEqual(theirs, A.article_for_imdb("tt1", facts, ours, year))

    def test_query_rows_group_by_item(self):
        rows = [binding("Q5", "M3GAN", date="2022-12-07T00:00:00Z", imdb="tt8760708"),
                binding("Q5", "M3GAN", date="2023-01-06T00:00:00Z", imdb="tt8760708"),
                binding("Q9", "M3GAN (film series)", film="false", imdb="tt8760708")]
        got = A.facts_for_imdb_ids(["tt8760708"], fetch=lambda q: rows)
        self.assertEqual("M3GAN", A.article_for_imdb("tt8760708", got))
        self.assertEqual([2022, 2023], [f for f in got["tt8760708"] if f["film"]][0]["years"])


class SearchHitTests(unittest.TestCase):
    """The nine wrong articles found in historical-comps.csv on 2026-11-27."""

    def pick(self, title, year, facts):
        return A.choose_from_hits(title, year, [f["title"] for f in facts],
                                  {f["title"]: f for f in facts})

    def test_a_title_inside_another_title_is_another_film(self):
        self.assertEqual("Beast (2022 American film)", self.pick("Beast", 2022, [
            fact("The Sea Beast (2022 film)", years=[2022]),
            fact("Beast (2022 Indian film)", years=[2022], us=False),
            fact("Beast (2022 American film)", years=[2022])]))
        self.assertEqual("Longlegs", self.pick("Longlegs", 2024, [
            fact("Daddy Longlegs (2009 film)", years=[2009]), fact("Longlegs", years=[2024])]))
        self.assertIsNone(self.pick("Longlegs", 2024, [
            fact("Daddy Longlegs (2009 film)", years=[2009])]))

    def test_a_sequel_number_is_not_a_year(self):
        self.assertEqual("The Accountant 2", self.pick("The Accountant 2", 2025, [
            fact("The Accountant (2016 film)", years=[2016]),
            fact("The Accountant 2", years=[2025])]))
        self.assertEqual("Nobody 2", self.pick("Nobody 2", 2025, [
            fact("Nobody (2025 film)", years=[2025]), fact("Nobody 2", years=[2025])]))
        self.assertEqual("Smile 2", self.pick("Smile 2", 2024, [
            fact("Smile (2022 film)", years=[2022]), fact("Smile 2", years=[2024])]))

    def test_an_older_film_of_the_same_name_is_refused(self):
        self.assertEqual("No Time to Die", self.pick("No Time to Die", 2021, [
            fact("No Time to Die (1958 film)", years=[1958], us=False),
            fact("No Time to Die", years=[2021], us=False)]))
        self.assertIsNone(self.pick("No Time to Die", 2021, [
            fact("No Time to Die (1958 film)", years=[1958])]))

    def test_series_lists_and_soundtracks_are_not_films(self):
        self.assertEqual("M3GAN", self.pick("M3GAN", 2023, [
            fact("M3GAN (film series)", film=False), fact("M3GAN", years=[2022, 2023])]))
        self.assertEqual("Killers of the Flower Moon", self.pick("Killers of the Flower Moon", 2023, [
            fact("List of accolades received by Killers of the Flower Moon (film)", film=False),
            fact("Killers of the Flower Moon", years=[2023])]))
        self.assertIsNone(self.pick("The Hunger Games: Sunrise on the Reaping", 2026, [
            fact("The Hunger Games: Sunrise on the Reaping (soundtrack)", film=False, years=[2026])]))

    def test_festival_premiere_the_year_before_still_fits(self):
        self.assertEqual("Talk to Me (2022 film)", self.pick("Talk to Me", 2023, [
            fact("Talk to Me (2022 film)", years=[2022, 2023], us=False),
            fact("Talk to Me (2007 film)", years=[2007])]))

    def test_punctuation_and_our_own_disambiguator_do_not_matter(self):
        self.assertEqual("Focker-in-Law", self.pick("Focker In-Law", 2026, [fact("Focker-in-Law")]))
        self.assertEqual("Moana (2026 film)", self.pick("Moana (2026)", 2026, [
            fact("Moana (2016 film)", years=[2016]), fact("Moana (2026 film)", years=[2026])]))

    def test_leading_article_and_accents_do_not_matter(self):
        self.assertEqual("The Runner (2026 film)", self.pick("Runner", 2026, [
            fact("The Runner (2026 film)", years=[2026])]))
        self.assertEqual("Joker: Folie à Deux", self.pick("Joker: Folie a Deux", 2024, [
            fact("Joker: Folie à Deux", years=[2024])]))
        self.assertIsNone(self.pick("Beast", 2022, [fact("The Sea Beast (2022 film)", years=[2022])]))

    def test_a_hit_wikidata_does_not_know_is_refused(self):
        self.assertIsNone(A.choose_from_hits("Beast", 2022, ["Beast (2022 American film)"], {}))

    def test_two_domestic_films_of_one_title_and_year_stay_unresolved(self):
        self.assertIsNone(self.pick("Twins", 2025, [
            fact("Twins (2025 film)", years=[2025]), fact("Twins (2025 drama film)", years=[2025])]))


class ResolveTests(unittest.TestCase):
    def test_imdb_first_and_search_only_as_fallback(self):
        calls = []

        def fetch(query):
            calls.append(query)
            if "VALUES ?imdb" in query:
                return [binding("Q7", "Longlegs", date="2024-07-12T00:00:00Z", imdb="tt23468450")]
            return []

        self.assertEqual(("Longlegs", "imdb"), A.resolve(
            "Longlegs", 2024, "https://www.imdb.com/title/tt23468450/",
            ["Daddy Longlegs (2009 film)"], fetch=fetch))
        self.assertEqual(1, len(calls))

    def test_search_fallback_when_wikidata_lacks_the_id(self):
        def fetch(query):
            if "VALUES ?imdb" in query:
                return []
            return [binding("Q3", "Knock at the Cabin", date="2023-02-03T00:00:00Z")]

        self.assertEqual(("Knock at the Cabin", "search-verified"), A.resolve(
            "Knock at the Cabin", 2023, "tt15679400", ["Knock at the Cabin"], fetch=fetch))

    def test_nothing_verified_is_nothing(self):
        self.assertEqual((None, ""), A.resolve("Beast", 2022, "", [], fetch=lambda q: []))
        self.assertEqual((None, ""), A.resolve(
            "Beast", 2022, "", ["The Sea Beast (2022 film)"],
            fetch=lambda q: [binding("Q1", "The Sea Beast (2022 film)", date="2022-07-08T00:00:00Z")]))


if __name__ == "__main__":
    unittest.main()


class PageNameHistoryTests(unittest.TestCase):
    """Tarot (2024): the name it had in release week now leads elsewhere."""
    REVISIONS = [
        {"timestamp": "2024-07-23T18:02:11Z",
         "comment": "Someone moved page [[Tarot (2024 film)]] to [[Tarot (2024 American film)]]: another 2024 film"},
        {"timestamp": "2023-12-18T09:00:00Z",
         "comment": "Someone moved page [[Draft:Horrorscope (film)]] to [[Horrorscope (film)]]"},
        {"timestamp": "2024-01-30T12:00:00Z",
         "comment": "Someone moved page [[Horrorscope (film)]] to [[Tarot (2024 film)]] over redirect"},
        {"timestamp": "2024-05-03T12:00:00Z", "comment": "/* Box office */ opening day"},
        {"timestamp": "2024-05-04T12:00:00Z"},
    ]

    def test_moves_in_order_without_draft_names(self):
        self.assertEqual([("2023-12-18", "Horrorscope (film)"),
                          ("2024-01-30", "Tarot (2024 film)"),
                          ("2024-07-23", "Tarot (2024 American film)")],
                         A.title_history(self.REVISIONS))

    def test_a_page_never_moved_has_no_history(self):
        self.assertEqual([], A.title_history([{"timestamp": "2024-01-01T00:00:00Z", "comment": "copyedit"}]))
        self.assertEqual({"Longlegs": ""}, A.past_names("Longlegs", "2024-07-11", lambda a: []))

    def test_names_held_by_the_release_week(self):
        got = A.past_names("Tarot (2024 American film)", "2024-05-02", lambda a: self.REVISIONS)
        self.assertEqual({"Horrorscope (film)": "2023-12-18", "Tarot (2024 film)": "2024-01-30"}, got)
        later = A.past_names("Tarot (2024 American film)", "2024-08-01", lambda a: self.REVISIONS)
        self.assertEqual("2024-07-23", later["Tarot (2024 American film)"])

    def test_a_name_taken_later_does_not_count_earlier(self):
        history = [("", "Black Bag (film)"), ("2025-03-12", "Black Bag")]
        self.assertEqual({"Black Bag (film)": ""}, A.names_through(history, "2025-03-11"))
        self.assertEqual({"Black Bag (film)": "", "Black Bag": "2025-03-12"},
                         A.names_through(history, "2025-03-13"))
