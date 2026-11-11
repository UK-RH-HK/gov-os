"""KPI line 1: every tracked path in exactly one namespace, in both forms, judged in the path map's language.

core-pathmap reads ``namespaces`` in the form the schema states (a mapping of a name to
its entry) and in the older list form. For each tracked path it names the path when it
matches no namespace or more than one, with the namespaces it matched; green when every
tracked path is in exactly one. ``*`` stays inside one folder, ``**`` crosses folders.
Run through the check's declared command in a planted repository.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_95_support as s  # noqa: E402

FILES = ["README.md", "src/app/main.py", "src/app/deep/util.py", "docs/guide.md"]

FORMS = {"mapping": s.mapping_form, "list": s.list_form}

# Every tracked path in exactly one namespace; `**` must cross folders (src/app/deep/util.py).
EXACTLY_ONE = {"code": ["src/**"], "docs": ["docs/**"], "governance": ["governance/**"], "root": ["README.md"]}

# README.md and docs/guide.md in no namespace; src/app/main.py in two (code, app).
NONE_AND_TWO = {"code": ["src/**"], "app": ["src/app/main.py"], "governance": ["governance/**"]}


def _assert_red(result, expected):
    """The check is red and names each path of ``expected`` with the namespaces it matched."""
    assert result.findings is not None, "the output is not JSON:\n" + result.describe()
    assert result.code != 0, "a path in no namespace or in two is reported green:\n" + result.describe()
    named = s.path_findings(result.findings)
    for path, namespaces in expected.items():
        assert path in named, f"{path} is not named:\n" + result.describe()
        assert any(s.matched(f) == sorted(namespaces) for f in named[path]), (
            f"{path} is not named with the namespaces it matched {sorted(namespaces)}:\n" + result.describe()
        )


@pytest.mark.parametrize("form", sorted(FORMS))
def test_w2_95_every_path_in_exactly_one_namespace_is_green(tmp_path, form):
    repo = s.Planted(tmp_path, FILES, FORMS[form](EXACTLY_ONE))
    result = repo.declared()
    assert result.code == 0, f"{form} form, every path in exactly one namespace, not green:\n" + result.describe()
    assert result.findings == [], result.describe()


@pytest.mark.parametrize("form", sorted(FORMS))
def test_w2_95_paths_in_none_and_in_two_are_named(tmp_path, form):
    repo = s.Planted(tmp_path, FILES, FORMS[form](NONE_AND_TWO))
    result = repo.declared()
    _assert_red(result, {"README.md": [], "docs/guide.md": [], "src/app/main.py": ["code", "app"]})
    named = s.path_findings(result.findings)
    for path in ("README.md", "docs/guide.md"):
        assert any(f.get("code") == s.NO_NAMESPACE for f in named[path]), result.describe()
    assert any(f.get("code") == s.MULTIPLE_NAMESPACES for f in named["src/app/main.py"]), result.describe()
    # A path in exactly one namespace is not named.
    assert "src/app/deep/util.py" not in named, result.describe()
    assert s.PATH_MAP not in named, result.describe()


@pytest.mark.parametrize("form", sorted(FORMS))
def test_w2_95_star_at_the_root_matches_only_root_files(tmp_path, form):
    # `*` stays inside one folder: it takes README.md and nothing under src/ or docs/.
    namespaces = {"root": ["*"], "code": ["src/**"], "docs": ["docs/**"], "governance": ["governance/**"]}
    repo = s.Planted(tmp_path, FILES, FORMS[form](namespaces))
    result = repo.declared()
    assert result.code == 0, f"{form} form: `*` at the root crossed into a folder:\n" + result.describe()
    assert result.findings == [], result.describe()


@pytest.mark.parametrize("form", sorted(FORMS))
def test_w2_95_star_alone_leaves_files_in_folders_unplaced(tmp_path, form):
    # Only `*`: the files in folders match no namespace and are named.
    repo = s.Planted(tmp_path, FILES, FORMS[form]({"root": ["*"]}))
    result = repo.declared()
    _assert_red(
        result,
        {"src/app/main.py": [], "src/app/deep/util.py": [], "docs/guide.md": [], s.PATH_MAP: []},
    )
    assert "README.md" not in s.path_findings(result.findings), result.describe()


def test_w2_95_star_inside_a_folder_does_not_cross_into_a_subfolder(tmp_path):
    # `src/app/*` takes src/app/main.py only; src/app/deep/util.py is in no namespace.
    namespaces = {"app": ["src/app/*"], "docs": ["docs/**"], "governance": ["governance/**"], "root": ["README.md"]}
    repo = s.Planted(tmp_path, FILES, s.mapping_form(namespaces))
    result = repo.declared()
    _assert_red(result, {"src/app/deep/util.py": []})
    assert "src/app/main.py" not in s.path_findings(result.findings), result.describe()
