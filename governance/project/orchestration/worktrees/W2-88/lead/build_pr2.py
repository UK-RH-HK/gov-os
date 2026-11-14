from pathlib import Path

LEAD = Path("/home/usain/gov-os-worktrees/W2-88/.gov-runtime/scratch/lead")
OUT = Path("/home/usain/gov-os-worktrees/W2-88/docs/probes/DAEO-2bdu/PR-DAEO-2bdu-round-2.md")
head = (LEAD / "pr-round-2-head.md").read_text()
verify = (
    "RED, parallel 6,237 tests, 9 failed, 8 skipped; serial 3 passed "
    "(`.gov-runtime/scratch/lead/log/verify/parallel.xml`, `serial.xml`). The 9: (i) four cases (W2-02 `test_core_schema_is_green_on_this_repository`, "
    "W1-08 `test_the_probe_schema_accepts_this_repository_s_probe_records`, W1-26 `test_this_repository_s_probe_records_are_well_formed` and "
    "`test_no_finding_of_the_check_on_this_repository_names_a_probe_record`) are this branch's: round 1's probe record lacked `implementer_session` "
    "(probe.schema.json requires it); fixed in the commit that adds this record, and this record carries it; "
    "(ii) `tests/acceptance/W2-124/test_w2_124_s1_semantic_fails_named.py::test_s1_hung_or_transient_failing_embedder_raises_rebuild_failed_semantic[hung]` "
    "took 61.8 s against 60 s under the full run's load; alone: 2 passed in 53 s (load-sensitive); "
    "(iii) three cases of `tests/unit/orchestration/test_cto_safety_nets.py` read the live CTO inbox (2 unread items at 12:01) and passed alone (15 passed): "
    "environment-dependent, not this branch's (the CTO's, DEC-1156 (7)); "
    "(iv) `tests/acceptance/W2-23/test_w2_23_space.py:94` (`context_watch.py` not in the settings' hook lines), red on the integrate tree in round 1 too: integrate's, not this branch's."
)
head = head.replace("@VERIFY@", verify)
head = head.replace("reviewer_session: c56e1745-57dd-42fb-bece-ed52b319a502\n",
                    "reviewer_session: c56e1745-57dd-42fb-bece-ed52b319a502\n"
                    "implementer_session: dab23ba0-5ebf-4d2b-ad86-7864ac080286 (eng-2, run 4's fix); 18a2ad97-3f9c-46b2-8b10-5f13aa084636 (eng-3, L-1)\n")
review = (LEAD / "log" / "rv-2.review.md").read_text().splitlines(keepends=True)
start = next(i for i, line in enumerate(review) if line.startswith("# W2-88 (DAEO-2bdu): review round 2"))
OUT.write_text(head + "".join(review[start:]).rstrip("\n") + "\n")
print(OUT, len(OUT.read_text().splitlines()))
