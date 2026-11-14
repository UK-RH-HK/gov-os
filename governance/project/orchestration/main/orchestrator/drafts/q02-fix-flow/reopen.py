#!/usr/bin/env python3
"""Apply W2-94's reopen (DEC-1180 (3)) to .tickets/DAEO-g87r.md: status, allowed_paths, KPIs S6-S12, F4-F6, a paragraph."""
import re, sys
p = sys.argv[1]
t = open(p, encoding="utf-8").read()
t = t.replace("status: closed\n", "status: in_progress\n", 1)
t = t.replace("- fixtures/evaluation/examin/hidden/**\n",
              "- fixtures/evaluation/examin/hidden/**\n"
              "- governance/project/orchestration/tools/indep_launch.py  # the one-question fix flow (reopen 2026-11-14, DEC-1180 (3))\n"
              "- tests/unit/orchestration/test_w2_94_fix_flow_unit.py  # the engineer's unit tests of the fix flow\n", 1)
S = [
 "S6 A writer round 2 run with `--fix <id> --reason <code>` (`--kind writer --round 2` only; `<id>` matches `q` and two digits; `<code>` is one of check_gold.py's per-question failure codes SOURCE_IS_SCAFFOLD, SOURCE_PATH_ABSENT, SOURCE_NOT_TEXT, SPAN_OUT_OF_FILE, HEADING_NOT_FOUND, ANSWER_NOT_IN_SPANS, NONEXISTENT_NAME_FOUND, NONEXISTENT_NO_NAME) is the one-question fix flow; either flag alone, another kind or round, a bad id or an unknown code refuses 17 with nothing built. Verify: planted runs of each wrong form, exit 17, no wall and no run folder made",
 "S7 The fix flow stages exactly three inputs: `input/<id>.yaml` (a byte copy of the set's `hidden/<id>.yaml`; absent or a link refuses 10), `input/verdict.txt` (the one line `<id> <code>`), and `input/sample.json` (`{\"sample\": [...]}`, the ordered `sample` list of the selection staged in the latest delivered round-1 writer run of the same set, read from that run's own record; none found refuses 10); besides the wall's fixed files, nothing else of the set or the sets root is staged (no `input/set/`, no `input/notes.md`). Verify: a planted set of several questions, the wall's file list and bytes after staging",
 "S8 The fix flow delivers only `out/<id>.yaml`: a plain file whose YAML parses to a mapping with `id` equal to `<id>`, else 20 and nothing lands; any file in `out/` other than it, `result.json` and `conflicts.md` refuses 20. On delivery it replaces `hidden/<id>.yaml` alone; every other file under the set's folder (both halves, `DRAW.txt`, `hidden/dropped/`, any `XCHECK-r*.md`, the release record) is byte-unchanged; the replaced file is packed into the run's archive and removed from the set. Verify: sha256 of every planted file before and after; the archive holds the old file",
 "S9 The fix flow's result is the writer schema's (`questions`, `by_kind`, `by_area`, optional `stopped`) plus `action`, one of `corrected` or `replaced`; `questions` is 1 and each of `by_kind` and `by_area` sums to 1, else 20; a stopped result delivers nothing (21, as today). The counts object records `fix: {\"id\": <id>, \"code\": <code>, \"action\": <action>}` and nothing of the question's content. Verify: planted results of each wrong form; the counts object's keys",
 "S10 The owner's approved variant (`EXAMIN-writer-q02-fix.md`, sha256 0703aebf69522cbb853d77f4e134e03843f1d961307b46c77ceaa575fa469173) launches through the fix flow end to end, byte for byte unchanged, on a planted sets root and launch clone with the fake session: its front matter is accepted as written. Verify: the planted end-to-end run, exit 0, the delivered file in place",
 "S11 The script's docstring gains the fix flow's usage line; `governance/project/indep-walls/**` and `governance/project/indep-briefs/**` are unchanged (the owner's class O). Verify: `git diff --stat` of the branch names only the ticket's paths",
 "S12 Without `--fix`, every existing flow behaves as before. Verify: the W2-149, W2-173 and W2-178 launcher unit suites pass unchanged",
]
F = [
 "F4 A hidden file other than the fixed question reaches the fix flow's wall, its result or its counts. Verify: S7's planted wall listing; a grep of the counts object for planted content markers",
 "F5 A fix run changes, moves or removes any set file other than `hidden/<id>.yaml`, or leaves the set changed after a refusal. Verify: S8's sha256 comparison, also after a planted refusal at delivery",
 "F6 The fix flow needs a change to the approved variant's bytes or to the walls' class O files to run. Verify: S10 runs the variant at its approved sha256; S11's diff",
]
m = re.search(r"\n  failure:\n", t)
ins = "".join("  - '" + s.replace("'", "''") + "'\n" for s in S)
t = t[:m.start()] + "\n" + ins.rstrip("\n") + t[m.start():]
m = re.search(r"\nprofile: ", t)
ins = "".join("  - '" + s.replace("'", "''") + "'\n" for s in F)
t = t[:m.start()] + "\n" + ins.rstrip("\n") + t[m.start():]
t = t.replace("- DEC-957\n", "- DEC-957\n- DEC-1175\n- DEC-1178\n- DEC-1180\n", 1)
t = t.rstrip("\n") + "\n\n" + (
 "**Reopened 2026-11-14 (DEC-1180 (3), the owner's P-Q02-RUN-1 (a): \"run today, as soon as it is built and reviewed\").** "
 "Hidden question q02 fails the gold check (ANSWER_NOT_IN_SPANS). The owner approved the writer's fix variant 0703aebf (DEC-1178 (5)), "
 "but the launch script's writer round 2 stages the whole set plus a checker's notes (EXAMIN's round 1 had none) and replaces the "
 "whole hidden folder, so the variant cannot run. S6-S12 add a one-question fix flow to `indep_launch.py`, which changes by a ticket "
 "(the class rules' catch-all), not an ACT; the walls' `kinds.yaml` and the briefs stay unchanged. After the land, the owner's operator "
 "installs the variant (its APPROVED line), commits it into the launch clone, runs the fix flow and `check_gold.py` (expected 20 of 20). "
 "No checker run: round 1 had none (FOR-THE-OWNER C8), and `check_gold` is the bar. The same flow can later carry the weekly re-anchor "
 "request (DECIDED-NOT-DONE row 203).\n")
open(p, "w", encoding="utf-8").write(t)
print("ok")
