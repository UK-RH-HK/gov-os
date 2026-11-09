# W2-56 — the independent test designer's brief, a small revision: the S9 real case (DAEO-wnnz)

You are the independent test designer for **W2-56** (`.tickets/DAEO-wnnz.md`). The second half's tests are on
`w2/W2-56-tests` at `72f2433f0` (`tests/acceptance/W2-56/`, README first). The CTO ran your four real cases outside the
sandbox with `GOV_W2_56_REAL=1` and a short `TMPDIR` (`/tmp/w56r.XXXX`; under a long TMPDIR the CLI's sandbox cannot
start: "Failed to create bridge sockets after 5 attempts", its bridge socket path too long). Results, on integrate's
code:
- `test_s2_real_sandbox_…`: **passed**.
- `test_s7_real_sandbox_…`: red, a product reason (in the sandbox the placeholder `.bash_profile` is a character
  device: `git add -A` fails "can only add regular files"). Keep it.
- `test_s13_real_sandbox_…`: red, a product reason (`gov rebuild` cannot remove `.gov-runtime/rebuild/stores.json`:
  read-only). Keep it.
- `test_s9_real_sandbox_a_second_unix_socket_is_refused`: **a test bug**: the planted script `elsewhere/socket.py`
  shadows Python's standard `socket` module, so the session's command exits 1 before it tries anything.

## Your job
1. Fix the S9 real case: name the planted script so it shadows nothing (and run it with `python3 -I` if that suits);
   keep its claim. If its planted socket path can be too long (it skipped once under a long TMPDIR), make it short
   (for example under a `mkdtemp(dir="/tmp")` folder the test removes), so it does not skip outside the sandbox.
2. In the README: the real cases need a short `TMPDIR` (say why); record the CTO's run above in the real cases'
   section; and **the CTO's settled points** below, in "Notes and decisions to take":
   - **D-11 settled (a):** `rerank.log` on the write list, made by the launcher if missing, never a link.
   - **D-12 settled as recommended:** a shorter launcher temp folder keeping the `gov-launch-` prefix; the daemon folders
     at the launcher's folder, found from `CLAUDE_CODE_TMPDIR`.
   - **D-13 measured by the CTO (2026-11-09, `claude -p` haiku, a planted socket server):** with
     `network.allowUnixSockets: [<the one path>]` the sandboxed command's connect is refused `PermissionError [Errno 1]`,
     exactly as with no allow; with `allowAllUnixSockets: true` it connects. On Linux a one-path allow does not open the
     socket. S8's settings-level form (the one path, nothing wider) is still built: inert on Linux, honoured where
     the CLI supports it; S8's reach and S10 on Linux go to the owner as a DEC-105 choice. Your S8 cases stay as written.
   - **D-14:** not added to W2-56's paths now (it matters only once a socket can be reached); carried with D-13.
3. Do not change any other case.

## Where you work and rules
- `/home/usain/gov-os-worktrees/W2-56-tests`, branch `w2/W2-56-tests`; write only `tests/acceptance/W2-56/`.
- Your record is your session's **final message**, in full (the launcher keeps it).
- Never read this ticket's implementation: never open, grep or list the engineer's worktree (base name `W2-56`,
  `/home/usain/gov-os-worktrees/W2-56`) or the branch `w2/W2-56`; keep every search inside your own worktree.
- You cannot run the real cases in your sandbox; run the file once to show it collects and skips cleanly
  (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-56-tests/src`, through the heavy slot `EMG-common.md` names). Then
  `python3 -m gov.cli.main accept W2-56 --root /home/usain/gov-os-worktrees/W2-56-tests` once: the counts as before.
- No GPU, model, network or installs. The hidden-half rule: never open anything under `~/gov-os-eval/` or
  `~/gov-os-runs/`, nor any `hidden`, `memory-verdict` or `memory-verdict-2` folder. DEC-1080: Read and Grep tools,
  one simple command per Bash call. Search again once (DEC-1092 (1)).
- **Commit** on `w2/W2-56-tests` with
  `--trailer "Task: DAEO-wnnz" --trailer "Implements: DEC-1112" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished. Waits and stops by pid only.

## Return
The twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first), the change, the commit, `gov accept`'s
counts, and `TESTS-READY <head>`.
