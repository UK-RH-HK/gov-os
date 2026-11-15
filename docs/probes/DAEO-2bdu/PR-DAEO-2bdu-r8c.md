---
type: probe
task: DAEO-2bdu
round: runs 8 and 8b narrow check of the runtime-path fallback (DEC-1154, the CTO's --owner-named DEC-1154; the CTO's P2 under DEC-338)
reviewer_session: ed99a094-8fc2-4763-9067-ffd6eb412a21
implementer_session: eng-13 ba629ed8-043d-4804-bbb2-8db35fe2c2be (the fallback); eng-14 955ac3d6-c6bc-40d1-ba03-33972b265650 (placement fixtures); eng-15 b72c10ea-df50-4595-a311-88b1813d849b (the nested-mark case's short base); test designer td-18 9b0fec8b-02d6-4930-9276-f0074da7b0c8 (the real-redis case's limit)
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: pass
probed_commit: c45fb6e1dce332b16b2abc60756c8232bd53490e
decisions_applied: [DEC-1154, DEC-338, DEC-1156, DEC-1185, DEC-1010, DEC-136, DEC-820, DEC-1052]
---

# Probe record: W2-88 (DAEO-2bdu), the narrow check of the runtime-path fallback: PASS

## The lead's judgement and triage

- **Why.** The lead's verify at b817f604c was red on one case, S25's real-redis case: first its A9 was cut by W2-124's 240 s limit (td-18, 162311d26: its own 2,400 s limit, the same call and session; the CTO read the diff as its narrow check), then the real tool did not start in the test's box: `config set ui_enabled false failed`. The lead proved the cause: the tool's runtime folder (`CBM_RUNTIME_DIR`, here `CODEINTEL_DAEMON_BASE` set by `w2_88_support.py:215` to a folder in the pytest box) passed the Unix socket path limit (a 147-byte runtime folder: `secure CLI coordination could not be created (endpoint)`; a short one works; the cache folder's length does not matter). The CTO decided (P2, delegated, under DEC-338): a fallback to `/tmp/gov-cbm-<uid>/<12 hex>` past the limit, else `CODEGRAPH_RUNTIME_PATH_TOO_LONG` (eng-13, 4ea9bc194); W2-56's placement fixtures raised `SOCKET_MAX` by the CTO's path route (eng-14, efb199ad4; d81ceb9b3); the nested-mark case's planted base made short (eng-15, c45fb6e1d, pre-approved by the CTO).
- **Who probed.** A fresh, read-only Independent Auditor (`ed99a094-8fc2-4763-9067-ffd6eb412a21`, claude-opus-5-5, high, C2, promoted), launched with `--owner-named DEC-1154`, at c45fb6e1d. Two earlier launches gave no check: nc-r8c ended at 04:50 on a note while its unit run waited for a heavy slot (the nightly held all three slots, DEC-1159 (1)); nc-r8c-2 was stopped by the lead at about 05:05 to take in eng-15's change. Its tripwire was clean; nc-r8c's tripwire change (the main tree's head d81ceb9b3d66 to 4aa66768f146 at about 04:31) is the CTO's own record commit (Task: DAEO-sdxk), as the CTO stated.
- **The lead's runs outside the sandbox:** S25's real-redis case alone at 4ea9bc194's code: 1 passed in 729.5 s (`log/alone-8c-redis.txt`); the code-graph acceptance lines and `tests/unit/codeintel` at c45fb6e1d: 102 passed, 0 failed, no `/tmp/cbm-n-*` left (`log/acc-cg-8c-2.txt`, `.xml`).
- **The verdict stands as PASS**, no finding. Its notes: N1 (the threshold counts `.sock.pending`, so runtime folders of 58 to 65 bytes also move; decided by the CTO), N2 (fallback folders in the shared place are not swept, as W2-67's known residual), N3 (the nested-mark case can only pass outside a launched sandbox; the sandbox profile should allow the short runtime root: a row), N4 (the A9 mapping is unit-tested at the mapper only), N5 (the length is counted on the path as given) are residuals and rows.

The reviewer's check follows, unchanged.

# W2-88 (DAEO-2bdu): narrow check of the runtime-path fallback (DEC-338, the CTO's P2)
probed_commit: c45fb6e1dce332b16b2abc60756c8232bd53490e
base: 90ab6d066

## Sandbox and identity
- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-2bdu','w')..."` failed as required (`[Errno 30] Read-only file system`), and no file exists.
- (b) `echo sandbox-trial | git hash-object -w --stdin` worked (`1ae28402a…`), and so did `git update-index --refresh` (exit 0).
- `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-2bdu`. HEAD was c45fb6e1dce332b16b2abc60756c8232bd53490e and `git status --porcelain` was empty, both at the start and at the end.
- No ollama or llama-server process is running (`ps` check empty).

## No path under the limit moved
I ran the same probe script under 90ab6d066's `src` (from `git archive`) and under the head's `src`. It covered each base a session can have:
- `CODEINTEL_DAEMON_BASE=/tmp/e…` (1 to 89 letters)
- a launched session `CLAUDE_CODE_TMPDIR=/tmp/gov-launch-<1 to 89 letters>/claude-1000`
- a test process's mark (a real mark file, pid ≠ self) naming `/tmp/m…` (1 to 89 letters)
- `DAEMON_BASE=/tmp/d…` (1 to 89 letters), plus the real default `/tmp/gov-cbm-1000`

Each base was tried with two roots, one short and one deep.

**Result:**
- All 251 placements whose socket (the rule's count, with `.sock.pending`) is ≤ 107 bytes are byte for byte 90ab6d066's: env 70, launch 40, mark 70, `DAEMON_BASE` 70, real default 1.
- All 462 placements over the limit moved to exactly `/tmp/gov-cbm-1000/` + the first 12 hex of sha256(realpath(old folder)). There were 0 mismatches, and the 462 distinct long folders gave 462 distinct short ones.
- Today's real bases are all well inside the limit: the default 34 bytes, this launched session's folder 45, `make_session_base` folders about 44 to 47.

## What I probed and found sound
- **Fallback (item 2).** `_placed` keeps the W2-56 folder whenever `socket_length(long) <= SOCKET_MAX`. Otherwise it gives `SHORT_BASE/<12 hex of sha256(realpath(long))>`. `_daemon_dir` makes the folder above and the folder itself 0700 and refuses a link or another owner, the same loop as before.
  - Probe: with a long base, a 0700 folder was made under a short base (parent 0700, socket 105 bytes), and the long folder was not made.
  - The length counted is the exact string given to the tool as `CBM_RUNTIME_DIR`.
- **Refusal (item 3).** If the short folder is still too long, or cannot be made (an OSError, a link, another owner), `_daemon_dir` raises `RuntimePathTooLong`. Its message starts with `CODEGRAPH_RUNTIME_PATH_TOO_LONG` and names the long folder, its socket length, the short folder, its length and the 107 limit. A link or wrong owner on a short base is never a silent fallback elsewhere.
  - End to end: `codeintel._graph(repo)` raised it before any tool start (length 224, limit 107).
  - `fabric.runtime_too_long` gives a `GovError` with code `CODEGRAPH_RUNTIME_PATH_TOO_LONG` and details `path, length, limit, long`.
  - In `fabric._stores` that except clause sits before the generic `except Exception`, so A9 raises the named code, not `unreadable` and not a bare `FABRIC_INCOMPLETE`. `index()` stages the files before calling the tool, so `code_i` is non-empty and the read is reached.
- **Unit cases (item 4).** `test_w2_88_runtime_path.py` asserts each stated behaviour:
  - the count, and the module's constant pinned at 107
  - a short base, and one exactly at 107, unchanged byte for byte
  - 108 bytes gives the 12-hex realpath folder
  - two long bases give two folders
  - 0700 creation
  - the refusal when still too long (path, length and 107 in the message), under a file, or through a link
  - the A9 mapping's code and details
- **Fixture change (item 4b).**
  - efb199ad4 only adds `monkeypatch.setattr(codeintel, "SOCKET_MAX", 4096)` to the autouse placement fixture of `test_codeintel.py` and to three placement cases of `test_w2_56_nested_daemon.py`. No assertion changed and no case was removed.
  - W2-56's own length assertions (`test_codeintel.py:125`, `:145`, `:161`, using `SOCKET_TAIL` from `:46`) compare against a literal 107, not `codeintel.SOCKET_MAX`, so the raised value does not loosen them.
  - `test_w2_88_runtime_path.py` does not raise it.
  - c45fb6e1d's nested case now plants `tempfile.mkdtemp(dir="/tmp", prefix="cbm-n-")`, removes it in `finally`, and keeps its assertion word for word.
- **Scope (item 5).**
  - 4ea9bc194 touches `docs/changes/W2-88-evidence.md`, `src/gov/adopt/fabric.py`, `src/gov/codeintel/__init__.py` and `tests/unit/codeintel/test_w2_88_runtime_path.py`, all in allowed_paths.
  - efb199ad4 and c45fb6e1d touch only the two W2-56 files, which d81ceb9b3 added to allowed_paths.
  - Each ticket commit carries `Task: DAEO-2bdu`.
  - The `Implements:` ids (DEC-954, CAP-44.b, CAP-44.f, CAP-17, CAP-20) are all in `sources:`. DEC-338 appears only as `Rewrite-Reason`.
  - d81ceb9b3 is the orchestrator's path-case edit of the ticket file.
  - efc3123 and 4d163c4 are other tasks' commits that came in with the w2/integrate merge f9687e363; both are on w2/integrate.

## Findings
None.

## Notes, not findings
- **N1 (conservative threshold).** The rule counts `.sock.pending` (50 bytes after the folder for uid 1000), but the measured `.sock` is 42. Runtime folders of 58 to 65 bytes, which would have worked at 90ab6d066, now take the fallback (64 of the 462 moved placements). This matches the engineer's stated rule and W2-56's existing count. No base a session has today is that long; only a hand-set deep `CODEINTEL_DAEMON_BASE` is. The fallback works there.
  - Ordinary work: no, because every base the code makes is 34 to 47 bytes.
  - Consequence: other (a working folder is replaced by another working folder).
- **N2 (fallback folders in the shared place).** In a test session with a long base, the short folder lies in the shared `/tmp/gov-cbm-<uid>`. The conftest's sweep never touches that place, so these folders are left behind like the default ones (W2-67's known residual). Isolation holds because each session's base hashes differently. The case's own clean-up follows `daemon_dir`, so it finds them.
  - Ordinary work: yes, because a test run with a deep base leaves one small folder.
  - Consequence: other.
- **N3 (eng-15's case in a sandbox).** The nested-mark case now writes to the real `/tmp`, so inside a launched sandbox it errors at setup (seen here). It can only pass outside. Without that change it would be red everywhere under the fallback, and no shorter writable place exists in the sandbox.
  - Ordinary work: yes, because a launched worker running the codeintel unit folder sees it red.
  - Consequence: other (a false red, never a false green).
- **N4 (A9 mapping is unit-tested only at the mapper).** `test_a9_shows_the_refusals_name` calls `fabric.runtime_too_long` directly; no unit case drives `_stores`. I confirmed the wiring by reading the code and by the `_graph` probe. In a repository with no graph-readable code files, the name would appear only in `FABRIC_INCOMPLETE`'s `reasons` (from the rebuild's `not_recreated` reason), not as the top-level code.
  - Ordinary work: no, because A9's code-graph route needs code files.
  - Consequence: other.
- **N5.** The length is counted on the path as given, not its realpath. That is the string the tool binds. A symlinked base that the tool resolves internally would differ, but nothing makes such a base.
  - Ordinary work: no.
  - Consequence: other.

```verdict
{"kpis": [{"kpi": "success-25", "verdict": "pass", "findings": []}, {"kpi": "success-28", "verdict": "pass", "findings": []}], "overall": "pass"}
```
