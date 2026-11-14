"""The differential matrix of ACT-GUARD-FIX-5's rehearsal: python3 -B -I matrix_cases.py <out.json>. Heads (a shell with and
without options, the readers that take a heredoc as data, a file-writing reader) x bodies x quoted and unquoted delimiter
x two tails, as an engineer and as an auditor. Not asserted case by case: the rehearsal asserts that no call refused
before is allowed after."""
import itertools
import json
import sys

T = "tests/acceptance/X/zz.py"
HEADS = ["bash", "sh", "bash -o pipefail", "bash -euo pipefail", "bash -O extglob", "bash +o history",
         "bash --rcfile /dev/null", "bash --norc", "bash -s", "bash -", "bash /dev/stdin", "bash -c 'echo hi'",
         "bash script.sh", "bash -o pipefail script.sh", "cat", "tee s.sh", "bash -o pipefail > s.sh", "python3 -",
         "bash -Z", "zsh -o errexit"]
BODIES = ["echo hi", f"touch {T}", f"echo x > {T}", f"echo $(touch {T})", "echo $(date)", f"echo `touch {T}`",
          "rm -rf tests/acceptance/X", "echo x > src/gov/zz.py"]
TAILS = ["", "\nbash s.sh"]
cases = []
for (h, b, quoted, tail), role in itertools.product(itertools.product(HEADS, BODIES, (False, True), TAILS),
                                                    ("engineer", "independent-auditor")):
    d = "'EOF'" if quoted else "EOF"
    cases.append({"id": f"{role[:3]}|{h}|{b}|{'q' if quoted else 'u'}|{'run' if tail else '-'}",
                  "command": f"{h} <<{d}\n{b}\nEOF{tail}", "role": role, "expect_after": "any"})
json.dump({"cases": cases}, open(sys.argv[1], "w"))
print(len(cases))
