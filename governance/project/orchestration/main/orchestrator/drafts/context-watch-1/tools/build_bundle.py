"""Builds acts/ACT-CONTEXT-WATCH-1 (the bundle) in the operator's form (as acts/ACT-DISPATCH-1 has it).
   python3 build_bundle.py freeze      before/ and after/ copies from ../frozen, list.txt, apply.sh
   python3 build_bundle.py manifest    manifest.json with the checks and the rehearsal log's sha256 (run after rehearse.sh)
The checks are run as `bash -c` from the repository root: each a here-document of one tools/check_*.py, no pytest."""
import hashlib
import json
import os
import shutil
import sys

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # drafts/context-watch-1
MAIN = "/home/usain/Dynamic-Agentic-Engineering-OS"
B = os.path.join(MAIN, ".gov-runtime/scratch/orchestrator/acts/ACT-CONTEXT-WATCH-1")
FROZEN = "/home/usain/gov-os-runs/W2-00/context-watch-1/frozen"
ACT = "ACT-CONTEXT-WATCH-1"
FILES = [".claude/settings.json", ".rulesync/hooks.jsonc"]
HOOK = "template/governance/kernel/hooks/context_watch.py"
HOOK_SHA = "c6dabb5eed394c89c31aae40a9466185355cfb3d161c44284c863c636559607c"


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


APPLY = '''#!/bin/bash
# ACT-CONTEXT-WATCH-1's apply.sh: check | apply | undo | verify, by list.txt (root|path|before sha256|after sha256), relative
# to the repository it is run in (its cwd); the bundle is read from the script's own folder. Two files: the repository's
# hooks block (.claude/settings.json) and the rulesync source it is generated from (.rulesync/hooks.jsonc). The one change,
# frozen in the after copies: a PostToolUse entry (matcher Bash, timeout 10) that runs
# template/governance/kernel/hooks/context_watch.py (W2-176) in the form of the PreCompact entry; nothing else moves.
# The state of each file is decided by its sha256 alone:
#   before   hashes as list.txt's before          applied  hashes as its after
#   other    anything else (changed since the freeze, missing, a link): refused, NOTHING is touched (every file is
#            read first; no file is written unless every file is as the step expects)
#   check    read-only: every file is the before AND the hook file is in place; exit 0, else exit 3 "moved: <path>" or
#            exit 6 "refused: <hook> is absent / is not the approved bytes"
#   apply    the same entry criterion (exit 6), then every file is the before (or the after: left as it is); the frozen
#            after copy of each file still the before is written to a temp file made by mktemp beside it, the mode kept,
#            then moved into place whole
#   undo     every file is the after (or the before: left as it is); the frozen before copy put back the same way
#            (no entry criterion: taking the registration out is always safe)
#   verify   every file is the after; exit 0, else exit 3 "not applied: <path>"
# The ENTRY CRITERION (the order): the hook file must exist at its template path as the approved bytes (the sha256 of
# W2-176's final head, in its CIT-P section 2). Registered while the file is absent, every Bash call would run a missing
# script (python exits 2 with "can't open file"), so check and apply refuse until W2-176 has merged.
# Each frozen copy is hashed against list.txt before it is used (exit 4 when it does not hash as listed). Nothing but the
# listed files is touched (a temp file is renamed over its file, so none is left). Claude Code reads the settings'
# hooks at a session's start (and when the file changes): sessions already running may need /hooks or a restart.
set -u
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="@HOOK@"
HOOK_SHA="@HOOK_SHA@"
step="${1:-}"
case "$step" in check|apply|undo|verify) ;; *) echo "usage: apply.sh check|apply|undo|verify" >&2; exit 2 ;; esac
h() { if [ -f "$1" ] && [ ! -L "$1" ]; then sha256sum "$1" | cut -c1-64; else echo null; fi; }
put() {  # put <frozen copy> <file>: the copy in place of the file, atomically, the mode kept
  local src="$1" f="$2" mode tmp
  mode="$(stat -c %a "$f")" || return 1
  tmp="$(mktemp "$f.act-XXXXXX")" || return 1
  if cat "$src" > "$tmp" && chmod "$mode" "$tmp" && mv -f "$tmp" "$f"; then return 0; fi
  rm -f "$tmp"
  return 1
}
entry() {  # the entry criterion: the hook file is there, as the approved bytes
  local now; now="$(h "$PWD/$HOOK")"
  if [ "$now" = null ]; then echo "refused: $HOOK is absent (W2-176 is not merged here); the registration would run a missing script on every Bash call; nothing touched" >&2; exit 6; fi
  if [ "$now" != "$HOOK_SHA" ]; then echo "refused: $HOOK is not the approved bytes (sha256 ${now:0:12}, approved ${HOOK_SHA:0:12}); nothing touched" >&2; exit 6; fi
}
roots=(); paths=(); befores=(); afters=()
while IFS='|' read -r root path before after; do
  [ -z "$root" ] && continue
  [ "$root" = repo ] || { echo "not a repository path: $root" >&2; exit 9; }
  roots+=("$root"); paths+=("$path"); befores+=("$before"); afters+=("$after")
done < "$B/list.txt"
[ "${#paths[@]}" -gt 0 ] || { echo "list.txt names no file" >&2; exit 9; }
# the first pass reads every file and refuses before anything is written
states=()
for i in "${!paths[@]}"; do
  now="$(h "$PWD/${paths[$i]}")"
  if [ "$now" = "${befores[$i]}" ]; then st=before; elif [ "$now" = "${afters[$i]}" ]; then st=applied; else st=other; fi
  states+=("$st")
  case "$step" in
    check) [ "$st" = before ] || { echo "moved: ${paths[$i]}" >&2; exit 3; } ;;
    verify) [ "$st" = applied ] || { echo "not applied: ${paths[$i]}" >&2; exit 3; } ;;
    apply|undo) [ "$st" != other ] || { echo "moved: ${paths[$i]} (neither the before nor the after; $step refused, nothing touched)" >&2; exit 3; } ;;
  esac
done
case "$step" in check) entry; echo "state before; $HOOK in place as approved"; exit 0 ;; verify) exit 0 ;; esac
if [ "$step" = apply ]; then
  for st in "${states[@]}"; do [ "$st" = applied ] || { entry; break; }; done
  want=applied; dir=after
else want=before; dir=before; fi
for i in "${!paths[@]}"; do
  [ "${states[$i]}" = "$want" ] && continue
  if [ "$step" = apply ]; then sum="${afters[$i]}"; else sum="${befores[$i]}"; fi
  src="$B/$dir/${roots[$i]}/${paths[$i]}"
  [ "$(h "$src")" = "$sum" ] || { echo "the frozen copy does not hash as listed: $src" >&2; exit 4; }
done
for i in "${!paths[@]}"; do
  if [ "${states[$i]}" = "$want" ]; then echo "already in place: ${paths[$i]} ($step)"; continue; fi
  put "$B/$dir/${roots[$i]}/${paths[$i]}" "$PWD/${paths[$i]}" || { echo "could not write ${paths[$i]}" >&2; exit 5; }
done
exit 0
'''


def freeze():
    rows = []
    for rel in FILES:
        for side in ("before", "after"):
            dst = os.path.join(B, side, "repo", rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(os.path.join(FROZEN, side, "repo", rel), dst)
            shutil.copymode(os.path.join(FROZEN, side, "repo", rel), dst)
        rows.append(f"repo|{rel}|{sha(os.path.join(B, 'before/repo', rel))}|{sha(os.path.join(B, 'after/repo', rel))}")
    with open(os.path.join(B, "list.txt"), "w") as f:
        f.write("\n".join(rows) + "\n")
    with open(os.path.join(B, "apply.sh"), "w") as f:
        f.write(APPLY.replace("@HOOK@", HOOK).replace("@HOOK_SHA@", HOOK_SHA))
    os.chmod(os.path.join(B, "apply.sh"), 0o755)
    print("frozen:", len(rows), "files; list.txt and apply.sh written")


def checks():
    def here(name):
        body = open(os.path.join(D, "tools", name)).read()
        assert "PYEOF" not in body
        return "python3 -I - <<'PYEOF'\n" + body + "PYEOF"
    cs = [{"cmd": "python3 -I -B -c 'import json,sys; json.load(open(sys.argv[1])); json.loads(__import__(\"re\").sub(r\"(?m)^\\s*//.*$\", \"\", open(sys.argv[2]).read()))' .claude/settings.json .rulesync/hooks.jsonc", "exit": 0, "count": None},
          {"cmd": here("check_register.py"), "exit": 0, "count": 6},
          {"cmd": f"test -f {HOOK} && test ! -L {HOOK} && test \"$(sha256sum {HOOK} | cut -c1-64)\" = {HOOK_SHA}", "exit": 0, "count": None},
          {"cmd": here("check_hook.py"), "exit": 0, "count": 7},
          {"cmd": "git ls-files --error-unmatch " + " ".join(FILES), "exit": 0, "count": None}]
    with open(os.path.join(D, "tools", "checks.json"), "w") as f:
        json.dump({"dec": "DEC-1140, DEC-1118, DEC-315, CAP-33", "checks": cs}, f, indent=1)
        f.write("\n")
    print(len(cs), "checks written")


def manifest():
    rows = [r.split("|") for r in open(os.path.join(B, "list.txt")).read().split("\n") if r]
    files = {}
    for _, rel, bef, aft in rows:
        assert sha(os.path.join(B, "before/repo", rel)) == bef and sha(os.path.join(B, "after/repo", rel)) == aft
        files[f"before/repo/{rel}"], files[f"after/repo/{rel}"] = bef, aft
    shutil.copyfile(os.path.join(D, "rehearsal.log"), os.path.join(B, "rehearsal.log"))
    for n in ("apply.sh", "list.txt", "rehearsal.log"):
        files[n] = sha(os.path.join(B, n))
    c = json.load(open(os.path.join(D, "tools", "checks.json")))
    m = {"act": ACT, "dec": c["dec"], "author": "cto", "claimed_class": "b",
         "touched": [{"root": r[0], "path": r[1], "before": r[2], "after": r[3]} for r in rows],
         "files": files, "checks": c["checks"], "commands": [],
         "rehearsal": {"log": "rehearsal.log", "sha256": files["rehearsal.log"]}}
    with open(os.path.join(B, "manifest.json"), "w") as f:
        json.dump(m, f, indent=1)
        f.write("\n")
    print("manifest.json written;", len(files), "files hashed; sha256", sha(os.path.join(B, "manifest.json")))


{"freeze": freeze, "checks": checks, "manifest": manifest}[sys.argv[1]]()
