"""The R3 narrow check's probe record: the lead's judgement, then the reviewer's return as returned."""
import json
L = "/home/usain/gov-os-worktrees/W2-42a/.gov-runtime/scratch/lead/log/"
OUT = "/home/usain/gov-os-worktrees/W2-42a/docs/probes/DAEO-03ub/PR-DAEO-03ub-r3.md"
r = json.load(open(L + "a6.json"))["result"]
front = """---
type: probe
task: DAEO-03ub
reviewer_session: f309b71b-2755-4f92-b864-c2faf18d8764
implementer_session: f09387c1-5b62-4ec7-8753-0bd972964efb
test_designer_session: 9c627295-3d73-422f-ae54-1433a10edef4
test_designer_map_session: b1c454d2-5477-4712-94f9-d2a7a97f642b
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: df74680150bb6add79ec8976a803488d3511ace5
base_commit: d3ba8e50b4c6e703eafa41093b580af87a336fe1
decisions_applied: [DEC-1164, DEC-1174, DEC-1154, DEC-409, DEC-958, DEC-1028, DEC-136, DEC-968, DEC-808]
---

# Probe record: W2-42a (DAEO-03ub), the narrow independent check of the R3 fix (DEC-1164 (18), DEC-1154)

## The lead's judgement

- **What was checked.** Only the change d3ba8e50b..df7468015 (d3ba8e50b merged w2/integrate into the branch): the
  test designers' merge ed77eb353 (tests/acceptance/W2-42a/test_w2_42a_here_string.py, 31 cases, red 12 on d3ba8e50b:
  5 write arguments after a here-string, 7 fallback fail-opens; README map rows) and the engineer's df7468015
  (src/gov/guard/bash_writes.py, src/gov/guard/decide.py, tests/unit/guard/test_w2_42a_here_string.py,
  docs/changes/W2-42a-evidence.md), against the CTO's reopening of 2026-11-14 (R3 and the unreadable fallback's
  here-string forms: the word after `<<<` is the here-string's text, never the command's end; the words after it stay
  the command's arguments; the text given to `bash <<<`/`sh <<<` is judged as a command; anything still unreadable
  fails closed; read-only forms stay free), DEC-409, and fail-closed. This is the CTO's own P2 round
  (DEC-1164 (18)) landed on a narrow independent check (DEC-1154); it is not a review round under DEC-1010.
- **Who probed.** A fresh read-only independent auditor (claude-opus-5-5, high), launched by the ticket lead with
  `launch_worker.sh`; brief `.gov-runtime/scratch/lead/r5/a6.md` (JUDGEMENT.md word for word); log
  `.gov-runtime/scratch/lead/log/a6.json`. Its tripwire is clean; `git status` empty.
- **At this head:** `gov accept W2-42a` 914 passed, 0 failed, 2 skipped, all 13 KPI lines pass; the scoped set with the
  opt-in tiers collected (GOV_TESTS_OPTIN=lifted,breadth: tests/unit/guard, tests/acceptance/W2-42a, tests/unit/hooks,
  DEC-409's cases in tests/unit/pause, tests/unit/containment/test_w1_50_freeze_flag.py, tests/acceptance/W1-50,
  W1-28, W2-16) 3834 passed, 2 xfailed, 6 failed, the 6 being W2-33's fixture copy
  (`tests/acceptance/W2-33/w2_33_support.py:376`; 4 in W1-50, 2 in W1-28), the same 6 as in the previous round,
  outside the guard and this change.
- **The verdict block, as returned:** R3, FALLBACK, DEC409 and FC pass; **RO fails** on F1 (in scope, ordinary work
  yes, consequence other: read-only here-strings with a variable or substituted text, such as `read -r a <<< "$v"`,
  `while read -r f; do …; done <<< "$(git status --porcelain)"`, `mapfile`/`readarray`, `sed`/`awk`/`bc <<< "$v"`,
  are now refused as the unresolvable target where d3ba8e50b allowed them; bash_writes.py:1778). It fails closed.
- **READY, by code (JUDGEMENT.md: only "yes" with "fails open" or "loses work" fails the probe).** No finding is in
  scope, ordinary work yes and fails open or loses work. F1 refuses ordinary work and the live hook is to copy this
  parser (DEC-1174 (1)), so it goes to the CTO to decide: a narrow follow-up before the live-hook ACT, or a row.
- **Rows (recorded, not a round; ordinary work no):**
  - F2 (FALLBACK, in scope, fails open, not worse than the base): xargs's output piped on to a shell
    (`xargs <<< 'touch T' | sh`) is not judged.
  - F3 (FC, out of scope, older, fails open): `eval "$(cat <<< 'touch T')"`, `eval "$(echo touch T)"`,
    `echo 'touch T' | xargs echo | sh`.
  - F4 (FALLBACK, in scope, other: fails closed): xargs option spellings the reading does not know (`-rn1`,
    `--max-args 1`, `-e`, `-l`, `-i`) are refused, also for an allowed path.
  - F5 (R3, out of scope, other): `tee 0<<< x …` is refused naming the target `0`, on both commits.
  - The lead's probe also saw `python3 <<< "open('T','w')"` and `parallel touch <<< T` allowed on both commits (the
    first answered as `python3 <<EOF` is, KPI 8; the second an unknown runner).
- **Judgement: pass.**

## The reviewer's record (as returned)

"""
open(OUT, "w").write(front + r.rstrip() + "\n")
print("written", OUT, r.count("```verdict"))
