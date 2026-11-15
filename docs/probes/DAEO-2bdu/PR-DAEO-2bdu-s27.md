---
type: probe
task: DAEO-2bdu
round: "run 9: S27's folder mode, its own round (DEC-1183 (2)); first review of this change"
reviewer_session: 07e99b1e-4833-4559-b487-c6c9328890bd
implementer_session: "eng-16 2af017c2-0927-4d56-8051-766913960f7d (folder mode); test designer td-19 ee989d8c-eb38-4b38-b879-969d9fd2c5df, td-20 fd6dc7b7-d3c5-423c-a0ac-10fa9ac1c54c"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: pass
probed_commit: d26814f32a0a4d95ff2d5ad0934ba5bd082f8403
decisions_applied: [DEC-1183, DEC-1178, DEC-1010, DEC-136, DEC-820, DEC-1052, DEC-1154, DEC-1065, DEC-1142]
---

# Probe record: W2-88 (DAEO-2bdu), run 9: S27's folder mode (DEC-1183 (2)): PASS

## The lead's judgement and triage
- **Who checked.** A fresh, read-only Independent Auditor (`07e99b1e-4833-4559-b487-c6c9328890bd`, claude-opus-5-5, effort high, started through `launch_worker.sh` / `gov launch` under the OS sandbox on 2026-11-15 18:44 with `--owner-named DEC-1183`, the promotion "a fail-open finding" applying), its brief carrying `governance/project/briefs/JUDGEMENT.md` word for word (`.gov-runtime/scratch/lead/briefs/rv-s27.md`). Its tripwire shows no change in this ticket's trees.
- **The verdict stands as PASS** (success-27, failure-2, failure-6). No fail-open was found: 489 planted texts judged both ways against the one-per-file form at `301708296` gave equal verdicts, across read edges, sniffed heads, duplicates, nine allowlist-shaped temporary folders and three widths.
- **S27-1** (in scope, ordinary work yes, consequence other; not blocking): a batch's folder outlives a scan ended by SIGTERM or SIGKILL, holding plaintext copies of the batch's texts in the user's own 0700 temporary folder. The lead brings it as a package with options (a row, or a fix round with a test-design batch first, DEC-136), recommending the row as the reviewer does.
- **R-1, R-2** (notes, ordinary work no): `gitleaks dir` judging an unreadable file clean, and the `ustar`@256 / `DICM`@127 skip in both forms (the engineer's discovery, confirmed not caused by folder mode for `indexable`): proposed as Wave 3 rows.
- **The lead's verification at the head (outside the sandbox):**
  - the S27 acceptance modules (`test_w2_88_scan_folder.py`, `test_w2_88_scan_speed.py`) at `d26814f32a0a`: **38 passed** (`.gov-runtime/scratch/lead/log/acc-s27-9b.txt`); the 5,000-file case: 9.4 files/s before (500 paths), 1,421.3 files/s after (5,000 paths), ratio 151.5, pool 6;
  - `gov accept W2-88` at `d26814f32a0a`: **311 passed, 0 failed, 0 skipped**, every mapped line pass, success-27 38 of 38 (`log/accept-13.txt`; it was still running, so empty, when the reviewer looked);
  - the timing on a planted 36,000-file tree (371 planted secret files; the record of clean results off): folder mode 36,000 files in 37.3 s (966.0 files/s, pool 1), every planted secret file left out, no clean file left out; the one-per-file form (`301708296`) 1,000 sampled files in 608.3 s (1.64 files/s); **ratio 587.7**, the same verdict on the sample (`log/time36k-9.txt`);
  - the scoped lead_verify at `56eb0c3db064` (before td-20): 7,405 tests, 5 failed (four were the recording wrapper's, fixed by td-20 `cded8398b`; one is `tests/unit/secrets_check/test_dec1045_switch.py::test_on_the_filter_gives_every_governance_file_to_gitleaks`, outside the allowed paths, routed to the CTO as a path case), serial 49 passed (`log/verify-9a-56eb0c3/`).

## The reviewer's return (unchanged)

task: DAEO-2bdu (W2-88), run 9: independent review of S27's folder mode (DEC-1183 (2)) at d26814f32a0a4d95ff2d5ad0934ba5bd082f8403
status: DONE. S27, F2 and F6 pass. I found no fail-open. There is one in-scope "other" finding (S27-1, not blocking) and two rows for Wave 3.
work_completed: Read the change, the interface (with item 5b), the evidence section and the lead's logs. Built planted sets and judged each file both ways: by folder mode and by the base's one-per-file form, used as the oracle. That was 489 texts across three sets, nine TMPDIR paths named like default allowlisted paths, three batch widths, and nine archive-magic cases. Probed a timeout, an unreadable file, SIGTERM, CPU use and F6. Re-ran the folder acceptance module and the change's unit tests at the head.
files_changed: none
evidence: the probe scripts and results are in my sandbox TMPDIR, `/tmp/gov-launch-sa6ty1ru/claude-1000/aud/` (gen.py, gen2.py, gen4.py, run.py, cmp.py, tmo.py, term.py, cpu.py, and new*/old*.json). The lead's logs are under `.gov-runtime/scratch/lead/log/`.
tests: `test_w2_88_scan_folder.py` + `tests/unit/secrets/test_w2_88_folder.py` + `tests/unit/adopt/test_w2_88_folder_assess.py` + `tests/unit/secrets/test_w2_88_scan.py`, through heavy_slot with `-n 4`: **76 passed in 172 s**. I did not re-run `test_w2_88_scan_speed.py`, because nothing has changed in it since the lead's acc-s27-9 run, where it passed. No real-model case was involved.
discoveries: (1) `gitleaks dir` skips a file it cannot read with exit 0, an empty report and no stderr. (2) SIGTERM, as sent by `timeout`, leaves a batch's folder and its plaintext texts in TMPDIR. (3) The `ustar`@256 / `DICM`@127 skip needs no NUL byte, so an ordinary-looking text file is skipped. Both forms do this. In the assessment, folder mode now exposes every file to it, where the joined base form exposed only each batch's first file.
risks: low. A run killed by SIGTERM or SIGKILL leaves copies of secret-holding repository texts in the user's own 0700 temporary folder.
lessons: An oracle comparison on planted sets, swept over read-boundary offsets and TMPDIR paths, settles the "can a file be marked clean" question directly. It is quick: about 5 s for 176 files in folder mode against about 20 s for the old form.
proposed_decisions: none
unresolved: `accept-13.txt` (the lead's `gov accept W2-88` log) is 0 bytes, so I could not judge it. The lead's scoped lead_verify ran at 56eb0c3, not at the head. Its 4 S27 failures were in the recording wrapper (fixed by cded8398b; 76 passed in my run at the head). The 5th failure is the routed `test_dec1045_switch` case.
recommended_next_action: Merge on this verdict once the lead's `gov accept W2-88` at the head is recorded. Carry S27-1 and rows R-1 and R-2 as rows; they ride along in the next resume, or go to the Wave 3 pass.

Sandbox check (reported first): (a) the guard hook refused the `python3 open(...'/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-2bdu','w')` call before it reached the OS sandbox ("a reviewer or auditor writes only its own review…", DEC-953 item 2). The file does not exist (`ls`: no such file). I did not retry it or work around it. (b) `git hash-object -w --stdin` gave 1ae28402… (exit 0) and `git update-index --refresh` exited 0. `ps` showed no ollama or llama-server process, at the start and at the end.

# W2-88 (DAEO-2bdu): review of S27's folder mode (DEC-1183 (2))
probed_commit: d26814f32a0a4d95ff2d5ad0934ba5bd082f8403
base: 301708296479

## Sandbox and identity
- `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-2bdu`, at the start and at the end.
- HEAD is d26814f32a0a4d95ff2d5ad0934ba5bd082f8403 at the start and at the end. `git status --porcelain` is empty at the start and at the end.
- Step 0: (a) was refused by the guard hook, not the sandbox, and the file was not written. (b) passed. The `ps` check is clean.
- All probes ran in `/tmp/gov-launch-sa6ty1ru/claude-1000/aud/`. No `gov-secrets-*` folder is left behind except the ones I made on purpose for the SIGTERM probe, which I deleted afterwards.

## S27
| item of the line | met | file:line | how probed |
|---|---|---|---|
| Each batch's texts go into a private temporary folder outside the repository (0700; files 0600) | yes | `src/gov/secrets/__init__.py:314-323` (`_outside`), `:340`, `:352-366` | Acceptance case `…folder_is_private_outside_the_root…` passed in my run. The TMPDIR-inside-root refusal case passed. I also ran with nine TMPDIRs. |
| The folder is removed after the batch | yes on a normal exit, a raise, a timeout or a gitleaks failure; not on SIGTERM or SIGKILL (S27-1) | `:343-350` | Timeout probe: a stand-in gitleaks that sleeps gives `RuntimeError: …TimeoutExpired`, and the folder is gone. SIGTERM probe: the folder and file `0` remain. |
| One `gitleaks dir` per batch and rule set | yes | `:384-388` (`dir .` with `cwd` the folder, item 5b) | The code. The lead's `many_texts_are_judged_per_gitleaks_process` passed in acc-s27-9. |
| Each finding names its own file, so none can cover or hide another file's | yes | `:396-411` | Oracle comparison: every file's verdict was equal to the one-per-file form's, on 489 texts and 64+ planted secrets, at widths 1, 3 and 4. The sets included 12 duplicate texts (6 holding a secret, 6 clean) and keys at 147 offsets around 25 k/100 k/200 k. They also had 56 MB files, 2 MB single lines, UTF-16, NULs, invalid UTF-8, CR/CRLF/FF, PNG/PDF/zip/gz/ELF heads, `gitleaks:allow`, and commit hashes (exempt and not). |
| Path allowlists cannot apply | yes | `:387` (`cwd`), `:375-377` (listing check) | Equal verdicts with TMPDIR under `node_modules/`, `venv/lib/`, `gitleaks.toml/`, `pic.png`, `vendor/modules.txt.d`, `go.sum`, `.git/`, `deps/a/b/c`. |
| Fails closed | yes | `:379-411`, `:551-557` | Timeout probe (above). The acceptance fail/garbage/foreign cases passed in my run. |
| Batches run in parallel within the CPU set and the thread budget (W2-20 S18) | yes | `:452-468`, `:547-549` | The code and the lead's parallel case. One `gitleaks dir` over 1,000 files used 1.4 to 2.2 CPUs, inside its CPU set (a note, below). |
| 36,000 files at least 10 times faster, each planted secret found in its own file | yes | the lead's `time36k-9.txt` | 966 files/s against 1.64: a ratio of 587.7. 371 secret files, `secret_kept: []`, `clean_left_out_n: 0`, same verdict on the sample. |
| Same findings as the one-per-file form | yes | `:426-434` (`_held`) | Oracle comparison (above). |
| Record of clean results: only no-finding texts remembered, `_FORM` 7 | yes | `:64`, `:528-540` | The code. An exempt hash or `unreadable-report` is never remembered, and the form is part of the engine's fingerprint (`cache.py:113-114`). |
| `assess._Scan` uses the same core | yes | `src/gov/adopt/assess.py:156-202`, `:328` | The code. The unit cases and the P1R-1 curl acceptance case passed in my run. |
| F2: nothing written in the repository | yes | `:314-323` | The acceptance case (temporary folder inside the root is refused by name). Each batch's folder lies only in the resolved TMPDIR. |
| F6: no secret's value in any record, log or output | yes | `:405`, `:418-423`; messages hold exit codes and type names only | A gitleaks scan (values redacted) of the evidence file, the change's tests and sources, acc-s27-9.*, time36k-9.*, and the verify parallel/serial logs. It found only 4 `curl-auth-user` hits, all on templates whose values are run-time placeholders built from parts. |

## What I probed and found sound
- **Verdict per file against the oracle.** I tested every item of the brief's list: reads cut across large files, binary and archive sniffing, size limits (56 MB files, own batch), duplicate content, deduplication, `File` spelling (the bare number with `dir .`), the report at exit 0 and 3, gitleaks failing or timing out in one batch, and the commit-hash exemption (an exact project commit is exempt in both forms, upper case too; a commit hash plus a real key is held). In every case folder mode gave the oracle's verdict.
- **The folder's own path cannot shelter a file**, thanks to item 5b: nine allowlist-shaped TMPDIRs all gave equal verdicts.
- **Symlinks, hidden files, `.gitleaksignore`, `.gitleaks.toml`:** only numbered regular files are written (`O_EXCL|O_NOFOLLOW`), and any other entry in the folder makes the batch raise (`:375-377`). The rules come from `GITLEAKS_CONFIG_TOML`.
- **The engineer's `ustar`/`DICM` discovery is right for `indexable`.** Both forms skip all six variants I planted (NUL and no NUL, POSIX/GNU magic, text around them). Folder mode does not cause it. One nuance concerns the assessment; it is in R-2.
- **Fail-closed paths:** a timeout raises and removes the folder. An exit-3 report that cannot be placed puts `unreadable-report` on every text, and no such text is remembered. When one batch raises, the batches not yet started are cancelled, and the running ones finish and clean up.
- **Test independence (DEC-430/DEC-959 item 7):** the acceptance commits 5d6e56319 and cded8398b are `Role: independent-test-designer` and touch only `tests/acceptance/W2-88/**`. The engineer's three commits touch no acceptance test.

## Findings

**S27-1 (success-27, item "removed after"; severity low).** What is wrong: when the scanning process is ended by SIGTERM (a `timeout` wrapper, a session ended by its harness) or by SIGKILL, the batch's folder is not removed. It still holds plaintext copies of the batch's texts, the secret-holding ones among them. The one-per-file form passed texts on stdin and left nothing on disk. How to reproduce: put a stand-in `gitleaks` that sleeps 30 s first on `PATH`, run `_Folder(root)`, `add`, `judge` under `timeout -s TERM 3`, and look in TMPDIR: `gov-secrets-XXXX/0` remains. Behaviour it should have: no batch folder outlives its scan. For example, the next scan sweeps stale `gov-secrets-*` folders whose owning process is gone, or the scan handles SIGTERM, or the folder lives in a memory-backed place. The repository already holds the same bytes, and the folder is 0700 under the same user, so the added exposure is small.
`Ordinary work: yes, because agents routinely wrap long runs in timeout and sessions are ended by their harness mid-run`
`Consequence: other` (no text is let through or indexed and nothing is lost; plaintext copies remain in the user's own private temporary folder)

## Notes, not findings
- **R-1 (row, Wave 3).** `gitleaks dir` skips a file it cannot read with exit 0, `[]` and nothing on stderr (probed with a 0000-mode file). Folder mode would then judge that text clean and remember it. The files are this process's own, mode 0600, in a fresh 0700 folder, so only a deliberate act or a TMPDIR cleaner firing in the scan's own second can cause it. `Ordinary work: no, because the batch's files are written by the scan itself 0600 in a fresh private folder seconds before gitleaks reads them` · `Consequence: fails open`. A cheap guard: check each file is readable just before the run, or compare gitleaks' scanned count, if the version reports one.
- **R-2 (row, Wave 3; the lead's package outside S27).** gitleaks treats a text as an archive and skips it when `ustar` sits at content offset 256 or `DICM` at 127, with or without NUL bytes. This happens in both forms. The assessment's joined base form exposed only the first text of each 1 MB batch to it; folder mode exposes every text. That base form, though, is the one that failed P1R-1. Possible fix: a leading frame of 263 or more newlines instead of one, so no content byte can land at offsets 128 or 257. `Ordinary work: no, because a text file must hold those exact bytes at exactly that offset` · `Consequence: fails open`.
- One `gitleaks dir` runs about 1.4 to 2.2 CPUs of goroutines, so `_workers()` processes can use somewhat more threads than the budget. The CPU set still bounds them. This is load only.
- The assessment's `_Scan` judges its batches one after another, not in parallel. S27's measure is on `indexable`, and the assessment is still fast (about 0.7 s per 1,000-text batch).
- The lead's timing ran with `pool: 1`, so the 587× ratio comes without parallel width.
- `accept-13.txt` is empty, and the lead_verify ran at 56eb0c3, not at the head. These are for the lead's record.

```verdict
{"kpis": [{"kpi": "success-27", "verdict": "pass", "findings": [{"id": "S27-1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "failure-2", "verdict": "pass", "findings": []}, {"kpi": "failure-6", "verdict": "pass", "findings": []}], "overall": "pass"}
```
