# ACT-EXAMIN-WRITERS-INSTALL-1: the two walled writer briefs, and their lines in the walls' approved list

- **Under:** DEC-1143 (1) (the owner approved the two briefs' bytes), DEC-1130 (3) (the walled writer route for EXAMIN's set,
  W2-94, and the proving ground's held-out half, W2-93). The model: ACT-MEMORY-AUDIT-INSTALL-1 (`0c5032bc8`).
- **Class (O):** rows `walled-sessions` of `governance/project/operator/class-rules.yaml` (`governance/project/indep-briefs/**`
  and `gov-os-eval/**`, the list `indep-walls/APPROVED`). The owner's operator applies it **by hand**; the operator agent
  never takes it; the CTO's sessions neither open the sets root nor commit the briefs.
- **Nothing live changes** until the operator runs the steps below. The real sets root was never opened; the live list is
  read for the first time by `apply.sh check` at the apply.

## What lands
1. Two files, byte for byte the approved drafts (`.gov-runtime/scratch/orchestrator/drafts/examin-sets/`), frozen in `after/repo/`:

   | Repository path | sha256 |
   |---|---|
   | `governance/project/indep-briefs/examin-sets/EXAMIN-writer.md` | `d37834e08c86e24c0fdb1884c4f11164d734af4dcb4b3a5536bd20e3efc0085f` |
   | `governance/project/indep-briefs/examin-sets/PROVING-GROUND-writer.md` | `57820503b56948bf9e6ebe41abb2182c9a81db234e685218f21f71c69076549c` |

   The folder sits under `governance/project/indep-briefs/`, which `tree-exclude.txt` leaves out of every wall's tree and the
   path map already names (rehearsed: `gov.check.pathmap` exits 0, and the dry walls' trees hold no `indep-briefs/`).
2. Two lines appended at the end of `<sets root>/indep-walls/APPROVED` (`lines.txt`, byte for byte), nothing else in the
   list changes:
   ```
   d37834e08c86e24c0fdb1884c4f11164d734af4dcb4b3a5536bd20e3efc0085f  brief writer governance/project/indep-briefs/examin-sets/EXAMIN-writer.md
   57820503b56948bf9e6ebe41abb2182c9a81db234e685218f21f71c69076549c  brief writer governance/project/indep-briefs/examin-sets/PROVING-GROUND-writer.md
   ```
   The form is what `parse_approved` reads (`governance/project/orchestration/tools/indep_launch.py`, lines 591-605: regex
   `([0-9a-f]{64})\s+(template|brief)\s+(.+?)\s*`, then kind and path split on whitespace; stage 10 at lines 2259-2264 needs
   the hash, the kind `writer` and the normalised path at `--commit`), spelled as the list's existing brief lines are
   (two spaces after the hash, then single spaces).
3. **The sets root** is the argument if given, else the path map's `sets_root_hidden.root` (`~/gov-os-eval`, so
   `$HOME/gov-os-eval`). Neither: refused. A missing list is refused, never created.

## The operator's steps (main tree, about one minute)
```
cd /home/usain/Dynamic-Agentic-Engineering-OS
A=.gov-runtime/scratch/orchestrator/acts/ACT-EXAMIN-WRITERS-INSTALL-1
bash $A/apply.sh check     # expect "state before (list sha256 ..., N lines; sets root from the path map's ...)"
bash $A/apply.sh apply     # expect "state applied (list sha256 ..., N+2 lines; ...)"
bash $A/apply.sh verify    # exit 0
git add governance/project/indep-briefs/examin-sets/ && git commit -m "ACT-EXAMIN-WRITERS-INSTALL-1: the two walled writer briefs as the owner approved them (DEC-1143 (1)), and their lines in the walls' approved list" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1143, DEC-1130" --trailer "Role: owner" -- governance/project/indep-briefs/examin-sets/
git show --name-status --format= HEAD   # expect exactly two A lines, the two briefs
```
- If `check` prints `state other: ...` (exit 3), apply nothing and send the line to the CTO; `apply` refuses by itself.
- `apply` keeps the list's mode (0400 stays 0400) and writes it by rename from a temp file beside it; on a failure part
  way it removes what it wrote and exits 5.
- **Undo:** `bash $A/apply.sh undo` (only from the state applied) removes the two files and exactly the two lines; every
  other line stays byte-identical, so right after an apply the list is byte for byte as before. If the commit was made,
  commit the two removals with the same three trailers.

## Files
`apply.sh` (check | apply | verify | undo [<sets root>]; its header holds the states and these steps), `list.txt`
(root|path|before|after), `lines.txt` (the two lines), `after/repo/...` (the two briefs), `rehearse.sh` and
`rehearsal.log` (the clone rehearsal, ends `failures: 0`), `manifest.json` (sha256 of every other bundle file, the touched
paths, the checks).
