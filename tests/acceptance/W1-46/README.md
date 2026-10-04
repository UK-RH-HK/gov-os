# W1-46 acceptance tests: worker session launcher (`gov launch`)

Ticket `DAEO-jdqr`, profile FULL. Written before implementation by the Independent Test Designer (MR-3, DEC-069),
proportional to the profile (DEC-221): every KPI line, success and failure, and every covers id has at least one test.

```
python3 -m pytest tests/acceptance/W1-46 -q -p no:cacheprovider                      # everything (starts two real sessions once gov launch exists)
python3 -m pytest tests/acceptance/W1-46 -q -p no:cacheprovider -m "not local_only"  # no session, no network, no cost
```

257 tests: 235 start nothing, 22 are `local_only`.

## How the tests see what the launcher builds

The launcher starts the CLI by its absolute path `~/.local/bin/claude` (DEC-205). Each test runs `gov launch` with a
temporary `HOME` whose `.local/bin/claude` is a stand-in program the test writes. The stand-in starts no session: it
records its arguments, its environment and the content of every `--settings` value, and ends. What it recorded is what
a worker session would have been started with. A second stand-in, first on `PATH` under the bare name `claude`,
records a launcher that did not use the absolute path. The stand-in answers `--version` with the version the tool
registry records.

No dry-run option is needed, and no internal is imported. The command line itself is not fixed by the ticket: see DP-1.

`gov launch` runs in a temporary project: this repository's `src/gov`, kernel template, role files, committed settings
and `pyproject.toml`, copied from git's listing, plus fixture tickets (engineer `DAEO-zz90`, auditor `DAEO-zz94`,
research `DAEO-zz97` with `allowed_paths: experiments/spikes/exp-901/**`), sibling experiments, and a `.gov-runtime/`
with findings, records, snapshots and scratch. Nothing is installed; `gov` is run the way W1-07's suite runs it.

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
| Success 1 [CAP-61.a], failures 1, 2, 8 | `test_w1_46_sandbox_settings.py`: strict sandbox for each of the four roles; no `excludedCommands`; one `--settings` argument; a sandbox block in the repository's settings (committed, local, local linked to scratch) changes nothing; refusal when the caller hands over a weaker sandbox (five forms); only the four worker roles are launched; the absolute CLI path (DEC-205); the session starts in the repository root; the settings come from a place no worker can write (DEC-136) | L |
| Success 2 [CAP-61.b] | `test_w1_46_role_settings.py`: `GOV_ROLE` and `GOV_TICKET` per role; both in the settings `env` block; the guard decides as that role on that ticket with the values the session was given. Live: `test_the_role_and_the_ticket_reach_the_session_and_its_hooks`, and the sandbox tests of the engineer session | L |
| Success 3 [CAP-61.c] | `test_w1_46_role_settings.py`: empty allowlist for three roles; the research allowlist accepts GitHub, PyPI, npm, Hugging Face, arXiv; it is a list of named domains. Live: the empty list refuses a connection; the research list accepts six hosts and refuses `example.com` | L |
| Success 4 [CAP-61.c], failures 4, 5 | `test_w1_46_research_fence.py`: every other top-level entry and sibling along the path is denied; the folder stays writable; `.git` is left out; glob-named entries are left out; a path that does not exist at launch is not listed; the list is computed at each launch; the guard refuses a research write to a new path. Live: sibling write fails; new path refused or reported | L (guard tests green already) |
| Success 5 [CAP-22.d] | `test_w1_46_research_role.py`: role file, its six parts, the agent definition, the roster entry; writes inside the folder allowed, outside denied; no scope on another role's ticket; no network decision by the guard | F, R |
| Success 6 [CAP-25.e], failures 6, 7 | `test_w1_46_research_installs.py`: 13 install forms let through in the folder (the four `uv` forms, DEC-216's value options, `uv pip install`, venv `pip`, `npm install`), below it, after `cd`, in every permission mode; no ask rule in the committed or the built settings; denied outside the folder, on another ticket, with `sudo`; denied for the three other roles. Live: the install succeeds into a venv in the folder; one outside the repository fails. W1-04's suite: run as it stands | R, L |
| Success 7 [CAP-61.d] | `test_w1_46_role_settings.py`: a temp directory of the session's own, which exists; two launches get two. Live: `mktemp` in each session | L |
| Success 8 [CAP-58.d] | Live: interpreter one-liner, command substitution, here-string, and a Write-tool call. `test_w1_46_research_role.py`: the guard refuses a file-tool write outside the repository for the four roles | L (guard tests green already) |
| Success 9 [CAP-49.b], failure 9 | `test_w1_46_held_out.py`: the `Read` rule per role; one per configured path; read at each launch; refusal on a missing key, an empty list, a key without a value, invalid YAML, a list at the top level, an empty file; no file of the ticket names a held-out path. Live: the stand-in looks empty | L |
| Success 10 (DEC-180) | `test_w1_46_role_settings.py`: the built rules cover the freeze flag, findings, records, snapshots and a new entry, and not scratch; the guard refuses the file tools. Live: opaque Bash writes and `ln` fail, scratch is writable | L |
| Failure 3 (a worker role installs system-wide) | the denials of success 6, `test_sudo_stays_denied_to_the_research_role`, live `test_a_research_install_outside_the_repository_fails_at_the_write_fence` | green / L |

## Green before implementation (105 tests), and why

- The three older roles already behave as the KPI says (48 cases): installs denied for engineer, test designer and
  auditor, also on the research ticket; file-tool writes outside the repository and under `.gov-runtime/` refused.
- The research role's **denials** are green for another reason: the guard denies an unknown role. They are kept
  because they must still hold once the guard knows the role (53 cases: writes outside the folder, installs outside
  the folder, new paths, another role's ticket, `sudo`, file tools outside the repository and under `.gov-runtime/`).
- `test_the_guard_grants_the_research_role_no_network_and_asks_nothing_for_it`: the guard allows a Bash command with
  no write target before it looks at the role.
- Static facts that hold today: no sandbox block in the repository's settings (DEC-161); no install ask rule in the
  committed settings (DEC-172); no file of the ticket names a held-out path.

## The `local_only` tests: cost and needs

`test_w1_46_live_sessions.py`, 22 tests over **two** real headless sessions per run, started through `gov launch`
with the CLI at `~/.local/bin/claude` and the caller's credentials (`-p`, `--permission-mode acceptEdits`,
`--model haiku`, `--max-turns 8`, `--allowedTools Bash,Write`):

| Session | Model work | Needs |
|---|---|---|
| engineer | one Bash call (a probe script in scratch) and one Write call | `bwrap`, `socat`; no network (the connection must be refused) |
| research | two Bash calls: the install, then a probe script in the experiment folder | `bwrap`, `socat`, `uv`, and the network: it connects to `github.com`, `pypi.org`, `files.pythonhosted.org`, `registry.npmjs.org`, `huggingface.co`, `arxiv.org` |

The install uses a wheel the test builds by hand (`--offline --no-index`), so nothing is downloaded. The "system-wide"
install targets a temporary directory outside the repository, so a failing sandbox pollutes nothing. Each session is
told its exact commands; a session that leaves no complete result file fails every test with that reason. Until
`gov launch` exists the 22 tests stop at the `launcher` fixture and start nothing. I could not run them: the probe
scripts and the `uv` command line are untested against a real sandbox.

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
6. The research hosts: one host per service DEC-158 names, two for PyPI (an install also fetches from
   `files.pythonhosted.org`). "Documentation sites" names no host and is not tested.
7. The experiment folder is the research ticket's single `allowed_paths` entry without its `/**`.
8. The role file may be `template/governance/kernel/roles/research*` or `.claude/agents/research.md`; one of them
   states all six parts, found by their words. The roster entry is any key or value `research` in
   `governance/project/roster.yaml`.
9. `product-spec` is not a worker role of the launcher: its experiments run as `research` (KPI success 2).
10. The launcher is not expected to check the CLI binary (digest, signature); the stand-in would not pass one.
11. Not tested, being residuals for EXP-002: subagents in a sandboxed session, `bypassPermissions`, hard-link and
    symlink tricks beyond the two `ln` cases, `denyWrite` on a path that does not exist.

## W1-07's registry test

`tests/acceptance/W1-07/test_w1_07_registry.py` has no `NOT_IMPLEMENTED` case for `launch`: `RESERVED_COMMANDS` holds
the twelve operations and `launch` is not one. Nothing was revised. No earlier suite was changed.

## Decision packages

**DP-1 (P1). The command line of `gov launch`.**
- Question: how are the role, the ticket and the CLI's own arguments given?
- Why now: every test that launches uses it, and a headless worker needs `-p` and its prompt passed on.
- Options: (a) `gov launch <role> <ticket> [-- <arguments for the CLI>]`; (b) `gov launch --role <role> --ticket <id>`,
  which collides with the shared `--role` option of W1-07 ("the role of the caller"); (c) a prompt option of the
  launcher's own and no pass-through.
- Impact: (a) is what the tests use, in one helper (`support.launch`) and one line of the live tests.
- Reversibility: high; a change touches those two places. Cost: none for (a).
- Recommendation: (a). Confidence: medium.

**DP-2 (P1). The session tests need a paid model call and depend on the model.**
- Question: are two real sessions per run acceptable evidence for the "launched worker" lines?
- Why now: the KPI asks for acceptance tests of a launched session; the sandbox is inside the CLI, so no command can
  be run in it without a session.
- Options: (a) as written: two short sessions, `local_only`; (b) the same behind an opt-in variable, with the risk of
  a close on skipped tests; (c) a builder-side `bwrap` reproduction, which tests a copy of the sandbox, not the
  sandbox.
- Impact: (a) costs two short sessions per full run; a model that does not run the stated command fails the tests
  with that reason, and the run is repeated.
- Reversibility: high. Cost: a few thousand tokens per run.
- Recommendation: (a). Confidence: medium.

**DP-3 (P2). A sandbox block in the repository's settings: ignore it or refuse?**
- Question: "reads no sandbox setting from the repository" is met by ignoring the block; but the CLI itself still
  loads the repository's settings and may merge them (`excludedCommands` is a list).
- Why now: failure line 2, and DEC-161 ("the repository's settings carry no sandbox block").
- Options: (a) refuse to launch when `.claude/settings.json` or `.claude/settings.local.json` carries a `sandbox`
  key; (b) ignore it.
- Impact: the test accepts both. With (a) it becomes a refusal test.
- Reversibility: high. Cost: a few lines.
- Recommendation: (a), it fails closed. Confidence: medium.

**DP-4 (P2). What "inside its experiment folder" means for the guard's install exception.**
- Question: which fact puts an install inside the folder?
- Why now: DEC-219 moves this test here, and the live install is `cd <folder> && uv ...`.
- Options: (a) the hook input's `cwd` is the folder or below it, or the command first changes into it with `cd`;
  (b) `cwd` only; (c) also follow `uv --directory` and `--project` values, and deny when one leaves the folder.
- Impact: the tests assume (a). Under (b), one deterministic test and the live install command change. (c) is not
  tested; an install that leaves the folder through such a value is stopped by the generated deny rules.
- Reversibility: high. Cost: small.
- Recommendation: (a) now, (c) as a described behaviour for the review. Confidence: medium.

**DP-5 (P2). The owner-extensible allowlist.**
- Question: in which file does the owner extend the research allowlist, and which hosts are "documentation sites"?
- Why now: the KPI says "built from an owner-extensible list"; no file or key is named, so extending it is not tested.
- Options: (a) a project file, for example `governance/project/research-allowlist.yaml`, added to the kernel default
  (the ticket's `allowed_paths` do not hold it); (b) the kernel file under `template/governance/kernel/launch/`
  alone, edited by the owner.
- Impact: once named, one test: an added domain appears in the built allowlist, a malformed file refuses the launch.
- Reversibility: high. Cost: one test, one path.
- Recommendation: (a). Confidence: low.

**DP-6 (P3). "Shows whether the session uses it" (DEC-159).**
- Question: the live temp-directory test asserts that each session's `mktemp` lands in a directory of its own. If the
  CLI cannot be made to use one, the KPI's answer is a residual in `bootstrap.md`, not a failing test.
- Options: (a) keep the assertion; if it fails for that reason, the orchestrator records the residual and the test is
  revised to assert the recorded state; (b) make the test report only.
- Recommendation: (a). Confidence: medium. Reversible; cost: one planned revision at most.

**DP-7 (P3). Cases the ticket leaves open, not tested.**
- A project with no `held-out.yaml` at all (the guard treats it as "nothing held out"; DEC-218 names a missing key,
  an empty list and a broken file).
- A research ticket with several `allowed_paths` entries, or none: which is the experiment folder.
- A ticket that is unknown, not in progress, or of another role: launch or refuse.
- Recommendation: refuse in all three; add tests when decided. Confidence: low.
