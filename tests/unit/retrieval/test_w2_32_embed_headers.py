"""W2-32, DEC-1067 order (5), index-time method 1: contextual headers when embedded. Each chunk is embedded after a
deterministic header (its path and the headings above it), behind ``embed_headers`` in ``rebuild.yaml``, off by
default. Regression evidence only (DEC-136): the embedder is a stand-in; no model is started. Each store is in a
temporary git repository.
"""
from __future__ import annotations

import sqlite3
import struct
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.config import loader, models  # noqa: E402
from gov.retrieval import chunking, lexical, semantic  # noqa: E402
from gov.store import STORE_REL  # noqa: E402

PINNED = models.DEFAULT_REVISION + "0" * 52
_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}

NOTES = """# Kiln Notes
The notes of the kiln.
## Firing
How the kiln is fired.
### Order
The bowls go in first. ###
## Glaze
The glaze is mixed wet.
"""
NOTES_HEADERS = {  # the section's first line -> its header, exactly
    "# Kiln Notes\n": "[path: open/notes.md]\n[section: Kiln Notes]\n",
    "## Firing\n": "[path: open/notes.md]\n[section: Kiln Notes > Firing]\n",
    "### Order\n": "[path: open/notes.md]\n[section: Kiln Notes > Firing > Order]\n",
    "## Glaze\n": "[path: open/notes.md]\n[section: Kiln Notes > Glaze]\n",
}
TOOL = """import os


class Kiln:
    def fire(self):
        return os.sep


def glaze():
    return 2
"""
PLAIN = "no heading here\njust lines of a plain file\n"


def _headers_of(path: str, text: str) -> dict[tuple[int, int], str]:
    """Each chunk's (first, last) line -> its header, through the chunker's own parents."""
    parent_rows, chunk_rows = chunking.chunk_file(path, "blob", text)
    lines = text.splitlines()
    firsts = [(parent_id, kind, start, lines[start - 1]) for parent_id, _, kind, start, _ in parent_rows]
    named = chunking.headers(path, firsts)
    return {(first, last): named.get(parent_id, chunking.header(path))
            for _, _, first, last, parent_id, _ in chunk_rows}


# --- the header's exact form -----------------------------------------------------------------------------------------

def test_a_markdown_section_s_header_names_its_path_and_every_heading_that_contains_it():
    got = _headers_of("open/notes.md", NOTES)
    lines = NOTES.splitlines(keepends=True)
    assert {lines[first - 1]: header for (first, _), header in got.items()} == NOTES_HEADERS


def test_a_part_before_the_first_heading_has_the_path_alone_and_a_shallower_heading_closes_deeper_ones():
    text = "Preamble line.\n## Second\nbody\n#### Deep\nbody\n## Back\nbody\n# Top\nbody\n"
    got = sorted(_headers_of("a.md", text).items())
    assert [header for _, header in got] == [
        "[path: a.md]\n",
        "[path: a.md]\n[section: Second]\n",
        "[path: a.md]\n[section: Second > Deep]\n",
        "[path: a.md]\n[section: Back]\n",
        "[path: a.md]\n[section: Top]\n",
    ]


def test_a_python_chunk_s_header_names_its_function_and_the_module_s_lines_the_path_alone():
    got = _headers_of("open/tool.py", TOOL)
    assert got == {
        (1, 4): "[path: open/tool.py]\n",  # the module's lines (the import and the class line)
        (7, 8): "[path: open/tool.py]\n",
        (5, 6): "[path: open/tool.py]\n[function: fire]\n",  # a method: the chunker knows its function, no class
        (9, 10): "[path: open/tool.py]\n[function: glaze]\n",
    }


def test_an_async_and_a_decorated_function_are_named_by_their_def_line():
    text = "import x\n\n@x.cache\nasync def load(a):\n    return a\n"
    assert _headers_of("m.py", text)[(4, 5)] == "[path: m.py]\n[function: load]\n"


@pytest.mark.parametrize("path, text", [("open/plain.txt", PLAIN), ("open/plain.md", PLAIN),
                                        ("open/plain.py", PLAIN.replace(" ", "_"))])
def test_a_file_with_no_headings_has_the_path_alone(path, text):
    assert set(_headers_of(path, text).values()) == {f"[path: {path}]\n"}


# --- the setting -----------------------------------------------------------------------------------------------------

def _settings(root: Path, text: str | None) -> None:
    path = root / "governance/project/rebuild.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    if text is None:
        path.unlink(missing_ok=True)
    else:
        path.write_text(text)


@pytest.mark.parametrize("text, on", [(None, False), ("", False), ("# comments alone\n", False),
                                      ("slow_after_s: 60\n", False), ("embed_headers: false\n", False),
                                      ("embed_headers: true\n", True), ("slow_after_s: 60\nembed_headers: true\n", True)])
def test_the_setting_is_off_unless_written_true(tmp_path, text, on):
    _settings(tmp_path, text)
    assert loader.embed_headers(tmp_path) is on


@pytest.mark.parametrize("value", ["yes", "on", "True", "TRUE", "'true'", '"false"', "1", "0", "", "[true]", "{a: 1}",
                                   "null"])
def test_any_other_value_is_refused_naming_the_key(tmp_path, value):
    _settings(tmp_path, f"embed_headers: {value}\n")
    with pytest.raises(GovError) as raised:
        loader.embed_headers(tmp_path)
    assert raised.value.code == "CONFIG_INVALID" and "embed_headers" in raised.value.message
    assert raised.value.details == {"file": "governance/project/rebuild.yaml", "key": "embed_headers"}


def test_a_settings_file_that_is_not_a_map_is_refused(tmp_path):
    _settings(tmp_path, "- embed_headers\n")
    with pytest.raises(GovError) as raised:
        loader.embed_headers(tmp_path)
    assert raised.value.code == "CONFIG_INVALID"


@pytest.mark.parametrize("value", ["yes", "1", "'true'", "word", "null"])
def test_the_config_loader_refuses_an_invalid_value_naming_the_key(tmp_path, value):
    """The CTO's red on ``ff347bcd``: refused by the loader itself, as every other configuration key is (DEC-185)."""
    _settings(tmp_path, f"slow_after_s: 60\nembed_headers: {value}\n")
    with pytest.raises(GovError) as raised:
        loader.load_config(tmp_path)
    assert raised.value.code == "CONFIG_INVALID" and "embed_headers" in raised.value.message
    assert raised.value.details == {"file": "governance/project/rebuild.yaml", "key": "embed_headers"}


@pytest.mark.parametrize("text", ["embed_headers: true\nslow_after_s: 60\n", "embed_headers: false\n", "lock: /x\n",
                                  "", "slow_after_s: [2\n", "- embed_headers\n"])
def test_the_config_loader_leaves_the_file_s_other_faults_to_the_rebuild(tmp_path, text):
    """Not YAML, not a map, or the rebuild's own keys: ``gov.rebuild.watch`` refuses those with REBUILD_FAILED (W2-76)."""
    _settings(tmp_path, text)
    loader.load_config(tmp_path)  # nothing raised


@pytest.mark.parametrize("value", ["yes", "1", "'true'"])
def test_gov_rebuild_fails_with_config_invalid_before_any_stage(tmp_path, monkeypatch, capsys, value):
    import json

    from gov.cli import main as cli
    from gov.rebuild import watch
    _settings(tmp_path, f"embed_headers: {value}\n")
    sent = []
    monkeypatch.setattr(semantic, "_ask", lambda *args, **kwargs: sent.append(args))
    monkeypatch.setattr(watch, "settings", lambda root: pytest.fail("a stage's settings were read"))
    code = cli.main(["rebuild", "--json", "--root", str(tmp_path)])
    envelope = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert code != 0 and envelope["ok"] is False and envelope["error"]["code"] == "CONFIG_INVALID"
    assert envelope["error"]["details"]["key"] == "embed_headers"
    assert sent == [] and not (tmp_path / STORE_REL).exists() and not (tmp_path / ".gov-runtime").exists()


def test_this_repository_s_setting_reads_as_written():
    # adopted at measure 4 (dc8a2829, DEC-1067): the repository's rebuild.yaml switches it on; whatever it says, it
    # reads as a boolean, never CONFIG_INVALID
    written = (REPO / "governance/project/rebuild.yaml").read_text(encoding="utf-8")
    assert loader.embed_headers(REPO) is ("embed_headers: true" in written)


def test_this_repository_s_setting_is_read_as_its_file_states_it():
    """Off until measure 4 adopted it (DEC-1067 (b)); the CTO switched it on in ``dc8a2829``."""
    import yaml
    written = yaml.safe_load((REPO / "governance/project/rebuild.yaml").read_text(encoding="utf-8")) or {}
    assert loader.embed_headers(REPO) is written.get("embed_headers", False)


# --- the embedder's input --------------------------------------------------------------------------------------------

def _git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env={**_ENV, "HOME": str(root)})


@pytest.fixture()
def project(tmp_path, monkeypatch):
    endpoint = {"sent": []}

    def ask(path, body=None, host=None):
        if path == "/api/tags":
            return {"models": [{"name": semantic.MODEL, "digest": PINNED}]}
        if path == "/api/ps":
            return {"models": [{"name": semantic.MODEL, "size": 4, "size_vram": 4}]}
        endpoint["sent"] += body["input"]
        return {"embeddings": [[float(len(text)), 1.0] for text in body["input"]]}

    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "_ask", ask)
    monkeypatch.setattr(semantic, "_ready", lambda connection, ensure=None: connection.create_function(
        "vec_distance_cosine", 2, lambda a, b: abs(struct.unpack("2f", a)[0] - struct.unpack("2f", b)[0])))
    monkeypatch.setenv("GOV_VECTOR_CACHE_DIR", str(tmp_path / "machine-cache"))
    root = tmp_path / "repo"
    (root / "governance/project").mkdir(parents=True)
    (root / ".gitignore").write_text(".gov-runtime/\n")
    (root / "governance/project/path-map.yaml").write_text(
        "namespaces:\n  open: {paths: ['open/**'], embedding_policy: embedded}\n")
    (root / "open").mkdir()
    (root / "open/notes.md").write_text(NOTES)
    (root / "open/tool.py").write_text(TOOL)
    (root / "open/plain.txt").write_text(PLAIN)
    _git(root, "init", "-q", "-b", "main")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "c")
    return root, endpoint


def _chunks(root: Path) -> list[tuple[str, str]]:
    """(path, text) of each embedded chunk, the text read from the file."""
    out = []
    for chunk in lexical.chunks(root):
        if chunk["path"].startswith("open/"):
            lines = (root / chunk["path"]).read_text().splitlines(keepends=True)
            out.append((chunk["path"], "".join(lines[chunk["start_line"] - 1:chunk["end_line"]])))
    return out


def _with_headers(root: Path) -> list[str]:
    tool = {(f, t): h for (f, t), h in _headers_of("open/tool.py", TOOL).items()}
    tool_texts = {"".join(TOOL.splitlines(keepends=True)[f - 1:t]): h for (f, t), h in tool.items()}
    wanted = []
    for path, text in _chunks(root):
        if path == "open/notes.md":
            wanted.append(NOTES_HEADERS[text.splitlines(keepends=True)[0]] + text)
        elif path == "open/tool.py":
            wanted.append(tool_texts[text] + text)
        else:
            wanted.append(f"[path: {path}]\n" + text)
    return wanted


def test_off_by_default_the_embedder_gets_today_s_input_byte_for_byte(project):
    root, endpoint = project
    assert semantic.refresh(root)["available"] is True
    assert sorted(endpoint["sent"]) == sorted(text for _, text in _chunks(root))
    assert not any(text.startswith("[path: ") for text in endpoint["sent"])
    assert semantic.manifest(root)[semantic.HEADERS_KEY] is False


def test_on_each_chunk_is_embedded_after_its_header(project):
    root, endpoint = project
    _settings(root, "embed_headers: true\n")
    assert semantic.refresh(root)["available"] is True
    assert sorted(endpoint["sent"]) == sorted(_with_headers(root))
    assert "[path: open/notes.md]\n[section: Kiln Notes > Firing > Order]\n### Order\n" \
           "The bowls go in first. ###\n" in endpoint["sent"]
    assert "[path: open/tool.py]\n[function: fire]\n    def fire(self):\n        return os.sep\n" in endpoint["sent"]
    assert semantic.manifest(root)[semantic.HEADERS_KEY] is True


def test_the_keyword_chunk_is_unchanged_with_headers_on(project):
    root, _ = project
    semantic.refresh(root)
    before = sorted((c["chunk_id"], c["start_line"], c["end_line"]) for c in lexical.chunks(root))
    texts = sorted(text for _, text in _chunks(root))
    _settings(root, "embed_headers: true\n")
    semantic.refresh(root)
    assert sorted((c["chunk_id"], c["start_line"], c["end_line"]) for c in lexical.chunks(root)) == before
    connection = sqlite3.connect(root / STORE_REL)
    stored = sorted(text for (text,) in connection.execute(
        "SELECT f.text FROM lexical_chunk c JOIN lexical_fts f ON f.rowid = c.id WHERE c.path LIKE 'open/%'"))
    connection.close()
    assert stored == texts and not any("[path: " in text for text in stored)


@pytest.mark.parametrize("first, then", [(None, "embed_headers: true\n"), ("embed_headers: true\n", None),
                                         ("embed_headers: true\n", "embed_headers: false\n")])
def test_switching_the_setting_marks_the_store_stale_and_the_next_build_re_embeds_every_chunk(project, first, then):
    root, endpoint = project
    _settings(root, first)
    assert semantic.refresh(root)["available"] is True
    assert semantic.search(root, "kiln", refresh=False)["available"] is True
    _settings(root, then)
    assert semantic.search(root, "kiln", refresh=False)["reason"] == "stale"
    endpoint["sent"].clear()
    report = semantic.refresh(root)
    assert report["available"] is True
    count = len(_chunks(root))
    assert len(endpoint["sent"]) + report["vector_cache"]["hits"] == count == 9  # every chunk again (S1)
    assert semantic.manifest(root)[semantic.HEADERS_KEY] is loader.embed_headers(root)
    assert semantic.search(root, "kiln", refresh=False)["available"] is True


def test_the_parents_query_bound_to_the_file_gives_the_same_rows_through_the_path_index(project):
    """Review F2: ``_PARENTS`` binds the chunk's path too, so SQLite plans it through ``lexical_chunk_by_path`` and
    not as a scan of the whole keyword table per file; a chunk lies in its parent's file, so the rows are the same."""
    root, _ = project
    semantic.refresh(root)
    unbound = semantic._Texts._PARENTS.replace(" AND c.path = ?", "")
    assert unbound != semantic._Texts._PARENTS
    connection = sqlite3.connect(root / STORE_REL)
    try:
        paths = [path for (path,) in connection.execute("SELECT DISTINCT path FROM lexical_parent ORDER BY path")]
        assert {"open/notes.md", "open/tool.py", "open/plain.txt"} <= set(paths)
        for path in paths:
            bound = sorted(connection.execute(semantic._Texts._PARENTS, (path, path)))
            assert bound == sorted(connection.execute(unbound, (path,))) and bound
        plan = " ".join(str(row) for row in connection.execute(
            "EXPLAIN QUERY PLAN " + semantic._Texts._PARENTS, ("open/notes.md", "open/notes.md")))
        assert "lexical_chunk_by_path" in plan, plan
    finally:
        connection.close()


def test_a_store_built_before_the_recipe_was_recorded_is_fresh_with_the_setting_off(project):
    root, endpoint = project
    semantic.refresh(root)
    connection = sqlite3.connect(root / STORE_REL)
    connection.execute("DELETE FROM semantic_pin WHERE key = ?", (semantic.HEADERS_KEY,))
    connection.commit()
    connection.close()
    semantic._STATUS.clear()
    assert semantic.manifest(root)[semantic.HEADERS_KEY] is False
    assert semantic.search(root, "kiln", refresh=False)["available"] is True
    endpoint["sent"].clear()
    assert semantic.refresh(root)["available"] is True and endpoint["sent"] == []  # nothing re-embedded


def test_a_refused_setting_refuses_the_build_and_the_search_by_name_and_sends_nothing(project):
    root, endpoint = project
    semantic.refresh(root)
    endpoint["sent"].clear()
    _settings(root, "embed_headers: yes\n")
    for report in (semantic.refresh(root), semantic.search(root, "kiln", refresh=False)):
        assert report["available"] is False and report["error"] == "CONFIG_INVALID"
        assert "embed_headers" in report["reason"]
    assert endpoint["sent"] == []


def test_the_header_counts_toward_the_limit_kept_while_the_text_is_cut_and_named(project, capsys):
    root, endpoint = project
    size = semantic.EMBED_LIMIT_CHARS - 5  # under the limit alone, over it with its header
    (root / "open/long.txt").write_text("z" * (size - 1) + "\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "long")
    report = semantic.refresh(root)  # off: sent whole, nothing cut
    assert "z" * (size - 1) + "\n" in endpoint["sent"] and report["cut"]["count"] == 0
    _settings(root, "embed_headers: true\n")
    endpoint["sent"].clear()
    report = semantic.refresh(root)
    header = "[path: open/long.txt]\n"
    assert header + "z" * (semantic.EMBED_LIMIT_CHARS - len(header)) in endpoint["sent"]
    assert all(len(text) <= semantic.EMBED_LIMIT_CHARS for text in endpoint["sent"])
    assert report["cut"] == {"limit": semantic.EMBED_LIMIT_CHARS, "count": 1, "paths": ["open/long.txt"]}
    assert "open/long.txt" in capsys.readouterr().err
