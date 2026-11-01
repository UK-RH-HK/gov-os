"""DEC-970: the resume parts for W2-107, W2-96, W2-95, W2-05 and W2-67 (briefs/<W2>-part-resume-dec970.md)."""
from pathlib import Path

O = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
A = "tests/" + "acceptance"
heads = dict(line.split() for line in (O / "log/resume-heads-dec970.txt").read_text().splitlines() if line.strip())

COMMON = f"""
## How this resume runs (the common brief holds; these are the points that changed since your last run)
- **The work order (DEC-963 as the common brief now states it):** a test designer works in the tests worktree (`/home/usain/gov-os-worktrees/{{W2}}-tests`, retrieving only from the integration branch's store); **you merge its branch** into this worktree while no worker's command runs here (the engineer's sandbox mounts the acceptance tests read-only, so it cannot); then the engineer, or a fresh one, runs the acceptance tests once, reading results only. A merge takes no `--trailer`: use a message file (`-F`).
- **Verification (DEC-968):** the scoped set `select_tests.py` gives, run once before you return, in the close's form. Never the full suite: the nightly runs it. `verify_lock.sh` now waits for nothing (DEC-970: a scoped run does not wait for a full run's room). A case that fails and that your change did not cause (it fails on `w2/integrate` too) is named for the CTO, who deals with it at once; one your change caused is yours to fix.
- **Installs** are refused for you; raise any as a P1. Scratch: 20 GB and 1,000,000 files and folders for you and your workers, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-{{W2}}`.
- **Clean up before you return:** remove your temp folders (`/tmp/gov-os-lead-{{W2}}` and your workers' `/tmp/gov-launch-*` folders) and any worktree you added; if a removal is refused, name what is left. {{LEFT}}
- **Return:** the twelve fields, then `brief_gaps:` and `guard_refusals:` (each refusal with time, the command's form, the rule, true or false-positive, and its cost), status DONE or PACKAGES.
"""

PARTS = {
    "W2-107": ("DAEO-kiar", "gitleaks results remembered by content hash", "FULL", "W2-107-A5-run1.json",
               "`?? pytest-of-usain/` only (a leftover of your run 1: remove it first)",
               f"""## What DEC-970 decided for you, and what is left
- **P-W2-107-1 (a):** your unit path is now `tests/unit/secrets_check/test_w2_107*` (the ticket's `allowed_paths`, commit `cc2632ef`). A fresh engineer `git mv`s your two unit files from `tests/unit/secrets/` to `tests/unit/secrets_check/` and runs them; `tests/unit/secrets/` must not exist afterwards (W2-69's `test_the_unit_folder_named_secrets_is_gone`).
- **P-W2-107-2 (a):** a fresh independent test designer revises `{A}/W1-16/test_w1_16_home.py::test_no_index_file_exists_outside_gov_runtime_after_a_run` so it leaves out exactly the scan cache's file (`<HOME>/.cache/gov-os/secrets-scan.sqlite`) and its `-wal` and `-shm`, `Rewrite-Reason: DEC-967`, lowering nothing else (the cache's place outside the repository is the owner's approved design).
- **P-W2-107-3:** the scanned/remembered counts line in the rebuild's record is the orchestrator's at merge (W2-76 has merged); do nothing for it. The nightly's `GOV_SECRETS_FULL_SCAN=1` line is the orchestrator's too.
- **Review:** FULL, your second review passed in run 1. A fresh review only if the move or the test revision changes anything the filter decides (they should not); if neither does, say so and skip it.
- **Then:** the scoped run once; W2-69's and W1-16's cases green; your 43 acceptance cases green.
- **Residual rows** (R-A, R-B, R-D, R-E and the others of your run 1) go in your return for the Wave 3 list."""),
    "W2-96": ("DAEO-ouet", "the opaque acceptance runner, gov accept", "FULL", "W2-96-A5-run1.json",
              "nothing",
              f"""## What DEC-970 decided for you, and what is left
- **P-W2-96-CMDLIST (a):** `src/gov/check/commands.py` is in your paths for one line only, `accept` in `RECORDED_GOV_COMMANDS` (W2-16, W2-20 and W2-37 hold the rest of that file). A test designer adds `accept` to W1-07's support list of recorded commands and to W1-07's and W1-32's pinned command tuples (`{A}/W1-07/`, `{A}/W1-32/`), `Rewrite-Reason: DEC-959 item 6`.
- **PKG-1 (a):** any failed or errored case, mapped or not, fails the run (exit 3); unmapped cases are still only counted, never named. Stricter only.
- **PKG-2 (c):** N1 is answered by PKG-1 (a). N2 (hold Ctrl-C during clean-up), N5 (unlock without recursion), N7 (keep an inherited SIGHUP ignore) and N8 (exit 128+N after a held-back signal) ride along in this resume (DEC-802).
- **The tests first:** a test designer adds the cases PKG-1 (a) and the ride-alongs need (red first), in parallel with the engineer.
- **Review:** FULL. This resume is a new round: a fresh reviewer (brief A3, `JUDGEMENT.md`, effort max) on what changed (PKG-1, the ride-alongs, the command line), up to two reviews in this round (DEC-916).
- **Then:** the scoped run once; W1-07's and W1-32's command cases green.
- **P3, left from run 1:** if the empty `{A}/.claude/.cc-writes/` folder a review's sandbox made is still there, your test designer removes it (it is in the acceptance folder; git does not show an empty folder).
- **KPI 6** (the brief change naming `gov accept`) stays the orchestrator's at merge. Say which README map forms the reader takes (your run 1 found 19 of 70 acceptance READMEs map today)."""),
    "W2-95": ("DAEO-57hm", "core-pathmap checks what it says", "STANDARD", "W2-95-A5-run1.json", "nothing",
              f"""## What DEC-970 decided for you, and what is left
- **Package 1 (a):** a fresh independent test designer gives W1-30's planted path maps that write `namespaces: {{}}` one catch-all namespace (`paths: ["**"]`), lowering nothing, `Rewrite-Reason: DEC-959 item 9`: `{A}/W1-30/test_w1_30_r15_command_success.py`, `test_w1_30_r15_context_tickets.py`, `test_w1_30_r15_policy_pairs.py`, `test_w1_30_r16_context_own_tickets.py`, `w1_30_r15_support.py`, `w1_30_support.py`, and any other W1-30 file that writes an empty namespaces map (the files are named in your ticket's body; they are the test designer's, never in an implementer's allowed_paths).
- **Then (package 2):** the scoped run once, the 165 W1-30 cases green, and your 49 acceptance cases green; `gov check`'s core-pathmap GREEN on this worktree (your KPI 4: 2,601 tracked paths, 11 namespaces, none in none or two, on `w2/integrate` at `c07a1115577f`).
- **Your reading of "where the project declares one"** (a repository with `governance/project/` must have a path map; a folder without it is not judged): confirmed by the CTO as your ticket's meaning."""),
    "W2-05": ("DAEO-0z8c", "the git environment of every check, hook and helper; the settings re-sort", "FULL",
              "W2-05-A5-resume-dec954.json", "nothing",
              f"""## What DEC-970 decided for you, and what is left
- **Package I (b):** keep the test runs pinned, but give `GIT_CONFIG_GLOBAL` a generated file holding only the person's `user.name`, `user.email` and `init.defaultBranch` (lowest precedence, so trace settings stay out and W2-M161's case stays green). One engineer batch with its unit tests, then a short review of that batch only (FULL; a new round). The nightly's bisect pinned the same way is the orchestrator's (the nightly folder), to be done at merge: say exactly what it needs.
- **P-W2-05-DRIFT-BASE (P3):** a small test-designer edit: the matcher-drift case builds its base pair from one source, so it passes because of the matcher, not an event difference ACT 1 left; no expectation lowered.
- **Not in this resume:** package H (ACT 1 against DEC-805 item 2) and P-W2-05-R3-1 wait for the owner. Your merge waits for H, so after I, the DRIFT-BASE edit and the scoped run, return (PACKAGES naming H as the only thing left).
- **Then:** the scoped run once (your 70 targets; your `verify5.sh` and `rerun5.sh` from run 4 still fit, without any wait for the gate)."""),
    "W2-67": ("DAEO-9nys", "test hygiene", "FULL", "W2-67-A5-resume-dec954.json",
              f"`?? {A}/W1-27/w2_67_td4_plant.py` only (the plant file, kept under DEC-920 item 5)",
              f"""## What DEC-970 decided for you, and what is left
- **P-W2-67-R6-DISP (a):** a second test-design batch for the two-line fix: in `{A}/W1-30/test_w1_30_disposition.py::test_disposition_with_context_failure`, `DEC-cyc1`/`DEC-cyc2` become `DEC-9003`/`DEC-9004` (W2-64's fixture ids), `Rewrite-Reason: DEC-954 merge of W2-64`, lowering nothing. Then a short review of that fix only (FULL; a new round).
- **Then:** the scoped run once; W1-30 green.
- **Rows for your return:** rev-6 G1 and G2 (README-W2-67's wording), KPI 4's count of four base folders on a run with a red, F-A, F-B and W2-L446.
- **Leftovers of run 6 to remove:** `.gov-runtime/scratch/td-10/after-PF15.log` and `.gov-runtime/scratch/lead/briefs/rev-5.filled.md` in this worktree."""),
}

for w2, (tid, title, prof, prev, status, body) in PARTS.items():
    head = heads[w2]
    text = (f"You are the ticket lead for ticket `{tid}` (`{w2}`, \"{title}\"), profile {prof}, working only in the worktree "
            f"`/home/usain/gov-os-worktrees/{w2}` on branch `w2/{w2}`.\n\n"
            f"**This is a resume, under DEC-968 and DEC-970: read your lead checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md`, "
            f"first**, and your last return (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/{prev}`). "
            f"`git rev-parse --short=12 HEAD` must show `{head}` (the orchestrator merged `w2/integrate` in: ACT-GUARD-FIX-2, DEC-968 to DEC-970, "
            f"your ticket's DEC-970 edit), and `git status --short` must show {status}. Anything else: stop and return PACKAGES naming it.\n\n"
            + body + "\n" + COMMON.replace("{W2}", w2).replace("{LEFT}", ""))
    (O / f"briefs/{w2}-part-resume-dec970.md").write_text(text)
    print(w2, head, len(text))
