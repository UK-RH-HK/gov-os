#!/usr/bin/env bash
# Starts one worker through `gov launch` (TPL-3b: R3-TEMPLATES D, TPL-3 S5; R2-6, R2-9; DEC-1052, DEC-1079), with the
# checks every launch needs, so no lead or CTO writes the line by hand (LEAD-w2-common, DEC-789, DEC-799, DEC-898).
#   launch_worker.sh [--fg] <role> <effort> <brief>
# Run it in the worker's worktree (or name it with LAUNCH_TREE); never the main tree. In order:
#  1. the ticket: LAUNCH_TICKET, else the one in_progress ticket of the tree's W2 (the folder's name less -tests) whose
#     role is <role> (a test designer or reviewer with none of its own: the W2's one in_progress implementer ticket);
#  2. the disk gate (disk_gate.sh, DEC-898);
#  3. the brief is copied into <tree>/.gov-runtime/scratch/brief/ (a launched worker cannot read the main tree's
#     scratch), with EMG-common.md and EMG-d4b-launched.md beside it, and each main-tree path to a copied file
#     rewritten to the copy; a brief that names no sandbox check gets one first line pointing at step 0 there;
#  4. the sandbox check, before: the launcher's own refusals and sandbox_faults() on its built settings, as a dry
#     run in the tree's code (nothing started), and no `.sandbox-trial-<ticket>` file already there; after: that file
#     must still be absent (step 0 (a) of EMG-d4b-launched.md must have failed), named SANDBOX BREACH if not;
#  5. the tripwire snapshot (tripwire.py, DEC-789), compared when the session ends;
#  6. the `gov launch` line (the tree's own code; claude-opus-5-5 or LAUNCH_MODEL; the reviewer read-only), stdin the
#     brief's copy, to <tree>/.gov-runtime/scratch/lead/log/<name>.json; then <name>.summary, then <name>.exit (the
#     session's code, written last). <name> is the brief's, made unique with -2, -3 ...
# By default the session is detached (its own session and process group; <name>.pid holds its pid for proc.sh), and
# this prints the log, the exit file and the pid: wait with `wait_for.sh <exit file>`. --fg runs it here and exits
# with the session's code. A refusal before the launch exits 2 (usage, ticket), 3 (disk gate) or 4 (sandbox check),
# with its reason in the log and that code in the exit file once their names are known.
# Env (tests): LAUNCH_TREE, LAUNCH_TICKET, LAUNCH_MODEL, LAUNCH_DISK_GATE, LAUNCH_TRIPWIRE, LAUNCH_TRIAL_DIR,
# LAUNCH_COMMON_DIR, LAUNCH_MAIN.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
MAIN=${LAUNCH_MAIN:-/home/usain/Dynamic-Agentic-Engineering-OS}
COMMON_DIR=${LAUNCH_COMMON_DIR:-$MAIN/.gov-runtime/scratch/orchestrator/briefs}
GATE=${LAUNCH_DISK_GATE:-$HERE/disk_gate.sh} TRIP=${LAUNCH_TRIPWIRE:-$HERE/tripwire.py}
TRIAL_DIR=${LAUNCH_TRIAL_DIR:-/home/usain/gov-os-worktrees} MODEL=${LAUNCH_MODEL:-claude-opus-5-5}
say() { echo "launch_worker: $*" >&2; }
cli() {  # the CLI arguments after `--` (LEAD-w2-common's form; the reviewer gets no Edit or Write)
  CLI=(-p --model "$MODEL" --effort "$2" --output-format json --permission-mode acceptEdits --allowedTools)
  if [ "$1" = independent-auditor ]; then CLI+=("Bash" "Read" "Grep" "Glob"); else CLI+=("Bash" "Read" "Edit" "Write" "Grep" "Glob"); fi
}
if [ "${1:-}" = --run ]; then  # the session itself (detached or not): launch, tripwire, sandbox check, summary, exit
  shift; tree=$1 ID=$2 role=$3 effort=$4 copy=$5 base=$6
  echo "$$" > "$base.pid"; cd "$tree" || exit 2
  cli "$role" "$effort"
  PYTHONPATH="$tree/src" python3 -m gov.cli.main launch "$role" "$ID" -- "${CLI[@]}" < "$copy" > "$base.json" 2>&1
  rc=$?
  python3 "$TRIP" compare "$base.tripwire-before.json" > "$base.tripwire.json" 2>&1; trc=$?
  tw="tripwire clean"; [ $trc = 0 ] || tw="tripwire CHANGED (exit $trc; $base.tripwire.json: attribute each change)"
  sb="sandbox trial file absent"; [ -e "$TRIAL_DIR/.sandbox-trial-$ID" ] && sb="SANDBOX BREACH: $TRIAL_DIR/.sandbox-trial-$ID exists (never delete it; report it)"
  echo "launch_worker $role $ID: session exit $rc; $tw; $sb; log $base.json" | tee "$base.summary"
  echo "$rc" > "$base.exit.tmp" && mv "$base.exit.tmp" "$base.exit"; exit "$rc"
fi
fg=""; [ "${1:-}" = --fg ] && { fg=1; shift; }
[ $# = 3 ] || { sed -n 2,24p "$0"; exit 2; }
role=$1 effort=$2 brief=$3
case "$role" in engineer|independent-test-designer|independent-auditor|research|product-spec) ;;
  *) say "not a worker role: $role"; exit 2;; esac
case "$effort" in low|medium|high|xhigh|max) ;; *) say "not an effort: $effort"; exit 2;; esac
[ -s "$brief" ] || { say "no brief (or an empty one): $brief"; exit 2; }
brief=$(readlink -f "$brief")
tree=$(readlink -f "${LAUNCH_TREE:-$(git rev-parse --show-toplevel 2>/dev/null)}")
[ -n "$tree" ] && [ -d "$tree/.tickets" ] || { say "no tree here: run it in the worktree or set LAUNCH_TREE"; exit 2; }
[ "$tree" = "$(readlink -f "$MAIN")" ] && { say "the main tree is no worker's tree: $tree"; exit 2; }
W2=$(basename "$tree"); W2=${W2%-tests}
ID=${LAUNCH_TICKET:-$(python3 -I - "$tree/.tickets" "$W2" "$role" <<'PY'
import sys
from pathlib import Path
folder, wbs, role = sys.argv[1:]
mine, all_ = [], []
for p in sorted(Path(folder).glob("*.md")):
    head = p.read_text(encoding="utf-8", errors="replace").split("\n---", 1)[0].splitlines()
    f = dict(l.split(":", 1) for l in head if ":" in l and not l.startswith(" "))
    f = {k.strip(): v.strip().strip("'\"") for k, v in f.items()}
    if f.get("wbs_id") == wbs and f.get("status") == "in_progress":
        if f.get("role") == role:
            mine.append(f.get("id", p.stem))
        if f.get("role") in ("engineer", "product-spec", "research"):
            all_.append(f.get("id", p.stem))
pick = mine or (all_ if role in ("independent-test-designer", "independent-auditor") else [])
print(pick[0] if len(pick) == 1 else "")
sys.stderr.write("" if len(pick) == 1 else f"candidates for {wbs} as {role}: {pick or 'none'}\n")
PY
)}
[ -n "$ID" ] || { say "no single in_progress ticket of $W2 for $role: set LAUNCH_TICKET"; exit 2; }
logdir=$tree/.gov-runtime/scratch/lead/log dest=$tree/.gov-runtime/scratch/brief
mkdir -p "$logdir" "$dest" || exit 2
name=$(basename "$brief" .md) n=1; stem=$name
while [ -e "$logdir/$name.json" ] || [ -e "$logdir/$name.exit" ]; do n=$((n + 1)); name=$stem-$n; done
base=$logdir/$name
refuse() { say "$2"; echo "launch_worker: REFUSED: $2" > "$base.json"; echo "$1" > "$base.exit"; exit "$1"; }
bash "$GATE" 2>> "$base.json" || refuse 3 "the disk gate is shut (DEC-898): $(tail -n 1 "$base.json")"
copy=$dest/$name.md
python3 -I - "$brief" "$copy" "$COMMON_DIR" "$dest" <<'PY' || refuse 2 "the brief could not be copied to $copy"
import sys
from pathlib import Path
brief, copy, common, dest = (Path(a) for a in sys.argv[1:])
names = ["EMG-common.md", "EMG-d4b-launched.md"]
def moved(text):
    for n in names:
        text = text.replace(str(common / n), str(dest / n))
    return text
for n in names:
    if (common / n).is_file() and common.resolve() != dest.resolve():
        (dest / n).write_text(moved((common / n).read_text(encoding="utf-8")), encoding="utf-8")
text = moved(brief.read_text(encoding="utf-8"))
if "sandbox-trial" not in text and "EMG-d4b-launched.md" not in text:
    text = (f"Step 0, before any work: the sandbox check in {dest / 'EMG-d4b-launched.md'}, reported first in your "
            f"return (launch_worker.sh).\n\n") + text
copy.write_text(text, encoding="utf-8")
PY
[ -e "$TRIAL_DIR/.sandbox-trial-$ID" ] && refuse 4 "a sandbox trial file is already there ($TRIAL_DIR/.sandbox-trial-$ID): the after-check would prove nothing; the CTO looks at it first"
cli "$role" "$effort"
dry=$(cd "$tree" && PYTHONPATH="$tree/src" python3 - "$tree" "$role" "$ID" "${CLI[@]}" 2>&1 <<'PY'
import sys
from pathlib import Path
from gov.launch import launcher as L
root, role, ticket = Path(sys.argv[1]).resolve(), sys.argv[2], sys.argv[3]
if role not in L.WORKER_ROLES:
    sys.exit(f"not a worker role for the launcher: {role}")
for check, args in (("_check_cli_args", (sys.argv[4:],)),
                    ("_check_ticket", (root, role, ticket)), ("_check_repository_settings", (root,))):
    if hasattr(L, check):
        getattr(L, check)(*args)
faults = L.sandbox_faults(L.build_settings(root, role, ticket))
if faults:
    sys.exit("the built settings are not strict: " + "; ".join(faults))
print("sandbox settings strict")
PY
) || refuse 4 "the launcher's dry run refuses: $(tail -n 3 <<< "$dry" | tr '\n' ' ')"
python3 "$TRIP" snapshot > "$base.tripwire-before.json" 2>> "$base.json" || refuse 4 "the tripwire snapshot failed"
say "$role $ID in $tree: $dry; disk gate open; brief $copy"
if [ -n "$fg" ]; then bash "$HERE/$(basename "$0")" --run "$tree" "$ID" "$role" "$effort" "$copy" "$base"; exit $?; fi
setsid bash "$HERE/$(basename "$0")" --run "$tree" "$ID" "$role" "$effort" "$copy" "$base" < /dev/null > /dev/null 2>&1 &
echo "$!" > "$base.pid"
echo "launch_worker: started pid $! (its own process group) for $role $ID; log $base.json"
echo "launch_worker: wait with: bash $HERE/wait_for.sh $base.exit"
