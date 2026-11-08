#!/usr/bin/env python3
"""Builds f80_e4_window.sh and f80_e4_replays.sh from the reviewed drafts/score-once/e4_window.sh (WITH its F1 restore
fix) and e4_replays.sh, by the explicit replacements below and nothing else, so the review reads only this list.
Each old text must stand exactly once in its source (else nothing is written). tests/test_figures_and_data.py::test_e4_copies_as_built_with_f1_kept rebuilds both in
memory and checks them byte for byte against the files here, and checks that the F1 lines survive.

    python3 make_f80_e4.py            (writes the two files beside this one)
    python3 make_f80_e4.py --check    (exit 1 when either file differs from what the list builds)

What changes, and why (the 80 is one set, memory-verdict-2 hidden, under the sets root; data only):
  - a header naming the copy; --sets-root parsed first; the run folder derived from it (no hidden path typed);
  - every E4 folder moved under <root>/runs/fresh-80/data/e4 (caches, count, trial runs, window logs);
  - the two sets r80, r60 become the one set v80, through f80_so_measure.sh (whose summary line names v80);
  - the pins: the reviewed E4 files as before AND the fresh-80 files (FRESH80-REVIEWED.sha256);
  - GOV_STORE refused (reviewer 1 S6);
  - the e0_figures.py and score138.py calls (two files, the 138) become one count line;
  - the output frame keeps F1's form (tee ignoring INT and TERM, -p) and adds a redaction stage, so standard output
    names the run folder "<run folder>": the log in the run folder keeps the full lines; under DRY=1 (no log) the
    output goes through the same redaction.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SO = HERE.parent / "score-once"

HEAD_W = """#!/usr/bin/env bash
# THE FRESH 80, DATA ONLY, NOT JUDGED (DEC-1097 (1)(c), (5)): E4's scoring window over the 80's candidates. Built by
# drafts/fresh80/make_f80_e4.py from drafts/score-once/e4_window.sh (its F1 restore fix kept); the list of changes is
# in make_f80_e4.py. Run after f80_e4_prep.sh, the hold ended:
#   DRY=1 bash f80_e4_window.sh --sets-root ~/gov-os-eval
#   setsid bash f80_e4_window.sh --sets-root ~/gov-os-eval [gte zer] > ~/gov-os-runs/fresh-80/e4-window.out 2>&1 &
# What follows is e4_window.sh's own text, changed only as the list says.
"""

PARSE = """SETS_ROOT=""; MODELS=()
while [ $# -gt 0 ]; do case "$1" in --sets-root) SETS_ROOT=${2:-}; shift 2 || exit 2;; --sets-root=*) SETS_ROOT=${1#*=}; shift;; *) MODELS+=("$1"); shift;; esac; done
[ ${#MODELS[@]} -gt 0 ] || MODELS=(gte zer)
ROOT=$(realpath -e "$SETS_ROOT" 2>/dev/null) || { echo "STOP: --sets-root <root> is required"; exit 2; }
RUNS=$ROOT/runs/fresh-80; F=$O/drafts/fresh80
"""

WINDOW = [
    ("#!/usr/bin/env bash\n", HEAD_W),
    ("Q=$P/e4; QC=$Q/caches; CNT=$Q/count; POINT=e4-window\n",
     PARSE + "Q=$RUNS/data/e4; QC=$Q/caches; CNT=$Q/count; POINT=trial\n"),
    ("if [ $# -gt 0 ]; then MODELS=(\"$@\"); else MODELS=(gte zer); fi\n", "# (the models: parsed above, with --sets-root)\n"),
    ('"reason": "the E4 scoring window ended (E3-E5-DESIGN §1)"',
     '"reason": "the fresh 80 E4 scoring window ended (data only, DEC-1097 (1)(c))"'),
    ("E4-WINDOW (E3-E5-DESIGN §1): the CTO", "E4-WINDOW ON THE FRESH 80 (data only): the CTO"),
    ('figures() { python3 -I "$D/e0_figures.py" "$1 alone on window 4 (the window\'s trial run)" '
     '"$P/$POINT/$1/r80/measure.txt" "$P/$POINT/$1/r60/measure.txt"; }',
     'figures() { echo "$1 alone on the 80 (the window\'s trial run): question lines $(grep -c \' (hidden): hit@5 \' '
     '"$Q/$POINT/$1/measure.txt")"; }'),
    ('  ( cd "$S" && sha256sum --quiet -c E4-REVIEWED.sha256 )\n}',
     '  ( cd "$S" && sha256sum --quiet -c E4-REVIEWED.sha256 ) || return 1\n'
     '  [ -s "$F/FRESH80-REVIEWED.sha256" ] && ( cd "$F" && sha256sum --quiet -c FRESH80-REVIEWED.sha256 )\n}'),
    ('counted() { [ -s "$CNT/need-$1.txt" ] && [ -s "$CNT/r80/measure.txt" ] && [ -s "$CNT/r60/measure.txt" ]; }',
     'counted() { [ -s "$CNT/need-$1.txt" ] && [ -s "$CNT/v80/measure.txt" ]; }'),
    ('  need "the measure, the scorer and the stop and backstop tools" test -f $S/so_measure.sh -a -f $D/e0_figures.py '
     '-a -f $O/tools/proc.sh -a -f $O/tools/gpu_backstop.sh\n',
     '  need "the measure and the stop and backstop tools" test -f $F/f80_so_measure.sh -a -f $O/tools/proc.sh '
     '-a -f $O/tools/gpu_backstop.sh\n'
     '  need "GOV_STORE unset (reviewer 1 S6)" test -z "${GOV_STORE+x}"\n'
     '  need "the fresh 80\'s hold has ended" eval \'! grep -q "FRESH-80 HOLD" $O/log/act-in-progress.txt 2>/dev/null\'\n'),
    ('    echo "  so_measure.sh $POINT $m r80, then r60: variant',
     '    echo "  f80_so_measure.sh $POINT $m (the 80, v80): variant'),
    ('  echo "after the window, no GPU: bash $S/e4_replays.sh',
     '  echo "after the window, no GPU: bash $F/f80_e4_replays.sh --sets-root <root>'),
    ('  echo "outputs: $Q/window/<stamp>/window.log; $P/$POINT/<m>/{r80,r60}/; gpu-<m>.txt; the caches $QC/<m>"',
     '  echo "outputs: $Q/window/<stamp>/window.log; $Q/$POINT/<m>/; gpu-<m>.txt; the caches $QC/<m>"'),
    ('    setsid bash "$S/so_measure.sh" "$POINT" "$m" "$2" "$VARIANT" "$QC/$m" < /dev/null & MP=$!',
     '    setsid bash "$F/f80_so_measure.sh" "$ROOT" "$POINT" "$m" "$VARIANT" "$QC/$m" < /dev/null & MP=$!'),
    ("  for set in r80 r60; do\n    measure \"$m\" \"$set\"", "  for set in v80; do\n    measure \"$m\" \"$set\""),
    ('stop "$m\'s runs failed (see $P/$POINT/measure.log)"', 'stop "$m\'s runs failed (see $Q/$POINT/measure.log)"'),
    ('exec > >(trap \'\' INT TERM; exec tee -p -a "$OUT/window.log") 2>&1; fi',
     'exec > >(trap \'\' INT TERM; tee -p -a "$OUT/window.log" | sed -u "s#$RUNS#<run folder>#g; s#$ROOT#<sets root>#g") 2>&1; '
     'else exec > >(sed -u "s#$RUNS#<run folder>#g; s#$ROOT#<sets root>#g") 2>&1; fi'),
    ('echo "== all models scored once; next, with no GPU: bash $S/e4_replays.sh"',
     'echo "== all models scored once; next, with no GPU: bash $F/f80_e4_replays.sh --sets-root <root>"'),
]

HEAD_R = """#!/usr/bin/env bash
# THE FRESH 80, DATA ONLY, NOT JUDGED (DEC-1097 (1)(c), (5)): E4's replays on the 80 (M3, M1), no GPU. Built by
# drafts/fresh80/make_f80_e4.py from drafts/score-once/e4_replays.sh; the list of changes is in make_f80_e4.py.
#   DRY=1 bash f80_e4_replays.sh --sets-root ~/gov-os-eval;  bash f80_e4_replays.sh --sets-root ~/gov-os-eval
# Then: fresh80_data.py e4 --sets-root ~/gov-os-eval (one reader call per question on each cell's first bundle).
# What follows is e4_replays.sh's own text, changed only as the list says.
"""

PARSE_R = """SETS_ROOT=""; CELLS=()
while [ $# -gt 0 ]; do case "$1" in --sets-root) SETS_ROOT=${2:-}; shift 2 || exit 2;; --sets-root=*) SETS_ROOT=${1#*=}; shift;; *) CELLS+=("$1"); shift;; esac; done
[ ${#CELLS[@]} -gt 0 ] || CELLS=(m3 m1)
ROOT=$(realpath -e "$SETS_ROOT" 2>/dev/null) || { echo "STOP: --sets-root <root> is required"; exit 2; }
RUNS=$ROOT/runs/fresh-80; F=$O/drafts/fresh80
"""

REPLAYS = [
    ("#!/usr/bin/env bash\n", HEAD_R),
    ("E=$P/e0b/caches; Q=$P/e4; QC=$Q/caches; CNT=$Q/count; POINT=e4\n",
     PARSE_R + "E=$P/e0b/caches; Q=$RUNS/data/e4; QC=$Q/caches; CNT=$Q/count; POINT=replays\n"),
    ("B80=$P/e0b/b/r80/measure.txt; B60=$P/e0b/b/r60/measure.txt\n", "BV=$Q/base/b/measure.txt\n"),
    ("if [ $# -gt 0 ]; then CELLS=(\"$@\"); else CELLS=(m3 m1); fi\n", "# (the cells: parsed above, with --sets-root)\n"),
    ('  ( cd "$S" && sha256sum --quiet -c E4-REVIEWED.sha256 )\n}',
     '  ( cd "$S" && sha256sum --quiet -c E4-REVIEWED.sha256 ) || return 1\n'
     '  [ -s "$F/FRESH80-REVIEWED.sha256" ] && ( cd "$F" && sha256sum --quiet -c FRESH80-REVIEWED.sha256 )\n}'),
    ('fresh() { local c; for c in "${CELLS[@]}"; do [ -e "$P/$POINT/$c" ] && return 1; done; return 0; }',
     'fresh() { local c; for c in "${CELLS[@]}"; do [ -e "$Q/$POINT/$c" ] && return 1; done; return 0; }'),
    ('  need "no output of these cells yet ($P/$POINT/<cell>)" fresh\n',
     '  need "no output of these cells yet ($Q/$POINT/<cell>)" fresh\n'
     '  need "GOV_STORE unset (reviewer 1 S6)" test -z "${GOV_STORE+x}"\n'),
    ('  need "E0b\'s run-B cache, the 0.6B\'s seed and run B\'s measures" test -s "$E/b/cache.db" -a -s "$E/seed/cache.db" '
     '-a -s "$B80" -a -s "$B60"',
     '  need "the 80\'s run-B cache (f80_e4_prep.sh), the 0.6B\'s seed and run B\'s measure" test -s "$QC/b/cache.db" '
     '-a -s "$E/seed/cache.db" -a -s "$BV"'),
    ('held q06 "$E/seed" "$E/b" 2>&1 | tail -1))" quietly held q06 "$E/seed" "$E/b";; esac',
     'held q06 "$E/seed" "$QC/b" 2>&1 | tail -1))" quietly held q06 "$E/seed" "$QC/b";; esac'),
    ('    echo "plan $c (${LABEL[$c]}): own cache $QC/own-$c = a fresh copy of $E/b; GOV_RX_COMBINE=${COMBINE[$c]}"',
     '    echo "plan $c (${LABEL[$c]}): own cache $QC/own-$c = a fresh copy of $QC/b; GOV_RX_COMBINE=${COMBINE[$c]}"'),
    ('    echo "  so_measure.sh $POINT $c r80, then r60: variant', '    echo "  f80_so_measure.sh $POINT $c (the 80, v80): variant'),
    ('    echo "  must read: unscored 0, texts scored live 0; kept outputs ~/gov-os-eval/runs/$POINT/$c-r80/, $c-r60/ '
     '(first call per question: the E4 bundle)"',
     '    echo "  must read: unscored 0, texts scored live 0; kept outputs $Q/$POINT/$c/kept/ (first call per question: '
     'the E4 bundle)"'),
    ('    echo "  figures: e0_figures.py; against E0b\'s run B: score138.py --same (reported)"',
     '    echo "  then: fresh80_data.py e4 (one reader call per question, data only)"'),
    ('    bash "$S/so_measure.sh" "$POINT" "$1" "$2" "$VARIANT" "$QC/own-$1"',
     '    bash "$F/f80_so_measure.sh" "$ROOT" "$POINT" "$1" "$VARIANT" "$QC/own-$1"'),
    ('local line; line=$(grep "^$1 $2: " "$P/$POINT/measure.log" | tail -1)',
     'local line; line=$(grep "^$1 $2: " "$Q/$POINT/measure.log" | tail -1)'),
    ('copy_own() { rm -rf "$QC/own-$1"; cp -a "$E/b" "$QC/own-$1"; }',
     'copy_own() { rm -rf "$QC/own-$1"; cp -a "$QC/b" "$QC/own-$1"; }'),
    ('figures() { python3 -I "$D/e0_figures.py" "${LABEL[$1]}" "$P/$POINT/$1/r80/measure.txt" "$P/$POINT/$1/r60/measure.txt"; }',
     'figures() { echo "${LABEL[$1]}: question lines $(grep -c \' (hidden): hit@5 \' "$Q/$POINT/$1/measure.txt")"; }'),
    ('against_b() { python3 -I "$D/score138.py" --same "$P/$POINT/$1/r80/measure.txt" "$P/$POINT/$1/r60/measure.txt" "$B80" "$B60"; }',
     'against_b() { echo "$1: compared with the judged run in fresh80_data.py e4 (data only)"; }'),
    ('if [ "${DRY:-0}" != 1 ]; then OUT=$Q/replays-$(date +%Y%m%d-%H%M%S).log; mkdir -p "$Q"; exec > >(tee -a "$OUT") 2>&1; fi',
     'if [ "${DRY:-0}" != 1 ]; then OUT=$Q/replays-$(date +%Y%m%d-%H%M%S).log; mkdir -p "$Q"; exec > >(tee -a "$OUT" | sed -u "s#$RUNS#<run folder>#g; s#$ROOT#<sets root>#g") 2>&1; '
     'else exec > >(sed -u "s#$RUNS#<run folder>#g; s#$ROOT#<sets root>#g") 2>&1; fi'),
    ('  for set in r80 r60; do\n    replay "$c" "$set"', '  for set in v80; do\n    replay "$c" "$set"'),
    ('replay "$c" "$set" || stop "$c $set: the replay failed (a text lacking stops it, by design; see $P/$POINT/$c/$set/rx.err)"',
     'replay "$c" "$set" || stop "$c $set: the replay failed (a text lacking stops it, by design; see $Q/$POINT/$c/rx.err)"'),
    ('echo "== $(date \'+%F %T\') E4 replays done; the bundles: ~/gov-os-eval/runs/$POINT/<cell>-<set>/, first calls by $P/$POINT/<cell>/<set>/measure.txt"',
     'echo "== $(date \'+%F %T\') E4 replays on the 80 done; next: fresh80_data.py e4 --sets-root <root>"'),
]


def build(src: Path, pairs) -> str:
    text = src.read_text()
    for old, new in pairs:
        n = text.count(old)
        if n != 1:
            raise SystemExit(f"make_f80_e4: {src.name}: a replacement's old text stands {n} times, not once: "
                             f"{old[:70]!r}")
        text = text.replace(old, new)
    return text


def outputs() -> dict:
    return {"f80_e4_window.sh": build(SO / "e4_window.sh", WINDOW),
            "f80_e4_replays.sh": build(SO / "e4_replays.sh", REPLAYS)}


if __name__ == "__main__":
    outs = outputs()
    if sys.argv[1:] == ["--check"]:
        bad = [n for n, t in outs.items() if not (HERE / n).is_file() or (HERE / n).read_text() != t]
        print("make_f80_e4: " + ("as built" if not bad else f"differs: {bad}"))
        sys.exit(1 if bad else 0)
    for n, t in outs.items():
        (HERE / n).write_text(t)
        print(f"make_f80_e4: wrote {n}")
