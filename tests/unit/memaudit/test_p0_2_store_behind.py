"""P0-2: the pre-flight's store check; a repository that names no integration_store is not checked."""

from gov.memaudit import preflight


def test_a_repository_naming_no_store_is_not_checked(tmp_path):
    assert preflight.store_behind(tmp_path) is None


def test_the_refusal_line_names_both_commits():
    out = preflight.lines("refused", {"store_behind": {"store": "a" * 40, "head": "b" * 40}})
    assert out[0].startswith("STORE_BEHIND") and "a" * 12 in out[0] and "b" * 12 in out[0]
    assert out[-1] == preflight.NOT_OK_WORD
