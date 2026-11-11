"""Build the path-map edit on a clone's governance/project/path-map.yaml (text edit; keeps every other byte).
Usage: python3 -I build_edit.py <clone> <entries.yaml>"""
import sys
from pathlib import Path

clone, entries = Path(sys.argv[1]), Path(sys.argv[2]).read_text()
p = clone / "governance/project/path-map.yaml"
s = p.read_text()

anchor = "# Commits that W1-01's MR-3 history case accepts though they touch tests/acceptance/ without the test designer's\n"
assert s.count(anchor) == 1
block = (
    "# Old merge commits without a Task: trailer, whose work no ticket measured, accepted as history by the owner's\n"
    "# decision (DEC-734, DEC-1127). Each entry names one commit and the owner's ACCEPTED decision, which names that\n"
    "# commit. Only the owner's commit adds an entry.\n"
    "accepted_history:\n" + entries
)
s = s.replace(anchor, block + anchor)

old = ('  - test: "tests/acceptance/W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95"\n'
       '    decision: DEC-757\n'
       '    reason: "p95 latency under parallel load (DEC-372)"\n'
       '    fixed_by: W2-M332\n')
new = ('  - test: "tests/acceptance/W1-19/test_w1_19_real_models.py::test_a_warm_query_answers_within_half_a_second_at_p95"\n'
       '    decision: DEC-1127  # DEC-757 is DONE, not ACCEPTED (DEC-1098 (3)); DEC-1125 (1) names the red\n'
       '    reason: "p95 latency under parallel load (DEC-372)"\n'
       '    fixed_by: W2-155\n')
assert s.count(old) == 1
s = s.replace(old, new)

# The three acceptance_exemptions entries that clear nothing (DEC-900 is DONE; DEC-1123 names neither commit): the
# decision becomes DEC-1127, the old one kept in the comment (W1-01 reads `decision` as DEC-<n>; a comment is ignored).
for commit, old, why in (
    ("c9a08678644485a7528bc875164e110881b63d93", "    decision: DEC-900\n",
     "was DEC-900 (DONE, DEC-1098 (3)): the owner's commit that retired W1-42's two accepted_reds entries and cases"),
    ("ab169d051b82072f0db4350b2066eabf6919ffa0",
     "    decision: DEC-1123  # item (3); the merge settled a README conflict as the test designer had (DEC-253)\n",
     "was DEC-1123 (item 3), which does not name it: a merge that settled a README conflict as the test designer had (DEC-253)"),
    ("15952bbfa576dcfabb7d36d95912a848077e5c3c",
     "    decision: DEC-1123  # item (3); the owner's ACT-GUARD-SETS-1 commit deleted W2-84's hidden-half cases (DEC-1061, DEC-1097)\n",
     "was DEC-1123 (item 3), which does not name it: the owner's ACT-GUARD-SETS-1 commit that deleted W2-84's hidden-half cases (DEC-1061, DEC-1097)"),
):
    entry = f'  - commit: "{commit}"\n' + old
    assert s.count(entry) == 1, commit
    s = s.replace(entry, f'  - commit: "{commit}"\n    decision: DEC-1127  # {why}\n')
p.write_text(s)
