"""F: any repo-wide prune left in the nightly; another worktree's registration or index lost; a clone's failed removal
hidden [DEC-939 item 5, DEC-915 item 4, row W2-M406].

The failure line's three conditions, on one night where all of them can happen together: the clone's removal fails
(the suite locks the clone), a second worktree holding a staged change is moved aside for the whole night, and a
stale registration is planted. The failure path is where a fallback prune would be most tempting; none may run.

Red reason on the base (README): the night runs ``git worktree prune``, which drops the hidden worktree (its
registration, its administrative folder and its index) and the stale registration, and the failed removal is in
neither the record nor standard error.
"""

import w2_77_support as support

STAGED = {"staged-change.txt": "a change staged in the hidden worktree\n"}


def test_no_prune_no_other_worktree_lost_and_the_failed_removal_not_hidden(tmp_path):
    project = support.Project(tmp_path, lock=True)
    hidden = project.add_worktree(tmp_path / "hidden", staged=STAGED)
    stale = project.plant_stale(tmp_path / "stale")
    with support.moved_aside(hidden.path):
        run = project.nightly()
    support.green(run)
    found = []
    prunes = support.worktree_calls(project.git_calls(), "prune")
    if prunes:
        found.append(f"a repo-wide git worktree prune ran: {prunes}")
    if not support.is_registered(project.root, hidden.path) or not hidden.entry.is_dir():
        found.append(f"the hidden worktree {hidden.path} lost its registration or its administrative folder")
    elif support.git_run(hidden.path, "diff", "--cached", "--name-only").stdout.split() != sorted(STAGED):
        found.append(f"the hidden worktree {hidden.path} lost its staged index")
    if not support.is_registered(project.root, stale.path):
        found.append(f"the stale registration of {stale.path} was dropped")
    record, rel = support.record_of(project, run)
    clone, _ = project.clone()
    if not isinstance(record.get(support.CLEANUP_KEY), dict):
        found.append(f"the clone's failed removal is not in the record {rel} (no {support.CLEANUP_KEY!r} key)")
    if not support.stderr_lines_naming(run, clone):
        found.append(f"no line of standard error names the clone {clone} whose removal failed")
    assert not found, "the failure line is met:\n- " + "\n- ".join(found)
