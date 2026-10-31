"""W2-110 acceptance fixtures: one generated product and one stand-in home per session, one copy of the product per
configuration (README, "How the cases run the code of the worktree they sit in")."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_110_support as support  # noqa: E402


@pytest.fixture(scope="session")
def workspace():
    """A temporary folder for the session's trees (under the ``TMPDIR`` the run is given), removed at its end."""
    base = Path(tempfile.mkdtemp(prefix="w2110-"))
    try:
        yield base
    finally:
        support.remove_tree(base)


@pytest.fixture(scope="session")
def generated(workspace):
    """The product: copier copy of the template assembled from this worktree, then rulesync generate (W2-90)."""
    try:
        project = support.wiring.generate_project(workspace / "generated", "product")
    except AssertionError as exc:
        pytest.fail(f"the product could not be generated from the template: {exc}", pytrace=False)
    hook = project / support.KERNEL_HOOK_REL
    template_hook = support.REPO_ROOT / support.TEMPLATE_HOOK_REL
    if not hook.is_file() or hook.read_bytes() != template_hook.read_bytes():
        pytest.fail(f"the generated product's {support.KERNEL_HOOK_REL} is not this worktree's "
                    f"{support.TEMPLATE_HOOK_REL}: the cases would judge other code (DEC-732)", pytrace=False)
    return project


@pytest.fixture(scope="session")
def sandbox(workspace):
    """The stand-in home (W1-38's ``make_session_sandbox``): its ``gov`` names this interpreter, its user site names
    this worktree's ``src``. Checked: the pinned line's interpreter, with ``-E``, imports this worktree's package."""
    box = support.session_support.make_session_sandbox(workspace / "session")
    found = support.gov_the_hook_imports(box)
    expected = (support.REPO_ROOT / "src" / "gov" / "__init__.py").resolve()
    if not found or Path(found).resolve() != expected:
        pytest.fail(f"the hook's interpreter imports gov from {found!r}, not this worktree's {expected}: the cases "
                    f"would judge other code (DEC-732)", pytrace=False)
    return box


@pytest.fixture(scope="session")
def products(generated, workspace):
    """``products(name)``: the product with configuration ``name`` and its generated settings, made once per session."""
    made = {}

    def product(name):
        if name not in made:
            try:
                project = support.configure(generated, workspace / "products" / name, name)
                made[name] = (project, support.wiring.load_settings(project))
            except support.ConfigurationUnusable as exc:
                made[name] = exc
        if isinstance(made[name], Exception):
            pytest.skip(f"configuration {name}: {made[name]}")
        return made[name]

    return product


@pytest.fixture
def ask(products, sandbox):
    """``ask(configuration, session, command, mode)``: the hook lines' answer to one Bash call in that product."""

    def _ask(configuration, session, command=support.INSTALL, mode="default"):
        project, settings = products(configuration)
        return support.call(project, settings, sandbox, session, command, mode)

    return _ask
