from app.retry import MAX_RETRIES


def test_max_retries_matches_legacy_expectation():
    # stale test: asserts the 2023 limit (2); code says 3, requirement says 5
    assert MAX_RETRIES == 2
