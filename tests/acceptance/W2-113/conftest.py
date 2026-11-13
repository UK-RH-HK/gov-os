"""W2-113 acceptance fixtures: one generated product and one stand-in home per session; one planted repository per
adoption case, adopted once and shared by the cases that judge it (README, "How the cases run")."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_113_support as support  # noqa: E402

w110 = support.w110


@pytest.fixture(scope="session")
def workspace():
    """A temporary folder for the session's trees (under the ``TMPDIR`` the run is given), removed at its end."""
    base = Path(tempfile.mkdtemp(prefix="w2113-"))
    try:
        yield base
    finally:
        support.remove_tree(base)


@pytest.fixture(scope="session")
def generated(workspace):
    """The product: copier copy of this worktree's template, then rulesync generate (W2-90), as W2-110 makes it."""
    try:
        project = w110.wiring.generate_project(workspace / "generated", "product")
    except AssertionError as exc:
        pytest.fail(f"the product could not be generated from the template: {exc}", pytrace=False)
    hook = project / w110.KERNEL_HOOK_REL
    template_hook = support.REPO_ROOT / w110.TEMPLATE_HOOK_REL
    if not hook.is_file() or hook.read_bytes() != template_hook.read_bytes():
        pytest.fail(f"the generated product's {w110.KERNEL_HOOK_REL} is not this worktree's "
                    f"{w110.TEMPLATE_HOOK_REL}: the cases would judge other code (DEC-732)", pytrace=False)
    return project


@pytest.fixture(scope="session")
def sandbox(workspace):
    """The stand-in home (W1-38's ``make_session_sandbox``): its ``gov`` names this interpreter, its user site names
    this worktree's ``src``. Checked: the hook's interpreter imports this worktree's package."""
    box = w110.session_support.make_session_sandbox(workspace / "session")
    found = w110.gov_the_hook_imports(box)
    expected = (support.REPO_ROOT / "src" / "gov" / "__init__.py").resolve()
    if not found or Path(found).resolve() != expected:
        pytest.fail(f"the hook's interpreter imports gov from {found!r}, not this worktree's {expected}: the cases "
                    f"would judge other code (DEC-732)", pytrace=False)
    return box


@pytest.fixture(scope="session")
def box(workspace):
    """The planted HOME, TMPDIR and outside folder of the ``gov adopt`` child process (W2-23's box)."""
    return support.w23.make_box(workspace / "adoption-box")


ROSTERS = {
    "standard": {},                                                       # no roster at all
    "names-by-id": {"roster": support.roster_naming(support.OTHER.id)},   # I2 (i): the key names an existing ticket
    "names-by-wbs": {"roster": support.roster_naming(support.OTHER.wbs)},
    "other-content": {"roster": support.OTHER_CONTENT},                   # I2 (ii): a roster without the key
    "no-tk": {"without_tk": True},                                        # I2 (iii): the vendored tk is missing
}


@pytest.fixture(scope="session")
def adoption(generated, box, workspace):
    """``adoption(name)``: the planted repository ``name`` adopted at A0 (``ROSTERS``), made once per session."""
    made = {}

    def adopted(name="standard"):
        if name not in made:
            made[name] = support.adopt(generated, workspace / "adopted" / name, box, **ROSTERS[name])
        return made[name]

    return adopted


@pytest.fixture(scope="session")
def adopted_product(adoption):
    """The standard adopted repository and its generated settings, after a successful A0 (a failed A0 is the red
    reason of every case that stands on it)."""
    adopted = adoption("standard")
    return adopted, w110.wiring.load_settings(adopted.project)


@pytest.fixture
def decide(adopted_product, sandbox):
    """``decide(session, command, mode)``: the hook lines' answer to one Bash call in the adopted repository."""

    def _decide(session, command=support.INSTALL, mode="default"):
        adopted, settings = adopted_product
        return w110.call(adopted.project, settings, sandbox, session, command, mode)

    return _decide


@pytest.fixture(scope="session")
def products(generated, workspace):
    """``products(name)``: W2-110's configuration ``name`` (its tickets and roster) and its generated settings."""
    made = {}

    def product(name):
        if name not in made:
            try:
                project = w110.configure(generated, workspace / "products" / name, name)
                made[name] = (project, w110.wiring.load_settings(project))
            except w110.ConfigurationUnusable as exc:
                made[name] = exc
        if isinstance(made[name], Exception):
            pytest.skip(f"configuration {name}: {made[name]}")
        return made[name]

    return product


@pytest.fixture
def ask(products, sandbox):
    """``ask(configuration, session, command, mode)``: the hook lines' answer in a W2-110 configuration."""

    def _ask(configuration, session, command=support.INSTALL, mode="default"):
        project, settings = products(configuration)
        return w110.call(project, settings, sandbox, session, command, mode)

    return _ask
