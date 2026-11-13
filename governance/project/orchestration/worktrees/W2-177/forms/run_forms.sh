#!/bin/bash
# W2-177 (DAEO-1k7y) S1/S2: run the six W2-96 signal cases (and R11's unit case, and any test_w2_177* file) in each
# start form, N times each.
# usage: bash run_forms.sh <tag> <N> [form ...]     forms: empty-home real-home setsid-bg bg-job (default: all four)
# Each run's output goes to <out>/<form>-<i>.txt (its first line: whether pytest began with SIGINT ignored); one line
# per run and the per-form counts go to <out>/counts.txt, <out> = .gov-runtime/scratch/forms/<tag>.
# The start forms:
#   empty-home  the verify's environment in the foreground: HOME an empty folder, PYTHONUSERBASE the real one
#   real-home   the real HOME, in the foreground (an interactive alone re-run's form)
#   setsid-bg   lead_verify.sh's form (line 30) and the cron nightly's (nightly_restart.sh line 181): `setsid ... &`
#               from a non-interactive bash, empty HOME
#   bg-job      a plain background job `... &` from a non-interactive bash, empty HOME
# A background job of a non-interactive bash starts with SIGINT and SIGQUIT ignored (bash, job control off).
set -u
TREE=/home/usain/gov-os-worktrees/W2-177
HERE=$TREE/.gov-runtime/scratch/forms
TAG=${1:?tag}; N=${2:?N}; shift 2
FORMS=("$@"); [ ${#FORMS[@]} -eq 0 ] && FORMS=(empty-home real-home setsid-bg bg-job)
OUT=$HERE/$TAG
EMPTY=$TREE/.gov-runtime/scratch/empty-home
mkdir -p "$OUT" "$EMPTY"
cd "$TREE" || exit 2
for form in "${FORMS[@]}"; do
  case $form in real-home) H=/home/usain ;; *) H=$EMPTY ;; esac
  pass=0; fail=0
  for i in $(seq 1 "$N"); do
    log=$OUT/$form-$i.txt
    case $form in
      empty-home|real-home) env HOME="$H" bash "$HERE/inner.sh" > "$log" 2>&1 < /dev/null ;;
      setsid-bg) env HOME="$H" setsid bash "$HERE/inner.sh" > "$log" 2>&1 < /dev/null & wait $! ;;
      bg-job)    env HOME="$H" bash "$HERE/inner.sh" > "$log" 2>&1 < /dev/null & wait $! ;;
      *) echo "unknown form $form"; exit 2 ;;
    esac
    summary=$(grep -E "^[0-9]+ (passed|failed|error)|^=+ .*(passed|failed|error)" "$log" | tail -1)
    ign=$(grep -o "SIGINT-ignored-at-start: [01]" "$log" | head -1)
    echo "$form run $i: $ign | $summary" | tee -a "$OUT/counts.txt"
    if grep -qE "failed|error|skipped|deselected" <<< "$summary" || [ -z "$summary" ]; then fail=$((fail+1)); else pass=$((pass+1)); fi
  done
  echo "FORM $form: $pass of $N runs all passed, $fail with a red (or skip)" | tee -a "$OUT/counts.txt"
done
