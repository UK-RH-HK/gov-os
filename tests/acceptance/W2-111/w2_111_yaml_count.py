"""Support for W2-111's S9 count case (DEC-1187 (1); the CTO's interface, DEC-1157 (3), the ticket's paragraph
"Interface for S9's count case"); standard library and PyYAML only.

The product guard's PreToolUse hook is run as W1-02 runs it (``w1_02_support.run_hook``: a fresh process with the
call on stdin, ``GOV_ROLE`` and ``GOV_TICKET``, the tree's ``src/`` on ``PYTHONPATH``). The only addition is a probe
folder put first on the child's ``PYTHONPATH``, holding a ``sitecustomize`` that Python imports at the child's start.
The probe never imports or patches the guard's modules; it watches two public things:

- **the YAML files the process opens under the project's ``governance/``**: an audit hook (``sys.addaudithook``) on
  the ``open`` event, which every ``open()``, ``io.open``, ``pathlib`` read and ``os.open`` raises;
- **the parses through yaml's public load API**: ``yaml.load``, ``safe_load``, ``full_load``, ``unsafe_load``, their
  ``*_all`` forms, ``compose``, ``compose_all`` and ``parse`` are wrapped, and, for a loader used directly, the
  constructor's ``get_single_data``; a parse is counted once at its outermost entry (``safe_load`` calls ``load``,
  which calls ``get_single_data``: one parse). Each parse is put to its file: the stream's ``name`` when it has one;
  for a text or bytes stream, the governance YAML file whose bytes it is; else ``<other>``.

Each event is appended at once to a report file named by ``W2_111_YAML_REPORT`` (the hook forks its decision process,
which may end without running exit handlers), with the process id, so one call's report holds every process's events.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import w2_111_support as support

guard = support.guard

SITECUSTOMIZE = r'''
"""W2-111 S9's count probe (the test's, not the product's): governance YAML opens and yaml parses, to a report."""
import os as _os
import sys as _sys
import threading as _threading

_REPORT = _os.environ.get("W2_111_YAML_REPORT")
_ROOT = _os.environ.get("W2_111_YAML_ROOT")


def _install():
    import json
    root = _os.path.realpath(_ROOT)
    gov = root + _os.sep + "governance" + _os.sep
    state = _threading.local()

    def busy():
        return getattr(state, "busy", False)

    def emit(record):
        record["pid"] = _os.getpid()
        line = (json.dumps(record) + "\n").encode("utf-8")
        state.busy = True
        try:
            fd = _os.open(_REPORT, _os.O_WRONLY | _os.O_APPEND | _os.O_CREAT, 0o600)
            try:
                _os.write(fd, line)
            finally:
                _os.close(fd)
        finally:
            state.busy = False

    def governance_rel(name):
        if isinstance(name, bytes):
            name = _os.fsdecode(name)
        if not isinstance(name, str) or not name.endswith((".yaml", ".yml")):
            return None
        full = _os.path.realpath(_os.path.abspath(name))
        if not full.startswith(gov):
            return None
        return _os.path.relpath(full, root)

    # The bytes of every governance YAML file (and, to name a parse of a ticket's front matter, of every ticket
    # file), read once here, before the product runs (not recorded).
    contents = {}
    state.busy = True
    try:
        for top, kinds in (("governance", (".yaml", ".yml")), (".tickets", (".md",))):
            for folder, _dirs, files in _os.walk(_os.path.join(root, top)):
                for f in files:
                    if not f.endswith(kinds):
                        continue
                    full = _os.path.join(folder, f)
                    try:
                        with open(full, "rb") as handle:
                            contents[handle.read()] = _os.path.relpath(_os.path.realpath(full), root)
                    except OSError:
                        pass
    finally:
        state.busy = False

    def audit(event, args):
        if event != "open" or busy() or not args:
            return
        rel = governance_rel(args[0])
        if rel is not None:
            emit({"kind": "open", "file": rel})

    _sys.addaudithook(audit)

    import yaml

    def file_of(stream):
        name = getattr(stream, "name", None)
        if isinstance(name, (str, bytes)) and not isinstance(stream, (str, bytes)):
            rel = governance_rel(name)
            return rel if rel is not None else "<other>"
        data = stream
        if not isinstance(data, (str, bytes)) and callable(getattr(data, "getvalue", None)):
            data = data.getvalue()   # an in-memory stream (io.StringIO, io.BytesIO)
        if isinstance(data, str):
            data = data.encode("utf-8")
        if isinstance(data, bytes):
            data = data.lstrip(b"\xef\xbb\xbf").replace(b"\r\n", b"\n")
            # The whole file, or a block of it (a parser may read one section's lines alone): its file.
            for text, rel in contents.items():
                if data.strip() and data in text.lstrip(b"\xef\xbb\xbf").replace(b"\r\n", b"\n"):
                    return rel
        return "<other>"

    def wrap(api, original, stream_of):
        def wrapper(*args, **kwargs):
            depth = getattr(state, "depth", 0)
            if depth == 0 and not busy():
                stream = None
                try:
                    stream = stream_of(args, kwargs)
                    where = file_of(stream)
                except Exception:
                    where = "<other>"
                emit({"kind": "parse", "api": api, "file": where, "stream": type(stream).__name__})
            state.depth = depth + 1
            try:
                return original(*args, **kwargs)
            finally:
                state.depth = depth
        wrapper.__name__ = getattr(original, "__name__", api)
        wrapper.__doc__ = getattr(original, "__doc__", None)
        wrapper.__wrapped__ = original
        return wrapper

    def first(args, kwargs):
        return args[0] if args else kwargs.get("stream")

    for api in ("load", "safe_load", "full_load", "unsafe_load", "load_all", "safe_load_all", "full_load_all",
                "unsafe_load_all", "compose", "compose_all", "parse"):
        original = getattr(yaml, api, None)
        if original is not None:
            setattr(yaml, api, wrap("yaml." + api, original, first))

    def loader_stream(args, kwargs):
        loader = args[0]
        for attribute in ("stream", "buffer"):
            value = getattr(loader, attribute, None)
            if isinstance(value, str) and value.endswith("\0"):
                value = value[:-1]
            if value is not None and value != "":
                return value
        name = getattr(loader, "name", None)
        return type("Named", (), {"name": name})() if isinstance(name, str) else None

    constructor = yaml.constructor.BaseConstructor
    constructor.get_single_data = wrap("Loader.get_single_data", constructor.get_single_data, loader_stream)


if _REPORT and _ROOT:
    _install()
'''

REPORT_ENV = "W2_111_YAML_REPORT"
ROOT_ENV = "W2_111_YAML_ROOT"
HELD_OUT_REL = "governance/project/held-out.yaml"
PATH_MAP_REL = support.PATH_MAP_REL


ROLE_PATHS = {
    guard.ENGINEER: {"reads_denied": ["{ticket_tests}"]},
    guard.TEST_DESIGNER: {"reads_denied": ["{ticket_impl}"]},
}


def count_path_map_text():
    """The kernel template's path map with W2-111's planted evaluation set (``w2_111_support.path_map_text``) and the
    ``role_paths`` section in the form this repository's own path map holds it (DEC-1065 (2)): the shape of the
    governance config the guard reads on a real project, where both sections are present."""
    import yaml
    document = yaml.safe_load(support.path_map_text())
    document["role_paths"] = ROLE_PATHS
    return yaml.safe_dump(document, sort_keys=False)


class CountWorld:
    """W1-02's fixture project with the two governance YAML files the guard reads: ``held-out.yaml`` (one held-out
    path, outside the project, that no call names) and ``path-map.yaml`` (the kernel template's, with W2-111's planted
    evaluation set that measures the engineer and the ``role_paths`` section); and the probe folder."""

    def __init__(self, base):
        base = Path(base).resolve()
        self.base = base
        self.sandbox = guard.make_sandbox(base / "sandbox")
        self.project = guard.make_project(base / "project")
        self.held_out = self.sandbox.elsewhere / "held-out-material"
        self.held_out.mkdir(parents=True, exist_ok=True)
        (self.held_out / "answers.txt").write_text("held out\n", encoding="utf-8")
        files = {
            HELD_OUT_REL: f"held_out_paths:\n- {self.held_out}\n",
            PATH_MAP_REL: count_path_map_text(),
        }
        for rel, text in files.items():
            path = self.project / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        guard.git(self.project, "add", "-A")
        guard.git(self.project, "commit", "-q", "-m", "W2-111 S9 count case: the governance YAML files")
        self.probe = base / "probe"
        self.probe.mkdir(parents=True, exist_ok=True)
        (self.probe / "sitecustomize.py").write_text(SITECUSTOMIZE, encoding="utf-8")
        self.reports = base / "reports"
        self.reports.mkdir(parents=True, exist_ok=True)
        self._n = 0

    def call(self, tool, tool_input, role=None, ticket=None):
        """Run the hook once on the call, with the probe; return (HookResult, Count)."""
        self._n += 1
        report = self.reports / f"call-{self._n:04d}.jsonl"
        extra = {
            "PYTHONPATH": os.pathsep.join([str(self.probe), str(guard.REPO_ROOT / guard.GOV_PACKAGE_PARENT_REL)]),
            REPORT_ENV: str(report),
            ROOT_ENV: str(self.project),
        }
        result = guard.run_hook(self.project, tool, tool_input, self.sandbox, role=role, ticket=ticket,
                                extra_env=extra)
        return result, Count.read(report)


class Count:
    """One call's report: the governance YAML files opened and the parses, per file."""

    def __init__(self, records):
        self.records = records
        self.opened = sorted({r["file"] for r in records if r["kind"] == "open"})
        self.parses = {}
        for r in records:
            if r["kind"] == "parse":
                self.parses[r["file"]] = self.parses.get(r["file"], 0) + 1
        self.total = sum(self.parses.values())
        self.processes = sorted({r["pid"] for r in records})

    @classmethod
    def read(cls, report):
        if not report.is_file():
            return cls([])
        return cls([json.loads(line) for line in report.read_text(encoding="utf-8").splitlines() if line.strip()])

    def describe(self):
        apis = sorted({r.get("api") for r in self.records if r["kind"] == "parse"})
        return (f"governance YAML files opened: {self.opened or 'none'}; yaml parses per file: "
                f"{self.parses or 'none'} ({self.total} in all, through {apis or 'no API'}); "
                f"processes reporting: {len(self.processes)}")


def probe_works(world):
    """The probe itself is live in the hook's process: a direct ``python -c`` with the same environment, loading the
    held-out file through ``yaml.safe_load``, is reported as one open and one parse of it."""
    import subprocess
    import sys
    report = world.reports / "probe-check.jsonl"
    env = guard.hook_environment(world.project, world.sandbox, extra_env={
        "PYTHONPATH": os.pathsep.join([str(world.probe), str(guard.REPO_ROOT / guard.GOV_PACKAGE_PARENT_REL)]),
        REPORT_ENV: str(report), ROOT_ENV: str(world.project)})
    code = f"import yaml\nwith open({str(world.project / HELD_OUT_REL)!r}) as f:\n    yaml.safe_load(f)\n"
    subprocess.run([sys.executable, "-c", code], env=env, cwd=str(world.project), check=True, capture_output=True)
    return Count.read(report)
