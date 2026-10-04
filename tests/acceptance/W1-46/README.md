# W1-46 acceptance tests: worker session launcher (`gov launch`)

Ticket `DAEO-jdqr`, profile FULL. Written before implementation by the Independent Test Designer (MR-3, DEC-069),
proportional to the profile (DEC-221): every KPI line, success and failure, and every covers id has at least one test.
Batch 2 revised the suite, still before implementation, for the decisions on batch 1's seven packages (DEC-231 to
DEC-234, DEC-240 to DEC-242).

```
python3 -m pytest tests/acceptance/W1-46 -q -p no:cacheprovider                      # everything (starts two real sessions once gov launch exists)
python3 -m pytest tests/acceptance/W1-46 -q -p no:cacheprovider -m "not local_only"  # no session, no network, no cost
```

281 tests: 247 start nothing, 34 are `local_only`.

## How the tests see what the launcher builds

The command line is `gov launch <role> <ticket> [-- <CLI arguments>]` (DEC-231): the role and the ticket are
positional, and everything after `--` goes to the CLI unchanged. The whole suite uses that form, through one helper
(`support.launch`) and one line of the live tests.

The launcher starts the CLI by its absolute path `~/.local/bin/claude` (DEC-205). Each test runs `gov launch` with a
temporary `HOME` whose `.local/bin/claude` is a stand-in program the test writes. The stand-in starts no session: it
records its arguments, its environment and the content of every `--settings` value, and ends. What it recorded is what
a worker session would have been started with. A second stand-in, first on `PATH` under the bare name `claude`,
records a launcher that did not use the absolute path. The stand-in answers `--version` with the version the tool
registry records. No dry-run option is needed, and no internal is imported.

`gov launch` runs in a temporary project: this repository's `src/gov`, kernel template, role files, committed
settings, `pyproject.toml` and `governance/project/research-allowlist.yaml` (once it exists), copied from git's
listing, plus fixture tickets (engineer `DAEO-zz90`, auditor `DAEO-zz94`, research `DAEO-zz97` with `allowed_paths:
experiments/spikes/exp-901/**`), sibling experiments, and a `.gov-runtime/` with findings, records, snapshots and
scratch. Nothing is installed; `gov` is run the way W1-07's suite runs it.

The guard is asked through the PreToolUse commands the project's committed settings register, run through the shell
as the harness runs them, with `GOV_ROLE`, `GOV_TICKET` and the session's `cwd`. No tool call is made.

**The held-out path.** `governance/project/held-out.yaml` is not copied, and the copy of `.claude/settings.json`
leaves out the `Read` rules with an absolute path. Every project gets a `held-out.yaml` the test writes, naming a
stand-in directory it made (DEC-218), as in W1-47. One static test reads the committed list at run time through
W1-47's `load_configured`, to check that no file of the ticket repeats a value; a value is never shown.

## KPI lines, tests and red reasons

Red reason **L**: `gov launch` is not a command yet (`gov launch --help` ends with exit code 2); the `launcher`
fixture stops the test, which pytest reports as an error. Red reason **R**: the guard does not know the role
`research`, so it denies the call. Red reason **F**: the file does not exist.

| KPI line | Tests | Red |
|---|---|---|
| Success 1 [CAP-61.a], failures 1, 2, 8 | `test_w1_46_sandbox_settings.py`: strict sandbox for each of the four roles; no `excludedCommands`; one `--settings` argument; **refusal when the repository's settings carry a `sandbox` key** (committed, local, local linked to scratch; a strict block and an empty one too) (DEC-233); refusal when the caller hands over a weaker sandbox (five forms); only the four worker roles are launched; the absolute CLI path (DEC-205); the session starts in the repository root; the settings come from a place no worker can write (DEC-136) | L |
| Success 2 [CAP-61.b] | `test_w1_46_role_settings.py`: `GOV_ROLE` and `GOV_TICKET` per role; both in the settings `env` block; the guard decides as that role on that ticket with the values the session was given. Live: `test_the_role_and_the_ticket_reach_the_session_and_its_hooks`, and the sandbox tests of the engineer session | L |
| Success 3 [CAP-61.c] | `test_w1_46_role_settings.py`: empty allowlist for three roles. `test_w1_46_research_allowlist.py` (DEC-241): the project file exists and is a list of hosts; the built research allowlist carries the seventeen starting hosts and the `*.readthedocs.io` entry; it is a list of named domains; a host added to the project file is in the next launch's allowlist, and the starting hosts stay; the file does not reach the three other roles; a malformed file refuses the launch (seven forms). Live: the empty list refuses a connection; the sandbox accepts a connection to each of the seventeen starting hosts and to `docs.readthedocs.io`, and refuses `example.com` | L; F for the file |
| Success 4 [CAP-61.c], failures 4, 5 | `test_w1_46_research_fence.py`: every other top-level entry and sibling along the path is denied; the folder stays writable; `.git` is left out; glob-named entries are left out; a path that does not exist at launch is not listed; the list is computed at each launch; the guard refuses a research write to a new path. `test_w1_46_launch_refusals.py` (DEC-242): a research ticket that is not exactly one experiment folder refuses the launch (five forms); a second research ticket gets its own fence. Live: sibling write fails; new path refused or reported | L (guard tests green already) |
| Success 5 [CAP-22.d] | `test_w1_46_research_role.py`: role file, its six parts, the agent definition, the roster entry; writes inside the folder allowed, outside denied; no scope on another role's ticket; no network decision by the guard | F, R |
| Success 6 [CAP-25.e], failures 6, 7 | `test_w1_46_research_installs.py`: 11 install forms let through in the folder (the four `uv` forms, three value options of DEC-216, `uv pip install`, venv `pip`, `npm install`), below it, after `cd` into it (DEC-240), in every permission mode; no ask rule in the committed or the built settings; denied outside the folder, after `cd` into another folder, on another ticket, with `sudo`; denied for the three other roles. Live: the install succeeds into a venv in the folder; one outside the repository fails. W1-04's suite: run as it stands | R, L |
| Success 7 [CAP-61.d] | `test_w1_46_role_settings.py`: a temp directory of the session's own, which exists; two launches get two. Live: `mktemp` in each session, asserted (DEC-234) | L |
| Success 8 [CAP-58.d] | Live: interpreter one-liner, command substitution, here-string, and a Write-tool call. `test_w1_46_research_role.py`: the guard refuses a file-tool write outside the repository for the four roles | L (guard tests green already) |
| Success 9 [CAP-49.b], failure 9 | `test_w1_46_held_out.py`: the `Read` rule per role; one per configured path; read at each launch; refusal on a missing key, an empty list, a key without a value, invalid YAML, a list at the top level, an empty file; **a project with no `held-out.yaml` launches, strictly sandboxed, with no held-out rule** (DEC-242, DEC-223); no file of the ticket names a held-out path. Live: the stand-in looks empty | L |
| Success 10 (DEC-180) | `test_w1_46_role_settings.py`: the built rules cover the freeze flag, findings, records, snapshots and a new entry, and not scratch; the guard refuses the file tools. Live: opaque Bash writes and `ln` fail, scratch is writable | L |
| Failure 3 (a worker role installs system-wide) | the denials of success 6, `test_sudo_stays_denied_to_the_research_role`, live `test_a_research_install_outside_the_repository_fails_at_the_write_fence` | green / L |
| DEC-242 (no KPI line of its own; refusals in the words of success 1) | `test_w1_46_launch_refusals.py`: an unknown ticket (engineer, research); a ticket that is `open` or `closed`, with the same ticket `in_progress` launching; a ticket of another role (research on an engineer's ticket, engineer on a research ticket, engineer on an auditor's ticket) | L |

Covers ids: CAP-61.a, CAP-61.b, CAP-61.c, CAP-61.d, CAP-22.d, CAP-25.e, CAP-58.d, CAP-49.b. Each has tests above.

## The red result before implementation

`-m "not local_only"`: **31 failed, 122 errors, 94 passed** (247 tests). The 34 `local_only` tests are errors too,
with reason L: they stop at the `launcher` fixture and start nothing.

- 122 errors: all reason L.
- 31 failures: 26 with reason R (the research role's installs and writes inside its folder, scratch), 5 with reason
  F (the role file, its six parts, the agent definition, the roster entry, `research-allowlist.yaml`).

New and revised tests of batch 2, and their red reason:

| Test | Decision | Red |
|---|---|---|
| `test_the_launcher_refuses_when_the_repositorys_settings_carry_a_sandbox_key` (6), revised from "changes nothing the launcher builds" | DEC-233 | L |
| `test_the_key_itself_refuses_the_launch_whatever_it_holds` (2) | DEC-233 | L |
| `test_w1_46_research_allowlist.py` (13; two of them moved from `test_w1_46_role_settings.py` and revised) | DEC-241 | L; `test_this_repository_has_the_research_allowlist_file`: F |
| `test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist` (18, was 6), `local_only` | DEC-241 | L |
| `test_w1_46_launch_refusals.py` (14) | DEC-242 | L |
| `test_a_project_without_a_held_out_file_launches_with_no_held_out_rule` (2) | DEC-242, DEC-223 | L |
| `test_a_research_install_after_cd_into_another_folder_is_denied` (1) | DEC-240 | green already (the role is unknown) |
| removed: the `uv --directory` and `uv --project` cases (14: 2 let through, 6 outside the folder, 6 for the other roles) | DEC-240 | (6 + 6 were green) |

## Green before implementation (94 tests), and why

- The three older roles already behave as the KPI says (42 cases): installs denied for engineer, test designer and
  auditor, also on the research ticket; file-tool writes outside the repository and under `.gov-runtime/` refused.
- The research role's **denials** are green for another reason: the guard denies an unknown role. They are kept
  because they must still hold once the guard knows the role (48 cases: writes outside the folder, installs outside
  the folder and after `cd` into another folder, new paths, another role's ticket, `sudo`, file tools outside the
  repository and under `.gov-runtime/`).
- `test_the_guard_grants_the_research_role_no_network_and_asks_nothing_for_it`: the guard allows a Bash command with
  no write target before it looks at the role.
- Static facts that hold today: no sandbox block in the repository's settings (DEC-161); no install ask rule in the
  committed settings (DEC-172); no file of the ticket names a held-out path.

## The `local_only` tests: cost and needs

`test_w1_46_live_sessions.py`, 34 tests over **two** real headless sessions per run (DEC-232), started through
`gov launch` with the CLI at `~/.local/bin/claude` and the caller's credentials (`-p`, `--permission-mode
acceptEdits`, `--model haiku`, `--max-turns 8`, `--allowedTools Bash,Write`). They are not behind an opt-in
variable, so the ticket cannot close on skipped tests. A run in which the model does not execute the stated command
fails with that reason and is repeated; it is not a finding against the launcher.

| Session | Model work | Needs |
|---|---|---|
| engineer | one Bash call (a probe script in scratch) and one Write call | `bwrap`, `socat`; no network (the connection must be refused) |
| research | two Bash calls: the install, then a probe script in the experiment folder | `bwrap`, `socat`, `uv`, and the network: one `curl` to each of the seventeen starting hosts of DEC-241 and to `docs.readthedocs.io` |

The install uses a wheel the test builds by hand (`--offline --no-index`), so nothing is downloaded. The "system-wide"
install targets a temporary directory outside the repository, so a failing sandbox pollutes nothing. Each session is
told its exact commands; a session that leaves no complete result file fails every test with that reason. Until
`gov launch` exists the 34 tests stop at the `launcher` fixture and start nothing. I could not run them: the probe
scripts and the `uv` command line are untested against a real sandbox. A starting host that is down, or that does not
answer `https://<host>/`, fails its one test with `curl`'s exit code and the HTTP status in the message.

## Readings

1. `spike-sandbox/EVIDENCE.md` is not in the repository (no commit ever held it). The sandbox key names are the KPI's
   and the Contract's: `sandbox.enabled`, `failIfUnavailable`, `allowUnsandboxedCommands`, `excludedCommands`,
   `sandbox.network.strictAllowlist`, `sandbox.network.allowedDomains`. All six names occur in the installed CLI.
2. "Empty allowlist": `sandbox.network.allowedDomains` is `[]` or absent.
3. `GOV_ROLE` and `GOV_TICKET` must be in the `env` block of the built settings (DEC-183: it "overrides the env block
   in `.claude/settings.local.json`", which in this repository names the orchestrator).
4. `Edit` and `Read` deny rules are read by what they cover, not by their spelling: `//absolute`, `~/`, or relative to
   the project; `*`, `?`, `[...]`, `**`; a rule on a directory covers what is under it. "`.gov-runtime/**` except
   `.gov-runtime/scratch/**`" therefore means: no deny rule covers scratch.
5. The `Read` rule has the form W1-47 accepts: `Read(/<path>)`, with `/` or `/**` after it.
6. The research hosts are DEC-241's, copied from the register: each of the seventeen named hosts is an entry of the
   built allowlist under its own name. "The subdomains of `readthedocs.io`" is the entry `*.readthedocs.io`: the
   installed CLI (2.1.288) accepts a host entry or a `*.` entry, and a `*.` entry matches subdomains only, not the
   bare domain. Nothing found before implementation says the sandbox refuses that form, so there is no package on
   it; the live research session is the proof (`docs.readthedocs.io`).
7. A sandbox key refuses whatever it holds (DEC-233: "carries a `sandbox` key"): a strict block and an empty one too.
8. The experiment folder is the research ticket's single `allowed_paths` entry without its `/**` (DEC-242). "Not
   exactly one experiment folder" is tested with: two entries, no entry, `**`, a pattern over several folders
   (`experiments/spikes/exp-*/**`), and a file. Not tested: a folder that does not exist at launch, an entry without
   `/**`, and where in the repository an experiment folder may be.
9. A missing `held-out.yaml` launches with no held-out rule (DEC-242, DEC-223): the built settings differ from the
   same launch with the file by exactly the held-out `Read` rule. A file that exists and is empty is a broken file
   and refuses (DEC-218), as the guard reads it.
10. "Inside its experiment folder" (DEC-240): the hook input's `cwd` is the folder or below it, or the command starts
    with `cd <folder> &&`. `uv --directory` and `uv --project` occur in no test; a reviewer probes them (DEC-136).
11. "A ticket of another role" (DEC-242) is tested where the ticket's `role` is a worker role other than the one
    launched and no rule gives that role work on the ticket. The test designer is launched on the engineer's ticket
    it writes tests for (MR-3; this suite was written that way), so that launch must succeed. See DP-8.
12. The project allowlist file is a YAML list of host names, at the top level or as the one list of a mapping; the
    key is the engineer's. Malformed: invalid YAML, a word where the list is, an entry that is a number, a mapping,
    empty, a URL, or `*`. See DP-9.
13. The role file may be `template/governance/kernel/roles/research*` or `.claude/agents/research.md`; one of them
    states all six parts, found by their words. The roster entry is any key or value `research` in
    `governance/project/roster.yaml`.
14. `product-spec` is not a worker role of the launcher: its experiments run as `research` (KPI success 2).
15. The launcher is not expected to check the CLI binary (digest, signature); the stand-in would not pass one.
16. Not tested, being residuals for EXP-002: subagents in a sandboxed session, `bypassPermissions`, hard-link and
    symlink tricks beyond the two `ln` cases, `denyWrite` on a path that does not exist.

## W1-07's registry test

`tests/acceptance/W1-07/test_w1_07_registry.py` has no `NOT_IMPLEMENTED` case for `launch`: `RESERVED_COMMANDS` holds
the twelve operations and `launch` is not one. Checked again in batch 2; nothing was revised, so no "planned: command
implemented" revision (DEC-190) is recorded. No earlier suite was changed.

## Decision packages

### Batch 1: all seven decided

| Package | Decided by | Decision | In the suite |
|---|---|---|---|
| DP-1, the command line | DEC-231 | `gov launch <role> <ticket> [-- <CLI arguments>]` | used as written; nothing changed |
| DP-2, real sessions | DEC-232 | two short real sessions, `local_only`, no opt-in variable | nothing changed |
| DP-3, a sandbox block in the repository's settings | DEC-233 | refuse | the test became a refusal test; two cases added |
| DP-4, inside the experiment folder | DEC-240 | `cwd` in the folder, or `cd` into it first; `--directory` and `--project` not followed | their 14 cases removed; one `cd` denial added |
| DP-5, the owner-extensible allowlist | DEC-241 | `governance/project/research-allowlist.yaml` extends the kernel default; eighteen starting entries | `test_w1_46_research_allowlist.py`; 18 live host tests |
| DP-6, the temp directory | DEC-234 | the assertion stays | nothing changed |
| DP-7, open cases | DEC-242 | refuse an unknown ticket, one not `in_progress`, one of another role, a research ticket that is not one folder; a missing `held-out.yaml` launches | `test_w1_46_launch_refusals.py`; two held-out tests |

### Batch 2: two open packages

**DP-8 (P2). "A ticket of another role" for the test designer and the auditor.**
- Question: on which tickets may `independent-test-designer` and `independent-auditor` be launched?
- Why now: DEC-242 refuses "a ticket of another role", but a test designer always works on a ticket whose `role` is
  another one (this session: `GOV_TICKET=DAEO-jdqr`, a ticket with `role: engineer`). A launcher that compares the two
  role names would refuse every test designer.
- Options: (a) engineer and research need a ticket of their own role; the test designer and the auditor may be
  launched on any `in_progress` ticket; (b) as (a), but the auditor only on a ticket whose `role` is
  `independent-auditor` (DEC-088's audit ticket); (c) as (a), but the two independent roles not on a research ticket.
- Impact: the suite fixes only what every option shares: the test designer launches on an engineer's ticket, the
  auditor on an auditor's ticket, and three refusals (research on an engineer's ticket, engineer on a research
  ticket, engineer on an auditor's ticket). The decided option adds two or three cases.
- Reversibility: high. Cost: a few lines and cases.
- Recommendation: (a); a FULL ticket's reviewer and its test designer both work on the implementation ticket.
  Confidence: medium.

**DP-9 (P3). The shape of `research-allowlist.yaml`, and a project without it.**
- Question: which key holds the list, and does a project with no such file launch a research session on the kernel
  default alone?
- Why now: DEC-241 names the file and its hosts, not its key; the tests change "the list the file holds" and require
  the file in this repository, and leave the missing file untested.
- Options: (a) a top-level key chosen by the engineer, entries as plain host names, and a missing file means no
  extension (as DEC-242 decided for `held-out.yaml`); (b) a fixed key, for example `allowed_domains`, and a missing
  file refuses.
- Impact: under (a) nothing changes but one added test (a missing file launches with the kernel default). Under (b)
  the helper `rewrite_allowlist` names the key and one refusal test is added.
- Reversibility: high. Cost: one test.
- Recommendation: (a). Confidence: medium.
