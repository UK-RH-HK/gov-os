"""The second review's findings (round 2, DEC-993), as behaviours: items 1, 2, 3 and 7 here; 4, 5 and 6 are the
runner's (``test_w2_81_runner.py``).

1 a large file moved by a reviewed action is judged where it now is; 2 the test runners' other configuration files
keep the orphaned test in; 3 the successor plan proposed for deletion or retirement; 7 a control in a namespace the
path map holds but does not embed (the reading: CLEAN, README "The controls and the vectors").
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

import w2_81_build as build
import w2_81_judge as judge
import w2_81_standin as standin

ALL = set(judge.CAPABILITIES)


@pytest.fixture(autouse=True)
def _removed_after(tmp_path):
    """Each case removes what it rendered, pass or fail; nothing it built is left (README, "Hermetic and bounded")."""
    yield
    for child in tmp_path.iterdir():
        shutil.rmtree(child) if child.is_dir() and not child.is_symlink() else child.unlink()
    assert not any(tmp_path.iterdir()), "a case left what it built"


def _judge(built_repo, model, folder, built=ALL):
    root, beside = standin.render(model, built_repo, folder / "adopted", folder / "beside")
    return judge.judge_repository(built_repo.manifest, root, beside, built_repo.secrets, built)


def _result(judgement, ident):
    return next(p for p in judgement["planted"] + judgement["controls"] if p["id"] == ident)


# --------------------------------------------------------------------------
# 1. A large file moved by a reviewed action is judged at its target
# --------------------------------------------------------------------------

FRAMES = {"id": "l1", "repository": "rust-workspace", "kind": "large-file", "variant": "frame-capture",
          "paths": ["captures/frames.bin"],
          "steps": [{"message": "A frame capture", "write": {"captures/frames.bin": "f" * 6000}}],
          "evidence": {"path": "captures/frames.bin", "size": 6000}}


@pytest.fixture(scope="module")
def rust_with_a_large_file(tmp_path_factory):
    """The Rust workspace with a large file of its own (a variant): the second shape that holds one."""
    base = tmp_path_factory.mktemp("w2-81-rust-large")
    built = build.build_rust(base / "repos" / "rust-workspace", 41, base)
    build.apply_variants({"rust-workspace": built}, [FRAMES], 41, base)
    for entry in built.manifest["planted"]:  # this case's own large file, not hidden material: judged by its id
        entry.pop("hidden", None)
    yield built
    shutil.rmtree(base)


def _large(ground, rust_with_a_large_file, which):
    if which == "rust-workspace":
        built_repo = rust_with_a_large_file
        entry = next(e for e in built_repo.manifest["planted"] if e["kind"] == "large-file")
    else:
        built_repo = ground["legacy-docs"]
        entry = next(e for e in built_repo.manifest["planted"] if e["kind"] == "large-file" and e["variant"] == which)
    return built_repo, entry


TARGETS = {  # the target's namespace and its vectors -> the status the large file must get
    "embedded-with-vectors": (False, True, judge.MISHANDLED),
    "embedded-without-vectors": (False, False, judge.MISHANDLED),
    "not-embedded-with-vectors": (True, True, judge.MISHANDLED),
    "not-embedded-without-vectors": (True, False, judge.FOUND),
}


@pytest.mark.parametrize("target_state", sorted(TARGETS))
@pytest.mark.parametrize("which", ["dataset", "media", "rust-workspace"])
def test_a_large_file_moved_by_a_reviewed_action_is_judged_at_its_target(ground, rust_with_a_large_file, tmp_path,
                                                                         which, target_state):
    built_repo, entry = _large(ground, rust_with_a_large_file, which)
    old = entry["evidence"]["path"]
    target = f"moved-out/{Path(old).name}"
    in_large_namespace, vectors, wanted = TARGETS[target_state]
    model = standin.perfect(built_repo)
    model["removed"].append(old)
    model["raw"][target] = (built_repo.root / old).read_bytes()
    standin.a3_entry(model, old).update(action="MOVE", target=target, batch=1)
    if in_large_namespace:
        model["path_map"]["namespaces"]["large"]["paths"].append(target)
    model["index"][target] = vectors
    assert old in model["path_map"]["namespaces"]["large"]["paths"], "the not-embedded namespace still names it"
    result = _result(_judge(built_repo, model, tmp_path), entry["id"])
    assert result["status"] == wanted, (which, target_state, result["evidence"])
    assert any(target in str(s.get("record")) + str(s.get("said")) for s in result["evidence"]
               if s["status"] == wanted), "the evidence does not name the target"


def test_a_large_file_moved_without_a_reviewed_action_stays_mishandled(ground, tmp_path):
    built_repo = ground["legacy-docs"]
    entry = next(e for e in built_repo.manifest["planted"] if e["kind"] == "large-file")
    old, target = entry["evidence"]["path"], "moved-out/x.bin"
    model = standin.perfect(built_repo)
    model["removed"].append(old)
    model["raw"][target] = (built_repo.root / old).read_bytes()
    model["path_map"]["namespaces"]["large"]["paths"].append(target)
    model["index"][target] = False
    assert _result(_judge(built_repo, model, tmp_path), entry["id"])["status"] == judge.MISHANDLED
    standin.a3_entry(model, old).update(action="MOVE", target=target, batch=1)
    model["records"]["A5"]["path_map_hash"] = "0" * 64  # A5 does not stand on this A3
    assert _result(_judge(built_repo, model, tmp_path / "unreviewed"), entry["id"])["status"] == judge.MISHANDLED


# --------------------------------------------------------------------------
# 2. Every configuration file a test runner reads keeps the orphaned test in
# --------------------------------------------------------------------------

def _python_configs(name):
    ignore = f"--ignore=tests/{name}"
    return {"pytest.toml": f"[pytest]\naddopts = [\"{ignore}\"]\n",
            ".pytest.toml": f"[pytest]\naddopts = [\"{ignore}\"]\n",
            ".pytest.ini": f"[pytest]\naddopts = {ignore}\n",
            "pytest.ini": f"[pytest]\naddopts = {ignore}\n",
            "tox.ini": f"[pytest]\naddopts = {ignore}\n",
            "setup.cfg": f"[tool:pytest]\naddopts = {ignore}\n",
            "pyproject.toml": None}  # the build's own, with the ignore appended


def _vite_configs(package, name):
    exclude = f"export default {{ test: {{ exclude: [\"test/{name}\"] }} }};\n"
    out = {f"{package}/vite.config.{ext}": exclude for ext in ("ts", "mts", "js", "mjs", "cts", "cjs")}
    out[f"{package}/vitest.config.ts"] = exclude
    out["vitest.workspace.ts"] = f"export default [\"{package}\"];\n// {name} left out\n"
    return out


CONFIG_CASES = [("python-app", f) for f in sorted(_python_configs("x"))] + \
               [("typescript-monorepo", f) for f in ("vite.config.ts", "vite.config.mts", "vite.config.js",
                                                     "vite.config.mjs", "vite.config.cts", "vite.config.cjs",
                                                     "vitest.config.ts", "vitest.workspace.ts")] + \
               [("python-app", "a new file in the test's own folder")]


@pytest.mark.parametrize("name, form", CONFIG_CASES)
def test_a_runner_configuration_that_keeps_the_orphaned_test_out_is_mishandled(ground, tmp_path, name, form):
    built_repo = ground[name]
    entry = next(e for e in built_repo.manifest["planted"] if e["kind"] == "orphaned-test")
    test = Path(entry["evidence"]["test"])
    model = standin.perfect(built_repo)
    if name == "python-app" and form == "a new file in the test's own folder":
        model["raw"][str(test.parent / "deselect.txt")] = f"{test.name}\n"
    elif name == "python-app":
        content = _python_configs(test.name)[form]
        if content is None:
            content = (built_repo.root / form).read_text() + f"\n[tool.pytest.ini_options]\naddopts = " \
                                                             f"\"--ignore={test.as_posix()}\"\n"
        assert not (built_repo.root / form).exists() or form == "pyproject.toml", form
        model["raw"][form] = content
    else:
        package = test.parent.parent.as_posix()
        rel = next(k for k in _vite_configs(package, test.name) if k.endswith(form))
        model["raw"][rel] = _vite_configs(package, test.name)[rel]
    result = _result(_judge(built_repo, model, tmp_path), entry["id"])
    assert result["status"] == judge.MISHANDLED, (name, form, result["evidence"])


# --------------------------------------------------------------------------
# 3. The successor plan proposed for deletion or retirement
# --------------------------------------------------------------------------

@pytest.mark.parametrize("capabilities", ["today", "all"])
@pytest.mark.parametrize("action", ["DELETE_FROM_ACTIVE_TREE", "RETIRE"])
def test_the_successor_plan_proposed_for_deletion_or_retirement_is_mishandled(ground, tmp_path, action, capabilities):
    holders = [b for b in ground.values() if any(e["kind"] == "superseded-plan" for e in b.manifest["planted"])]
    assert len(holders) >= 2
    for n, built_repo in enumerate(holders):
        entry = next(e for e in built_repo.manifest["planted"] if e["kind"] == "superseded-plan")
        model = standin.perfect(built_repo)
        standin.a3_entry(model, entry["evidence"]["successor"]).update(
            action=action, batch=1, **({"kind": "rule-file"} if action == "RETIRE" else {}))
        result = _result(_judge(built_repo, model, tmp_path / str(n), None if capabilities == "today" else ALL),
                         entry["id"])
        assert result["status"] == judge.MISHANDLED, (built_repo.name, action, capabilities)
        assert any(s["status"] == judge.MISHANDLED and entry["evidence"]["successor"] in s["said"]
                   for s in result["evidence"])


# --------------------------------------------------------------------------
# 7. A control in a namespace the path map holds but does not embed: the reading is CLEAN
# --------------------------------------------------------------------------

def test_a_control_in_a_held_namespace_that_is_not_embedded_is_clean(ground, tmp_path):
    built_repo = ground["python-app"]
    for n, control in enumerate(built_repo.manifest["controls"]):
        model = standin.perfect(built_repo)
        path = control["paths"][0]
        spaces = model["path_map"]["namespaces"]
        model["path_map"]["namespaces"] = {"plain": {**spaces["project"], "paths": [path],
                                                     "embedding_policy": judge.NOT_EMBEDDED}, **spaces}
        standin.a2_entry(model, path)["namespace"] = "plain"
        model["index"][path] = False  # in the lexical index, without vectors
        result = _result(_judge(built_repo, model, tmp_path / str(n)), control["id"])
        assert result["status"] == judge.CLEAN, result["evidence"]
