"""W2-185's folder runs its own cases and the existing cases its Verify clauses name.

``gov accept`` runs pytest on the ticket's declared folder. The README maps each KPI line to cases: the ones in this
folder, and the ones that stay in other folders (W2-23 S6, program_env's and W2-05's two-sources cases, W1-38's
fixture case). So that a run of this folder is a run of exactly those, a run whose only argument is this folder is
pointed at the README's node ids: the mapped cases of other folders, each with its own folder's conftest and fixtures,
then this folder's own cases. A name the README gives that no file holds makes pytest report a collection error, which
``gov accept`` reports for the whole run, so a mapped case cannot go missing unseen. A run that names a node of this
folder, or this folder with another path, keeps its arguments.
"""
import os
from pathlib import Path

from w2_185_support import HERE, ROOT, external_node_ids, own_node_ids


def _is_this_folder(config, arg: str) -> bool:
    if "::" in arg:
        return False
    path = Path(arg)
    if not path.is_absolute():
        path = Path(config.invocation_params.dir) / path
    return Path(os.path.normpath(path)).resolve() == HERE


def pytest_configure(config):
    ids = external_node_ids() + own_node_ids()
    if ids and config.args and all(_is_this_folder(config, arg) for arg in config.args):
        config.args[:] = [str(ROOT / node) for node in ids]
