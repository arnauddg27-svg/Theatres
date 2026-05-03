import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "box-office-pipeline.yml"
DISPATCHER = ROOT / "box-office-tracker" / "scripts" / "dispatch_box_office_pipeline.sh"
CRON_EXAMPLE = ROOT / "box-office-tracker" / "scripts" / "box-office-dispatch.cron.example"


class WorkflowReliabilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text()

    def test_all_push_loops_autostash_before_rebase(self):
        self.assertNotIn("git pull --rebase -X ours origin main", self.workflow)
        self.assertGreaterEqual(
            self.workflow.count("git pull --rebase --autostash -X ours origin main"),
            3,
        )

    def test_snapshot_scrapes_have_separate_concurrency_lane(self):
        start = self.workflow.index("concurrency:")
        end = self.workflow.index("\njobs:", start)
        block = self.workflow[start:end]

        self.assertIn("github.event.inputs.snapshots_only", block)
        self.assertIn("'snapshot'", block)
        self.assertIn("'regular'", block)

    def test_snapshot_scrapes_are_low_impact_and_staggered(self):
        scrape_start = self.workflow.index("  scrape:")
        scrape_end = self.workflow.index("  finalize:", scrape_start)
        scrape_block = self.workflow[scrape_start:scrape_end]
        start = scrape_block.index("      - name: Phase 2")
        end = scrape_block.index("      - name: Write scrape manifest", start)
        block = scrape_block[start:end]

        self.assertIn("SNAPSHOT_MAX_CONCURRENT_TABS=1", block)
        self.assertIn("SNAPSHOT_DELAY_SECONDS", block)
        self.assertIn("${{ matrix.tz }}", block)
        self.assertIn('sleep "$SNAPSHOT_DELAY_SECONDS"', block)

    def test_snapshot_scrapes_wait_for_regular_capacity_window(self):
        self.assertIn("run-name:", self.workflow)
        self.assertIn("scrape regular", self.workflow)
        self.assertIn("scrape snapshot", self.workflow)

        scrape_start = self.workflow.index("  scrape:")
        scrape_end = self.workflow.index("  finalize:", scrape_start)
        scrape_block = self.workflow[scrape_start:scrape_end]
        start = scrape_block.index("      - name: Acquire AMC lock")
        end = scrape_block.index("      - name: Phase 2", start)
        block = scrape_block[start:end]

        self.assertIn("box-office-tracker/scripts/amc_lock.py acquire", block)
        self.assertIn("GH_TOKEN: ${{ github.token }}", block)
        self.assertIn('lane="regular"', block)
        self.assertIn('lane="snapshot"', block)
        self.assertIn("--wait-seconds 21600", block)
        self.assertIn("--github-output \"$GITHUB_OUTPUT\"", block)

    def test_snapshot_capacity_guard_runs_after_dependency_install(self):
        scrape_start = self.workflow.index("  scrape:")
        scrape_end = self.workflow.index("  finalize:", scrape_start)
        scrape_block = self.workflow[scrape_start:scrape_end]

        install_pos = scrape_block.index("      - name: Install dependencies")
        guard_pos = scrape_block.index("      - name: Acquire AMC lock")
        phase2_pos = scrape_block.index("      - name: Phase 2")

        self.assertLess(install_pos, guard_pos)
        self.assertLess(guard_pos, phase2_pos)

    def test_snapshot_only_does_not_repair_phase1_links(self):
        scrape_start = self.workflow.index("  scrape:")
        scrape_end = self.workflow.index("  finalize:", scrape_start)
        scrape_block = self.workflow[scrape_start:scrape_end]
        start = scrape_block.index("      - name: Phase 2")
        end = scrape_block.index("      - name: Write scrape manifest", start)
        block = scrape_block[start:end]

        self.assertIn("ENSURE_LINKS_FLAG", block)
        self.assertIn('github.event.inputs.snapshots_only', block)
        self.assertIn('ENSURE_LINKS_FLAG=""', block)
        self.assertIn('ENSURE_LINKS_FLAG="--ensure-links"', block)
        self.assertIn("python scraper.py $ENSURE_LINKS_FLAG", block)
        self.assertNotIn("python scraper.py --ensure-links", block)

    def test_scrape_matrix_uploads_artifacts_instead_of_pushing(self):
        start = self.workflow.index("  scrape:")
        end = self.workflow.index("  finalize:", start)
        block = self.workflow[start:end]

        self.assertNotIn("git commit", block)
        self.assertNotIn("git push", block)
        self.assertIn("Write scrape manifest", block)
        self.assertIn("Upload scrape artifact", block)
        self.assertIn("SNAPSHOT_FLAG", block)
        self.assertIn("--pre-reservation-snapshots", block)
        self.assertIn("--snapshots-only", block)
        self.assertIn("if: always()", block)
        self.assertIn("scrape-${{ matrix.tz }}-${{ github.run_id }}-${{ github.run_attempt }}", block)
        self.assertIn("if-no-files-found: error", block)
        self.assertIn("box-office-tracker/data/scrape-manifest/${{ matrix.tz }}.env", block)
        self.assertIn("box-office-tracker/data/seat-counts.csv", block)
        self.assertIn("box-office-tracker/data/pre-reservation-snapshots.csv", block)
        self.assertNotIn("box-office-tracker/data/run-log.md", block)
        self.assertIn("box-office-tracker/data/run-logs", block)
        self.assertIn("box-office-tracker/data/theatre-counts.json", block)

    def test_snapshot_only_runs_bypass_normal_scrape_dedup_guard(self):
        scrape_start = self.workflow.index("  scrape:")
        scrape_end = self.workflow.index("  finalize:", scrape_start)
        scrape_block = self.workflow[scrape_start:scrape_end]
        start = scrape_block.index("      - name: Dedup guard")
        end = scrape_block.index("      - name: Install dependencies", start)
        block = scrape_block[start:end]

        self.assertIn("scripts/scrape_dedup_guard.py", block)
        self.assertIn("--snapshots-only \"${{ github.event.inputs.snapshots_only }}\"", block)
        self.assertNotIn("pattern=\"data: box office", block)

    def test_finalize_downloads_merges_and_commits_once(self):
        start = self.workflow.index("  finalize:")
        end = self.workflow.index("  calibrate:", start)
        block = self.workflow[start:end]

        self.assertIn("Download scrape artifacts", block)
        self.assertIn("uses: actions/download-artifact@v4", block)
        self.assertNotIn("continue-on-error: true", block)
        self.assertIn("pattern: scrape-*", block)
        self.assertIn("python scripts/merge_scrape_artifacts.py data/scrape-artifacts", block)
        self.assertIn("--summary-file /tmp/box-office-merge-summary.json", block)
        self.assertIn("git status --short --", block)
        self.assertIn("box-office-tracker/data/seat-counts.csv", block)
        self.assertIn("box-office-tracker/data/pre-reservation-snapshots.csv", block)
        self.assertIn("box-office-tracker/data/polymarket-markets.csv", block)
        self.assertIn("box-office-tracker/data/run-logs", block)
        self.assertIn("scripts/stage_finalize_outputs.py", block)
        self.assertNotIn("git add box-office-tracker/data/seat-counts.csv \\", block)
        self.assertIn("data: box office scrape merge + predictions", block)

    def test_all_amc_touching_jobs_use_lock_and_release_it(self):
        collect_start = self.workflow.index("  collect-links:")
        scrape_start = self.workflow.index("  scrape:")
        finalize_start = self.workflow.index("  finalize:")
        collect_block = self.workflow[collect_start:scrape_start]
        scrape_block = self.workflow[scrape_start:finalize_start]

        for block in (collect_block, scrape_block):
            self.assertIn("      - name: Acquire AMC lock", block)
            self.assertIn("scripts/amc_lock.py acquire", block)
            self.assertIn("      - name: Release AMC lock", block)
            self.assertIn("scripts/amc_lock.py release", block)
            self.assertIn("steps.amc_lock.outputs.acquired == 'true'", block)

    def test_scrape_matrix_is_serialized_for_strict_zero_amc_overlap(self):
        scrape_start = self.workflow.index("  scrape:")
        finalize_start = self.workflow.index("  finalize:", scrape_start)
        scrape_block = self.workflow[scrape_start:finalize_start]

        self.assertIn("max-parallel: 1", scrape_block)

    def test_collect_links_retries_once_under_same_lock(self):
        collect_start = self.workflow.index("  collect-links:")
        scrape_start = self.workflow.index("  scrape:")
        collect_block = self.workflow[collect_start:scrape_start]
        phase_start = collect_block.index("      - name: Phase 1")
        release_start = collect_block.index("      - name: Release AMC lock", phase_start)
        phase_block = collect_block[phase_start:release_start]

        self.assertIn("retrying once under the same AMC lock", phase_block)
        self.assertEqual(2, phase_block.count("python3 scraper.py --collect-links"))

    def test_repo_contains_vps_dispatcher_for_snapshot_schedule(self):
        dispatcher = DISPATCHER.read_text()
        cron = CRON_EXAMPLE.read_text()

        self.assertIn("gh workflow run", dispatcher)
        self.assertIn("WORKFLOW_FILE:-box-office-pipeline.yml", dispatcher)
        self.assertIn("GH_TOKEN_FILE", dispatcher)
        self.assertIn("pre_reservation_snapshots=true", dispatcher)
        self.assertIn("snapshots_only=true", dispatcher)
        self.assertIn("snapshot", cron)
        self.assertIn('"$DISPATCH" snapshot', cron)
        self.assertIn("GH_TOKEN_FILE=/root/box-office-dispatch/.env", cron)
        self.assertIn("git -C \"$REPO_DIR\" pull --ff-only origin main", cron)
        self.assertIn("30 18", cron)
        self.assertNotIn("30 22", cron)
        self.assertNotIn("30 2", cron)
        self.assertIn("phase=scrape", cron)
        self.assertIn("phase=collect-links", cron)
        self.assertNotIn(" MT ", cron)
        self.assertNotIn("4-0", cron)
        self.assertNotIn("5-1", cron)


if __name__ == "__main__":
    unittest.main()
