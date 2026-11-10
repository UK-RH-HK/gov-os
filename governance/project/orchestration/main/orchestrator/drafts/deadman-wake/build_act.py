#!/usr/bin/env python3
"""Builds ACT-DEADMAN-WAKE-1's bundle for the operator agent (OPERATOR-AGENT-1's interface), from this folder.

    python3 build_act.py build       acts/ACT-DEADMAN-WAKE-1/: before/, after/, list.txt, apply.sh, manifest.json
                                     (its rehearsal entry pending); refuses when the live deadman.py is not HEAD's
    python3 build_act.py finalize    after rehearse.sh: rehearsal.log hashed into the manifest; prints the manifest sha
    python3 build_act.py gates       the operator's own code on the bundle, read-only: validate_manifest, the path
                                     rule, act_class.classify; the files as the manifest hashes them

One touched file: governance/project/orchestration/tools/deadman.py (the `watchers` row: (b), a control path). The
wake's test, the README line and test_cto_safety_nets.py's ORCH fixture are the CTO's own commit after the ACT (their
paths fall to the catch-all row, (O) in a manifest: never an ACT's business).
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
ACT = "ACT-DEADMAN-WAKE-1"
BUNDLE = REPO / ".gov-runtime/scratch/orchestrator/acts" / ACT
PATH = "governance/project/orchestration/tools/deadman.py"
WAKE_JSON = '{"type":"assistant","timestamp":"2026-11-10T02:35:00Z","message":{"content":[{"type":"text"}]}}'
DAY_JSON = '{"type":"assistant","timestamp":"2026-11-10T12:00:00Z","message":{"content":[{"type":"text"}]}}'
# Standard library and coreutils only: the operator's dry run plants HOME, so no user-site package (pytest) is there.
# Every file the tool writes is under the check's own mktemp folder (ORCH, --state, --log, --inbox-stale named).
OWN = ('--session-file "$T/none" --standby "$T/none" --state "$T/st/state.json" --log "$T/deadman.log"')
ONE = ("T=\"$(mktemp -d)\" && mkdir -p \"$T/st\" && printf '%s\\n' '{j}' > \"$T/s.jsonl\" && TZ=UTC ORCH=\"$T/o\" "
       "python3 " + PATH + " --projects \"$T\" --now '{now}' --channel nothing --inbox-stale \"$T/none\" " + OWN +
       " > \"$T/note.json\" && ")
WATCH = ("T=\"$(mktemp -d)\" && mkdir -p \"$T/st\" \"$T/d/inbox\" && "
         "printf '{{\"type\":\"assistant\",\"timestamp\":\"%s\",\"message\":{{\"content\":[{{\"type\":\"text\"}}]}}}}\\n' "
         "\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\" > \"$T/s.jsonl\" && {plant}"
         "printf 'inbox: {n} item(s) unread; the oldest 20261110-033600-deadman-wake.txt\\n' > \"$T/d/inbox-stale.txt\" && "
         "ORCH=\"$T/o\" python3 " + PATH + " --watch --every 1 --max 1 --projects \"$T\" --inbox-stale "
         "\"$T/d/inbox-stale.txt\" " + OWN)
WAKE_ITEM = "touch -d '40 minutes ago' \"$T/d/inbox/20261110-033600-deadman-wake.txt\" && "
GUARD_ITEM = "touch -d '35 minutes ago' \"$T/d/inbox/20261110-034000-guard-131.txt\" && "
CHECKS = [
    {"cmd": ONE.format(j=WAKE_JSON, now="2026-11-10 03:36") + "grep -q '\"verdict\": \"alive\"' \"$T/note.json\" && "
            "ls \"$T/st/inbox\" | grep -c -- '-deadman-wake.txt$'", "exit": 0, "count": 1},
    {"cmd": ONE.format(j=DAY_JSON, now="2026-11-10 13:01") + "grep -cF '\"line\": \"P1 DEADMAN | the CTO session is "
            "idle since 12:00 (its turn ended and nothing woke it), 61 min | approve or restart it\"' \"$T/note.json\"",
     "exit": 0, "count": 1},
    {"cmd": WATCH.format(plant=WAKE_ITEM, n=1), "exit": 0, "count": None},
    {"cmd": WATCH.format(plant=WAKE_ITEM + GUARD_ITEM, n=2), "exit": 10, "count": None},
]
APPLY = r'''#!/bin/bash
# ACT-DEADMAN-WAKE-1's apply.sh: check | apply | undo | verify, by list.txt (root|path|before sha256|after sha256),
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
