#!/usr/bin/env python3
"""Builds ACT-DEADMAN-STANDBY-1's bundle for the operator agent (OPERATOR-AGENT-1's interface), from this folder.

    python3 build_act.py build       acts/ACT-DEADMAN-STANDBY-1/ beside this file: before/, after/, list.txt, apply.sh,
                                     manifest.json (its rehearsal entry pending); refuses when the repository's
                                     deadman.py is not HEAD's, or HEAD's is not the frozen deadman.py.head
    python3 build_act.py finalize    after rehearse.sh: rehearsal.log hashed into the manifest; prints the manifest sha
    python3 build_act.py gates       the operator's own code on the bundle, read-only: validate_manifest, the path
                                     rule, act_class.classify; the files as the manifest hashes them

One touched file: governance/project/orchestration/tools/deadman.py (the `watchers` row: (b), a control path). The new
unit cases (tests/unit/orchestration/test_cto_safety_nets.py) are the CTO's own commit after the ACT (their path falls
to the catch-all row, (O): never an ACT's business). The bundle is built here, in drafts/; the CTO copies the folder
`acts/ACT-DEADMAN-STANDBY-1/` to .gov-runtime/scratch/orchestrator/acts/ (the manifest does not name its own place).
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
ACT = "ACT-DEADMAN-STANDBY-1"
BUNDLE = HERE / "acts" / ACT
PATH = "governance/project/orchestration/tools/deadman.py"
IDLE_JSON = '{"type":"assistant","timestamp":"2026-11-10T15:49:00Z","message":{"content":[{"type":"text"}]}}'
OLD_JSON = '{"type":"assistant","timestamp":"2026-11-01T01:46:20Z","message":{"content":[{"type":"text"}]}}'
# Standard library and coreutils only: the operator's dry run plants HOME, so no user-site package (pytest) is there.
# Every file the tool writes is under the check's own mktemp folder (ORCH, --state, --log, --inbox, --standby named).
OWN = ('--session-file "$T/none" --state "$T/st/state.json" --log "$T/deadman.log" --inbox "$T/st/inbox" '
       '--inbox-stale "$T/none"')
NOTE = "2026-11-10 15:49:50 CTO 412a4e37 waits on the owner: the ACT yes lines"
ONE = ("T=\"$(mktemp -d)\" && mkdir -p \"$T/st\" && printf '%s\\n' '{j}' > \"$T/s.jsonl\" && {plant}TZ=UTC "
       "ORCH=\"$T/o\" python3 " + PATH + " --projects \"$T\" --now '{now}' --channel nothing " + OWN +
       " --standby \"$T/sb\" > \"$T/note.json\" && ")
WATCH = ("T=\"$(mktemp -d)\" && mkdir -p \"$T/st\" && printf '%s\\n' '" + OLD_JSON + "' > \"$T/s.jsonl\" && "
         "printf '%s CTO waits on the owner\\n' \"$(date -u -d '{ago}' '+%F %T')\" > \"$T/sb\" && "
         "ORCH=\"$T/o\" python3 " + PATH + " --watch --every 1 --max 1 --projects \"$T\" " + OWN + " --standby \"$T/sb\"")
PLANT = "printf '%s\\n' '" + NOTE + "' > \"$T/sb\" && "
PLANT_MTIME = "printf 'waiting on the owner\\n' > \"$T/sb\" && touch -d '2026-11-10 15:49:50 UTC' \"$T/sb\" && "
CHECKS = [
    # a fresh note (70 minutes old) still mutes the ALERT
    {"cmd": ONE.format(j=IDLE_JSON, plant=PLANT, now="2026-11-10 17:00") + "grep -cF '\"verdict\": \"standby: "
            + NOTE + "\"' \"$T/note.json\"", "exit": 0, "count": 1},
    # the 11-10 incident: the same note at 19:18 (208 minutes old) no longer mutes, and the alert says why
    {"cmd": ONE.format(j=IDLE_JSON, plant=PLANT, now="2026-11-10 19:18") + "grep -cF '\"line\": \"P1 DEADMAN | the CTO "
            "session is idle since 15:49 (its turn ended and nothing woke it), 209 min | approve or restart it | its "
            "stand-by note had expired (written 2026-11-10 15:49 UTC, 208 min ago)\"' \"$T/note.json\"",
     "exit": 0, "count": 1},
    # a note without a time is aged by the file's mtime
    {"cmd": ONE.format(j=IDLE_JSON, plant=PLANT_MTIME, now="2026-11-10 19:00") + "grep -cF '\"standby\": \"expired "
            "(written 2026-11-10 15:49 UTC, 190 min ago)\"' \"$T/note.json\"", "exit": 0, "count": 1},
    # no stand-by at all: the day ALERT line byte for byte as before
    {"cmd": ONE.format(j=IDLE_JSON, plant="", now="2026-11-10 17:00") + "grep -cF '\"line\": \"P1 DEADMAN | the CTO "
            "session is idle since 15:49 (its turn ended and nothing woke it), 71 min | approve or restart it\"' "
            "\"$T/note.json\"", "exit": 0, "count": 1},
    # the sentinel's watch on a stalled session: a note written now mutes it (exit 0), one 3 hours old does not (exit 10)
    {"cmd": WATCH.replace("{ago}", "now"), "exit": 0, "count": None},
    {"cmd": WATCH.replace("{ago}", "3 hours ago"), "exit": 10, "count": None},
]
APPLY = r'''#!/bin/bash
# ACT-DEADMAN-STANDBY-1's apply.sh: check | apply | undo | verify, by list.txt (root|path|before sha256|after sha256),
# relative to the repository it is run in (its cwd); the bundle is read from the script's own folder. Each frozen copy
# is hashed against list.txt before it is written, then moved into place whole (the running watch keeps its loaded
# code; the sentinel's next watch start reads the new file). Nothing but the listed file is touched.
#   check   the live file is the "before" (exit 3 "moved: <path>" otherwise)
#   apply   the "after" copy put in place          undo   the "before" copy put back
#   verify  the live file is the "after" (exit 3 "not applied: <path>" otherwise)
set -u
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
step="${1:-}"
case "$step" in check|apply|undo|verify) ;; *) echo "usage: apply.sh check|apply|undo|verify" >&2; exit 2 ;; esac
h() { if [ -f "$1" ]; then sha256sum "$1" | cut -c1-64; else echo null; fi; }
while IFS='|' read -r root path before after; do
  [ -z "$root" ] && continue
  [ "$root" = repo ] || { echo "not a repository path: $root" >&2; exit 9; }
  f="$PWD/$path"
  case "$step" in
    check) [ "$(h "$f")" = "$before" ] || { echo "moved: $path" >&2; exit 3; } ;;
    verify) [ "$(h "$f")" = "$after" ] || { echo "not applied: $path" >&2; exit 3; } ;;
    apply|undo)
      if [ "$step" = apply ]; then want=$after; src="$B/after/$root/$path"; else want=$before; src="$B/before/$root/$path"; fi
      [ "$(h "$src")" = "$want" ] || { echo "the frozen copy does not hash as listed: $src" >&2; exit 4; }
      cat "$src" > "$f.act-tmp" && chmod 644 "$f.act-tmp" && mv -f "$f.act-tmp" "$f" || exit 5 ;;
  esac
done < "$B/list.txt"
exit 0
'''


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def build():
    head = subprocess.run(["git", "-C", str(REPO), "show", f"HEAD:{PATH}"], capture_output=True, check=True).stdout
    live = (REPO / PATH).read_bytes()
    if hashlib.sha256(head).digest() != hashlib.sha256(live).digest():
        sys.exit(f"the live {PATH} is not HEAD's: nothing built")
    if head != (HERE / "deadman.py.head").read_bytes():
        sys.exit("HEAD's deadman.py is not the frozen deadman.py.head the patch was made against: nothing built")
    after = (HERE / "deadman.py").read_bytes()
    if BUNDLE.exists():
        if (BUNDLE / "review.md").exists():
            sys.exit(f"{BUNDLE} holds a review: a rebuild would make it stale; move it aside first")
        shutil.rmtree(BUNDLE)
    for side, data in (("before", head), ("after", after)):
        f = BUNDLE / side / "repo" / PATH
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(data)
    b, a = hashlib.sha256(head).hexdigest(), hashlib.sha256(after).hexdigest()
    (BUNDLE / "list.txt").write_text(f"repo|{PATH}|{b}|{a}\n")
    (BUNDLE / "apply.sh").write_text(APPLY)
    (BUNDLE / "apply.sh").chmod(0o755)
    write_manifest(None)
    print(f"built {BUNDLE}: before {b[:12]}, after {a[:12]}")


def write_manifest(rehearsal_sha):
    files = {f"before/repo/{PATH}": sha(BUNDLE / "before/repo" / PATH),
             f"after/repo/{PATH}": sha(BUNDLE / "after/repo" / PATH),
             "apply.sh": sha(BUNDLE / "apply.sh"), "list.txt": sha(BUNDLE / "list.txt")}
    m = {"act": ACT, "dec": "DEC-998, DEC-1112", "author": "cto", "claimed_class": "b",
         "touched": [{"root": "repo", "path": PATH, "before": files[f"before/repo/{PATH}"],
                      "after": files[f"after/repo/{PATH}"]}],
         "files": files, "checks": CHECKS, "commands": []}
    if rehearsal_sha:
        files["rehearsal.log"] = rehearsal_sha
        m["rehearsal"] = {"log": "rehearsal.log", "sha256": rehearsal_sha}
    (BUNDLE / "manifest.json").write_text(json.dumps(m, indent=1) + "\n")
    return sha(BUNDLE / "manifest.json")


def finalize():
    log = BUNDLE / "rehearsal.log"
    text = log.read_text()
    if not text.rstrip().endswith("failures: 0"):
        sys.exit("the rehearsal did not end with failures: 0: not finalized")
    print(f"manifest sha256 {write_manifest(sha(log))}")


def gates():
    sys.path.insert(0, str(REPO / "governance/project/operator"))
    sys.dont_write_bytecode = True
    import act_class  # noqa: E402
    import operator_run as orun  # noqa: E402
    m = json.loads((BUNDLE / "manifest.json").read_text())
    orun.validate_manifest(m)
    print("validate_manifest: pass")
    for rel, want in m["files"].items():
        assert sha(BUNDLE / rel) == want, rel
    print(f"files: {len(m['files'])} hash as the manifest says")
    s = {"repo": str(REPO), "home": str(Path.home())}
    texts = [("apply.sh", (BUNDLE / "apply.sh").read_text())] + [("a check", c["cmd"]) for c in m["checks"]]
    for where, text in texts:
        why = orun.live_path_refs(text, s)
        assert why is None, f"{where}: {why}"
    print("path rule: pass (apply.sh and every check)")
    v = act_class.classify(str(BUNDLE))
    print(f"act_class.classify: class {v['class']}; hits {v['hits']}; why {v['why']}")
    print(f"manifest sha256 {sha(BUNDLE / 'manifest.json')}")


if __name__ == "__main__":
    {"build": build, "finalize": finalize, "gates": gates}[sys.argv[1]]()
