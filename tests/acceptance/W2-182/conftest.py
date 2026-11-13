"""W2-182's folder runs the revised cases of other folders, and only those.

``gov accept`` runs pytest on the ticket's declared folder alone, and this folder holds no revised case of its own:
the cases the revision changed stay in their own files (W1-18, W1-32, W2-121, W2-123, W2-128, W2-136, W2-23), each
with the fixtures of its own folder's conftest. So that a run of this folder is a run of exactly the cases the README
maps (DEC-892: a test-revision ticket is judged on its declared revised suites), the run is pointed at the README's
node ids: every backticked ``tests/acceptance/...::test_...`` in its tables, in order, each once. The cases keep their
own node ids, their own files and their own folders' conftests; nothing is copied, imported by name or re-written
here. A name in the README that no file holds makes pytest report a collection error, which ``gov accept`` reports as
an error for the whole run, so a mapped case cannot go missing unseen.
"""
from w2_182_support import ROOT, mapped_node_ids


def pytest_configure(config):
    """Replace the folder argument by the mapped cases' node ids (absolute, so the run's directory does not matter)."""
    ids = mapped_node_ids()
    if ids:
        config.args[:] = [str(ROOT / node) for node in ids]
