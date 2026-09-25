"""Historical lesson/failure retrieval (ARCHITECTURE.md section 6.3): a profile over existing units, ordered by
commit time and labelled -- withdrawn/superseded records surface with their current lifecycle."""
from govbridge.graph import history


def test_history_finds_withdrawn_seed(fixture_repo, view_path, registry_path):
    result = history.history("FX-WITHDRAWN-0001", repo=str(fixture_repo.root), view_path=view_path,
                              registry_path=registry_path)
    kinds = {e["kind"] for e in result["entries"]}
    assert "withdrawn_or_superseded" in kinds


def test_history_finds_lesson_mention(fixture_repo, view_path, registry_path):
    result = history.history("FX-0001", repo=str(fixture_repo.root), view_path=view_path,
                              registry_path=registry_path)
    kinds = [e["kind"] for e in result["entries"]]
    assert "lesson" in kinds


def test_history_entries_sorted_by_commit_time(fixture_repo, view_path, registry_path):
    result = history.history("FX-0001", repo=str(fixture_repo.root), view_path=view_path,
                              registry_path=registry_path)
    times = [e["commit_time"] or "" for e in result["entries"]]
    assert times == sorted(times)
