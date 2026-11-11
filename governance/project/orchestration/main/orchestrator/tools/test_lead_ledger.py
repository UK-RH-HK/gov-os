"""Tests for lead_ledger.py and lead_mem_watch.py: planted fixtures under a tmp dir, nothing from the real records.
Run: python3 -m pytest -q -p no:cacheprovider tools/test_lead_ledger.py  (one small file; no heavy slot needed)."""
import hashlib
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lead_ledger as L  # noqa: E402
import lead_mem_watch as M  # noqa: E402

NOW = datetime(2026, 11, 11, 19, 0, 0)


def ts(dt):
    return dt.replace(tzinfo=timezone.utc).timestamp()


def T(s):
    return L.parse_t(s)


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = os.path.join(self.tmp.name, "orch")
        self.wt = os.path.join(self.tmp.name, "wt")
        for d in ("dispatch", "log", "drafts/batch-prep"):
            os.makedirs(os.path.join(self.root, d))
        os.makedirs(self.wt)

    def w(self, path, text="", mt=None):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(text)
        if mt:
            os.utime(path, (ts(T(mt)), ts(T(mt))))
        return path

    def rootf(self, rel, text="", mt=None):
        return self.w(os.path.join(self.root, rel), text, mt)

    def wtlog(self, tree, name, text="", mt=None):
        return self.w(os.path.join(self.wt, tree, ".gov-runtime", "scratch", "lead", "log", name), text, mt)

    def dispatch(self, *lines):
        self.rootf("dispatch/dispatch.log", "\n".join(lines) + "\n")

    def lead_json(self, name, status, cost, dur_ms, mt, turns=10, extra=""):
        body = {"type": "result", "subtype": "success", "is_error": False, "duration_ms": dur_ms, "num_turns": turns,
                "result": f"task: X\nstatus: {status}. {extra}\nwork_completed: things", "total_cost_usd": cost}
        self.rootf("log/" + name, json.dumps(body) + "\n", mt)

    def status_json(self, time_s, leads):
        self.rootf("dispatch/status.json", json.dumps({"time": time_s, "leads": leads}))

    def spend(self, *rows):
        self.rootf("log/spend.jsonl", "".join(json.dumps(r) + "\n" for r in rows))

    def batch_prep(self, rows):
        self.rootf("drafts/batch-prep/BATCH-PREP.md",
                   "# BATCH-PREP\n\nWritten 2026-11-11 (about 14:30 UTC) by a helper.\n\n## 2. The table\n\n"
                   "| ticket | state | next step | role | brief | cost |\n|---|---|---|---|---|---|\n" + rows +
                   "\n## 3. Cost\n\ntext\n")

    def ledger(self, since="2026-11-11 00:00:00", now=NOW, alive=lambda pid: True, basis="hi"):
        led = L.Ledger(self.root, self.wt, now=now, since=T(since), est_basis=basis, alive=alive)
        runs, _ = led.build()
        return led, {(r["W2"], r["run"]): r for r in led.rows(runs)}


class TestParsing(unittest.TestCase):
    def test_status_line_forms(self):
        self.assertEqual(L.status_line("task: x\nstatus: PACKAGES. waits"), "PACKAGES")
        self.assertEqual(L.status_line("**status:** DONE\n"), "DONE")
        self.assertEqual(L.status_line("a\n- status: LAUNCH_BLOCKED. no"), "LAUNCH_BLOCKED")
        self.assertIsNone(L.status_line("no such line"))

    def test_load_result_takes_the_object_with_a_result_and_ignores_trailing_text(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.json")
            two = '{"type":"system","a":1}\n{"type":"result","result":"status: DONE","total_cost_usd":1.25}\nTRAILING NOISE {'
            open(p, "w").write(two)
            r = L.load_result(p)
            self.assertEqual(r["total_cost_usd"], 1.25)
            open(p, "w").write("")
            self.assertIsNone(L.load_result(p))

    def test_parse_t_forms(self):
        self.assertEqual(L.parse_t("2026-11-11T18:08"), datetime(2026, 11, 11, 18, 8))
        self.assertEqual(L.parse_t("2026-11-11 18:08:07+00:00"), datetime(2026, 11, 11, 18, 8, 7))
        self.assertEqual(L.parse_t("Sun Nov  1 19:19:56 GMT 2026"), datetime(2026, 11, 1, 19, 19, 56))
        self.assertIsNone(L.parse_t("garbage"))

    def test_phase_mapping(self):
        for name, sub, want in (("td-1", "", "tests"), ("eng-2", "", "build"), ("rev-2", "", "review"),
                                ("probe-1", "", "review"), ("verify", "verify", "verify"), ("reds-alone", "", "verify"),
                                ("accept", "", "verify"), ("rebuild-1", "", "verify"), ("merge-tests", "", "land"),
                                ("ps-1", "", "other"), ("review-4", "", "review"), ("en-1", "", "build")):
            self.assertEqual(L.phase_of(name, sub), want, name)

    def test_union_minutes_counts_parallel_once(self):
        a, b, c = T("2026-11-11 10:00"), T("2026-11-11 10:10"), T("2026-11-11 10:20")
        self.assertEqual(L.union_minutes([(a, b), (a, c), (c, c)]), 20.0)


class TestRefusalsAndEstimate(Fixture):
    def setUp(self):
        super().setUp()
        self.batch_prep("| W2-04 `u4oz` FULL | merged | review | lead | brief | 0.5 h; $6; 0.22 pt (E: x) |\n"
                        "| W2-11 `k7hz` STANDARD | state | resume | lead | brief | 4-6 h; $18-26; 0.7 pt (E) |\n"
                        "| W2-96 `ouet` FULL | merged | close | CTO | none | 20-25 min; 0.05 pt |\n")
        self.dispatch(
            "2026-11-11 18:08:07 started W2-04 (DAEO-u4oz) b.md -> W2-04-A5-r6-review.json (launcher exit 0)",
            "2026-11-11 18:11:04 started W2-11 (DAEO-k7hz) b.md -> W2-11-A5-r5-resume.json (launcher exit 0)",
            "2026-11-11 18:13:08 started but never ran: W2-04 W2-04-A5-r6-review.json",
            "2026-11-11 18:15:08 started W2-04 (DAEO-u4oz) b.md -> W2-04-A5-r6b-review.json (launcher exit 0)",
            "2026-11-11 18:18:07 started W2-04 (DAEO-u4oz) b.md -> W2-04-A5-r6c-review.json (launcher exit 0)",
            "2026-11-11 18:40:01 started but never ran: W2-04 W2-04-A5-r6b-review.json")
        self.rootf("log/W2-04-20261111-1808-launch.txt", "admitted\nLAUNCH_NO_TEMPLATE: the role template is missing\n")
        self.rootf("log/W2-04-20261111-1815-launch.txt", "admitted\nError: Input must be provided either through stdin\n")
        self.rootf("log/W2-04-20261111-1818-launch.txt", "admitted\ndisk gate open\n")
        self.rootf("log/W2-11-20261111-1811-launch.txt", "admitted\nLAUNCH_NO_TEMPLATE: missing\n")
        self.rootf("log/W2-04-A5-r6b-review.json", "", "2026-11-11 18:15:08")
        self.lead_json("W2-04-A5-r6c-review.json", "DONE", 4.80, 1180962, "2026-11-11 18:39:20")
        self.wtlog("W2-04", "rev-2.pid", "984055", "2026-11-11 18:22:32")
        self.wtlog("W2-04", "rev-2.json", json.dumps({"type": "result", "result": "ok", "total_cost_usd": 2.04,
                                                      "duration_ms": 383000, "num_turns": 49}), "2026-11-11 18:28:52")
        self.wtlog("W2-04", "rev-2.exit", "0\n", "2026-11-11 18:28:55")
        self.status_json("2026-11-11 18:58:00", [])
        self.spend({"at": "2026-11-11 18:28", "kind": "launched", "wbs": "W2-04", "cost_usd": 2.04,
                    "extra": {"log": "/x/W2-04/.gov-runtime/scratch/lead/log/rev-2.json", "num_turns": 49}})

    def test_refusals_never_ran_and_waits_before_start(self):
        _, rows = self.ledger()
        r6, r6b, r6c = rows[("W2-04", "r6-review")], rows[("W2-04", "r6b-review")], rows[("W2-04", "r6c-review")]
        self.assertEqual((r6["status"], r6b["status"], r6c["status"]), ("REFUSED", "REFUSED", "DONE"))
        self.assertIn("LAUNCH_NO_TEMPLATE", r6["refusal"])
        self.assertIn("empty brief", r6b["refusal"])
        self.assertEqual(r6["waits"][0]["kind"], "launch refusal")
        self.assertEqual(r6["waits"][0]["minutes"], 7.0)     # 18:08:07 to the next attempt at 18:15:08
        self.assertEqual(r6b["waits"][0]["minutes"], 3.0)
        self.assertFalse(r6["waits"][0]["open"])
        self.assertEqual(r6["wall_minutes"], 0.0)

    def test_open_refusal_has_no_end_and_counts_to_now(self):
        _, rows = self.ledger()
        r = rows[("W2-11", "r5-resume")]
        self.assertEqual(r["status"], "REFUSED")
        self.assertTrue(r["waits"][0]["open"])
        self.assertEqual(r["waits"][0]["minutes"], minutes_between("2026-11-11 18:11:04", NOW))
        self.assertEqual(r["estimate"]["hours_lo"], 4.0)
        self.assertEqual(r["estimate"]["hours_hi"], 6.0)
        self.assertAlmostEqual(r["estimate"]["elapsed_h"], 0.82, places=2)     # to now, not to the refusal
        self.assertFalse(r["flag"])

    def test_chain_time_against_batch_prep_estimate_includes_the_refusals(self):
        _, rows = self.ledger()
        r = rows[("W2-04", "r6c-review")]
        e = r["estimate"]
        self.assertEqual(e["chain_runs"], ["r6-review", "r6b-review", "r6c-review"])
        self.assertEqual(e["by"], "BATCH-PREP")
        self.assertAlmostEqual(e["elapsed_h"], 0.52, places=2)       # 18:08:07 to 18:39:20
        self.assertAlmostEqual(e["ratio_elapsed"], 1.04, places=2)
        self.assertFalse(r["flag"])
        self.assertIsNone(rows[("W2-04", "r6-review")]["estimate"])   # the estimate rides on the last run

    def test_worker_phase_cost_and_review_round(self):
        _, rows = self.ledger()
        r = rows[("W2-04", "r6c-review")]
        self.assertEqual(r["rev_rounds"], 1)
        self.assertEqual(r["phases_min"]["review"], 6.4)
        self.assertEqual(r["cost"]["lead_usd"], 4.8)
        self.assertEqual(r["cost"]["workers_usd"], 2.04)       # once: the json and the spend row are one worker
        self.assertEqual(r["cost"]["total_usd"], 6.84)
        self.assertTrue(any(w["kind"] == "review round" and w["cause"] == "rev-2" for w in r["waits"]))

    def test_close_row_without_hours_has_no_estimate(self):
        led = L.Ledger(self.root, self.wt, now=NOW)
        ests, bp, bpt = led.load_estimates()
        self.assertNotIn("W2-96", bp)
        self.assertEqual(bp["W2-04"]["hours"], [0.5, 0.5])
        self.assertEqual(bp["W2-04"]["usd"], [6.0, 6.0])
        self.assertEqual(bp["W2-11"]["usd"], [18.0, 26.0])
        self.assertEqual(bpt, datetime(2026, 11, 11, 14, 30))


def minutes_between(a, b):
    return L.minutes(T(a), b)


class TestPackagesFlagAndCopiedWorker(Fixture):
    def setUp(self):
        super().setUp()
        self.rootf("log/lead-estimates.json", json.dumps({"W2-170:tests": {"hours": 1.5, "usd": None, "source": "x", "by": "CTO"},
                                                         "W2-170:build": {"hours": 4, "source": "y"}}))
        self.dispatch(
            "2026-11-11 15:17:16 would start W2-170 (DAEO-61vm) t.md -> W2-170-A5-tests.json",
            "2026-11-11 15:18:03 started W2-170 (DAEO-61vm) t.md -> W2-170-A5-tests.json (launcher exit 0)",
            "2026-11-11 17:54:06 started W2-170 (DAEO-61vm) t2.md -> W2-170-A5-tests2.json (launcher exit 0)")
        self.lead_json("W2-170-A5-tests.json", "PACKAGES", 0.77, 114200, "2026-11-11 15:20:01")
        self.lead_json("W2-170-A5-tests2.json", "DONE", 2.02, 1966447, "2026-11-11 18:29:35")
        # the designer's files were copied at 18:28:40 (all one mtime), its json holds the duration; spend has the minute
        for ext, txt in (("pid", "984055"), ("exit", "0\n"), ("summary", "x"), ("json", json.dumps(
                {"type": "result", "result": "r", "total_cost_usd": 9.15, "duration_ms": 1625479, "num_turns": 126}))):
            self.wtlog("W2-170", f"td-1.{ext}", txt, "2026-11-11 18:28:40")
        self.spend({"at": "2026-11-11 18:26", "kind": "launched", "wbs": "W2-170", "cost_usd": 9.15,
                    "extra": {"log": "/x/W2-170-tests/.gov-runtime/scratch/lead/log/td-1.json", "num_turns": 126}})
        self.status_json("2026-11-11 18:58:00", [])

    def test_packages_wait_then_flag_with_the_reason(self):
        _, rows = self.ledger()
        t1, t2 = rows[("W2-170", "tests")], rows[("W2-170", "tests2")]
        self.assertEqual(t1["status"], "PACKAGES")
        w = [x for x in t1["waits"] if x["kind"] == "waiting on the CTO or the owner"][0]
        self.assertEqual(w["minutes"], 154.1)          # 15:20:01 to 17:54:06
        self.assertFalse(w["open"])
        self.assertTrue(t2["flag"])
        self.assertIn("154 min waiting on the CTO or the owner", t2["flag_reason"])
        self.assertIn("2.1x", t2["flag_reason"])
        self.assertEqual(t2["estimate"]["key"], "W2-170:tests")     # 'tests2' reads as 'tests'
        self.assertEqual(t2["estimate"]["by"], "CTO")
        self.assertGreater(t2["estimate"]["ratio_elapsed"], 1.5)
        self.assertLess(t2["estimate"]["ratio_active"], 1.5)

    def test_admission_wait_under_a_minute_is_not_listed(self):
        _, rows = self.ledger()
        self.assertFalse([x for x in rows[("W2-170", "tests")]["waits"] if x["kind"] == "admission"])

    def test_copied_worker_files_take_end_from_spend_and_start_from_duration(self):
        _, rows = self.ledger()
        w = rows[("W2-170", "tests2")]["workers"][0]
        self.assertEqual(w["name"], "td-1")
        self.assertEqual(w["phase"], "tests")
        self.assertEqual(w["end"], "2026-11-11 18:26:30")
        self.assertEqual(w["start"], "2026-11-11 17:59:24")
        self.assertEqual(w["minutes"], 27.1)
        self.assertIn("spend.jsonl", w["note"])
        self.assertEqual(rows[("W2-170", "tests2")]["cost"]["total_usd"], 11.17)

    def test_active_over_threshold_also_flags(self):
        self.rootf("log/lead-estimates.json", json.dumps({"W2-170:tests": {"hours": 0.25}}))
        _, rows = self.ledger()
        t2 = rows[("W2-170", "tests2")]
        self.assertTrue(t2["flag"])
        self.assertGreater(t2["estimate"]["ratio_active"], 1.5)

    def test_est_basis_lo_mid_hi_for_a_range(self):
        self.rootf("log/lead-estimates.json", json.dumps({"W2-170:tests": {"hours": [1.0, 3.0]}}))
        self.assertTrue(self.ledger(basis="lo")[1][("W2-170", "tests2")]["flag"])
        self.assertFalse(self.ledger(basis="hi")[1][("W2-170", "tests2")]["flag"])


class TestRunningMemoryBrakeNotes(Fixture):
    def test_running_run_uses_status_json_and_a_live_worker(self):
        self.rootf("log/lead-estimates.json", json.dumps({"W2-170:build": {"hours": 4}}))
        self.dispatch("2026-11-11 18:32:04 started W2-170 (DAEO-61vm) b.md -> W2-170-A5-build.json (launcher exit 0)")
        self.rootf("log/W2-170-A5-build.json", "", "2026-11-11 18:32:04")
        self.status_json("2026-11-11 18:59:30", ["W2-170"])
        self.wtlog("W2-170", "eng-1.pid", "1089044", "2026-11-11 18:33:55")
        self.wtlog("W2-170", "eng-1.json", "", "2026-11-11 18:33:55")
        self.w(os.path.join(self.wt, "W2-170/.gov-runtime/scratch/lead/CHECKPOINT.md"),
               "task: x\nSTATE: build run 1 | HEAD: 49c7 | NEXT: wait | WAITING ON: eng-1\n")
        self.rootf("log/lead-hour-watch.jsonl",
                   json.dumps({"at": "2026-11-11 18:40:00", "leads_mb": {"W2-170": 500}}) + "\n" +
                   json.dumps({"at": "2026-11-11 18:50:00", "leads_mb": {"W2-170": 679}}) + "\n" +
                   json.dumps({"at": "2026-11-11 17:00:00", "leads_mb": {"W2-170": 9999}}) + "\n")
        self.rootf("log/lead-mem.jsonl", json.dumps({"t": "2026-11-11T18:45:00", "leads_kb": {"DAEO-61vm": 700 * 1024}}) + "\n")
        _, rows = self.ledger(alive=lambda pid: pid == 1089044)
        r = rows[("W2-170", "build")]
        self.assertEqual(r["status"], "RUNNING")
        self.assertIsNone(r["end"])
        self.assertTrue(r["running"])
        self.assertEqual(r["workers"][0]["name"], "eng-1")
        self.assertTrue(r["workers"][0]["running"])
        self.assertEqual(r["phases_min"]["build"], 26.1)            # 18:33:55 to now (19:00)
        self.assertEqual(r["mem"]["peak_mb"], 700)                    # the larger source wins; the 17:00 sample is outside the run
        self.assertEqual(r["mem"]["source"], "lead-mem")
        self.assertEqual(r["mem"]["by_source"]["lead-hour-watch"]["mb"], 679)
        self.assertEqual(r["checkpoint"]["waiting_on"], "eng-1")
        self.assertAlmostEqual(r["estimate"]["elapsed_h"], 0.47, places=2)
        self.assertFalse(r["flag"])

    def test_a_running_run_past_one_and_a_half_times_is_flagged(self):
        self.rootf("log/lead-estimates.json", json.dumps({"W2-170:build": {"hours": 0.25}}))
        self.dispatch("2026-11-11 18:32:04 started W2-170 (DAEO-61vm) b.md -> W2-170-A5-build.json (launcher exit 0)")
        self.rootf("log/W2-170-A5-build.json", "", "2026-11-11 18:32:04")
        self.status_json("2026-11-11 18:59:30", ["W2-170"])
        _, rows = self.ledger()
        r = rows[("W2-170", "build")]
        self.assertTrue(r["flag"])
        self.assertIn("No wait is recorded", r["flag_reason"])
        self.assertIn("the run's own working time", r["flag_reason"])      # no wait explains it: never guessed

    def test_a_stale_status_json_does_not_lose_a_run_without_a_return(self):
        self.dispatch("2026-11-11 18:32:04 started W2-170 (DAEO-61vm) b.md -> W2-170-A5-build.json (launcher exit 0)")
        self.rootf("log/W2-170-A5-build.json", "", "2026-11-11 18:32:04")
        self.status_json("2026-11-11 12:00:00", [])
        _, rows = self.ledger()
        self.assertEqual(rows[("W2-170", "build")]["status"], "RUNNING")
        self.assertIn("stale", rows[("W2-170", "build")]["running_source"])

    def test_brake_gap_note_and_merge_conflict(self):
        self.dispatch("2026-11-11 16:00:00 started W2-20 (DAEO-r30l) b.md -> W2-20-A5-run2.json (launcher exit 0)")
        self.lead_json("W2-20-A5-run2.json", "DONE", 1.0, 3600000, "2026-11-11 17:00:00",
                       extra="A merge conflict in two files was resolved.")
        self.status_json("2026-11-11 18:58:00", [])
        self.spend({"at": "2026-11-11 16:30", "kind": "brake", "wbs": "W2-20", "what": "runaway brake on W2-20"},
                   {"at": "2026-11-11 16:31", "kind": "brake-clear", "wbs": "W2-20", "what": "cleared"})
        self.w(os.path.join(self.root, "log/brake/cleared/W2-20-20261111-163106.json"), "{}")
        for n, a, b, dm in (("td-1", "16:05:00", "16:10:00", 300000), ("eng-1", "16:20:00", "16:50:00", 1800000)):
            self.wtlog("W2-20", n + ".pid", "1", f"2026-11-11 {a}")
            self.wtlog("W2-20", n + ".json", json.dumps({"result": "r", "total_cost_usd": 1.0, "duration_ms": dm}), f"2026-11-11 {b}")
            self.wtlog("W2-20", n + ".exit", "0", f"2026-11-11 {b}")
        self.rootf("log/lead-ledger-notes.jsonl", json.dumps(
            {"at": "2026-11-11 16:52", "W2": "W2-20", "run": "run2", "wait": "waiting on owner", "minutes": 8, "note": "asked about X"}) + "\n")
        _, rows = self.ledger()
        kinds = {w["kind"]: w for w in rows[("W2-20", "run2")]["waits"]}
        self.assertEqual(kinds["brake"]["minutes"], 1.1)               # 16:30 to the clear at 16:31:06
        self.assertEqual(kinds["gap between workers"]["cause"], "unattributed")
        self.assertEqual(kinds["gap between workers"]["minutes"], 10.0)    # 16:10 to 16:20
        self.assertEqual(kinds["waiting on owner"]["minutes"], 8)
        self.assertEqual(kinds["waiting on owner"]["source"], "CTO note")
        self.assertIsNone(kinds["merge conflict"]["minutes"])             # named, minutes not recorded
        self.assertEqual(rows[("W2-20", "run2")]["phases_min"], {"tests": 5.0, "build": 30.0})

    def test_no_merge_conflict_wait_when_the_return_says_there_was_none(self):
        self.dispatch("2026-11-11 16:00:00 started W2-20 (DAEO-r30l) b.md -> W2-20-A5-run2.json (launcher exit 0)")
        self.lead_json("W2-20-A5-run2.json", "DONE", 1.0, 3600000, "2026-11-11 17:00:00", extra="There was no merge conflict.")
        self.status_json("2026-11-11 18:58:00", [])
        _, rows = self.ledger()
        self.assertFalse([w for w in rows[("W2-20", "run2")]["waits"] if w["kind"] == "merge conflict"])

    def test_spend_only_worker_when_its_log_is_gone(self):
        self.dispatch("2026-11-11 16:00:00 started W2-20 (DAEO-r30l) b.md -> W2-20-A5-run2.json (launcher exit 0)")
        self.lead_json("W2-20-A5-run2.json", "DONE", 1.0, 3600000, "2026-11-11 17:00:00")
        self.status_json("2026-11-11 18:58:00", [])
        self.spend({"at": "2026-11-11 16:40", "kind": "launched", "wbs": "W2-20", "cost_usd": 3.5,
                    "extra": {"log": "/gone/rev-1.json", "num_turns": 30}})
        _, rows = self.ledger()
        r = rows[("W2-20", "run2")]
        self.assertEqual(r["cost"]["workers_usd"], 3.5)
        self.assertEqual(r["workers"][0]["source"], "spend.jsonl")
        self.assertEqual(r["rev_rounds"], 1)

    def test_since_filter_and_a_return_log_no_start_names(self):
        self.dispatch("2026-11-10 09:00:00 started W2-20 (DAEO-r30l) b.md -> W2-20-A5-old.json (launcher exit 0)",
                      "2026-11-11 16:00:00 started W2-20 (DAEO-r30l) b.md -> W2-20-A5-run2.json (launcher exit 0)")
        self.lead_json("W2-20-A5-old.json", "DONE", 1.0, 1000, "2026-11-10 09:10:00")
        self.lead_json("W2-20-A5-run2.json", "DONE", 1.0, 1000, "2026-11-11 16:10:00")
        self.lead_json("W2-31-A5-chained.json", "DONE", 2.0, 600000, "2026-11-11 12:10:00")   # nobody logged its start
        self.status_json("2026-11-11 18:58:00", [])
        _, rows = self.ledger()
        self.assertEqual(sorted(k[1] for k in rows), ["chained", "run2"])
        self.assertEqual(rows[("W2-31", "chained")]["start"], "2026-11-11 12:00:00")     # end less duration_ms
        self.assertEqual(rows[("W2-31", "chained")]["start_source"], "return log only")
        _, rows_all = self.ledger(since="2000-01-01")
        self.assertIn(("W2-20", "old"), rows_all)


class TestCliAndReadOnly(Fixture):
    def digest(self, d):
        h = hashlib.sha256()
        for base, _, files in sorted(os.walk(d)):
            for f in sorted(files):
                p = os.path.join(base, f)
                h.update(p.encode())
                h.update(open(p, "rb").read())
                h.update(str(os.stat(p).st_mtime_ns).encode())
        return h.hexdigest()

    def test_cli_writes_only_its_jsonl_rebuilt_whole_and_prints_the_table(self):
        self.rootf("log/lead-estimates.json", json.dumps({"W2-170:tests": {"hours": 0.25}}))
        self.dispatch("2026-11-11 17:54:06 started W2-170 (DAEO-61vm) t2.md -> W2-170-A5-tests2.json (launcher exit 0)")
        self.lead_json("W2-170-A5-tests2.json", "DONE", 2.02, 1966447, "2026-11-11 18:29:35")
        self.status_json("2026-11-11 18:58:00", [])
        out = os.path.join(self.tmp.name, "ledger.jsonl")
        open(out, "w").write("stale line\n" * 5)
        before = self.digest(self.root), self.digest(self.wt)
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = L.main(["--root", self.root, "--wt", self.wt, "--out", out, "--since", "2026-11-11T00:00",
                         "--now", "2026-11-11T19:00", "--md"])
        self.assertEqual(rc, 0)
        self.assertEqual(before, (self.digest(self.root), self.digest(self.wt)))       # nothing else touched
        lines = open(out).read().splitlines()
        self.assertEqual(len(lines), 1)                                                # rebuilt whole
        self.assertEqual(json.loads(lines[0])["run"], "tests2")
        table = buf.getvalue()
        self.assertIn("| W2 | run | start | end | status |", table)
        self.assertIn("FLAG", table)
        self.assertIn("W2-170 tests2: elapsed", table)
        self.assertIn("td-* = tests", table)

    def test_bad_since_is_refused(self):
        self.assertEqual(L.main(["--root", self.root, "--wt", self.wt, "--since", "garbage", "--no-write"]), 2)


class TestSampler(unittest.TestCase):
    def fake_proc(self, base, wt, procs):
        for pid, cwd, rss in procs:
            d = os.path.join(base, str(pid))
            os.makedirs(d)
            os.symlink(cwd, os.path.join(d, "cwd"))
            open(os.path.join(d, "status"), "w").write(f"Name:\tx\nVmRSS:\t{rss} kB\n")

    def test_owner_of(self):
        self.assertEqual(M.owner_of("W2-170-tests", ["W2-170"]), "W2-170")
        self.assertEqual(M.owner_of("W2-129-d6-tests", ["W2-129-d6", "W2-129"]), "W2-129-d6")
        self.assertEqual(M.owner_of("W2-129-d6", []), "W2-129")
        self.assertEqual(M.owner_of("W2-61h", []), "W2-61h")
        self.assertIsNone(M.owner_of("research-retrieval", []))
        self.assertIsNone(M.owner_of("EMG-queue", []))

    def test_sample_sums_rss_by_cwd_never_by_name(self):
        with tempfile.TemporaryDirectory() as d:
            wt, proc = os.path.join(d, "wt"), os.path.join(d, "proc")
            os.makedirs(proc)
            self.fake_proc(proc, wt, [(11, wt + "/W2-170", 300), (12, wt + "/W2-170-tests/src", 200),
                                      (13, wt + "/W2-04", 100), (14, wt + "/W2-00-store", 999),
                                      (15, d + "/elsewhere", 777), (16, wt + "/research-retrieval", 50)])
            open(os.path.join(proc, "abc"), "w").write("not a pid")
            got = M.sample(wt, ["W2-170"], proc)
            self.assertEqual(got, {"W2-170": {"kb": 500, "procs": 2}, "W2-04": {"kb": 100, "procs": 1}})
            got = M.sample(wt, ["W2-170", "W2-00"], proc)
            self.assertEqual(got["W2-00"], {"kb": 999, "procs": 1})        # listed in status.json: counted

    def test_make_row_lists_a_status_lead_with_no_process_and_an_empty_sample(self):
        with tempfile.TemporaryDirectory() as d:
            sj = os.path.join(d, "status.json")
            json.dump({"leads": ["W2-170"]}, open(sj, "w"))
            proc = os.path.join(d, "proc")
            os.makedirs(proc)
            row = M.make_row(os.path.join(d, "wt"), sj, now=0, proc=proc)
            self.assertEqual(row["at"], "1970-01-01 00:00:00")
            self.assertEqual(row["leads"]["W2-170"], {"mb": 0, "kb": 0, "procs": 0, "in_status": True})
            os.remove(sj)
            self.assertEqual(M.make_row(os.path.join(d, "wt"), sj, proc=proc)["leads"], {})

    def test_append_rotates_at_the_bound_and_keeps_one_old_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "w.jsonl")
            for i in range(40):
                M.append(p, {"i": i, "pad": "x" * 100}, 1000)
            self.assertTrue(os.path.exists(p + ".1"))
            self.assertFalse(os.path.exists(p + ".2"))
            self.assertLess(os.path.getsize(p), 1200)
            rows = [json.loads(l) for f in (p + ".1", p) for l in open(f)]
            self.assertEqual(rows[-1]["i"], 39)

    def test_main_count_writes_samples_and_removes_its_pidfile(self):
        with tempfile.TemporaryDirectory() as d:
            out, pidf = os.path.join(d, "o.jsonl"), os.path.join(d, "p.pid")
            rc = M.main(["--count", "2", "--every", "0.01", "--out", out, "--pidfile", pidf,
                         "--wt", os.path.join(d, "wt"), "--status-json", os.path.join(d, "none.json")])
            self.assertEqual(rc, 0)
            self.assertEqual(len(open(out).read().splitlines()), 2)
            self.assertFalse(os.path.exists(pidf))

    def test_ledger_reads_the_samplers_file(self):
        class F(Fixture):
            def runTest(self):
                pass
        f = F()
        f.setUp()
        try:
            f.dispatch("2026-11-11 18:32:04 started W2-170 (DAEO-61vm) b.md -> W2-170-A5-build.json (launcher exit 0)")
            f.lead_json("W2-170-A5-build.json", "DONE", 1.0, 600000, "2026-11-11 18:42:00")
            f.status_json("2026-11-11 18:58:00", [])
            f.rootf("log/lead-mem-watch.jsonl", json.dumps({"at": "2026-11-11 18:35:00", "avail_mb": 1,
                                                           "leads": {"W2-170": {"mb": 812, "kb": 1, "procs": 3, "in_status": True}}}) + "\n")
            _, rows = f.ledger()
            m = rows[("W2-170", "build")]["mem"]
            self.assertEqual((m["peak_mb"], m["source"]), (812, "lead-mem-watch"))
        finally:
            f.tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
