"""KPI success 3: lexical search returns "unavailable" instead of raising [W2-M071, W2-M100, DEC-260, DEC-342].

A missing, empty, stale or unreadable index answers ``available: false`` with the state ``FACET_UNAVAILABLE`` and a
reason, and no hit; it never raises. A question with no token, and a question that FTS5 would read as syntax, never
make search raise either. ``gov retrieve`` on such a store, or with such a question, answers a bundle or a
governance error (exit 0 or 1, one JSON envelope), never a traceback.

The latency half of the line is in ``test_w2_13_latency.py``.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

import w2_13_support as support

pytestmark = pytest.mark.needs("git", "gitleaks", "sqlite_vec")

# The lexical index as W1-17 left it on the base (w2/integrate at c38a5b49bc86): "a store from before this change".
# Copied as the frozen "before" form; one file's rows, so the base itself answers it as stale.
BEFORE_FORM = (
    "CREATE TABLE lexical_file (path TEXT PRIMARY KEY, blob TEXT NOT NULL, indexed INTEGER NOT NULL)",
    "CREATE TABLE lexical_parent (parent_id TEXT PRIMARY KEY, path TEXT NOT NULL, kind TEXT NOT NULL, "
    "start_line INTEGER NOT NULL, end_line INTEGER NOT NULL)",
    "CREATE TABLE lexical_chunk (id INTEGER PRIMARY KEY, chunk_id TEXT NOT NULL UNIQUE, path TEXT NOT NULL, "
    "start_line INTEGER NOT NULL, end_line INTEGER NOT NULL, parent_id TEXT NOT NULL)",
    "CREATE VIRTUAL TABLE lexical_fts USING fts5(text, tokenize = \"porter unicode61 tokenchars '_'\")",
    "INSERT INTO lexical_parent VALUES ('p-readme', 'README.md', 'section', 1, 3)",
    "INSERT INTO lexical_chunk VALUES (1, 'c-readme', 'README.md', 1, 3, 'p-readme')",
    "INSERT INTO lexical_fts (rowid, text) VALUES (1, '# A project\n\nOrdinary text about the project.')",
)

STORES = ("missing", "an empty file", "not a database", "a database without the lexical table",
          "the form before this change", "stale")


def make_store(box, root, state):
    """Give the clone ``root`` the store ``state`` names."""
    store = Path(root) / support.STORE_REL
    if state == "missing":
        return
    if state == "stale":
        box.rebuild(root)
        support.write(root, support.BEST, support.RANKED[support.BEST] + "A line added after the rebuild.\n")
        support.commit(root, "a change after the rebuild")
        return
    store.parent.mkdir(parents=True, exist_ok=True)
    if state == "an empty file":
        store.write_bytes(b"")
    elif state == "not a database":
        store.write_bytes(b"W2-13: these bytes are not an SQLite database.\n" * 64)
    else:
        with sqlite3.connect(str(store)) as connection:
            if state == "a database without the lexical table":
                connection.execute("CREATE TABLE unrelated (name TEXT)")
                connection.execute("INSERT INTO unrelated VALUES ('W2-13')")
            else:
                blob = support.git(root, "rev-parse", "HEAD:README.md").strip()
                connection.execute(BEFORE_FORM[0])
                connection.execute("INSERT INTO lexical_file VALUES ('README.md', ?, 1)", (blob,))
                for statement in BEFORE_FORM[1:]:
                    connection.execute(statement)
        connection.close()


@pytest.mark.parametrize("state", STORES)
def test_a_search_of_an_unusable_index_answers_unavailable_and_never_raises(box, repo, state):
    make_store(box, repo, state)
    outcome = box.run([(support.LEXICAL, "search", [support.path_arg(repo), support.PLAIN_QUESTION],
                        {"refresh": False})])
    error = outcome.error()
    assert error is None, f"lexical search raised {error['type']} on a store that is {state}: {error['message']}"
    answer = support.check_answer(outcome.value(), support.PLAIN_QUESTION)
    assert answer["available"] is False, f"a store that is {state} is answered as available: {answer!r}"


@pytest.mark.parametrize("state", [state for state in STORES if state not in ("missing", "stale")])
def test_a_default_search_that_may_refresh_never_raises_on_an_unreadable_store(box, repo, state):
    """A default search may rebuild first (DEC-342); whatever it does with a store it cannot read, it answers."""
    make_store(box, repo, state)
    outcome = box.run([(support.LEXICAL, "search", [support.path_arg(repo), support.PLAIN_QUESTION], {"refresh": True})])
    error = outcome.error()
    assert error is None, f"a default lexical search raised {error['type']} on a store that is {state}: " \
                          f"{error['message']}"
    support.check_answer(outcome.value(), support.PLAIN_QUESTION)


@pytest.mark.parametrize("state", STORES)
def test_gov_retrieve_on_an_unusable_index_answers_without_a_traceback(box, repo, state):
    make_store(box, repo, state)
    support.no_traceback(box.retrieve(repo, support.PLAIN_QUESTION))


# ---- questions

NO_TOKEN = ("", "   ", "?", "?!", "...", "--", "()", '""', "*", ":", "^", "+-", "'")
FTS5_SYNTAX = ('"', 'say "hello', "AND", "OR", "NOT", "NEAR", "harbour AND", "AND pilot", "pilot OR", "NOT tide",
               "NEAR(pilot tide)", "NEAR(pilot tide, 2)", "pilot*", "*pilot", "pil*ot", "text:pilot", "body:harbour",
               "title: pilot", "id:DEC-0042", "text : tide", "{text title}: pilot", "col:value", "a:b:c", "(pilot",
               "pilot)", "(pilot OR tide) AND", "^harbour", "-pilot", "pilot + tide", '"pilot" "tide"',
               "pilot's tide", "DEC-0042 AND NOT", "lexical_fts:pilot", "\\", "%", "_")
QUESTIONS = {"no token": NO_TOKEN, "FTS5 syntax": FTS5_SYNTAX}


@pytest.mark.parametrize("kind", list(QUESTIONS))
def test_no_question_makes_a_search_raise(box, built, kind):
    """The index is fresh: every answer is available, and none raises (W2-M100)."""
    answers = box.searches(built, list(QUESTIONS[kind]))
    raised = {question: answer["raised"] for question, answer in answers.items() if "raised" in answer}
    assert not raised, f"lexical search raised for these questions: {raised}"
    for question, answer in answers.items():
        support.check_answer(answer, question)
        assert answer["available"] is True, f"a fresh index is answered as unavailable for {question!r}: {answer!r}"


@pytest.mark.parametrize("question", ['"', "NEAR(pilot tide)", "text:pilot", "?!", "(pilot OR tide) AND"])
def test_gov_retrieve_answers_any_question_without_a_traceback(box, built, question):
    """An empty question is left out: the command may refuse it as a usage error (exit 2, W1-21's interface)."""
    support.no_traceback(box.retrieve(built, question))
