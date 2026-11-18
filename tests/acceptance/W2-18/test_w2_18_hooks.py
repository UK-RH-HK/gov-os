"""Success 3 [W2-M123, W2-H032, W2-M279] and success 4 [W2-L172, W2-L230, W2-L173, W2-L174]: the kernel hook
command lines of the template's `.rulesync/hooks.jsonc`, run with `bash -c` as Claude Code runs them."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

import w2_18_support as s

CHECKPOINT_EVENTS = ("preCompact", "stop")


@dataclass(frozen=True)
class HookProduct:
    main: Path
    linked: Path
    marker: Path


@pytest.fixture(scope="module")
def hook_product(adopted, releases, tmp_path_factory):
    """A product with a pin of release A, its own `src/gov` package (importing its `gov.checkpoint.record` writes
    the marker), a ticket for GOV_TICKET, and a linked worktree."""
    base = tmp_path_factory.mktemp("w2-18-hook-product")
    project = s.copy_project(adopted, base / "product")
    marker = base / "marker"
    s.add_product_gov_package(project, marker)
    s.add_ticket(project)
    s.commit_all(project, "the product's own package named gov, and a ticket")
    linked = base / "linked"
    s.git(project, "worktree", "add", "-q", "-b", "linked-tree", str(linked))
    s.plant_pin(project, releases, s.VERSION_A, s.make_sandbox(base / "sandbox"))
    return HookProduct(project, linked, marker)


@pytest.mark.parametrize("event", CHECKPOINT_EVENTS)
@pytest.mark.parametrize("where", ["main-tree", "linked-worktree"])
def test_checkpoint_hooks_write_the_record_with_the_pinned_gov_never_the_product_s_package(
        hook_product, where, event, sandbox):
    lines = [line for line in s.hook_lines() if line.event == event]
    assert lines, f"the template's hooks.jsonc has no {event} command line"
    tree = hook_product.main if where == "main-tree" else hook_product.linked
    env = s.base_env(sandbox, GOV_TICKET=s.TICKET)
    for line in lines:
        hook_product.marker.unlink(missing_ok=True)
        before = s.records(tree)
        done = s.run_hook(line, tree, env)
        written = sorted(set(s.records(tree)) - set(before))
        assert not hook_product.marker.exists(), (
            f"the {line.ident} hook line imported the product's own src/gov ({hook_product.marker.read_text()!r}) "
            f"in the {where}\n{done.describe()}")
        assert done.returncode == 0 and written, (
            f"the {line.ident} hook line, with GOV_TICKET={s.TICKET} and a pin of release {s.VERSION_A}, wrote no "
            f"checkpoint record under .gov-runtime/scratch/checkpoints/ in the {where}\n{done.describe()}")


@pytest.fixture(scope="module")
def bare_product(adopted, tmp_path_factory):
    """A product with no pin and a ticket for GOV_TICKET."""
    project = s.copy_project(adopted, tmp_path_factory.mktemp("w2-18-bare-product") / "product")
    s.add_ticket(project)
    s.commit_all(project, "a ticket")
    return project


@pytest.mark.parametrize("line", s.hook_lines(), ids=lambda line: line.ident)
def test_each_hook_line_without_any_gov_exits_zero_saying_so_in_one_line(bare_product, line, sandbox):
    python = s.w216.write_python_without_gov(Path(sandbox.elsewhere) / "python-without-gov")
    env = s.base_env(sandbox, path=f"{python}:{s.SYSTEM_PATH}", GOV_TICKET=s.TICKET, GOV_ROLE="engineer")
    assert not s.pin_folder(bare_product).exists() and not (Path(sandbox.home) / ".local" / "bin" / "gov").exists()
    s.no_gov_on(env, bare_product)
    done = s.run_hook(line, bare_product, env)
    said = [text for text in done.stderr.splitlines() if text.strip()]
    assert done.returncode == 0, f"with no gov the {line.ident} hook line exits {done.returncode}\n{done.describe()}"
    assert len(said) == 1 and said[0].startswith("gov hook: no gov") and any(
        where in said[0] for where in ("bin/gov", "PATH")), (
        f"with no gov the {line.ident} hook line does not print one line on stderr beginning 'gov hook: no gov' and "
        f"naming where it looked\n{done.describe()}")
    assert '"deny"' not in done.stdout and '"block"' not in done.stdout, (
        f"with no gov the {line.ident} hook line refuses the call\n{done.describe()}")
