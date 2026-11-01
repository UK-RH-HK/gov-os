"""Runs `gov rebuild --json` in-process for the tree in the current directory and times the secrets filter.

The filter's functions are wrapped where the lexical and code-index stages call them, as W2-76's watch does: the wall
time while at least one call runs (threads at once count once). Prints one JSON line with the figures.
Usage: python3 measure_rebuild.py <label>   (PYTHONPATH chooses the code under test)
"""

import functools
import io
import json
import sys
import threading
import time
from contextlib import redirect_stdout


class Spans:
    def __init__(self):
        self.lock, self.active, self.since, self.spent, self.calls = threading.Lock(), 0, None, 0.0, 0

    def wrap(self, function):
        @functools.wraps(function)
        def timed(*args, **kwargs):
            with self.lock:
                if not self.active:
                    self.since = time.monotonic()
                self.active += 1
                self.calls += 1
            try:
                return function(*args, **kwargs)
            finally:
                with self.lock:
                    self.active -= 1
                    if not self.active:
                        self.spent += time.monotonic() - self.since
                        self.since = None
        return timed


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "run"
    import gov
    import gov.codeintel as codeintel
    import gov.retrieval.lexical as lexical
    import gov.secrets as secrets
    from gov.cli.main import main as cli

    spans = Spans()
    lexical.indexable = spans.wrap(lexical.indexable)
    codeintel.indexable = spans.wrap(codeintel.indexable)
    codeintel.path_holds_secret = spans.wrap(codeintel.path_holds_secret)
    counts = getattr(secrets, "scan_counts", None)
    before = counts() if counts else None
    started = time.monotonic()
    out = io.StringIO()
    with redirect_stdout(out):
        code = cli(["rebuild", "--json"])
    total = time.monotonic() - started
    try:
        record = json.loads(out.getvalue())
    except ValueError:
        record = {"unparsed_tail": out.getvalue()[-400:]}
    print(json.dumps({"label": label, "gov_file": gov.__file__, "exit": code, "rebuild_s": round(total, 1),
                      "secrets_s": round(spans.spent, 1), "filter_calls": spans.calls,
                      "counts_before": before, "counts_after": counts() if counts else None,
                      "status": {k: v.get("status") if isinstance(v, dict) else v for k, v in record.items()
                                 if k in ("lexical", "semantic", "codeintel", "status", "ok")},
                      "timing": record.get("timing")}))


if __name__ == "__main__":
    main()
