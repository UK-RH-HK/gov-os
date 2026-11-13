# ACT-EFFORT-HIGH-2: the default effort to high, for the models that read it (DEC-1119 (4))

## 0. What the owner says
Class **(b)**: the owner's yes, then the operator agent. The line the operator agent reads, on its own line:

yes ACT-EFFORT-HIGH-2 0be009e8

- **For:** the owner's yes, then the operator agent. One file changes, outside the repository: `~/.claude/settings.json`
  (root `home`, path `.claude/settings.json`), two changes (§2).
- **By:** a helper of the CTO (orchestrator `DAEO-sdxk`), 2026-11-10. Built and rehearsed in a planted HOME. **Nothing
  live changes until it runs.** The live file was only read.
- **Under:** DEC-1119 (4) (the default effort from xhigh to high), DEC-957 (the floor, high), DEC-1120 (RUBRIC-2),
  DEC-1057 (rehearsed), OPERATOR-AGENT-1 §2 and §3.
- **Bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-EFFORT-HIGH-2/`. **Manifest sha256
  `0be009e84c86c22c8f1e62ff63289912cf16d225f8207b22285d76d0980d0ac8`.**
- **Replaces ACT-EFFORT-HIGH-1**, withdrawn and never applied (its package carries a line saying so).

## 1. What -1 got wrong, and why -2
The independent review of -1 (READY, three findings) found:
- **F1: the top-level `effortLevel` is a legacy key for the 5.5 models.** In Claude Code 2.1.318 it applies only to a
  fixed list of older models (Fable 5.1 among them). Opus 5.5 was already high through its own `modelSettings` entry;
  Sonnet 5.5 and Haiku 5.5 sessions started without `--effort` stay at the model default. The working form is one
  `modelSettings.<model>.effortLevel` entry per model, as `/effort` saves it. -2 adds Sonnet's entry and still sets the
  top-level key.
- **F2: `apply` accepted a file changed since the freeze** while its top-level value was still `xhigh`; only the hashes
  guarded. In -2, `check` and `apply` decide by the file's sha256 alone: the frozen before is `before`, the frozen after
  is `applied`, anything else is `other` and refused (exit 3).
- **F3: on the agent route, G4 would not accept a review not made under the operator's fixed brief.** -2 follows
  ACT-DEADMAN-WAKE-1: a review under `~/gov-os-operator/install/reviewer-brief.md` (sha256 `e86703304144…`, its line in
  `install/APPROVED`) is dropped into the bundle as `review.md`, with `reviewer_brief_sha256` set to that line. G1
  skips `review.md` in the file check, so it needs no manifest entry. **`review.md` is absent now**; the CTO launches
  that review after this build.

## 2. What changes (before and after)
In `~/.claude/settings.json`:
```
24c24
<   "effortLevel": "xhigh",
---
>   "effortLevel": "high",
26a27,29
>       "effortLevel": "high"
>     },
>     "claude-sonnet-5-5": {
```
`diff` aligns the second hunk this way; read as a change it is the Opus entry's `}` becoming `},` and this new entry:
```
    "claude-opus-5-5": {
      "effortLevel": "high"
    },
    "claude-sonnet-5-5": {
      "effortLevel": "high"
    }
```
Everything else is byte for byte as before: `env` (`CLAUDE_CODE_SUBAGENT_MODEL` stays `claude-opus-5-5`), permissions, hooks,
the Opus entry (still high), key order, layout, mode 644. sha256 before `bc0dde042f00`, after `2a1c84693189`.
No Haiku entry (RUBRIC-2: watchers and C0 helpers on Haiku take effort as needed, set per spawn).

## 3. The effect, per model
| Model | Effect |
|---|---|
| Opus 5.5 | unchanged: high (its own entry, as today) |
| Sonnet 5.5 | default effort now high, when a session starts without `--effort` |
| Fable 5.1 and the older models on the legacy list | high through the top-level key (was xhigh) |
| Haiku 5.5 | untouched: its model default |

Launched workers pass `--effort` on every launch (`launch_worker.sh`), so they never use this default. Read from the
installed binary (2.1.318), not from a running session.

## 4. The class and the route
**(b).** `governance/project/operator/class-rules.yaml` (identical to `~/gov-os-operator/install/class-rules.yaml`,
`cmp` silent), the `settings` row: `match: {root: home, path: ".claude/settings*.json"}`, `only_added: ["permissions.deny"]`,
`else: b`; why: "allow rules, hooks blocks, any other key alter a control (b)". The operator's own
`act_class.classify` on the bundle gives (b), row `settings`, no hits. Route: the owner's yes, then the operator agent's
queue (G1 to G9); G4 reads the fixed-brief review (§1, F3). By hand is the same steps (§7).

## 5. The bundle (all hashed in the manifest; sha256 cut to 12)
| File | sha256 | What |
|---|---|---|
| `manifest.json` | `0be009e84c86` | touched, files, two checks, rehearsal |
| `apply.sh` | `da290f4f604a` | `check`, `apply`, `undo`, `verify`; honours HOME; state by sha256 alone |
| `list.txt` | `d57f5eed79bf` | the one file, before and after sha256 |
| `before/home/.claude/settings.json` | `bc0dde042f00` | the frozen original |
| `after/home/.claude/settings.json` | `2a1c84693189` | the frozen result |
| `rehearsal.log` | `1c8cd68c5898` | the rehearsal, `failures: 0` |
| `review.md` | absent | to come: a review under the fixed brief |

- `check` (read-only): `state before|applied (sha256 ...)`, exit 0; `state other: ...` on stderr, exit 3.
- `apply`: only from `before`; the frozen after copy is put in place atomically (temp file beside the file, then moved,
  mode kept); already applied it changes nothing; a frozen copy that does not hash as listed gives exit 4.
  `ACT_BACKUP_BESIDE=1` first copies the file to `settings.json.bak-<UTC stamp>-ACT-EFFORT-HIGH-2` beside it, for a hand run
  only (the agent's clean environment never sets it, so the agent route leaves no stray backup in HOME: rule G8).
- `undo`: the frozen original put back byte for byte, only when the file is the ACT's own after.
- The two checks (after the apply): top-level and both model entries high, Opus's and Sonnet's in that order, `env` and
  `permissions.defaultMode` unchanged; the file parses (`python3 -I -m json.tool`). The first is red on the before file.
- -1's `effort.py` is not carried over: with the hash gate, the apply is the frozen after copy, so no splice is needed.

## 6. Rehearsal (DEC-1057; `rehearsal.log`)
**Result: `failures: 0`** (check, apply, applied, diff, parse, Opus unchanged, undo, byte-identical, re-apply, F2, max, missing,
all as below).
A planted HOME holding a copy of the live file (its sha256 `bc0dde042f00` the same after): check (before); verify refused ->
apply (with backup) -> check `applied` -> the diff of §2 (exactly that, the backup byte for byte the original) -> the
result parses (`python3 -m json.tool`) -> the parsed result is the original plus the two intended changes only, key order
kept -> Opus's entry unchanged -> hashes as the manifest's after, mode kept -> apply again: exit 0, no change -> undo:
byte for byte the original, `cmp` with the live file identical; a second undo harmless; a re-apply works -> a later change:
undo refused, the later change kept -> **F2:** a file differing from the freeze (its `tui` value; and a one-byte change) with
top-level still `xhigh`: `check`, `apply` and `undo` refused (exit 3), file untouched, no temp or backup left -> `"max"`,
the -1 result (top-level high, no Sonnet entry), a missing file (not created) and a link refused; HOME unset refused ->
tampered frozen copies (on a copy of the bundle): undo and apply refuse (exit 4), file untouched -> the agent's dry-run
shape (no backup): the changed set is exactly the one file, both checks green after the apply, check 0 red before, the
undo restores the HOME byte for byte -> the live file untouched.

**The operator's own code, read-only** (`validate_manifest`, the file hashes, the path rule over `apply.sh` and the
checks, `act_class.classify`): all pass, class (b), no hits. Both checks exit 0 on the after copy; check 0 exits 1 on the
before copy. G2: DEC-1119, DEC-957 and DEC-1120 are all ACCEPTED.

## 7. The operator's steps (the yes line again)
yes ACT-EFFORT-HIGH-2 0be009e8

**By the operator agent:** after the owner's yes, the CTO writes the request line (the ACT's id and the manifest sha) in
`~/gov-os-operator/queue/`, once `review.md` (fixed brief) is in the bundle; the agent runs G1 to G9, applies, and runs
the two checks. No commit: the file is outside the repository.

**The message for the owner's operator** (if by hand, about a minute):
> **ACT-EFFORT-HIGH-2 (DEC-1119 (4)): `~/.claude/settings.json`: the top-level effortLevel from xhigh to high, and a high
> effort entry for claude-sonnet-5-5.** Class (b).
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> G=.gov-runtime/scratch/orchestrator/acts/ACT-EFFORT-HIGH-2
> sha256sum $G/manifest.json                    # expect 0be009e84c86c22c8f1e62ff63289912cf16d225f8207b22285d76d0980d0ac8
> bash $G/apply.sh check                        # expect: state before (sha256 bc0dde042f00)  (state other: stop, tell the CTO)
> ACT_BACKUP_BESIDE=1 bash $G/apply.sh apply    # expect: backup ...settings.json.bak-<stamp>-ACT-EFFORT-HIGH-2 (sha256 bc0dde042f00), then state applied (sha256 2a1c84693189)
> bash $G/apply.sh verify                       # silent, exit 0
> bash $G/apply.sh check                        # expect: state applied (sha256 2a1c84693189)
> ```
> **Undo:** `bash $G/apply.sh undo` (expect `state before (sha256 bc0dde042f00)`). If the file has been changed since, undo
> refuses and says so; the backup beside the file is the hand copy, and is the operator's to remove.

## 8. Residuals
- **The global subagent model stays.** `env.CLAUDE_CODE_SUBAGENT_MODEL` is `claude-opus-5-5` and is not changed here;
  RUBRIC-2's tiers for in-session helpers are a separate matter.
- **When it takes effect.** A new session reads the file at start. The installed binary holds a settings change
  detector, so a running session might re-read it; whether it re-resolves the effort was **not verified**. Restart sessions
  that should have it.
- **Drift.** The bundle freezes the file as it is (`bc0dde042f00`, last changed 2026-11-03). If anything rewrites it before
  the apply (`/effort`, `/model`, `/config`, a hand edit), G7 or `check` refuses and the bundle is rebuilt, re-rehearsed and
  re-reviewed. That is by design (F2).
- **Reach rests on reading the minified 2.1.318**, not on a running session; a Claude Code update can change it.
- **First `root: home` ACT through the agent** (per -1's review): the HOME path through the agent's code passed on
  copies but has not run live.
- `jq` is not installed here: the parse check is `python3 -m json.tool`.

## Review: pending
Under the operator's fixed brief (F3); then `review.md` in the bundle.

[DEC-1119 (4), DEC-957, DEC-1120, DEC-1057, OPERATOR-AGENT-1 §2 and §3; the review of -1, F1 to F3]
