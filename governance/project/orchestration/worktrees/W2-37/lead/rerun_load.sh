#!/bin/bash
# Re-runs the load-sensitive cases (DEC-372, DEC-760, DEC-762) alone, each in its own pytest process, to its end.
W=/home/usain/gov-os-worktrees/W2-37
L=$W/.gov-runtime/scratch/lead/log
cd $W || exit 2
run() {
  tag=$1; suite=$2; expr=$3
  PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-37/src \
    python3 -m pytest tests/acceptance/$suite -q -p no:cacheprovider -rs -k "$expr" > $L/$tag.txt 2>&1
  echo $? > $L/$tag.rc
}
run r2-W1-02 W1-02 "test_decision_p95_is_under_100_ms"
run r2-W1-19 W1-19 "test_a_warm_query_answers_within_half_a_second_at_p95"
run r2-W1-46 W1-46 "research_install or research_bash_write or research_write_to_a_new_path or starting_host or refuses_a_domain or temp_directory_of_its_own"
echo done > $L/r2.done
