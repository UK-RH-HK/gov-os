**Withdrawn 2026-11-10, never applied: replaced by ACT-EFFORT-HIGH-2 (review F1-F3).**

# ACT-EFFORT-HIGH-1: `~/.claude/settings.json`'s default effort from xhigh to high (DEC-1119 (4))

## 0. What the owner says
Class **(b)**: the owner's yes, then the operator agent. The line the operator agent reads, on its own line:

yes ACT-EFFORT-HIGH-1 d7dcf753

- **For:** the owner's yes, then the operator agent (as ACT-DEADMAN-WAKE-1 runs). One file changes, outside the
  repository: `~/.claude/settings.json` (root `home`, path `.claude/settings.json`).
- **By:** a helper of the CTO (orchestrator `DAEO-sdxk`), 2026-11-10. Built and rehearsed in a planted HOME. **Nothing
  live changes until it runs.** The live file was only read.
- **Under:** DEC-1119 (4) (the default effort from xhigh to high, as a small ACT for the owner's operator), DEC-957 (the
  floor, high), DEC-1057 (rehearsed), OPERATOR-AGENT-1 §2 and §3.
- **Bundle:** `.gov-runtime/scratch/orchestrator/acts/ACT-EFFORT-HIGH-1/`. **Manifest sha256
  `d7dcf75335ef98437bd46bedc8dea2c1d50bd90e96dc8e796bb5dea4de478c9c`.**

## 1. The class and the route
**(b).** `governance/project/operator/class-rules.yaml` (identical to `~/gov-os-operator/install/class-rules.yaml`: `diff`
is empty), the `settings` row:
- match: `{root: home, path: ".claude/settings*.json"}`;
- the rule's line: `why: "settings: items only added to permissions.deny tighten (a); allow rules, hooks blocks, any other key alter a control (b) ..."`, with `else: b`.

A changed `effortLevel` is "any other key", so (b). The operator's own `act_class.classify` on the bundle gives (b), no
script hits (§4). Route: (b) goes through the operator agent's queue after the owner's yes; by hand is the same steps
(§5).

## 2. What changes (one line)
In `~/.claude/settings.json`, line 24, the top-level key only:
```
-  "effortLevel": "xhigh",
+  "effortLevel": "high",
```
The nested `modelSettings["claude-opus-5-5"].effortLevel` (line 27) is already `"high"` and is not touched. Every other
byte stays: sha256 before `bc0dde042f00`, after `ec0113a8902a`, mode 644 kept, `diff` of the two: that one line.

## 3. The bundle (all hashed in the manifest; sha256 cut to 12)
| File | sha256 | What |
|---|---|---|
| `manifest.json` | `d7dcf75335ef` | touched, files, two checks, rehearsal |
| `apply.sh` | `4e8086883682` | `check`, `apply`, `undo`, `verify`; honours HOME |
| `effort.py` | `28f53e218033` | the JSON-aware edit: a text splice at the top-level value's own span, so key order and layout stay; the result is parsed and compared (only that key may differ) |
| `list.txt` | `16fd89b2fdee` | the one file, before and after sha256 |
| `before/home/.claude/settings.json` | `bc0dde042f00` | the frozen original |
| `after/home/.claude/settings.json` | `ec0113a8902a` | the frozen result |
| `rehearsal.log` | `6dcd9c84ebd7` | the rehearsal, `failures: 0` |

- `check` (read-only) prints `state before|applied (sha256 ...)`, exit 0; for anything else (a top-level effortLevel that
  is neither "xhigh" nor "high", no single top-level key, an unreadable file, a link) it prints `state other: ...` and exits 3.
- `apply` edits atomically (temp file beside the file, then moved, mode kept); already applied it changes nothing.
  `ACT_BACKUP_BESIDE=1` first copies the file to `settings.json.bak-<UTC stamp>-ACT-EFFORT-HIGH-1` beside it, for a hand run.
- `undo` puts the frozen original back byte for byte, only when the file is the ACT's own after (a later change is never
  overwritten).
- The two manifest checks (run after the apply): top-level and nested effortLevel are both "high" and `permissions.defaultMode`
  is unchanged; the file parses (`python3 -I -m json.tool`).

## 4. Rehearsal (DEC-1057; `rehearsal.log`, 0 failures)
A planted HOME holding a copy of the live file (the live file read only, its sha256 `bc0dde042f00` the same after):
check (before) -> apply -> check (applied) -> `diff` exactly one changed line, one hunk -> the result parses; the nested
effortLevel unchanged; key order kept and every other key equal -> apply again: exit 0, no change -> undo: byte for byte
the original, a second undo harmless -> an apply, a later change, then undo refused with the later change untouched ->
a planted `"max"` refused by `check` and `apply` (exit 3), file untouched; a file with only a nested key, and a missing
file, refused -> a tampered frozen copy: undo refuses (exit 4) -> the agent's dry-run shape (no backup): the changed set
is exactly the one file, both manifest checks green, the undo restores the HOME byte for byte.

**The operator's own code, read-only** (`validate_manifest`, the file hashes, the path rule over `apply.sh` and the
checks, `act_class.classify`): all pass, class (b), no hits. The checks are green on the after copy and check 0 is red
on the before copy.

## 5. The operator's steps (the yes line again)
yes ACT-EFFORT-HIGH-1 d7dcf753

**By the operator agent:** after the owner's yes, the CTO writes the request line (the ACT's id and the manifest sha) in
`~/gov-os-operator/queue/`; the agent runs G1 to G9, applies, and runs the two checks. There is no commit: the file is outside the repository.

**The message for the owner's operator** (if by hand, rehearsed): about a minute.
> **ACT-EFFORT-HIGH-1 (DEC-1119 (4)): the default effort in `~/.claude/settings.json` from xhigh to high; one line.**
> Class (b).
> ```
> cd /home/usain/Dynamic-Agentic-Engineering-OS
> G=.gov-runtime/scratch/orchestrator/acts/ACT-EFFORT-HIGH-1
> sha256sum $G/manifest.json                    # expect d7dcf75335ef98437bd46bedc8dea2c1d50bd90e96dc8e796bb5dea4de478c9c
> bash $G/apply.sh check                        # expect: state before (sha256 bc0dde042f00)  (anything else: stop, tell the CTO)
> ACT_BACKUP_BESIDE=1 bash $G/apply.sh apply    # expect: backup ...settings.json.bak-<stamp>-ACT-EFFORT-HIGH-1 (sha256 bc0dde042f00), then state applied (sha256 ec0113a8902a)
> bash $G/apply.sh verify                       # silent, exit 0
> bash $G/apply.sh check                        # expect: state applied (sha256 ec0113a8902a)
> ```
> **Undo:** `bash $G/apply.sh undo` (expect `state before (sha256 bc0dde042f00)`; rehearsed byte for byte). If the file has
> been changed since, undo refuses and says so; the backup beside the file is the hand copy.

## 6. Residuals
- **Drift.** The bundle freezes the file as it is today (`bc0dde042f00`, last changed 2026-11-03). If anything rewrites
  `~/.claude/settings.json` before the apply (a Claude Code settings command, a hand edit), the operator agent's G7 refuses and the
  bundle is rebuilt and re-rehearsed. `check` alone would still accept any "xhigh" or "high" file; the hashes are the guard.
- **The backup beside the file is for a hand run only.** The agent's dry run holds the whole planted HOME to the touched list, so the
  agent route sets no backup; its undo is the frozen original. A hand run's backup file is the operator's to remove.
- **Reach.** The file's own structure keeps `claude-opus-5-5` at "high" through `modelSettings`; the new default applies
  to every model without such an entry. When a running session picks up the change was not tested here; a new session reads it.
- `jq` is not installed here: the parse check is `python3 -m json.tool`.

## Review
pending

[DEC-1119 (4), DEC-957, DEC-1057, OPERATOR-AGENT-1 §2 and §3]
