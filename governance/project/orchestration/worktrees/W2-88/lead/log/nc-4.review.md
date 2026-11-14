task: DAEO-2bdu (W2-88), the narrow re-check of P1-1's fix (S27) at d766514fd
status: DONE. The fix closes P1-1 as reproduced, but S27 still fails on one new blocker, P1R-1: the same kind of secret let through, by two other default rules the `#` fence does not stop.
work_completed: Step 0 and the identity checks; read the diff ef9c773c3..d766514fd, the three commits' scope and trailers, and the ticket's sources and allowed_paths; extracted gitleaks 8.30.1's built-in default rules and read every rule whose classes cross lines; ran 1,404 batch cases against a23678e27's one-per-file verdict with real gitleaks; ran end-to-end checks on 12 planted files with the base, the head twice and a form-4 record; ran two direct probes of `_scan_batch`; re-measured speed on a 5,000-file tree; ran the ticket's secrets unit tests.
files_changed: none (`git status --porcelain` was empty at the end)
evidence: everything is under my TMPDIR `/tmp/gov-launch-nnl0_kx6/claude-1000/p1r/`: `gen.py` and `cases.json` (the cases), `run2.py`, `cmp2.py`, `oracle.json`, `out_head_*.json` (the pair probe), `e2e.py` (end to end), `curl.py` and `pk.py` (the direct probes), `speed.py`, `default.toml` (gitleaks' built-in rules, taken from the binary), and the exports `base/` (a23678e27) and `ef9/` (ef9c773c3)
tests: `tests/unit/secrets/test_w2_88_scan.py` through heavy_slot with `-m "not local_only" -k "not real and not green_here and not time_limit"`: 17 passed in 188.5 s, and the filter deselected none. I ran no acceptance cases: the lead's `accept-8.txt` was still empty when I finished, and `verify-8.txt` did not exist.
discoveries: P1R-1. The fence stops the value classes of the generic-key rules, but two default rules can still cross it. `curl-auth-user` has a gap of up to five lines that takes in `#`; `private-key` has a body class that takes in anything. When the matching text is then dropped by a filter (the rule's own allowlist, or the global allowlist's `false`), it still swallows the next file's own secret, and that file is judged clean and recorded clean.
risks: The wrong "clean" verdict is written to the reuse record under HOME. A second run in the same HOME answered the curl case from that record (0 scanned, 12 remembered).
lessons: The fix's premise "no rule's value class takes in `#`" holds only for the generic-key rules. The rules that span lines (curl-auth-user and curl-auth-header up to five line breaks, private-key without limit) need a separation that their line reach cannot cross, or a check that does not rely on the report.
proposed_decisions: none
unresolved: I did not reproduce the evidence's absolute speed of 119.8 files/s: my run was under full machine load, with all 3 slots taken. The ratio of at least 10 holds in my run (27.7 times).
recommended_next_action: The engineer closes P1R-1 within `src/gov/secrets/__init__.py`, so each file's verdict is again the one-per-file form's for curl-auth-user's line reach and the private-key body. The test designer adds the two shapes as cases, with the one-per-file form as the oracle. Then S27 gets one more narrow re-check. This is the second review round under DEC-1010; if it still blocks after that, it goes to the owner once.

# W2-88 (DAEO-2bdu): narrow re-check of P1-1's fix (S27)
probed_commit: d766514fd651b6b463d628625feee431e9faffd4
base: ef9c773c3

## Sandbox and identity
- Step 0 (EMG-d4b-launched.md):
  - (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-2bdu` failed with `OSError: [Errno 30] Read-only file system`, and the file does not exist.
  - (b) `git hash-object -w --stdin` (exit 0, object 1ae28402a) and `git update-index --refresh` (exit 0) both worked. This wrote one loose object, as the launcher's check requires; the status stayed empty.
- `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-2bdu`.
- HEAD was d766514fd651b6b463d628625feee431e9faffd4 and the status empty, at the start and at the end.
- `ps` showed no ollama or llama-server process at the end.
- Refusals: the deny rule refused one `sed` that named the ticket through a relative path. I read the ticket with Grep and awk from the main repository instead; the `sed` form was not retried.
- heavy_slot could not write its waits log (read-only), which is harmless; it waited once for a free slot.

## P1-1
| item of the stated behaviour | status | file:line | how probed |
|---|---|---|---|
| A file ending in a bare generic key (`password:`, `token =`, `secret:`, `token:` plus blank lines, no final newline, CRLF, `\r`, a last line of `#`) does not swallow the next file's generic-api-key secret | fixed | src/gov/secrets/__init__.py:306,319 | 26 tails × 17 heads in the orders AB, BA, C-A-B-D and the middle of 16 (1,404 cases), head's `indexable` against a23678e27's verdict per file: every generic-key case is equal |
| The pair in both orders; in a long batch with the pair in the middle | fixed | same | the same cases ("ba", "mid") |
| End to end on 12 planted files, as the checker ran it | fixed | same | `e2e.py p11`: the base and the head both leave out `config/11-prod.env` and keep 11 of 12 |
| A finding is put back on every file its StartLine to EndLine covers, and on the file after | fixed | :338-350 | unit cases; direct probe: a reported cross-file match (curl-auth-user from line 4 to 9) gives owners [0, 1] |
| The `_FORM` change: form-4 records are not reused | fixed | :61 | ef9c773c3 (form 4) wrote all 12 clean in a HOME; the head in the same HOME re-scanned all 12 and left out `11-prod.env` |
| A second run in the same HOME gives the same verdict | fixed | cache use :199-216 | second head run: same 11 of 12 (1 scanned, 11 remembered) |
| The fence stops every rule of the project's `.gitleaks.toml` from running into the next text | **not met** (P1R-1) | :301-306 | `curl.py` and `pk.py`: curl-auth-user and private-key cross `#\n\n`; once filtered out, the match hides the next file's secret |

## What I probed and found sound
1. **Scope:** d766514fd touches only `src/gov/secrets/__init__.py`, `tests/unit/secrets/test_w2_88_scan.py` and `docs/changes/W2-88-evidence.md`, all in allowed_paths. a4eff2312 and e66a9cb58 touch only `tests/acceptance/W2-88/`. All three carry `Task: DAEO-2bdu`. Their `Implements:` ids (DEC-954, CAP-44.b, CAP-44.f, CAP-17, CAP-20) are all in the ticket's `sources:` (ticket lines 87-132).
2. **The fence on the generic-key rules:** in `default.toml` (gitleaks' built-in rules), generic-api-key's separator, operator and value classes (`[\s'"]`, `[\x60'"\s=]`, `[\w.=-]`, `[a-z0-9+/]`) contain no `#`. In 1,404 cases no generic-key tail crossed it, including a last line of `#`, no final newline, CRLF and a bare `\r`.
3. **No false positive brought in:** in all 1,404 cases the batch never left out a file the one-per-file form keeps. That includes heads that begin with `#`, a bare value on B's first line after `password:`, and blank-line heads.
4. **Other rules:** private-key (head after any tail), curl-auth-header (lazy) and the canary rule gave equal verdicts in the pair probe. kubernetes-secret-yaml has a `path` filter, so it never fires on standard input.
5. **Oracle check:** a23678e27 catches all 14 planted heads alone and none of the 26 tails or 3 clean files (`oracle.json`: 14 of 59).
6. **S27 ratio:** `speed.py` through heavy_slot at `GOV_HEAVY_THREAD_BUDGET=1`, with `GOV_SECRETS_CACHE` empty:
   - head: 5,000 files in 100.3 s (49.9 files/s), all 100 planted files left out;
   - a23678e27: every 20th file, 250 in 139.0 s (1.8 files/s);
   - ratio 27.7 times, so at least 10 holds. Lower absolute figures than the evidence's (119.8 files/s) because all 3 slots were busy.
7. **Tests:**
   - e66a9cb58's cases plant exactly P1-1. They first prove with real gitleaks that B alone is caught by generic-api-key only and A alone by nothing, use the base's one-per-file form as the oracle, and assert on two calls in the same HOME. They assert the stated behaviour.
   - The new unit tests cover the pair in both orders, 4×4 tails and heads, the middle of 16, the case without the fence and a form-4 record: 17 passed.
   - The one changed unit assertion (`len(alone) == 2`, the file after the owner is scanned too) matches the fix.
8. **a4eff2312:**
   - No assertion is removed: the diff deletes 0 `assert` lines. Only `archive()` and `before_src` change, from exporting the whole tree to named paths.
   - The named paths (`src`, `pyproject.toml`, `copier.yml`, `template`, `governance/project/retrieval.yaml`, `indep-walls`, `MEMORY-AUDIT-1/briefs`) do not include `governance/project/held-out.yaml`, and none of those folders contains a held-out file.
   - `git -C <folder> archive` exports that folder alone, as my own export of `src` confirmed.

## Findings
**P1R-1** (success-27, severity **blocker**): a match that runs over the fence and is then dropped by a filter still swallows the next file's secret.
- **What is wrong:**
  - The fence `#\n\n` stops only value classes that refuse `#`. Two default rules take it in:
    - curl-auth-user's gap `(?:.*|.*(?:[\r\n]{1,2}.*){1,5})` crosses up to five line breaks and any byte;
    - private-key's body `[\s\S-]{64,}?` crosses anything.
  - If file A ends in a `curl` line with no `-u`, the greedy match runs from A's `curl` to the farthest `-u` within reach in file B.
  - If that `-u` is one the rule's allowlist drops (`user:$PASSWORD`), gitleaks reports nothing. The match still consumed B's earlier real `curl -u deploy:<password>`, so B is judged clean and recorded clean in the reuse record.
  - The private-key shape is similar: A holds a bare `-----BEGIN RSA PRIVATE KEY-----` line, then a line containing `false`. The match runs to B's own header and is dropped by the global allowlist's unanchored `false`, so B's key goes unreported.
  - The evidence's "Fix 3" and the comment at :301-305 ("no rule's value class takes in it") are therefore wrong for these rules.
- **Reproduce:**
  - Pair probe (`cmp2.py`): 9 of 1,404 cases differ, all the same shape. A's last line is `curl https://api.example.com/health` (also with a trailing `\` or `-s … \`); B is `curl -u <user:pw> …`, then `echo ok`, then `curl -u user:$PASSWORD …`; in the orders AB, C-A-B-D and the middle of 16. The batch keeps B; the one-per-file form leaves it out.
  - Direct probe (`curl.py`): with A's curl on its last line, the batch report is empty and owners is []; B alone is caught. With A's curl on its second-to-last line, it is reported (lines 3 to 9) and handled.
  - End to end (`e2e.py curl`, 12 files): a23678e27 leaves out `config/11-deploy.sh`; the head keeps all 12. A second head run in the same HOME answers from the record (0 scanned, 12 remembered) and keeps it again.
  - Private key (`pk.py`): order A then PEM gives `alone [False, True]` and `batch owners []`.
- **Behaviour it should have:** each file's verdict is the one-per-file form's for every rule of the project's `.gitleaks.toml`, the rules that span lines included. A separation must be one that no rule's line or byte reach can cross, or the result must be checked without relying on what gitleaks reports. A test-designer case should plant the curl pair and the private-key pair.
- What would reverse it: the moderator judging that a file ending in a curl example, followed in path order by a script with a hard-coded `curl -u` credential and an allowlisted `-u` within its first three or four lines, is an unusual construction. That would make it a row, not a blocker.
- Ordinary work: yes, because it needs no construction: a README or doc ending in a `curl` example, followed in path order by a deploy script that holds a hard-coded basic-auth credential and, a line or two later, a `$PASSWORD` curl, is ordinary content in a repository being adopted. It is rare, as P1-1 was, and is an accident of the same kind.
- Consequence: fails open (a file holding a secret is judged indexable, and the wrong clean verdict persists in the machine-wide reuse record).

## Notes, not findings
- The private-key shape (an unterminated BEGIN header, then `false`, before the next file's key) is much rarer than the curl shape. I list it under P1R-1 as a second reproduction, not as a finding of its own. Ordinary work: no on its own, because a bare private-key header followed by `false` and then a real key file next in path order is unusual. Consequence: fails open.
- The evidence's re-measure extrapolates the old form from 250 files (it says so). My independent figures give 27.7 times at budget 1 under load, so "at least 10 times" holds as written. The evidence's "the verdicts are the same" holds on its own planted tree, not in general (P1R-1). Ordinary work: yes, because every reader of the evidence relies on it. Consequence: other.
- The lead's `accept-8.txt` was empty and `verify-8.txt` absent while I worked. `verify/` holds files from 16:51 to 17:18, before d766514fd was committed (18:02). Ordinary work: yes. Consequence: other (the record's results are the lead's to attach).
- e66a9cb58's cases and the new unit tests plant only the generic-key shape, so they could not catch P1R-1. Ordinary work: yes. Consequence: other.

```verdict
{"kpis": [{"kpi": "success-27", "verdict": "fail", "findings": [{"id": "P1R-1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]}], "overall": "fail"}
```