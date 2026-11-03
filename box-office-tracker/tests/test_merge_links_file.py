"""showtime-links.json rebase conflicts are resolved by union, not by failing.

2026-11-03 17Z PT collect-links: three push attempts conflicted with the
17:31Z snapshot finalize (which now rewrites showtime-links.json) and the
job ended "data not committed"."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import merge_links_file as L  # noqa: E402

WORKFLOW = ROOT.parent / ".github" / "workflows" / "box-office-pipeline.yml"
LINKS = "box-office-tracker/data/showtime-links.json"


def links(weekend, theatres, stamp="2026-11-03T13:00:00+00:00"):
    return {"date": weekend, "weekend_of": weekend, "collected_at": stamp, "theatres": theatres}


def theatre(tz, date, movies, stamp="2026-11-03T13:00:00+00:00"):
    return {"tz": tz, "cohort": "core", "show_date": date, "movies": movies,
            "dates": {date: {"movies": movies, "collected_at": stamp}}}


class ResolveTest(unittest.TestCase):
    def _write(self, td, name, data):
        p = Path(td) / name
        p.write_text(json.dumps(data))
        return p

    def test_same_weekend_is_unioned(self):
        with tempfile.TemporaryDirectory() as td:
            main = self._write(td, "main.json", links("2026-11-06", {
                "AMC Empire 25": theatre("ET", "2026-11-06", {"Godzilla Minus Zero": [{"showtime_id": "g1"}]})}))
            ours = self._write(td, "ours.json", links("2026-11-06", {
                "AMC Empire 25": theatre("ET", "2026-11-06", {"Godzilla Minus Zero": [{"showtime_id": "g1"}],
                                                              "Drummer Boy": [{"showtime_id": "d1"}]},
                                         stamp="2026-11-03T17:20:00+00:00"),
                "AMC Burbank 16": theatre("PT", "2026-11-06", {"Drummer Boy": [{"showtime_id": "d2"}]})}))
            note = L.resolve(str(main), str(ours))
            self.assertIn("unioned 2", note)
            out = json.loads(main.read_text())["theatres"]
            self.assertEqual(sorted(out["AMC Empire 25"]["dates"]["2026-11-06"]["movies"]), ["Drummer Boy", "Godzilla Minus Zero"])
            self.assertIn("AMC Burbank 16", out)

    def test_newer_weekend_wins_whole(self):
        with tempfile.TemporaryDirectory() as td:
            old = links("2026-10-30", {"AMC Empire 25": theatre("ET", "2026-10-31", {"Clayface": [{"showtime_id": "c"}]})})
            new = links("2026-11-06", {"AMC Burbank 16": theatre("PT", "2026-11-06", {"Drummer Boy": [{"showtime_id": "d"}]})})
            main = self._write(td, "main.json", old)
            ours = self._write(td, "ours.json", new)
            self.assertIn("took ours", L.resolve(str(main), str(ours)))
            self.assertEqual(json.loads(main.read_text())["weekend_of"], "2026-11-06")
            main = self._write(td, "main2.json", new)
            ours = self._write(td, "ours2.json", old)
            self.assertIn("kept main", L.resolve(str(main), str(ours)))
            self.assertEqual(json.loads(main.read_text())["weekend_of"], "2026-11-06")

    def test_unreadable_ours_keeps_main(self):
        with tempfile.TemporaryDirectory() as td:
            main = self._write(td, "main.json", links("2026-11-06", {}))
            ours = Path(td) / "ours.json"
            ours.write_text("{not json")
            self.assertIn("kept main", L.resolve(str(main), str(ours)))
            self.assertEqual(json.loads(main.read_text())["weekend_of"], "2026-11-06")


class RebaseConflictTest(unittest.TestCase):
    """Replays the workflow's resolution commands on a real conflicting rebase:
    `--ours` during a rebase is upstream (main), which is what the resolver
    expects as TARGET."""

    def _git(self, cwd, *args, env=None):
        e = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@x", GIT_COMMITTER_NAME="t",
                 GIT_COMMITTER_EMAIL="t@x", GIT_EDITOR="true", **(env or {}))
        return subprocess.run(["git", *args], cwd=cwd, env=e, capture_output=True, text=True)

    def test_workflow_resolution_sequence(self):
        with tempfile.TemporaryDirectory() as td:
            origin = Path(td) / "origin.git"
            self.assertEqual(self._git(td, "init", "-q", "--bare", "-b", "main", str(origin)).returncode, 0)
            work = Path(td) / "work"
            self._git(td, "clone", "-q", str(origin), str(work))
            self._git(work, "checkout", "-q", "-b", "main")
            f = work / LINKS
            f.parent.mkdir(parents=True)
            base = links("2026-11-06", {"AMC Empire 25": theatre("ET", "2026-11-06", {"Godzilla Minus Zero": [{"showtime_id": "g1"}]})})
            f.write_text(json.dumps(base, indent=2))
            self._git(work, "add", "-A")
            self._git(work, "commit", "-q", "-m", "base")
            self._git(work, "push", "-q", "-u", "origin", "main")
            # "finalize" pushes a union first
            other = Path(td) / "other"
            self._git(td, "clone", "-q", str(origin), str(other))
            fin = json.loads(base and json.dumps(base))
            fin["theatres"]["AMC Shiloh 14"] = theatre("MT", "2026-11-06", {"Godzilla Minus Zero": [{"showtime_id": "m1"}]})
            (other / LINKS).write_text(json.dumps(fin, indent=2))
            self._git(other, "commit", "-q", "-am", "data: box office scrape merge + predictions")
            self.assertEqual(self._git(other, "push", "-q", "origin", "main").returncode, 0)
            # "collect-links" rewrites the file whole with its own additions
            ours = json.loads(json.dumps(base))
            ours["theatres"]["AMC Burbank 16"] = theatre("PT", "2026-11-06", {"Drummer Boy": [{"showtime_id": "d1"}]})
            f.write_text(json.dumps(ours, indent=2))
            self._git(work, "commit", "-q", "-am", "data: box office PT collect-links")
            saved = Path(td) / "our-showtime-links.json"
            saved.write_text(f.read_text())
            pull = self._git(work, "pull", "--rebase", "--autostash", "origin", "main")
            self.assertNotEqual(pull.returncode, 0, "expected a conflict")
            unmerged = self._git(work, "diff", "--name-only", "--diff-filter=U").stdout.split()
            self.assertEqual(unmerged, [LINKS])
            self.assertEqual(self._git(work, "checkout", "--ours", "--", LINKS).returncode, 0)
            self.assertIn("AMC Shiloh 14", json.loads(f.read_text())["theatres"])   # --ours is main during a rebase
            res = subprocess.run([sys.executable, str(ROOT / "scripts" / "merge_links_file.py"), str(f), str(saved)],
                                 capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, res.stderr)
            self._git(work, "add", LINKS)
            self.assertEqual(self._git(work, "rebase", "--continue").returncode, 0)
            self.assertEqual(self._git(work, "push", "-q", "origin", "main").returncode, 0)
            final = json.loads(f.read_text())["theatres"]
            self.assertEqual(sorted(final), ["AMC Burbank 16", "AMC Empire 25", "AMC Shiloh 14"])


class WorkflowWiringTest(unittest.TestCase):
    def test_both_rewriting_lanes_resolve_link_conflicts(self):
        text = WORKFLOW.read_text()
        blocks = [b for b in text.split("for i in 1 2 3; do")[1:]]
        resolving = [b for b in blocks if "merge_links_file.py" in b]
        self.assertEqual(len(resolving), 2, "collect-links and finalize push loops must both resolve")
        for b in resolving:
            head = b.split("echo \"Push attempt")[0]
            self.assertIn("git diff --name-only --diff-filter=U", head)
            self.assertIn("git checkout --ours -- box-office-tracker/data/showtime-links.json", head)
            self.assertIn("GIT_EDITOR=true git rebase --continue && git push && break", head)
        self.assertEqual(text.count("cp box-office-tracker/data/showtime-links.json /tmp/our-showtime-links.json"), 2)


if __name__ == "__main__":
    unittest.main()
