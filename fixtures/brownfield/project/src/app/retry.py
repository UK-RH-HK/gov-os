"""Retry helper. NOTE: spec says 5, code says 3 (deliberate code/spec disagreement)."""
MAX_RETRIES = 3


def with_retry(fn, attempts: int = MAX_RETRIES):
    last = None
    for _ in range(attempts):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            last = e
    raise RuntimeError(f"failed after {attempts} attempts: {last}")
