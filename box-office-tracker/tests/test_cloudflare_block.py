import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scraper  # noqa: E402


class CloudflareBlockSentinelTest(unittest.TestCase):
    def test_classifier_matches_the_hard_block_page_only(self):
        # 2026-09-02 onward: every GitHub-hosted (and VPS) seat-map navigation
        # landed on Cloudflare's hard block; a residential real browser
        # renders "Select Seats". The classifier must catch the block and
        # never the real page or a Queue-It redirect.
        self.assertTrue(scraper._is_cloudflare_block("Attention Required! | Cloudflare"))
        self.assertTrue(scraper._is_cloudflare_block("", "Sorry, you have been blocked"))
        self.assertFalse(scraper._is_cloudflare_block("Select Seats"))
        self.assertFalse(scraper._is_cloudflare_block("Attention Required!"))  # needs Cloudflare
        self.assertFalse(scraper._is_cloudflare_block("", "Loading"))

    def test_sentinel_and_abort_threshold_are_wired(self):
        self.assertIsNot(scraper.CF_BLOCK_SENTINEL, scraper.QUEUE_SENTINEL)
        self.assertIn("Cloudflare", scraper.CF_BLOCK_ISSUE)
        # Fail fast but not on a single flaky page: >= 3, default 12.
        self.assertGreaterEqual(scraper.CF_BLOCK_ABORT_AFTER, 3)
        self.assertLessEqual(scraper.CF_BLOCK_ABORT_AFTER, 30)


if __name__ == "__main__":
    unittest.main()
