"""W2-116 fix P0-1 (plan item 0-1; DAEO-f58b "Fix: the refresh retried and checked"): a failed refresh is retried at the
next ``--when-due`` tick and checked by ``gov status``, ``gov brief`` and ``gov retrieve``.

Each case builds a store at the integration branch's head (a successful refresh at 18:05, so no time makes the next tick
due), lands a merge (the store is behind the branch head by two commits) and works with that. The failed refresh is the
build's embedder gone (``OLLAMA_HOST`` at an address where nothing listens). The tick's output goes to a log file the case
owns, as a cron line does. README: "P0-1".
"""

from __future__ import annotations

import re

import w2_116_p0_support as p0
import w2_116_s2_support as s2
import w2_116_support as support
from w2_116_s2_support import DAY1, at


def test_p0_1_a_failed_refresh_is_logged_the_next_tick_retries_and_succeeds(box, env, project):
    h1 = p0.built_store(box, env, project)
    h2 = support.land_h2(project)
    cron = p0.Cron(box, project, env)
    # nothing is due by the clock (the record is from 18:05) but the store is behind the branch head: that is due
    failed = cron.tick(at(DAY1, "18:10"), env=p0.broken(env))
    assert "REBUILD_FAILED" in cron.text(), (
        f"the tick's log does not hold REBUILD_FAILED (a store behind the head is due, and its refresh failed)\n"
        f"{failed.describe()}")
    assert failed.returncode != 0, f"a tick whose refresh failed exited 0\n{failed.describe()}"
    assert support.worktrees(project).get(support.assert_link(box), {}).get("head") == h1, (
        "the failed refresh moved the link off the store at H1")
    mark = len(cron.text())
    # the next tick, the fault removed: the same refresh is retried, with nothing due by the clock
    retried = cron.tick(at(DAY1, "18:11"))
    later = cron.text()[mark:]
    assert retried.returncode == 0, f"the retry tick did not succeed\n{retried.describe()}"
    assert "retry" in later.lower(), f"the retry tick's output does not say it is a retry:\n{later}"
    assert h2[:12] in later, f"the retry tick's output has no success line naming the head {h2[:12]}:\n{later}"
    assert "REBUILD_FAILED" not in later, f"the retry tick failed again:\n{later}"
    assert support.worktrees(project).get(support.assert_link(box), {}).get("head") == h2, (
        "the retry did not bring the store to the branch head")
    # at the head with nothing due: the tick builds nothing
    quiet = cron.tick(at(DAY1, "18:12"))
    s2.assert_not_due(
        support.gov(project, s2.now_env(env, at(DAY1, "18:12")), "rebuild", "--json", support.INTEGRATION,
                    support.BRANCH, "--when-due"), box, support.BRANCH, "the store at the head, nothing due")
    assert quiet.returncode == 0, f"a tick with nothing to do failed\n{quiet.describe()}"


def test_p0_1_status_json_gives_behind_by_and_red_while_behind_and_zero_once_equal(box, env, project):
    h1 = p0.built_store(box, env, project)
    h2 = support.land_h2(project)
    behind = p0.status_run(project, env, "--json")
    part = p0.part_of(behind)
    expected = p0.commits_between(project, h1, h2)
    assert expected >= 1
    assert part.get("behind_by") == expected, f"behind_by is {part.get('behind_by')!r}, expected {expected}\n{behind.describe(800)}"
    assert p0.red_flag(behind) is True, "a store behind the head: the status is not red"
    support.built_integration(project, env)
    equal = p0.status_run(project, env, "--json")
    part = p0.part_of(equal)
    assert part.get("behind_by") == 0, f"the store equals the head, behind_by is {part.get('behind_by')!r}"
    assert p0.red_flag(equal) is False, "the store equals the head: the status is red"


def test_p0_1_status_text_prints_the_sentence_while_behind_and_nothing_of_it_once_equal(box, env, project):
    h1 = p0.built_store(box, env, project)
    h2 = support.land_h2(project)
    n = p0.commits_between(project, h1, h2)
    behind = p0.status_run(project, env)
    assert p0.sentence(n) in behind.stdout, f"`gov status` does not print {p0.sentence(n)!r}\n{behind.describe(1500)}"
    assert behind.returncode != 0 or re.search(r"status: red|\"red\": true", behind.stdout), (
        f"a store behind the head: `gov status` exits 0 and says nothing red\n{behind.describe(1500)}")
    support.built_integration(project, env)
    equal = p0.status_run(project, env)
    assert p0.BEHIND_SENTENCE not in equal.stdout + equal.stderr, (
        f"the store equals the head, `gov status` still names it behind\n{equal.describe(1500)}")


def test_p0_1_gov_retrieve_names_a_store_behind_head_with_both_commits_and_nothing_once_equal(box, env, project):
    support.rebuild(project, env)                        # the project's own store, at H1
    assert (project / support.STORE_REL).is_file(), "premise: the rebuild made no store in the project"
    h1 = support.head(project)
    h2 = support.land_h2(project)
    behind = support.gov(project, env, "retrieve", s2.QUESTION, timeout=support.WAIT_S)
    text = behind.stdout + behind.stderr
    assert p0.BEHIND_SENTENCE in text, f"`gov retrieve` does not name the store behind HEAD\n{behind.describe(1500)}"
    assert h1[:12] in text and h2[:12] in text, (
        f"`gov retrieve` does not name both the store's commit {h1[:12]} and HEAD {h2[:12]}\n{behind.describe(1500)}")
    again = support.rebuild(project, env)
    assert again.ok, f"premise: the second rebuild did not succeed\n{again.describe()}"
    equal = support.gov(project, env, "retrieve", s2.QUESTION, timeout=support.WAIT_S)
    assert p0.BEHIND_SENTENCE not in equal.stdout + equal.stderr, (
        f"the store equals HEAD, `gov retrieve` still names it behind\n{equal.describe(1500)}")


def test_p0_1_gov_brief_names_a_store_behind_head_with_both_commits_and_nothing_once_equal(box, env, project):
    b197 = p0.brief_ready(project)
    built = support.rebuild(project, env)
    assert built.ok, f"premise: the rebuild did not succeed\n{built.describe()}"
    h1 = support.head(project)
    h2 = support.land_h2(project)
    run, text = p0.brief(project, env, b197)
    assert run.returncode == 0 and text.strip(), f"premise: gov brief did not print a brief\n{run.describe(1500)}"
    assert p0.BEHIND_SENTENCE in text, f"`gov brief` does not name the store behind HEAD\n{text[-1500:]}"
    assert h1[:12] in text and h2[:12] in text, (
        f"`gov brief` does not name both the store's commit {h1[:12]} and HEAD {h2[:12]}\n{text[-1500:]}")
    again = support.rebuild(project, env)
    assert again.ok, f"premise: the second rebuild did not succeed\n{again.describe()}"
    run, text = p0.brief(project, env, b197)
    assert run.returncode == 0, f"premise: gov brief refused at the head\n{run.describe(1500)}"
    assert p0.BEHIND_SENTENCE not in text, f"the store equals HEAD, `gov brief` still names it behind\n{text[-1500:]}"
