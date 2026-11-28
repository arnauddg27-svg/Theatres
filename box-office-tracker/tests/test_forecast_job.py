"""The forecast-only pipeline phase (2026-11-28): scheduler slots, workflow
job, staging allow-list and the finalize-in-flight check."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "box-office-tracker" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import finalize_in_flight as F  # noqa: E402
import schedule_box_office_pipeline as S  # noqa: E402
import stage_finalize_outputs as SFO  # noqa: E402

WORKFLOW = (ROOT / ".github" / "workflows" / "box-office-pipeline.yml").read_text()
RUNNER = (SCRIPTS / "run_forecast.sh").read_text()


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), text=True, capture_output=True, check=True)


class ForecastSlotsTest(unittest.TestCase):
    def setUp(self):
        self.slots = [s for s in S.SLOTS if s.inputs.get("phase") == "forecast"]

    def test_weekend_clock_follows_seat_counts_and_reported_grosses(self):
        weekend = {(s.hour, s.minute) for s in self.slots if s.cron_days == frozenset({5, 6, 0, 1})}
        self.assertEqual(weekend, {(10, 20), (16, 20), (18, 20), (20, 20)})
        # the first one runs once yesterday's seat counts are complete
        import chain_forecast
        self.assertGreaterEqual(10 * 60 + 20, chain_forecast.DAY_COMPLETE_UTC_HOUR * 60)

    def test_pre_release_days_get_two_reads(self):
        pre = {(s.hour, s.minute) for s in self.slots if s.cron_days == frozenset({2, 3, 4})}
        self.assertEqual(pre, {(13, 20), (21, 20)})

    def test_slot_names_are_unique_and_dispatch_the_forecast_phase(self):
        names = [s.name for s in S.SLOTS]
        self.assertEqual(len(names), len(set(names)))
        for s in self.slots:
            self.assertEqual(s.name, f"forecast {s.hour:02d}:{s.minute:02d}Z")
            self.assertEqual(s.inputs["phase"], "forecast")
            self.assertEqual(S.retry_gap_minutes(s.name), 0)       # not an AMC slot: retried at once


class WorkflowJobTest(unittest.TestCase):
    def setUp(self):
        self.block = WORKFLOW[WORKFLOW.index("\n  forecast:\n"):]

    def test_job_runs_only_for_its_phase_and_never_on_the_amc_runner(self):
        self.assertIn("if: github.event.inputs.phase == 'forecast'", self.block)
        self.assertIn("runs-on: ubuntu-24.04", self.block)
        self.assertNotIn("self-hosted", self.block)
        self.assertNotIn("needs:", self.block)

    def test_job_hands_over_to_the_runner_with_a_token_for_the_finalize_check(self):
        self.assertIn("bash box-office-tracker/scripts/run_forecast.sh", self.block)
        self.assertIn("GITHUB_TOKEN: ${{ github.token }}", self.block)
        # only the fact that a proxy exists, never the credential
        self.assertIn("HAS_PROXY: ${{ secrets.AMC_SEAT_PROXY_URL != '' }}", self.block)
        self.assertEqual(self.block.count("secrets.AMC_SEAT_PROXY_URL"), 1)

    def test_phase_is_documented_as_an_input(self):
        self.assertIn("forecast (forecast + logs without the AMC scrape)", WORKFLOW)


class RunnerScriptTest(unittest.TestCase):
    def test_a_failed_forecast_fails_the_job(self):
        self.assertIn("python3 predict.py || exit 1", RUNNER)
        self.assertIn('forecast || { echo "::error::predict.py failed"; exit 1; }', RUNNER)

    def test_it_stages_by_allow_list_and_checks_finalize_before_every_push(self):
        self.assertIn("stage_finalize_outputs.py\" --forecast", RUNNER)
        self.assertNotIn("git add", RUNNER)
        check, push = RUNNER.index("finalize_in_flight.py\"; then"), RUNNER.index("git push")
        self.assertLess(check, push)

    def test_it_starts_from_main_and_redoes_the_forecast_when_main_moved_under_it(self):
        self.assertIn("git reset -q --hard origin/main", RUNNER)
        self.assertIn("return 2", RUNNER)
        self.assertIn('if [ "$rc" = "2" ]', RUNNER)

    def test_it_runs_the_same_forecast_steps_as_finalize(self):
        for step in ("scripts/fetch_daily_actuals.py", "predict.py", "holdover_forecast.py",
                     "scripts/log_polymarket_odds.py", "scripts/fetch_trade_forecasts.py",
                     "scripts/ensemble_forecast.py", "scripts/paper_trade.py"):
            self.assertIn(step, RUNNER)
            self.assertIn(step.split("/")[-1], WORKFLOW[WORKFLOW.index("\n  finalize:\n"):WORKFLOW.index("\n  scrape-fandango:\n")])
        order = [RUNNER.index(s) for s in ("fetch_daily_actuals.py", "python3 predict.py", "log_polymarket_odds.py",
                                           "ensemble_forecast.py", "paper_trade.py")]
        self.assertEqual(order, sorted(order))


class ForecastStagingTest(unittest.TestCase):
    def test_every_forecast_file_is_also_committed_by_finalize(self):
        self.assertTrue(set(SFO.FORECAST_OUTPUT_FILES) <= set(SFO.OUTPUT_FILES))

    def test_canonical_scrape_files_are_never_in_the_forecast_list(self):
        for name in ("seat-counts.csv", "pre-reservation-snapshots.csv", "calibration.json", "showtime-links.json"):
            self.assertFalse(any(p.endswith("/" + name) for p in SFO.FORECAST_OUTPUT_FILES), name)

    def test_forecast_mode_stages_only_its_own_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            git("init", cwd=repo)
            git("config", "user.name", "Test", cwd=repo)
            git("config", "user.email", "test@example.com", cwd=repo)
            data = repo / "box-office-tracker" / "data"
            data.mkdir(parents=True)
            for name in ("prediction-log.csv", "seat-counts.csv", "calibration.json"):
                (data / name).write_text("a\n")
            git("add", ".", cwd=repo)
            git("commit", "-m", "init", cwd=repo)
            for name in ("prediction-log.csv", "seat-counts.csv", "calibration.json"):
                (data / name).write_text("a\nb\n")
            (data / "chain-pace.csv").write_text("new\n")
            done = subprocess.run([sys.executable, str(SCRIPTS / "stage_finalize_outputs.py"), "--repo-root", str(repo),
                                   "--forecast"], text=True, capture_output=True)
            self.assertEqual(done.returncode, 0, done.stderr)
            staged = git("diff", "--cached", "--name-only", cwd=repo).stdout.split()
            self.assertEqual(sorted(staged), ["box-office-tracker/data/chain-pace.csv",
                                              "box-office-tracker/data/prediction-log.csv"])

    def test_finalize_mode_still_needs_its_summary(self):
        done = subprocess.run([sys.executable, str(SCRIPTS / "stage_finalize_outputs.py")], text=True, capture_output=True)
        self.assertNotEqual(done.returncode, 0)


class FinalizeInFlightTest(unittest.TestCase):
    RUNS = [{"id": 1, "display_title": "box office scheduled cinemark pre 14:20Z s3"},
            {"id": 2, "display_title": "box office scheduled snapshot fandango census 16Z"},
            {"id": 3, "display_title": "box office scheduled snapshot 14:30Z"},
            {"id": 4, "display_title": "box office scheduled regular scrape 07Z"},
            {"id": 5, "display_title": "box office scheduled forecast 16:20Z"}]

    def test_only_scrape_phase_runs_are_asked_for_their_jobs(self):
        self.assertEqual([r["id"] for r in F.candidate_runs(self.RUNS)], [3, 4])
        self.assertEqual([r["id"] for r in F.candidate_runs(self.RUNS, own_run_id="3")], [4])

    def test_a_running_finalize_job_is_in_flight_a_scraping_leg_is_not(self):
        self.assertTrue(F.finalize_running([{"name": "scrape (ET)", "status": "completed"},
                                            {"name": "finalize", "status": "in_progress"}]))
        self.assertFalse(F.finalize_running([{"name": "scrape (PT)", "status": "in_progress"}]))
        self.assertFalse(F.finalize_running([{"name": "finalize", "status": "completed"}]))

    def test_in_flight_names_the_run(self):
        def get(url, _token):
            if "/jobs" in url:
                running = "/runs/4/" in url
                return {"jobs": [{"name": "finalize", "status": "in_progress" if running else "queued"}]}
            return {"workflow_runs": self.RUNS}
        self.assertEqual(F.in_flight("o/r", "t", get=get), "box office scheduled regular scrape 07Z")
        self.assertIsNone(F.in_flight("o/r", "t", own_run_id="4", get=get))

    def test_no_token_or_an_api_error_never_blocks_a_forecast(self):
        with mock.patch.dict(os.environ, {"GITHUB_REPOSITORY": "", "GITHUB_TOKEN": "", "GH_TOKEN": ""}):
            self.assertEqual(F.main([]), 0)
        with mock.patch.dict(os.environ, {"GITHUB_REPOSITORY": "o/r", "GITHUB_TOKEN": "t"}), \
                mock.patch.object(F, "in_flight", side_effect=OSError("down")):
            self.assertEqual(F.main([]), 0)

    def test_exit_status_one_while_a_finalize_runs(self):
        with mock.patch.dict(os.environ, {"GITHUB_REPOSITORY": "o/r", "GITHUB_TOKEN": "t"}), \
                mock.patch.object(F, "in_flight", return_value="box office scheduled snapshot 14:30Z"):
            self.assertEqual(F.main([]), 1)


if __name__ == "__main__":
    unittest.main()
