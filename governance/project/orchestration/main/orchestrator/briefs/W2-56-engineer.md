# W2-56 — the engineer's brief: `gov launch` usable for every worker, on the guard alone (DAEO-wnnz)

You are the engineer for **W2-56** (`.tickets/DAEO-wnnz.md`: read it in full, with "The first half's points settled"
and "The guard-alone outcome (DEC-1112 (1))"). The owner decided W2-56 builds on the path-map guard alone, with today's
launcher sandbox for workers unchanged (not generated from the path map). The acceptance cases are written (both
halves, by the independent test designer); the interface they assume is below, handed to you from the start (the spec,
not the tests). Build to it, keeping every KPI line. Where the interface and a KPI line disagree, the KPI line wins: say
so in your return.

**Your job:**
1. **The product** in your paths (`src/gov/launch/launcher.py` at its call sites and argument checks;
   `src/gov/launch/sandbox.py` and `src/gov/launch/environ.py` as new modules of your own; `src/gov/codeintel/__init__.py`
   for the daemon's folder only; `tests/conftest.py` for S1's two lines only, D-1): S1 (one daemon folder per test
   session, cleaned; the tool off PATH but in W1-16 and W1-20; a launched session's daemon folder under its own temp
   folder), S4 (no placeholder reaches a commit), S5 (the cleaned environment), S6 (the refused arguments), S7 (the
   short start lock), S8/S9 (the reranker's one socket, nothing else), S11 (a sandboxed unranked search counted), S12
   (signals to the group), S14 (the template's one allow rule in `template/governance/kernel/settings.json`, now in your
   paths, DEC-1083; the hooks stay), S15 (temp folders removed), F2 (every refusal today still refuses).
2. **Your unit tests** in `tests/unit/launch/**` and `tests/unit/codeintel/**` (`tests/unit/codeintel/test_codeintel.py`
   asserts today's `/tmp/gov-cbm-<uid>`: change it to the new place).
3. **The CIT-E** `docs/changes/W2-56-CIT-E.md`: how each allowed-path form is held (S3), the script-write gap (S2), the
   accepted-arguments list weighed against the refusal list (S6, lens E R6), S7's way, S11's way; S10's section is the
   CTO's (leave a heading).

## Where you work
- `/home/usain/gov-os-worktrees/W2-56`, branch `w2/W2-56` (from `w2/integrate`; the acceptance cases are merged in
  before you start). Your paths are the ticket's `allowed_paths`; a file you need outside them is a package in your
  return, not an edit.
- **You never read `tests/acceptance/`** (W2-56's, and W1-27's revised for this ticket; G-14, DEC-820 (c)): only
  `gov accept`'s results.
- **The exclusion line (DEC-1093 (2)), by base name:** every recursive grep carries `--exclude-dir=acceptance`; every
  Grep or Glob call that could reach it carries `!tests/acceptance/**`; find carries `-path '*/acceptance' -prune`;
  never open the test designer's worktree (base name `W2-56-tests`). If a search shows you a line of a case anyway,
  stop reading it and say so.

## Verify
- Through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-56/src` and `-m "not local_only" -k "not real and not green_here and not time_limit"`:
  your unit tests (`tests/unit/launch tests/unit/codeintel`); then
  `python3 -m gov.cli.main accept W2-56 --root /home/usain/gov-os-worktrees/W2-56` (counts per line; the real-sandbox
  cases skip here, the CTO runs them outside); then `accept W1-27` (its W2-67 cases); then `tests/unit/guard
  tests/unit/retrieval tests/unit/resources`, every red named with its cause. Never the full suite.
- **Commit as you go**, each part as it passes.

## Rules
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. Never touch the Ollama servers, the reranker service, `~/.local/bin`,
  `~/.ollama`, `~/.gov-os/`, `~/.cache/gov-os/` or any service; no GPU job; no installs.
- DEC-1080: Read and Grep tools; one simple command per Bash call; no `cd … &&` chains. Search again once
  (DEC-1092 (1)) if needed.
- Do not merge `w2/integrate`. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-56` with
  `--trailer "Task: DAEO-wnnz" --trailer "Implements: DEC-1112, DEC-799" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished. Waits and stops by pid only.

## Return
Your whole return is your session's **final message**, in full (the launcher keeps it; it is the record): the twelve
labelled fields of `EMG-common.md` (sandbox and `ps` checks first), what changed per KPI line, `gov accept`'s counts per
line for W2-56 and W1-27, the unit and regression counts with every red named, packages for files outside your paths,
and any place where the interface and a KPI line disagree.

---

# The interface the acceptance cases assume (the designer's README, as written)

## The interface these tests assume (for the engineer)

- **A refusal** exits non-zero, its output (stdout or stderr) says `LAUNCH_REFUSED` and names the refused argument
  as written before any `=` (for example `--mcp-config`), starts no session and leaves no `gov-launch-*` folder in
  the launcher's temp root. The refused arguments are refused in every position after `--`, alone, with a spaced
  value and in the `=` form; a prompt that only names one inside a longer word list is no argument and starts.
- **The environment** the launcher passes to the CLI process, and the `env` block of `--settings`: PATH (every
  entry of the parent's kept), HOME, LANG, LC_ALL, USER and LOGNAME as the parent's; TMPDIR and CLAUDE_CODE_TMPDIR
  one folder, the launcher's own, not the parent's TMPDIR; GOV_ROLE and GOV_TICKET, where present, the launched
  role and ticket (in `--settings` they must be, as today); no other parent CLAUDE* or GOV* variable, no
  PYTHONPATH, and no parent value under any other name. A parent variable that is none of the listed kinds does not
  pass either (`test_s5_an_unrelated_parent_variable_is_not_passed`: S5 read as the list of what passes). No test
  sets a sign-in variable.
- **The start lock** (or another way, S7) lets three launches made at once from three worktrees of one repository
  all start, lets their sessions run at the same time (a lock held for a session's whole life fails the test after
  25 s) and is gone afterwards (a fourth launch starts).
- **Signals:** the launcher, sent SIGTERM, SIGINT or SIGHUP at its own pid, ends the session's whole process group
  (a grandchild of the CLI is gone within END_WAIT_S + 5 s; one that ignores the signal is gone after the kill
  that follows END_WAIT_S), and still ends with 130 (DEC-392).
- **The session's temp folder** (its TMPDIR) is gone after every ending (exit 0, exit 3, the CLI killed by SIGKILL,
  each ending signal, a CLI that cannot be started), even when it holds folders its owner may not write (mode 0500,
  as a module cache leaves them), a fifo and a link to a file outside (removed as a link; the target is untouched).
- **Placeholders:** the names in `w2_56_support.PLACEHOLDERS`, planted as empty files while a session runs, are
  neither staged nor committed by `git add -A` or `git add .` and `git commit`, both by the worker inside the
  session (its environment) and by the caller in the same worktree while the session runs (the caller's
  environment); an ordinary new file beside them is committed, and so is `docs/gitconfig-notes.md`.
- **S1's suite half** holds in a plain `python3 -m pytest` session started at the repository's root (a conftest or
  the code index itself), not only under a runner: in a suite other than W1-16 and W1-20 `codebase-memory-mcp` is
  not on PATH at test time; the daemon folders of one session lie in one folder of its own, apart from another
  session's, gone when the session ends, and each is short enough for the tool's socket (107 bytes, DEC-338).
- **The template:** `template/governance/kernel/settings.json`'s `permissions.allow` is exactly
  `["Bash(gov launch:*)"]`, and its hooks stay.

### The second half's interface (DEC-1112 (1))

- **The sandbox block** of a worker's `--settings` (every worker role; a path entry is read with one leading `/`,
  so today's `//<absolute path>` and `/<absolute path>` are the same):
  - `sandbox` keys only from today's: `enabled` (true), `failIfUnavailable` (true), `allowUnsandboxedCommands`
    (false), `network`, `filesystem`; never `excludedCommands`, `enableWeakerNestedSandbox` or any other key.
  - `network` keys only `strictAllowlist` (true), `allowedDomains` (today's: empty, the research allowlist for
    research) and `allowUnixSockets`: exactly one entry, `<HOME>/.cache/gov-os/rerank.sock`, where `HOME` is the
    launcher's and the rest is `gov.retrieval.rerank`'s `CACHE_REL` and `SOCKET` (the service's own setting); no
    pattern, never the folder. No `allowAllUnixSockets`, `allowLocalBinding` or port key.
  - `filesystem` keys only `allowWrite` (and the narrowing `denyWrite`, `denyRead`). `allowWrite`: the session's
    temp folder (the `TMPDIR` the CLI is handed), exactly one run folder under `<HOME>/gov-os-runs`, and **S11's
    one log file** `<HOME>/.cache/gov-os/rerank.log` (`CACHE_REL` and `LOG`), nothing else: no entry from the
    ticket's allowed paths, none in the worktree, never `/tmp/gov-cbm-<uid>`. The settings are the same for two
    tickets whose allowed paths differ (but for the two folders), and name none of the allowed paths.
  - `permissions.deny` keeps today's literal rules: `Edit(//<root>/.gov-runtime/<name>)` for each entry of
    `.gov-runtime/` but `scratch` that exists at launch, none for `scratch`, and `Edit(//<root>/tests/acceptance)`
    for every role but the test designer.
- **Links (fail open if followed):** a `rerank.log` that is a link puts neither the link nor its target on the write
  list (and the target is untouched); a `rerank.sock` that is a link allows neither. The launch may refuse instead.
- **S11 (choice: one log file):** the log is a regular file when the session starts (the launcher makes it if it is
  missing: the sandbox cannot bind a file that is not there). A search in the session that the service does not
  answer leaves one FALLBACK line that `gov.retrieval.rerank.status()` (what `gov status` shows as `reranker`)
  counts. The decision package D-11 weighs the other way.
- **`sandbox_faults`:** `from gov.launch.launcher import sandbox_faults` still works; `sandbox_faults(settings)`
  returns a list of reasons, empty for the settings the launcher built, and non-empty for each of: `enabled` false,
  `failIfUnavailable` false, `allowUnsandboxedCommands` true, `strictAllowlist` false, `excludedCommands`,
  `allowAllUnixSockets`, a second Unix socket, another socket in the reranker's place, a socket pattern, the socket's
  folder, `allowLocalBinding`, `httpProxyPort`, `enableWeakerNestedSandbox`. It is called in a process whose `HOME`
  is the launcher's (the reranker's socket is read from it).
- **The guard** (`template/governance/kernel/hooks/pretooluse.py`, copied into the fixture project, event JSON on
  stdin, `GOV_ROLE` and `GOV_TICKET` set): for every worker role, a `Write` or `Edit` outside the ticket's paths and a
  Bash write it names (`>`, `tee`, `cp`, `touch`, `mv`, `sed -i`, a path in another worktree) are refused; a write
  inside each role's scope is allowed. A name pattern `tests/unit/test_batch*` lets `tests/unit/test_batch_one.py`
  through and refuses `tests/unit/test_other.py`, `tests/unit/sub/test_batch_four.py` and `tests/test_batch_five.py`
  (one `*` holds within one folder). A script's write the guard cannot name is the gap the CIT-E names: not tested.
- **S1, the daemon's place:** `gov.codeintel.daemon_dir(root)` stays public and names the daemon folder of `root` as
  the calling process sees it. In a launched session, with `TMPDIR` and `CLAUDE_CODE_TMPDIR` set to
  `<session temp>/claude-<uid>` (as the CLI sets them for its commands; seen in a launched session on 2026-11-09),
  and with `TMPDIR` a folder deeper under that (as a test session inside sets it), it lies under the session's temp
  folder, and with the launcher's temp root taken as `/tmp` the folder plus the tool's 50-byte socket tail is at most
  107 bytes. W1-27's W2-67 cases read the place through `daemon_dir` and through the `CBM_RUNTIME_DIR` the code index
  hands the tool (D-2's revision).
- **The stand-in's `run` step** (added to `w2_56_support`): runs a command with the session's own environment and
  the step's overrides (`{tmpdir}`, `{cwd}`, `{uid}` filled), recording its exit code and output.
- **The real cases:** skipped unless `GOV_W2_56_REAL=1`; `GOV_W2_56_REAL_MODEL` names the model (default `haiku`,
  empty for no `--model`). They use the real `HOME` and `~/.local/bin/claude`, and need a machine whose resource
  gate is open.


## The designer's notes that bear on the build (D-3, D-5, D-7, D-8, D-9, and the CTO's settled points)

- **D-3. S5's list.** Read as the list of what passes, an unrelated parent variable does not reach the session
  (`test_s5_an_unrelated_parent_variable_is_not_passed`). "What the CLI needs to sign in" is not named: no test sets a
  sign-in variable. If the CLI's sign-in needs a CLAUDE* variable (for example an OAuth token variable), it is the one
  CLAUDE* exception the CIT-E names.
- **D-5. S12's kill reaches the group.** A grandchild that ignores the ending signal is taken as still "reached":
  the launcher's kill after END_WAIT_S must reach the group too, not only a leader that already ended.
- **D-7. F6's wording.** "A raw claude launch stays unallowed in the template" is read with DEC-715: the failure is a
  template whose only launch is an unallowed raw `claude`; the test asks that `gov launch …` is admitted and no raw
  `claude` launch is.
- **D-8. Placeholders.** The names are the CLI sandbox's fixed write denials (shell and git start-up files, editor
  folders, the CLI's command and agent folders) and the launcher's literal `.gov-runtime/` prefixes of `scratch`.
  `docs/source`, seen once in W1 (bootstrap.md, row W2-I012), has no known origin and is not planted. A placeholder
  file named `.vscode` is not caught by the ignore line `.vscode/` (folders only). Inside a real sandbox the
  placeholders are character devices; whether `git add -A` then fails on them is for after the experiment.
- **D-9. A launcher killed by SIGKILL** cannot remove its folder; S15's "whatever its exit" is read as the session's
  exit, and the weekly sweep (DEC-902) takes the rest.
### The CTO's settled points (2026-11-09)

- **D-11 settled (a):** `<HOME>/.cache/gov-os/rerank.log` on the write list, made by the launcher if missing, never a
  link. The five `test_s11_the_reranker_log_is_on_the_write_list_as_the_service_names_it` cases stand as written.
- **D-12 settled as recommended:** a shorter launcher temp folder keeping the `gov-launch-` prefix; the daemon folders
  at the launcher's folder, found from `CLAUDE_CODE_TMPDIR`.
- **D-13 measured by the CTO** (2026-11-09, `claude -p` with haiku, a planted Unix socket server): with
  `network.allowUnixSockets: [<the one path>]` the sandboxed command's connect is refused `PermissionError [Errno 1]`,
  exactly as with no allow; with `allowAllUnixSockets: true` it connects. On Linux a one-path allow does not open the
  socket. S8's settings-level form (the one path, nothing wider) is still built: inert on Linux, honoured where the
  CLI supports it. S8's reach and S10 on Linux go to the owner as a DEC-105 choice. The S8 cases stay as written.
- **D-14:** not added to W2-56's paths now (it matters only once a socket can be reached); carried with D-13.


## The CTO's run outside the sandbox (integrate's code; results only)
- Real cases (`GOV_W2_56_REAL=1`, short TMPDIR): S2 and S9 pass. **S7 red:** inside the real sandbox the placeholder
  `.bash_profile` is a character device and `git add -A` fails "can only add regular files, symbolic links or
  git-directories" (S4's placeholders must be out of git's way inside the session too). **S13 red:** `gov rebuild`
  inside the sandbox fails "`.gov-runtime/rebuild/stores.json` could not be removed: Read-only file system" (today's
  literal deny rules on `.gov-runtime/<name>`, DEC-180, kept by S2): reconcile S13 with S2 within your paths, or name
  the conflict in your return with the smallest change that would resolve it; do not drop a deny rule silently.
- **D-13:** on Linux a one-path `network.allowUnixSockets` leaves a sandboxed connect refused (EPERM); build S8's
  settings-level form anyway (exactly the one path, from the service's own setting; nothing wider); its reach on Linux
  is the owner's choice. Do not add `allowAllUnixSockets`.
