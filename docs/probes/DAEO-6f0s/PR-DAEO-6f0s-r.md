---
type: probe
task: DAEO-6f0s
check: "narrow independent check of R1-R3 after the reopening (DEC-1154; the CTO under DEC-1180 (4)); not a review round (DEC-1010)"
reviewer_session: 7fa5e020-b064-4384-b7eb-bb47b6ff6ca0
implementer_session: fddda06e-4efb-484e-8335-6d322d560d40, cee1beef-a9fe-4ce9-8989-4aa186043e0a
reviewer_wrote_nothing: true
commissioned_by: orchestrator (the W2-184 ticket lead)
judged_by: orchestrator (the W2-184 ticket lead)
judgement: pass
probed_commit: 90e657a3583bf4e8edfd40e69a0591e981097dfa
base_commit: bbe1510f899b4599222a1cfc6939bf13b5350222
---

# Narrow check of DAEO-6f0s (W2-184) R1-R3: judgement pass

- **Head checked:** 90e657a3583bf4e8edfd40e69a0591e981097dfa (branch w2/W2-184). The change is the diff from bbe1510f899b4599222a1cfc6939bf13b5350222.
- **Session:** role independent-auditor, model claude-opus-5-5, effort high. Fresh session, wrote none of the audited files.
- **Step 0 (the sandbox check, launch_worker.sh):** (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-184` failed (`OSError: [Errno 30] Read-only file system`) and no file was left. (b) `git hash-object -w --stdin` worked (1ae28402a…), and so did `git update-index --refresh` (exit 0).
- **What I ran.** Everything ran in `$TMPDIR/aud`, with `HOME` set to an empty scratch folder:
  - `git archive` copies of the head and the base.
  - The two R unit files on the head copy (`test_w2_184_r_fixes.py` and `test_w2_184_r_engineer.py`): 81 passed.
  - Seven mutants of the head copy, each run against the matching R cases.
  - The three R3/F1 acceptance cases on the head copy and on the R3 mutant.
  - Four probe scripts: `probe_r2.py` (a kill or an `OSError` injected at each step), `probe_r2_race.py` (writers racing readers), `probe_r3.py` (`launcher._promotion` over three roots, run on both head and base) and `test_probe_r1.py` (`gov launch` through the W2-184 fixtures).
  - No whole suite was re-run. Nothing under the evaluation sets or any hidden folder was opened.
- **Independence (MR-3, DEC-430):**
  - The test designer's commit 19324ca4b touches only `tests/acceptance/W2-184/**` and `tests/unit/launch/test_w2_184_r_fixes.py`. It carries `Role: independent-test-designer` and `Rewrite-Reason: DEC-1180 (4), rv-f1 F3`.
  - The engineer's commits f2f76a154 and 90e657a35 touch no file under `tests/acceptance/`.

## Findings

**F1 (R2): a folder whose file system has no hard links refuses every worker launch, and there is no fallback.**
`record.write` (`src/gov/launch/record.py:115`) uses only `os.link`. There is no rename fallback; the ticket's R2 line allows "linked or renamed", but interface 10.2 prescribes the link. I probed by injecting `EPERM` and `EXDEV` at `os.link`. Each time the write refused with "the launch record cannot be written in <folder>" and the folder was left empty: no final-name file and no `.tmp`.

So the code still never overwrites, and it fails closed. Before the change, such a file system could write records; now a launch there is refused, naming the folder. Nothing refused before becomes allowed.

What would reverse this: a supported setup whose main checkout's `.gov-runtime/launches/` sits on a file system without hard links.
- Ordinary work: no, because the record folder lies in the main checkout on the local disk, and every common local file system supports hard links.
- Consequence: other (fails closed: the launch is refused naming the folder; nothing opens and no work is lost).
- Scope: in

**F2 (R2): if the temporary file cannot be removed after the link, a whole record can stay behind under a refusal.**
This is the branch at `record.py:123-127`. When `os.unlink(temporary)` fails, the code tries to remove the final name, then refuses. If that removal fails too, a whole `<session_id>.json` and its `.tmp` stay behind while the launch is refused. I injected the fault by making every `os.unlink` raise `EACCES`, and the folder then held both files.

For an auditor launch on a FULL ticket, such a record would count toward 6.1's review count. Interface 10.2 does not list this step. Separately, leftover `.tmp` files from killed launches are never cleaned up; they only clutter the folder and are read by nothing.

What would reverse this: an ordinary way for an unlink to fail in a folder where the same process has just created and linked a file.
- Ordinary work: no, because it needs the folder's permissions to change in the microseconds between the link and the unlink.
- Consequence: other (the launch is refused; at worst a stray whole record is left, not a partial one).
- Scope: in

**Probed and found sound:**

- **R1, through the CLI.** I tried `orchestrator` and `lead` with each of the following forms:

  | Option form | Result |
  |---|---|
  | `--reason=` | exit 2 |
  | `--trial=` | exit 2 |
  | `--owner-named=` | exit 2 |
  | `--owner-named garbage` | exit 2 |
  | each option alone, all three together, empty `--reason` (the test designer's cases) | exit 2 |
  | abbreviations (`--reas`, `--own`, `--tri`) | exit 2: argparse rejects them as unrecognized, so none can slip past |
  | `--reason x --plan` | exit 1 with the old "has no plan" refusal: `--plan` is unchanged |

  In every case: no CLI call, no launch record, and no `launch.log` line. The stderr message names each option given and includes "a lead launch … takes none of --reason, --trial and --owner-named".
  - The check in `command.py` runs before `launcher.launch`, and the launcher's own fence (`launcher.py:952-957`) runs before `_admit_lead`. So by reading the code, the gate is not consulted and no plan-override line can be logged; the test designer's shut-gate case confirms the gate part.
  - Unchanged: a lead without the options, the same words after `--`, and a worker launch with each option.
- **R2, kills.** I killed the writer with SIGKILL at the create, write, fsync, close, link and unlink steps.
  - It never left a final-name file that was empty or partial.
  - A kill before the link left only `.<sid>.<hex>.tmp`, and a later write of the same id succeeded.
  - A kill after the link left a whole record plus a `.tmp`, and a later write of the same id was refused as "already there".
- **R2, `OSError`s.** `ENOSPC` at the write, `EIO` at the fsync, and `EPERM` or `EXDEV` at the link: each refused and left neither file. A read-only folder refused and left nothing.
- **R2, existing final name.** An existing record, an empty file, or a dangling symlink at the final name: each was refused as "already there", and the existing file was left byte-for-byte unchanged.
- **R2, races.**
  - Twelve writers racing on one session id: exactly one won and its record parsed; the other eleven were refused as "already there"; no `.tmp` was left.
  - Four writers (1,600 records of about 20 KB) against three readers using `glob("*.json")`: 72,831 reads and 0 unparsable.
- **R2, readers.** The only readers of the record folder are `_launch_records` (`glob("*.json")`) and `record.original` (`<sid>.json`), and neither can take a `.tmp`. I found no other lister in `src/`, `scripts/`, `.claude/hooks/` or `governance/`.
- **R3, against base.** Each case gave the result interface 10.3 calls for, compared with base:

  | Case | Head | Base |
  |---|---|---|
  | Stale launch-root copy, fail-open copy under another root (also with three roots) | promoted, `a fail-open finding`, root-relative record | None |
  | Three differing failed copies of one path | None (one review) | None |
  | Identical failed copies under three roots | None (one review) | None |
  | Two paths failed, each only under another root | promoted, `two failed reviews` | None |
  | Bad YAML or a non-JSON verdict block in another root's copy | refused, naming `rel (path)` | None |
  | Fail-open in both 01 and 02 | 01 named, sorted path order | 01 named |

  The base never promotes or refuses where the head does not.
- **Nothing refused before becomes allowed.**
  - R1 adds refusals only.
  - R2's refusals (an existing name, including a dangling link, and any `OSError`) all still hold; its one new refusal is F1's.
  - R3 still reads the launch root's copy, so every promotion or refusal at base still happens at head.
- **The tests catch real faults.** Every mutant was caught:

  | Mutant | Caught by |
  |---|---|
  | No CLI lead check | 12 R1 cases failed |
  | No launcher fence | 6 failed |
  | Record written straight to the final name | 8 R2 cases failed |
  | `os.replace` instead of the link (overwrites) | 5 failed |
  | Temporary file named `*.json` | 3 failed |
  | First copy only (the old P-td5-2) | 5 R3 unit cases and 2 of the 3 revised acceptance cases failed |
  | Failed copies counted per copy | 1 failed |

## Per KPI line

- **R1: pass.** Both lead roles are refused with exit 2 for every option form, before the launcher, with nothing started or recorded and the required message. `launcher.launch` called directly with a lead role refuses with LAUNCH_REFUSED. Lead launches without the options, the words after `--`, `--plan` and worker launches are unchanged.
- **R2: pass.** The write goes to a temporary file, is fsynced, then hard-linked without overwriting, then the temporary file is removed. No kill or fault at any step left an empty or partial final-name file. Leftover temporary files are never read and never refuse a launch or a later write. Two writers end with one whole record and one "already there" refusal. A final-name file that is not JSON still refuses (the test designer's planted cases). F1 and F2 are recorded rows, not blocking.
- **R3: pass.** Every root's copy is read, and identical bytes count once. Any copy that refuses still refuses, naming the file. A path holds a fail-open finding or a failure if any of its copies does, and it counts as one review at most. The promotion's record is the root-relative path.

```verdict
{"kpis": [{"kpi": "R1", "verdict": "pass", "findings": []}, {"kpi": "R2", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "R3", "verdict": "pass", "findings": []}]}
```

judgement: pass

## The lead's triage (DEC-1010 item 1)

- No finding blocks: none is in scope with ordinary work yes and a consequence that fails open or loses work.
- F1 (no hard links in the record folder's file system: every worker launch refused, fails closed; ordinary work no)
  and F2 (an unlink failing in the microseconds after the link can leave a whole record under a refusal; ordinary work
  no, consequence other): for the CTO, who decides under DEC-1180 (4) whether they are fixed in this flow or are
  rows.
- The launch of this check: review_round 4, owner_named DEC-1180, model_source promotion (a fail-open finding,
  `docs/probes/DAEO-6f0s/PR-DAEO-6f0s-f1.md`), effort high (`after --`).
