"""KPI success 4 (round 3): where the cache cannot be written (a sandboxed worker, whose .gov-runtime is read-only),
the same text still gets the same vector; a test shows it inside a launched, sandboxed worker [owner, 2026-10-18,
P-W2-32 (a)].

One real worker session is started through ``gov launch`` under its OS sandbox (``local_only``), as W1-46's live
cases start theirs (W1-46's fixture project, its launcher, its environment with no ``CLAUDE*`` variable, DEC-784).
The session runs one Bash command, a probe the case wrote into the session's scratch folder. Inside the sandbox the
probe:

1. starts the suite's stand-in embedder (round 2's, with its variation: a text after a different text gets another
   vector) on the sandbox's own loopback: this machine's Ollama is not reachable from inside (the sandbox has its own
   network, and the engineer's allowlist is empty), and the probe records that;
2. reads a project with a built index that lies **outside** the launched repository, so its ``.gov-runtime/`` is
   read-only to the worker by the sandbox's write fence (the probe records that a new file cannot be made there);
3. asks one text, a different text, and the first text again, each read in a process of its own, through the
   semantic search (its hits and distances) and through ``gov retrieve --json`` (its bundle), with this worktree's
   ``src/`` (DEC-732).

The case then asks the same text, outside the sandbox, in an ordinary process, of the same project with the same
environment and a fresh stand-in. The two answers inside and the answer outside must be one answer. A worker whose
semantic facet gave no answer fails the case.

**Why a project outside the launched repository.** On this machine the sandbox makes read-only only the names under
``.gov-runtime/`` that a literal deny rule names at launch (DEC-311: the Linux sandbox skips a rule with a pattern);
a new file there, such as a cache made after launch, is writable from the worker's Bash. A project outside the
repository is read-only to the worker as a whole (W1-46 success 8), which is the state the KPI line names.

**Cost and needs.** One headless session with the real CLI at ``~/.local/bin/claude`` and the caller's own
credentials (``--model haiku``, one Bash call, about one to two minutes); ``bwrap``, ``socat``, ``gitleaks`` and
``sqlite_vec``. No network: the embedder is the stand-in inside the sandbox. The case fails, as W1-46's live cases do,
when a prerequisite is missing. Leave it out with ``-m "not local_only"``.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

import pytest

import w2_54_support as S

sys.path.insert(0, str(S.REPO_ROOT / "tests/acceptance/W1-46"))
import w1_46_support as L  # noqa: E402

pytestmark = pytest.mark.local_only

SCRATCH = ".gov-runtime/scratch/w2-54"
SESSION_TIMEOUT_S = 420.0
TEXT = "who fires the glazed bowls"
OTHER = "who reads the harbour tide tables"


def _prerequisites():
    missing = [name for name in ("bwrap", "socat", "gitleaks") if shutil.which(name) is None]
    if not (Path.home() / L.CLI_REL).is_file():
        missing.append("~/.local/bin/claude")
    if S.importlib.util.find_spec("sqlite_vec") is None:
        missing.append("sqlite_vec")
    if missing:
        pytest.fail(f"a launched, sandboxed worker with a built index needs {missing} on this machine", pytrace=False)


def _launch_environment(project, sandbox):
    """W1-46's live sessions' environment (DEC-784): no ``CLAUDE*`` variable, no ``GOV_ROLE``, no ``GOV_TICKET``."""
    env = {key: value for key, value in os.environ.items()
           if not key.startswith("CLAUDE") and key not in ("GOV_ROLE", "GOV_TICKET")}
    env.update({"PYTHONPATH": str(project / "src"), "PYTHONPYCACHEPREFIX": str(sandbox.pycache)})
    return env


# The reader: the same program inside the sandbox and outside it. It reads one project, each read in a process of its
# own, with the environment it is given (only OLLAMA_HOST and TMPDIR differ), and writes what each read gave.
_READER = r'''
import errno, json, os, subprocess, sys
from pathlib import Path

spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
root = spec["root"]
env = dict(spec["env"])
env["OLLAMA_HOST"] = spec.get("host") or Path(spec["host_file"]).read_text(encoding="utf-8").strip()
env["TMPDIR"] = os.environ.get("TMPDIR") or "/tmp"
result = {"ollama_host": env["OLLAMA_HOST"], "reads": []}
probe = Path(root) / ".gov-runtime" / "w2-54-worker-write-probe"
try:
    probe.open("x").close()
    probe.unlink()
    result["runtime_new_file"] = "made"
except OSError as exc:
    result["runtime_new_file"] = errno.errorcode.get(exc.errno, str(exc.errno))
done = subprocess.run([spec["python"], "-c", "import gov; print(gov.__file__)"], env=env, capture_output=True,
                      text=True)
result["gov_file"] = done.stdout.strip()
for text in spec["texts"]:
    search = subprocess.run([spec["python"], spec["driver"], root, json.dumps([["search", text]])], env=env,
                            capture_output=True, text=True, cwd=spec["cwd"])
    command = subprocess.run([spec["python"], "-c", spec["gov"], "retrieve", "--json", "--root", root, text],
                             env=env, capture_output=True, text=True, cwd=spec["cwd"])
    result["reads"].append({"text": text,
                            "search": {"code": search.returncode, "stdout": search.stdout, "stderr": search.stderr},
                            "retrieve": {"code": command.returncode, "stdout": command.stdout,
                                         "stderr": command.stderr}})
Path(spec["out"]).write_text(json.dumps(result), encoding="utf-8")
'''

# The stand-in embedder inside the sandbox: round 2's, from this suite's support file, on the sandbox's loopback.
_EMBEDDER = r'''
import json, signal, sys, time
sys.path.insert(0, @SUITE@)
import w2_54_support as S

stand_in = S.EmbedderStandIn()


def stop(*_):
    with open(sys.argv[2], "w", encoding="utf-8") as handle:
        json.dump(stand_in.embedded(), handle)
    sys.exit(0)


signal.signal(signal.SIGTERM, stop)
with open(sys.argv[1], "w", encoding="utf-8") as handle:
    handle.write(stand_in.host)
while True:
    time.sleep(0.2)
'''

_PROBE = f"""#!/bin/bash
# W2-54 acceptance probe: one text, another, the first again, read inside the sandbox.
D={SCRATCH}
OUT=$D/results.txt
: > "$OUT"
echo "ollama_of_this_machine=$(curl -s -o /dev/null -m 5 -w '%{{http_code}}' http://127.0.0.1:11434/api/version; echo " $?")" >> "$OUT"
python3 $D/embedder.py $D/host $D/embedded.json > $D/embedder.log 2>&1 &
EMBEDDER=$!
for i in $(seq 300); do [ -s $D/host ] && break; sleep 0.1; done
echo "embedder=$(cat $D/host 2>/dev/null)" >> "$OUT"
python3 $D/reader.py $D/inside.json > $D/reader.log 2>&1; echo "reader=$?" >> "$OUT"
kill $EMBEDDER; wait $EMBEDDER
echo "end=1" >> "$OUT"
"""

PROMPT = ("Do exactly this one step, once, and nothing else. If it is refused or fails, do not retry it and do not "
          f"work around it. Run this Bash command as written: bash {SCRATCH}/probe.sh  Then answer DONE.")


def _reads(result, where):
    """Each read's semantic answer and bundle; a read that failed, or gave no semantic answer, fails the case."""
    out = []
    for number, read in enumerate(result["reads"], start=1):
        for kind in ("search", "retrieve"):
            assert read[kind]["code"] == 0 and "Traceback" not in read[kind]["stderr"], (
                f"{where}, read {number} ({read['text']!r}), {kind}: exit code {read[kind]['code']}\n"
                f"{read[kind]['stderr'][-1500:]}")
        answer = json.loads(read["search"]["stdout"].strip().splitlines()[-1])[0]
        assert answer.get("available") is True and S.hits_of(answer), (
            f"{where}, read {number} ({read['text']!r}): the semantic facet gave no answer (it did not reach an "
            f"embedder): {answer}")
        envelope = json.loads(read["retrieve"]["stdout"])
        bundle = envelope.get("result") or {}
        assert envelope.get("ok") is True and bundle.get("facets", {}).get("semantic", {}).get("available") is True, \
            f"{where}, read {number} ({read['text']!r}): gov retrieve's semantic facet gave no answer: {envelope}"
        out.append((read["text"], answer, bundle))
    return out


def _evidence(bundle):
    return [(item.get("chunk_id"), item.get("path")) for item in bundle.get("evidence") or []]


def test_inside_a_launched_sandboxed_worker_one_text_gets_one_answer_where_the_cache_cannot_be_written(
        box, tmp_path):
    """*Red.* Inside a worker started by ``gov launch`` under its OS sandbox, reading a project whose
    ``.gov-runtime/`` it cannot write: one text, a different text, the first text again. The two answers to the
    first text are one answer (hits, order, distances; the same bundle from ``gov retrieve``), and the answer an
    ordinary process outside the sandbox gets for it. Today the second answer differs (the variation of the
    embedder, and no cache to fall back on)."""
    _prerequisites()
    # The project the worker reads: a built index, outside the launched repository (read-only to the worker).
    builder = S.EmbedderStandIn()
    try:
        read_root = S.semantic_project(box, tmp_path / "read", builder)
    finally:
        builder.close()
    runtime_before = S.runtime_digest(read_root)
    # The launched project: W1-46's fixture project, with W1-46's held-out stand-in.
    project = L.make_project(tmp_path / "repo")
    sandbox = L.cli_support.make_sandbox(tmp_path / "sandbox")
    L.w47.configure_stand_in(project, L.w47.make_stand_in(sandbox.elsewhere / "held-out-stand-in"))
    scratch = project / SCRATCH
    scratch.mkdir(parents=True)
    env = {key: value for key, value in S.embed_env(box, None).items() if key not in ("OLLAMA_HOST", "TMPDIR")}
    env.pop("PYTHONPYCACHEPREFIX", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    common = {"root": str(read_root), "env": env, "python": sys.executable, "driver": str(scratch / "driver.py"),
              "gov": S._GOV, "texts": [TEXT, OTHER, TEXT], "cwd": str(read_root)}
    (scratch / "driver.py").write_text(S._DRIVER, encoding="utf-8")
    (scratch / "reader.py").write_text(_READER, encoding="utf-8")
    (scratch / "embedder.py").write_text(_EMBEDDER.replace("@SUITE@", repr(str(Path(S.__file__).parent))),
                                         encoding="utf-8")
    (scratch / "inside.json").write_text(json.dumps({**common, "host_file": str(scratch / "host"),
                                                     "out": str(scratch / "inside-result.json")}), encoding="utf-8")
    (scratch / "probe.sh").write_text(_PROBE, encoding="utf-8")

    run = L.run_gov(project, sandbox, "launch", L.ENGINEER, L.TICKET_OF[L.ENGINEER], "--", "-p", PROMPT,
                    "--permission-mode", "acceptEdits", "--model", "haiku", "--max-turns", "6",
                    "--allowedTools", "Bash", env=_launch_environment(project, sandbox), timeout=SESSION_TIMEOUT_S)
    results_path = scratch / "results.txt"
    if not results_path.is_file() or "end=1" not in results_path.read_text(encoding="utf-8"):
        pytest.fail(f"the launched worker did not run the probe to its end (no complete {SCRATCH}/results.txt)\n"
                    f"{run.describe()[-1500:]}", pytrace=False)
    marks = dict(line.split("=", 1) for line in results_path.read_text(encoding="utf-8").splitlines() if "=" in line)
    logs = "\n".join(f"{name}: {(scratch / name).read_text(encoding='utf-8')[-800:]}"
                     for name in ("embedder.log", "reader.log") if (scratch / name).is_file())
    assert (scratch / "inside-result.json").is_file(), f"the reader left no result inside the sandbox: {marks}\n{logs}"
    inside = json.loads((scratch / "inside-result.json").read_text(encoding="utf-8"))

    # The premises: this worktree's code; the cache could not be written; the embedder reached is the one inside.
    assert inside["gov_file"] == str(S.SRC / "gov" / "__init__.py"), f"inside, gov came from {inside['gov_file']!r}"
    assert inside["runtime_new_file"] != "made", \
        "the premise: the worker could make a file in the read project's .gov-runtime/ (it is not read-only)"
    assert S.runtime_digest(read_root) == runtime_before, "the worker changed the read project's .gov-runtime/"
    embedded = json.loads((scratch / "embedded.json").read_text(encoding="utf-8")) \
        if (scratch / "embedded.json").is_file() else []
    assert any(text.endswith(TEXT) for text in embedded), \
        f"the stand-in inside the sandbox was never asked the text: {embedded[:4]}\n{marks}\n{logs}"
    reads = _reads(inside, "inside the sandbox")
    (_, first, first_bundle), _, (_, again, again_bundle) = reads

    # Outside the sandbox: an ordinary process, the same project and environment, a fresh stand-in.
    outside_embedder = S.EmbedderStandIn()
    try:
        (tmp_path / "outside.json").write_text(json.dumps({**common, "host": outside_embedder.host,
                                                           "texts": [TEXT], "out": str(tmp_path / "outside.out")}),
                                               encoding="utf-8")
        done = S.run([sys.executable, scratch / "reader.py", tmp_path / "outside.json"], cwd=box.workdir / "elsewhere",
                     env=S.embed_env(box, outside_embedder), timeout=S.CALL_TIMEOUT_S)
    finally:
        outside_embedder.close()
    assert done.returncode == 0, done.describe()
    outside = json.loads((tmp_path / "outside.out").read_text(encoding="utf-8"))
    (_, reference, reference_bundle), = _reads(outside, "outside the sandbox")

    assert S.hits_of(again) == S.hits_of(first), (
        "inside the sandbox, one text got two answers (asked again after another text, no cache to write)\n"
        f"first: {S.hits_of(first)[:3]}\nagain: {S.hits_of(again)[:3]}")
    assert S.canonical(again_bundle) == S.canonical(first_bundle), (
        f"inside the sandbox, gov retrieve gave one text two bundles:\n{_evidence(first_bundle)}\n"
        f"{_evidence(again_bundle)}")
    assert S.hits_of(first) == S.hits_of(reference), (
        "the answer inside the sandbox is not the answer outside it\n"
        f"inside:  {S.hits_of(first)[:3]}\noutside: {S.hits_of(reference)[:3]}")
    assert _evidence(first_bundle) == _evidence(reference_bundle), (
        f"gov retrieve inside the sandbox and outside it gave two bundles:\n{_evidence(first_bundle)}\n"
        f"{_evidence(reference_bundle)}")
