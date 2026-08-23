import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "box-office-pipeline.yml"
SCHEDULER_WORKFLOW = ROOT / ".github" / "workflows" / "box-office-scheduler.yml"
SCHEDULER_SCRIPT = ROOT / "box-office-tracker" / "scripts" / "schedule_box_office_pipeline.py"
DISPATCHER = ROOT / "box-office-tracker" / "scripts" / "dispatch_box_office_pipeline.sh"
CRON_EXAMPLE = ROOT / "box-office-tracker" / "scripts" / "box-office-dispatch.cron.example"


class WorkflowReliabilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text()
        cls.scheduler = SCHEDULER_WORKFLOW.read_text()
        cls.scheduler_script = SCHEDULER_SCRIPT.read_text()

    def test_all_push_loops_autostash_before_rebase(self):
        self.assertNotIn("git pull --rebase -X ours origin main", self.workflow)
        self.assertGreaterEqual(
            self.workflow.count("git pull --rebase --autostash origin main"),
            3,
        )

    def test_no_push_loop_uses_ours_strategy(self):
        """-X ours on a REBASE silently discards the commit being replayed.

        `ours` is upstream during a rebase, so a conflicting hunk keeps
        origin/main and drops the local patch. Confirmed live 2026-08-07: the
        CT collect-links leg committed 9,196 insertions and the rebase logged
        `dropping <sha> -- patch contents already upstream`, then exited 0 —
        a green run over a lost weekend of theatre links. Without the strategy
        option a real conflict stops the rebase and the step fails loudly.
        """
        for line in self.workflow.splitlines():
            if "git pull --rebase" in line:
                self.assertNotIn("-X ours", line, f"push loop still discards data: {line.strip()}")
                self.assertNotIn("-X theirs", line, f"push loop overwrites upstream: {line.strip()}")

    def test_finalize_has_a_vps_independent_rotation_net(self):
        """Rotation must not depend solely on the self-hosted VPS runner.

        rotate_pre_reservation_snapshots.py is invoked from the weekly
        `calibrate` job (runs-on: [self-hosted, vps]). If that droplet is
        offline the live CSVs grow ~25MB/weekend until they cross GitHub's
        100MB push limit — the failure that bricked the snapshot lane on
        2026-07-12. finalize runs on ubuntu-latest and carries a size-gated
        fallback so the cliff cannot return while the VPS is down.
        """
        start = self.workflow.index("  finalize:")
        end = self.workflow.index("\n  calibrate:", start)
        block = self.workflow[start:end]
        self.assertIn("rotate_pre_reservation_snapshots.py", block)
        self.assertIn("ubuntu-latest", block)

    def test_scrape_matrix_stays_sequential_for_the_lock_self_break(self):
        """amc_lock breaks a lock whose holder run id equals the CURRENT run.

        That is only safe because the scrape matrix is max-parallel: 1, so no
        sibling leg can hold the lock while another executes — a holder
        carrying my own run id must be a FINISHED earlier leg. The invariant
        lives in this workflow file, but the code relying on it is in
        scripts/amc_lock.py and cannot see it. Raising max-parallel (the
        obvious optimisation now that each leg gets its own IP) would let leg
        CT break leg ET's LIVE lock and double-run AMC, corrupting data. Assert
        it here so that change fails loudly instead.
        """
        start = self.workflow.index("  scrape:")
        end = self.workflow.index("  finalize:", start)
        block = self.workflow[start:end]
        self.assertIn("max-parallel: 1", block)
        self.assertIn("current_run_id", SCHEDULER_SCRIPT.parent.joinpath(
            "amc_lock.py").read_text())

    def test_snapshot_scrapes_have_separate_concurrency_lane(self):
        start = self.workflow.index("concurrency:")
        end = self.workflow.index("\njobs:", start)
        block = self.workflow[start:end]

        self.assertIn("github.event.inputs.snapshots_only", block)
        self.assertIn("'snapshot'", block)
        self.assertIn("'regular'", block)

    def test_snapshot_scrapes_have_dedicated_capacity_without_extra_stagger(self):
        scrape_start = self.workflow.index("  scrape:")
        scrape_end = self.workflow.index("  finalize:", scrape_start)
        scrape_block = self.workflow[scrape_start:scrape_end]

        self.assertIn("SNAPSHOT_MAX_CONCURRENT_TABS=3", scrape_block)
        self.assertNotIn("SNAPSHOT_DELAY_SECONDS", scrape_block)
        self.assertNotIn("Stagger snapshot-only matrix leg", scrape_block)

    def test_snapshot_scrapes_have_remaining_weekend_top_theatre_runtime_budget(self):
        scrape_start = self.workflow.index("  scrape:")
        scrape_end = self.workflow.index("  finalize:", scrape_start)
        scrape_block = self.workflow[scrape_start:scrape_end]
        phase_start = scrape_block.index("      - name: Phase 2")
        phase_end = scrape_block.index("      - name: Release AMC lock", phase_start)
        phase_block = scrape_block[phase_start:phase_end]

        self.assertIn("timeout-minutes: 190", phase_block)
        self.assertIn("PHASE2_DEADLINE_SEC=9000", phase_block)
        self.assertIn("SNAPSHOT_MAX_CONCURRENT_TABS=3", phase_block)
        self.assertIn("SNAPSHOT_TOP_THEATRE_CAP=200", phase_block)
        self.assertIn("SNAPSHOT_MIN_THEATRE_COVERAGE_RATIO=0.80", phase_block)
        self.assertIn("PHASE1_MIN_FRESH_LINK_RATIO=0.90", phase_block)
        # Snapshot scrape + targeted link repair must fit the step timeout:
        # 9000s + 1800s = 180m <= 190m. The job-level chain (lock wait + step
        # + buffers <= 360m) is asserted by test_amc_lock_wait_budget_fits_job_timeouts.
        self.assertIn("PHASE1_DEADLINE_SEC=1800", phase_block)

    def test_regular_scrapes_have_full_day_runtime_budget(self):
        scrape_start = self.workflow.index("  scrape:")
        scrape_end = self.workflow.index("  finalize:", scrape_start)
        scrape_block = self.workflow[scrape_start:scrape_end]
        phase_start = scrape_block.index("      - name: Phase 2")
        phase_end = scrape_block.index("      - name: Release AMC lock", phase_start)
        phase_block = scrape_block[phase_start:phase_end]

        self.assertIn("REGULAR_PHASE2_MIN_DEADLINE_SEC=9000", phase_block)
        self.assertIn("REGULAR_PHASE2_MAX_DEADLINE_SEC=10800", phase_block)
        self.assertIn("PHASE2_THEATRE_TIMEOUT_SEC=180", phase_block)
        self.assertIn("Regular lane:", phase_block)

    def test_regular_scrapes_have_full_day_runtime_budget(self):
        scrape_start = self.workflow.index("  scrape:")
        scrape_end = self.workflow.index("  finalize:", scrape_start)
        scrape_block = self.workflow[scrape_start:scrape_end]
        phase_start = scrape_block.index("      - name: Phase 2")
        phase_end = scrape_block.index("      - name: Release AMC lock", phase_start)
        phase_block = scrape_block[phase_start:phase_end]

        self.assertIn("REGULAR_PHASE2_MIN_DEADLINE_SEC=9000", phase_block)
        self.assertIn("REGULAR_PHASE2_MAX_DEADLINE_SEC=10800", phase_block)
        self.assertIn("PHASE2_THEATRE_TIMEOUT_SEC=180", phase_block)
        self.assertIn("Regular lane:", phase_block)

    def test_snapshot_scrapes_go_directly_from_install_to_amc_lock(self):
        scrape_start = self.workflow.index("  scrape:")
        scrape_end = self.workflow.index("  finalize:", scrape_start)
        scrape_block = self.workflow[scrape_start:scrape_end]

        install_pos = scrape_block.index("      - name: Install dependencies")
        lock_pos = scrape_block.index("      - name: Acquire AMC lock")
        phase2_pos = scrape_block.index("      - name: Phase 2")

        self.assertLess(install_pos, lock_pos)
        self.assertLess(lock_pos, phase2_pos)
        self.assertNotIn("sleep \"$SNAPSHOT_DELAY_SECONDS\"", scrape_block[install_pos:lock_pos])

    def test_snapshot_scrapes_wait_for_regular_capacity_window(self):
        self.assertIn("run-name:", self.workflow)
        self.assertIn("github.event.inputs.schedule_slot", self.workflow)
        self.assertIn("box office scheduled {0}", self.workflow)
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
        self.assertIn("--wait-seconds 7200", block)
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

    def test_regular_scrapes_repair_phase1_links_and_snapshots_use_targeted_repair(self):
        scrape_start = self.workflow.index("  scrape:")
        scrape_end = self.workflow.index("  finalize:", scrape_start)
        scrape_block = self.workflow[scrape_start:scrape_end]
        start = scrape_block.index("      - name: Phase 2")
        end = scrape_block.index("      - name: Write scrape manifest", start)
        block = scrape_block[start:end]

        self.assertIn('ENSURE_LINKS_FLAG="--ensure-links"', block)
        self.assertIn('ENSURE_LINKS_FLAG=""', block)
        self.assertIn("SNAPSHOT_REPAIR_LINKS=1", block)
        self.assertIn('SNAPSHOT_REPAIR_FLAG="--repair-snapshot-links"', block)
        self.assertIn("PHASE1_DEADLINE_SEC=2400", block)
        self.assertIn("PHASE1_MAX_THEATRE_DATE_VISITS=500", block)
        self.assertIn("phase1-repair-budget=${PHASE1_DEADLINE_SEC}s", block)
        self.assertIn('if [ "${{ github.event.inputs.snapshots_only }}" = "true" ]; then', block)
        self.assertIn(
            "python scraper.py $FORCE_FLAG $TEST_FLAG $SNAPSHOT_FLAG $SNAPSHOT_REPAIR_FLAG $ENSURE_LINKS_FLAG",
            block,
        )

    def test_scrape_matrix_uploads_artifacts_instead_of_pushing(self):
        start = self.workflow.index("  scrape:")
        end = self.workflow.index("  finalize:", start)
        block = self.workflow[start:end]

        self.assertNotIn("git commit", block)
        self.assertNotIn("git push", block)
        self.assertIn("Write scrape manifest", block)
        self.assertIn("snapshots_only=${{ github.event.inputs.snapshots_only }}", block)
        self.assertIn("pre_reservation_snapshots=${{ github.event.inputs.pre_reservation_snapshots }}", block)
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

    def test_collect_links_dedup_guard_requires_canonical_link_file(self):
        collect_start = self.workflow.index("  collect-links:")
        scrape_start = self.workflow.index("  scrape:")
        collect_block = self.workflow[collect_start:scrape_start]
        start = collect_block.index("      - name: Dedup guard")
        end = collect_block.index("      - name: Install dependencies", start)
        block = collect_block[start:end]

        self.assertIn("scripts/collect_links_dedup_guard.py", block)
        self.assertIn("--tz \"${{ github.event.inputs.tz_group }}\"", block)
        self.assertIn("--force \"${{ github.event.inputs.force }}\"", block)
        self.assertNotIn("git log --since", block)
        self.assertNotIn("pattern=\"data: box office", block)

    def test_collect_links_runs_on_github_hosted_runner(self):
        collect_start = self.workflow.index("  collect-links:")
        scrape_start = self.workflow.index("  scrape:")
        collect_block = self.workflow[collect_start:scrape_start]

        self.assertIn("runs-on: ubuntu-latest", collect_block)
        self.assertNotIn("runs-on: [self-hosted, vps]", collect_block)
        self.assertNotIn("/home/gha/actions-runner", collect_block)

    def test_collect_links_resyncs_shared_cache_after_acquiring_lock(self):
        collect_start = self.workflow.index("  collect-links:")
        scrape_start = self.workflow.index("  scrape:")
        collect_block = self.workflow[collect_start:scrape_start]
        lock_pos = collect_block.index("      - name: Acquire AMC lock")
        resync_pos = collect_block.index("      - name: Re-sync shared Phase 1 cache after lock acquisition")
        phase_pos = collect_block.index("      - name: Phase 1")
        resync_block = collect_block[resync_pos:phase_pos]

        self.assertLess(lock_pos, resync_pos)
        self.assertLess(resync_pos, phase_pos)
        self.assertIn("steps.amc_lock.outputs.acquired == 'true'", resync_block)
        self.assertIn("git fetch origin main", resync_block)
        self.assertIn("git reset --hard origin/main", resync_block)

    def test_collect_links_commits_shared_cache_before_releasing_lock(self):
        collect_start = self.workflow.index("  collect-links:")
        scrape_start = self.workflow.index("  scrape:")
        collect_block = self.workflow[collect_start:scrape_start]
        phase_pos = collect_block.index("      - name: Phase 1")
        commit_pos = collect_block.index("      - name: Commit showtime links")
        release_pos = collect_block.index("      - name: Release AMC lock")
        upload_pos = collect_block.index("      - name: Upload Phase 1 logs")
        commit_block = collect_block[commit_pos:release_pos]

        self.assertLess(phase_pos, commit_pos)
        self.assertLess(commit_pos, release_pos)
        self.assertLess(release_pos, upload_pos)
        self.assertIn("steps.amc_lock.outputs.acquired == 'true'", commit_block)
        self.assertIn("git push", commit_block)

    def test_finalize_downloads_merges_and_commits_once(self):
        start = self.workflow.index("  finalize:")
        end = self.workflow.index("  calibrate:", start)
        block = self.workflow[start:end]

        self.assertIn("Download scrape artifacts", block)
        self.assertIn("uses: actions/download-artifact@v4", block)
        # The core finalize write path (merge -> predict -> commit -> push) must
        # fail loudly. Only the best-effort word-of-mouth fetches (Rotten
        # Tomatoes reviews + Wikipedia anticipation), which run before predict,
        # may swallow errors so a flaky external API can't block the prediction
        # commit. Assert nothing from predict onward is continue-on-error, and
        # that the only such steps are those two known fetches.
        self.assertNotIn(
            "continue-on-error: true",
            block[block.index("run: python predict.py"):],
        )
        # 3 = the two best-effort word-of-mouth fetches (RT + Wikipedia) plus
        # the capture-completeness watchdog, each deliberately unable to fail
        # the merge-and-commit path
        self.assertEqual(block.count("continue-on-error: true"), 3)
        self.assertIn("pattern: scrape-*", block)
        self.assertIn("python scripts/merge_scrape_artifacts.py data/scrape-artifacts", block)
        self.assertIn('python scripts/clean_canonical_data.py --repo-root "$GITHUB_WORKSPACE"', block)
        self.assertLess(
            block.index("python scripts/clean_canonical_data.py"),
            block.index("run: python predict.py"),
        )
        self.assertIn("--summary-file /tmp/box-office-merge-summary.json", block)
        self.assertIn("git status --short --", block)
        self.assertIn("box-office-tracker/data/seat-counts.csv", block)
        self.assertIn("box-office-tracker/data/pre-reservation-snapshots.csv", block)
        self.assertIn("box-office-tracker/data/polymarket-markets.csv", block)
        self.assertIn("box-office-tracker/data/run-logs", block)
        self.assertIn("row_changes=$(python3 -c", block)
        self.assertIn(
            '"seat_added", "seat_metadata_updated", "pre_reservation_added", "polymarket_added"',
            block,
        )
        self.assertIn(
            "No canonical seat, snapshot, market rows, or seat metadata were merged",
            block,
        )
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

    def test_collect_links_has_full_weekend_runtime_budget(self):
        collect_start = self.workflow.index("  collect-links:")
        scrape_start = self.workflow.index("  scrape:")
        collect_block = self.workflow[collect_start:scrape_start]
        phase_start = collect_block.index("      - name: Phase 1")
        release_start = collect_block.index("      - name: Release AMC lock", phase_start)
        phase_block = collect_block[phase_start:release_start]

        self.assertIn("timeout-minutes: 250", phase_block)
        self.assertIn("PHASE1_FULL_WEEKEND_LINKS: 'true'", phase_block)
        self.assertIn("PHASE1_DEADLINE_SEC: '7200'", phase_block)
        self.assertIn("PHASE1_MIN_FRESH_LINK_RATIO: '0.90'", phase_block)
        self.assertIn("PHASE1_MAX_THEATRE_DATE_VISITS: '2000'", phase_block)

    def test_phase1_commit_stages_required_outputs_without_optional_masking(self):
        collect_start = self.workflow.index("  collect-links:")
        scrape_start = self.workflow.index("  scrape:")
        collect_block = self.workflow[collect_start:scrape_start]
        commit_start = collect_block.index("      - name: Commit showtime links")
        commit_block = collect_block[commit_start:]

        self.assertIn("git add box-office-tracker/data/showtime-links.json", commit_block)
        self.assertIn("git add box-office-tracker/data/theatre-counts.json", commit_block)
        self.assertIn('if [ -f "box-office-tracker/data/polymarket-markets.csv" ]; then', commit_block)
        self.assertNotIn("box-office-tracker/data/polymarket-markets.csv 2>/dev/null || true", commit_block)

    def test_amc_lock_wait_budget_fits_job_timeouts(self):
        collect_start = self.workflow.index("  collect-links:")
        scrape_start = self.workflow.index("  scrape:")
        finalize_start = self.workflow.index("  finalize:")
        collect_block = self.workflow[collect_start:scrape_start]
        scrape_block = self.workflow[scrape_start:finalize_start]

        collect_timeout = int(re.search(r"timeout-minutes: (\d+)", collect_block).group(1))
        scrape_timeout = int(re.search(r"timeout-minutes: (\d+)", scrape_block).group(1))
        collect_wait = int(re.search(r"--wait-seconds (\d+)", collect_block).group(1)) // 60
        scrape_wait = int(re.search(r"--wait-seconds (\d+)", scrape_block).group(1)) // 60

        collect_phase_start = collect_block.index("      - name: Phase 1")
        collect_release_start = collect_block.index("      - name: Release AMC lock", collect_phase_start)
        collect_phase_block = collect_block[collect_phase_start:collect_release_start]
        scrape_phase_start = scrape_block.index("      - name: Phase 2")
        scrape_release_start = scrape_block.index("      - name: Release AMC lock", scrape_phase_start)
        scrape_phase_block = scrape_block[scrape_phase_start:scrape_release_start]

        collect_phase_timeout = int(re.search(r"timeout-minutes: (\d+)", collect_phase_block).group(1))
        scrape_phase_timeout = int(re.search(r"timeout-minutes: (\d+)", scrape_phase_block).group(1))

        cleanup_buffer_minutes = 20
        dependency_install_buffer_minutes = 30
        self.assertLessEqual(collect_timeout, 360)
        self.assertLessEqual(scrape_timeout, 360)
        self.assertLessEqual(
            collect_wait
            + collect_phase_timeout
            + cleanup_buffer_minutes
            + dependency_install_buffer_minutes,
            collect_timeout,
        )
        self.assertLessEqual(
            scrape_wait
            + scrape_phase_timeout
            + cleanup_buffer_minutes
            + dependency_install_buffer_minutes,
            scrape_timeout,
        )

    def test_calibration_commit_stages_required_file_before_optional_freezes(self):
        start = self.workflow.index("  calibrate:")
        block = self.workflow[start:]

        self.assertIn("git add box-office-tracker/data/calibration.json", block)
        self.assertIn('compgen -G "box-office-tracker/data/calibration-freezes/*.json"', block)
        self.assertNotIn(
            "git add box-office-tracker/data/calibration.json \\\n"
            "                  box-office-tracker/data/calibration-freezes/*.json",
            block,
        )

    def test_github_native_scheduler_dispatches_all_production_slots(self):
        scheduler = self.scheduler
        script = self.scheduler_script

        self.assertIn("name: Box Office Scheduler", scheduler)
        self.assertIn("cron: '*/30 * * * *'", scheduler)
        self.assertIn("actions: write", scheduler)
        self.assertIn("contents: read", scheduler)
        self.assertIn("box-office-scheduler", scheduler)
        self.assertIn("GITHUB_TOKEN: ${{ github.token }}", scheduler)
        self.assertIn("TARGET_WORKFLOW: box-office-pipeline.yml", scheduler)
        self.assertIn("TARGET_REF: main", scheduler)
        self.assertIn("LOOKBACK_MINUTES", scheduler)
        self.assertIn("actions/checkout@v4", scheduler)
        self.assertIn("schedule_box_office_pipeline.py", scheduler)
        self.assertIn("--mode primary", scheduler)
        self.assertIn("recent_pipeline_run_exists", script)
        self.assertIn("scheduled_display_title", script)
        self.assertIn("schedule_slot", script)
        self.assertIn("schedule_mode", script)
        self.assertIn("display_title", script)
        self.assertIn("/dispatches", script)

        for slot in (
            "collect-links ET 13Z",
            "collect-links CT 15Z",
            "collect-links PT 17Z",
            "collect-links ET 19Z",
            "collect-links CT 21Z",
            "collect-links PT 23Z",
            "snapshot 02:30Z",
            "regular scrape 07Z",
            "calibrate Wednesday 12Z",
        ):
            self.assertIn(slot, script)

        self.assertIn("frozenset({2, 3})", script)
        self.assertIn("frozenset({0, 4, 5, 6})", script)
        self.assertIn("frozenset({0, 1, 5, 6})", script)
        self.assertIn("frozenset({3})", script)
        self.assertIn('"pre_reservation_snapshots": snapshots', script)
        self.assertIn('"snapshots_only": snapshots_only', script)
        self.assertNotIn("GH_TOKEN_FILE", scheduler)

    def test_pipeline_declares_github_scheduler_as_primary(self):
        header = self.workflow[: self.workflow.index("permissions:")]

        self.assertIn(".github/workflows/box-office-scheduler.yml", header)
        self.assertIn("short-lived workflow token", header)
        self.assertIn("watchdog fallback", header)
        self.assertIn("missed a slot after a grace window", header)

    def test_repo_contains_vps_watchdog_fallback_for_snapshot_schedule(self):
        dispatcher = DISPATCHER.read_text()
        cron = CRON_EXAMPLE.read_text()

        self.assertIn("gh workflow run", dispatcher)
        self.assertIn("WORKFLOW_FILE:-box-office-pipeline.yml", dispatcher)
        self.assertIn("GH_TOKEN_FILE", dispatcher)
        self.assertIn("pre_reservation_snapshots=true", dispatcher)
        self.assertIn("snapshots_only=true", dispatcher)
        self.assertIn("snapshot", cron)
        self.assertIn('"$DISPATCH" snapshot', cron)
        self.assertIn(
            "DISPATCH=/opt/box-office-tracker/box-office-tracker/scripts/dispatch_box_office_pipeline.sh",
            cron,
        )
        self.assertNotIn("DISPATCH=$REPO_DIR", cron)
        self.assertIn("GH_TOKEN_FILE=/root/box-office-dispatch/.env", cron)
        self.assertIn("Primary scheduling lives in .github/workflows/box-office-scheduler.yml", cron)
        self.assertIn("not the old blind cron", cron)
        self.assertIn("dispatches a slot after the primary scheduler missed it", cron)
        self.assertIn("WATCHDOG=/opt/box-office-tracker/box-office-tracker/scripts/schedule_box_office_pipeline.py", cron)
        self.assertIn("10,40 * * * *", cron)
        self.assertIn(":10/:40 offset avoids racing GitHub's primary scheduler", cron)
        self.assertIn("--mode watchdog", cron)
        self.assertIn("--lookback-minutes 240", cron)
        self.assertIn("--fallback-grace-minutes 30", cron)
        self.assertIn("--token-env GH_TOKEN", cron)
        self.assertIn("git -C \"$REPO_DIR\" pull --ff-only origin main", cron)
        self.assertIn("Tuesday full-weekend mode targets the upcoming", cron)
        self.assertIn("Wednesday repeats are fallback", cron)
        self.assertIn("looks back to Tuesday on Wednesdays", cron)
        self.assertIn("# 0 13 * * 2,3", cron)
        self.assertIn("# 0 15 * * 2,3", cron)
        self.assertIn("# 0 17 * * 2,3", cron)
        self.assertIn("# 0 19 * * 2,3", cron)
        self.assertIn("# 0 21 * * 2,3", cron)
        self.assertIn("# 0 23 * * 2,3", cron)
        self.assertNotIn("0 21 * * 0,3,4,5,6", cron)
        self.assertNotIn("0 23 * * 0,3,4,5,6", cron)
        self.assertNotIn("0 1 * * 0,1,4,5,6", cron)
        self.assertIn("# 30 2 * * 0,4,5,6", cron)
        self.assertNotIn("# 30 2 * * 0,1,4,5,6", cron)
        self.assertIn("# 0 7 * * 0,1,5,6", cron)
        self.assertNotIn("0 7 * * 0,1,4,5,6", cron)
        self.assertIn("using Tuesday's committed Phase 1 cache", cron)
        self.assertIn("# 0 12 * * 3", cron)
        self.assertNotIn("0 12 * * 2", cron)
        self.assertNotIn("0 14 * * 2", cron)
        self.assertNotIn("30 22", cron)
        self.assertNotIn("30 18", cron)
        self.assertIn("phase=scrape", cron)
        self.assertIn("phase=collect-links", cron)
        self.assertNotIn(" MT ", cron)
        self.assertNotIn("4-0", cron)
        self.assertNotIn("5-1", cron)
        active_commands = [
            line for line in cron.splitlines()
            if re.match(r"^[0-9*]", line) and "--mode watchdog" not in line
        ]
        self.assertEqual([], active_commands)

    def test_vps_dispatcher_dedupes_duplicate_dispatch_slots(self):
        dispatcher = DISPATCHER.read_text()

        self.assertIn("DISPATCH_STATE_DIR", dispatcher)
        self.assertIn("DISPATCH_DEDUP_WINDOW_SEC", dispatcher)
        self.assertIn("run_once_per_slot", dispatcher)
        self.assertIn("slot_key_for", dispatcher)
        self.assertIn(".lockdir", dispatcher)
        self.assertIn('mkdir "$lock_dir"', dispatcher)
        self.assertIn("duplicate slot already active", dispatcher)
        self.assertIn("recent dispatch already sent", dispatcher)
        self.assertIn('run_once_per_slot "$mode" "ALL"', dispatcher)
        self.assertIn('run_once_per_slot "$mode" "$tz"', dispatcher)


if __name__ == "__main__":
    unittest.main()

    def test_finalize_runs_the_completeness_watchdog_informationally(self):
        """Green-but-empty lanes must trip a volume watchdog, and the watchdog
        itself must never be able to fail finalize (continue-on-error)."""
        start = self.workflow.index("  finalize:")
        end = self.workflow.index("  calibrate:", start)
        block = self.workflow[start:end]
        self.assertIn("capture_completeness.py", block)
        i = block.index("capture_completeness.py")
        self.assertIn("continue-on-error: true", block[max(0, i - 700):i])
