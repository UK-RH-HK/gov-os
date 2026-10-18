"""Support code for the W2-52 acceptance tests: the lite A7 and A10 gates of ``gov adopt`` (CAP-44.f, CAP-44.h).

W2-52 adds two stages to ``gov adopt --lite``. Every case runs them on a project the case's fixtures build file by
file in a temporary folder, as a git repository of its own, with W1-41's support (``build_project``, ``Adoption``,
the A5 verdict). Nothing of this repository is copied: the only files read from it are the kernel's two canary
declarations, copied one by one into the temporary project as an installed kernel would carry them.

- **The code under test** is this worktree's ``gov`` package: the launcher W1-07's support writes, with
  ``src/`` of this worktree on the child's ``PYTHONPATH`` (W1-41's ``environment``). ``gov_file`` shows it.
- **No model, no network.** The semantic index is built through a stand-in embedding endpoint on a loopback port
  (the vectors of W1-22's stand-in: a hash of each word); a case that needs the endpoint out of reach keeps
  W1-41's dead loopback address. ``sqlite_vec`` is reached through a folder holding one link to the installed
  package, as W1-22's support does.
- **The auditor's records** are written and committed by the case as the Independent Auditor commits its report
  (``Role: independent-auditor``, DEC-182), as W1-41 does for the A5 verdict.

The interface the cases hold is in ``README.md`` ("The interface the cases hold").
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import os
import posixpath
import re
import shutil
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import yaml

_HERE = Path(__file__).resolve().parent
for _folder in (_HERE.parent / "W1-07", _HERE.parent / "W1-41"):
    if str(_folder) not in sys.path:
        sys.path.insert(0, str(_folder))

import w1_41_support as support  # noqa: E402

REPO_ROOT = support.REPO_ROOT
base = support.base

# --- what the sources fix ---------------------------------------------------
GATES = ("A7", "A10")                                        # CAP-44.f (lite), DEC-722, DEC-741
GATE_CHECKS = {"A7": ("A3", "A4", "A5", "A6"),               # A7: the A6 migration against the A3 path map and
               "A10": ("A8",)}                               # the A4 plan reviewed at A5; A10: A8's extraction
#                                                              and retirement (and the rebuild, the canaries)
WAVE_3 = {                                                   # CAP-44.k; CIT-P §3.2 "What of A7/A10 stays"
    "A7": ("CAP-44.k", "CAP-47.a"),
    "A10": ("CAP-44.k", "CAP-47.a", "CAP-49", "A9"),
}
CONDITION_STATES = ("met", "not met", "accepted")             # W2-02's adoption-verdict.schema.json, condition
CONDITION_KEYS = ("name", "source", "state", "owner_entry")
DECISION_ID_RE = re.compile(r"^DEC-\d+$")
CONDITION_SOURCES = ("CAP-44.f", "CAP-44.h")                 # the item a gate's condition comes from
VERDICTS = ("ADOPTED_HEALTHY", "ADOPTED_WITH_ACCEPTED_EXCEPTIONS", "NOT_ADOPTED_HEALTHY")   # CAP-44.h
INDEXES = ("lexical", "semantic")                            # the indexes with canaries (W1-22, CAP-55)
AUDITOR_ROLE = support.AUDITOR_ROLE
ADOPTER_SESSION = support.ADOPTER_SESSION
GATE_SESSION = {"A7": "auditor-007", "A10": "auditor-010"}   # fresh auditor sessions, not the adopter's
GATE_VERDICT_REL = {"A7": "audit/adoption/a7-verdict.md", "A10": "audit/adoption/a10-verdict.md"}
GATE_VERDICT_ID = {"A7": "AV-0007", "A10": "AV-0010"}
CANARY_FILES = ("lexical.yaml", "semantic.yaml")
KERNEL_CANARIES = REPO_ROOT / "template/governance/kernel/canaries"
PROJECT_CANARIES = "governance/kernel/canaries"              # where an installed kernel holds them

# The project's moves (A6) and its legacy material (A8), as W1-41 writes them.
MOVES = {item["path"]: item["target"] for item in support.moves_proposal()}
EXTRACTION_REL, EXTRACTION_ID = support.EXTRACTION_REL, support.EXTRACTION_ID


def proposal():
    """Three move batches (A6) and every legacy file retired (A8): what A7 and A10 each check."""
    return support.moves_proposal() + support.legacy_proposal()


def build_harbour(destination):
    """W1-41's harbour project, with the kernel's canary declarations where an installed kernel holds them."""
    extra = {f"{PROJECT_CANARIES}/{name}": (KERNEL_CANARIES / name).read_text(encoding="utf-8")
             for name in CANARY_FILES}
    return support.build_project(destination, extra=extra)


# --------------------------------------------------------------------------
# The stand-in embedding endpoint (no model; loopback only). The vectors of W1-22's stand-in.
# --------------------------------------------------------------------------

EMBED_MODEL = "qwen3-embedding:0.6b"
DIMENSIONS = 1024
_STOP = {"the", "and", "for", "with", "that", "this", "each", "does", "when", "who", "what", "into", "from", "its",
         "are", "was", "has", "have", "before", "after", "then", "any", "all", "given", "query", "instruct",
         "retrieve", "relevant", "passages", "search", "web", "answer", "which", "every"}


def stand_in_vector(text):
    vector = [0.0] * DIMENSIONS
    for word in re.findall(r"[a-z0-9]+", str(text).lower()):
        if len(word) >= 3 and word not in _STOP:
            digest = hashlib.sha256(word.encode()).digest()
            vector[int.from_bytes(digest[:4], "big") % DIMENSIONS] += 1.0 if digest[4] % 2 else -1.0
    norm = math.sqrt(sum(v * v for v in vector))
    if norm == 0.0:
        vector[0], norm = 1.0, 1.0
    return [v / norm for v in vector]


class EmbeddingStandIn:
    """An HTTP endpoint on 127.0.0.1 that answers as an embedding server would, with deterministic vectors."""

    def __init__(self):
        model = {"name": EMBED_MODEL, "model": EMBED_MODEL, "digest": "ac6da0dfba84" + "0" * 52}

        class Handler(BaseHTTPRequestHandler):
            def answer(self):
                length = int(self.headers.get("Content-Length") or 0)
                try:
                    asked = json.loads(self.rfile.read(length) or b"{}") if length else {}
                except ValueError:
                    asked = {}
                route, reply, status = self.path.split("?")[0].rstrip("/"), {}, 200
                if route == "/api/version":
                    reply = {"version": "0.35.0"}
                elif route == "/api/tags":
                    reply = {"models": [model]}
                elif route == "/api/embed":
                    given = asked.get("input", "")
                    texts = [given] if isinstance(given, str) else list(given)
                    reply = {"model": EMBED_MODEL, "embeddings": [stand_in_vector(t) for t in texts]}
                else:
                    status = 404
                payload = json.dumps(reply).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            do_GET = do_POST = do_HEAD = answer

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.host = f"127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def vector_site(destination):
    """A folder holding one link to the installed ``sqlite_vec`` package (None where it is not installed)."""
    spec = importlib.util.find_spec("sqlite_vec")
    if spec is None or not spec.origin:
        return None
    origin = Path(spec.origin)
    source = origin.parent if spec.submodule_search_locations else origin
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    link = destination / source.name
    if not link.is_symlink():
        link.symlink_to(source, target_is_directory=source.is_dir())
    return destination


# --------------------------------------------------------------------------
# Running gov with this worktree's code
# --------------------------------------------------------------------------

def environment(sandbox, endpoint=None, site=None):
    """W1-41's environment (this worktree's ``src/``, an empty HOME, a git identity, no model), with the stand-in
    endpoint where ``endpoint`` is given and ``sqlite_vec`` where ``site`` is given."""
    env = support.environment(sandbox)
    if endpoint:
        env["OLLAMA_HOST"] = endpoint
    if site:
        env["PYTHONPATH"] = env["PYTHONPATH"] + os.pathsep + str(site)
    return env


def run_gov(project, sandbox, *args, endpoint=None, site=None):
    """``gov <args>`` in ``project`` (never this repository), with this worktree's code."""
    support.assert_own_project(project)
    launcher = base.write_launcher(REPO_ROOT, sandbox)
    started = time.perf_counter()
    try:
        done = subprocess.run([sys.executable, str(launcher), *args], cwd=str(project),
                              env=environment(sandbox, endpoint, site), capture_output=True, text=True,
                              timeout=support.COMMAND_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"gov {' '.join(args)} did not end within {support.COMMAND_TIMEOUT_S:.0f} s") from None
    return base.Run(tuple(args), done.returncode, done.stdout, done.stderr, time.perf_counter() - started)


def gov_file(sandbox):
    """Where a child started as the cases start ``gov`` imports the package from."""
    done = subprocess.run([sys.executable, "-c", "import gov; print(gov.__file__)"], cwd=str(sandbox.elsewhere),
                          env=environment(sandbox), capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, done.stderr
    return Path(done.stdout.strip())


@dataclass
class GateAdoption(support.Adoption):
    """W1-41's adoption, run with the stand-in endpoint (``endpoint``) and ``sqlite_vec`` (``site``)."""
    endpoint: str | None = None
    site: Path | None = None

    def run(self, stage, *extra, without=(), session=None):
        return run_gov(self.project, self.sandbox, "adopt", "--lite", "--stage", stage, *extra, "--json",
                       "--session", session or self.session, endpoint=self.endpoint, site=self.site)

    def gov(self, *args, endpoint=None):
        return run_gov(self.project, self.sandbox, *args, endpoint=endpoint or self.endpoint, site=self.site)

    def records_folder(self):
        """The adoption run's own folder: where stage A0 put its record."""
        return posixpath.dirname(self.stages["A0"].record)


@dataclass
class Snapshot:
    """A temporary project after some stages, kept for the cases to copy."""
    root: Path
    stages: dict = field(default_factory=dict)


def snapshot(adoption):
    return Snapshot(adoption.project, dict(adoption.stages))


def copy_adoption(kept, destination, interface, endpoint=None, site=None):
    """A copy of a temporary project the fixtures built (never of this repository), without its derived state,
    with a sandbox of its own."""
    destination = Path(destination)
    project = destination / "harbour"
    shutil.copytree(kept.root, project, symlinks=True, ignore=shutil.ignore_patterns(".gov-runtime"))
    support.assert_own_project(project)
    adoption = GateAdoption(project, support.make_sandbox(destination / "sandbox"), interface,
                            endpoint=endpoint, site=site)
    adoption.stages = dict(kept.stages)
    return adoption


# --------------------------------------------------------------------------
# The auditor's record for a gate (the A5 precedent)
# --------------------------------------------------------------------------

def record_hash(project, rel):
    data = support.at_head(project, rel)
    assert data is not None, f"{rel} is not committed"
    return support.sha256(data)


def checked_records(adoption, gate):
    """The stage records the auditor checks for ``gate``, by path, as the stages left them."""
    return [adoption.stages[stage].record for stage in GATE_CHECKS[gate]]


def gate_verdict_text(adoption, gate, verdict="pass", session=None, checked=None, hashes=None, **override):
    """The auditor's record: frontmatter with the stage, the verdict, the auditor's session and the records it
    checked, each with the sha256 of the record as it stands at HEAD. ``hashes`` replaces the hash of a path;
    a key of ``override`` given as None is left out."""
    rels = checked_records(adoption, gate) if checked is None else list(checked)
    listed = [{"record": rel, "sha256": (hashes or {}).get(rel) or record_hash(adoption.project, rel)}
              for rel in rels]
    front = {
        "id": GATE_VERDICT_ID[gate], "type": "evidence", "status": "ACTIVE", "state_class": "EVIDENCE",
        "stage": gate, "verdict": verdict, "auditor_session": session or GATE_SESSION[gate], "checked": listed,
    }
    for key, value in override.items():
        if value is None:
            front.pop(key, None)
        else:
            front[key] = value
    return ("---\n" + yaml.safe_dump(front, sort_keys=False) + f"---\n\n# {GATE_VERDICT_ID[gate]}: lite {gate} gate\n\n"
            "A fresh Independent Auditor session checked the records listed above and the project at HEAD.\n")


def write_gate_verdict(adoption, gate, role=AUDITOR_ROLE, text=None, rel=None, commit=True, **keys):
    """Write the auditor's record for ``gate`` and commit it with ``Role: <role>`` (none where ``role`` is None)."""
    rel = rel or GATE_VERDICT_REL[gate]
    support.write(adoption.project, rel, text if text is not None else gate_verdict_text(adoption, gate, **keys))
    if commit:
        trailers = [f"Task: HARB-{gate.lower()}aa"] + ([f"Role: {role}"] if role else [])
        support.commit(adoption.project, f"{gate}: the Independent Auditor's record", *trailers)
    return rel


# --------------------------------------------------------------------------
# Observing a gate: what it answered, and what it left in the project
# --------------------------------------------------------------------------

@dataclass
class Outcome:
    stage: str
    run: object
    before: dict          # path -> blob at HEAD before the run
    after: dict           # path -> blob at HEAD after the run
    folder: str           # the adoption run's own folder
    project: Path
    porcelain: str

    def envelope(self):
        try:
            data = json.loads(self.run.stdout)
        except ValueError:
            return None
        return data if isinstance(data, dict) else None

    def added(self):
        return sorted(set(self.after) - set(self.before))

    def changed(self):
        """Paths that were at HEAD before the run and changed or left."""
        return sorted(rel for rel, blob in self.before.items() if self.after.get(rel) != blob)

    def records(self):
        """Every file the run added whose frontmatter names this stage."""
        found = []
        for rel in self.added():
            text = (support.at_head(self.project, rel) or b"").decode("utf-8", "replace")
            try:
                front = support.frontmatter(text, rel)
            except (AssertionError, yaml.YAMLError):
                continue
            if front.get("stage") == self.stage:
                found.append((rel, front, text))
        return found

    def describe(self):
        return f"{self.run.describe()}\nadded at HEAD: {self.added()}\nchanged at HEAD: {self.changed()}"


def observe_gate(adoption, gate, *extra, session=None, untracked=()):
    """Run ``gate`` and keep what it answered and what it left; asserts nothing. ``untracked`` names files the
    case itself left uncommitted: they are not counted against the gate's clean tree."""
    before = support.tree(adoption.project)
    run = adoption.run(gate, *extra, session=session)
    lines = [line for line in support.porcelain(adoption.project).splitlines()
             if not any(line.endswith(" " + rel) for rel in untracked)]
    return Outcome(gate, run, before, support.tree(adoption.project), adoption.records_folder(), adoption.project,
                   "\n".join(lines))


def run_gate(adoption, gate, verdict_rel=None, session=None, untracked=()):
    """The gate, given the auditor's record (``--verdict``, the A5 precedent)."""
    return observe_gate(adoption, gate, "--verdict", verdict_rel or GATE_VERDICT_REL[gate], session=session,
                        untracked=untracked)


def assert_stage_taken(outcome):
    """The red reason before W2-52: ``--stage`` does not offer the gate (argparse's usage error, exit code 2)."""
    run = outcome.run
    assert not ("invalid choice" in run.stderr or (run.returncode == 2 and not run.stdout.strip())), \
        f"gov adopt --lite does not take --stage {outcome.stage}\n{run.describe()}"
    assert not support.not_built(run), f"gov adopt --lite answers that stage {outcome.stage} is not built\n" \
                                       f"{run.describe()}"


def assert_only_its_own_record(outcome):
    """The gate wrote nothing but records in the adoption run's own folder, changed no file that was there, and
    left the tree clean (never over another stage's record; the gate moves and retires nothing)."""
    assert not outcome.changed(), f"stage {outcome.stage} changed or removed files: {outcome.changed()}\n" \
                                  f"{outcome.describe()}"
    outside = [rel for rel in outcome.added() if posixpath.dirname(rel) != outcome.folder]
    assert not outside, f"stage {outcome.stage} added files outside the adoption run's folder " \
                        f"{outcome.folder}: {outside}\n{outcome.describe()}"
    assert outcome.porcelain == "", f"stage {outcome.stage} left the tree dirty:\n{outcome.porcelain}\n" \
                                    f"{outcome.describe()}"


def conditions(value):
    """Every object, at any depth of ``value``, that has the three keys of W2-02's condition."""
    found = []
    if isinstance(value, dict):
        if {"name", "source", "state"} <= set(value):
            return [value]
        for item in value.values():
            found.extend(conditions(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(conditions(item))
    return found


def assert_condition_form(condition, where):
    """W2-02's condition: ``name`` and ``source`` non-empty texts, ``state`` one of three, ``owner_entry`` (a
    decision id) where accepted, and no other key."""
    extra = sorted(set(condition) - set(CONDITION_KEYS))
    assert not extra, f"{where}: the condition {condition} has keys W2-02's condition does not have: {extra}"
    for key in ("name", "source"):
        assert isinstance(condition[key], str) and condition[key].strip(), \
            f"{where}: the condition's {key} is not a non-empty text: {condition}"
    assert condition["state"] in CONDITION_STATES, \
        f"{where}: the condition's state {condition['state']!r} is not one of {CONDITION_STATES}"
    if condition["state"] == "accepted":
        assert DECISION_ID_RE.match(str(condition.get("owner_entry", ""))), \
            f"{where}: an accepted condition names no owner entry: {condition}"


def lite_verdict(found):
    """The verdict CAP-44.h gives a list of conditions: healthy when every one is met; with accepted exceptions
    when each one not met is accepted; otherwise not healthy."""
    states = [item["state"] for item in found]
    if states and all(state == "met" for state in states):
        return "ADOPTED_HEALTHY"
    if states and all(state in ("met", "accepted") for state in states):
        return "ADOPTED_WITH_ACCEPTED_EXCEPTIONS"
    return "NOT_ADOPTED_HEALTHY"


def the_record(outcome):
    """The one record of this stage the run added: (path, frontmatter, text)."""
    records = outcome.records()
    assert records, f"stage {outcome.stage} left no record of its own in {outcome.folder}\n{outcome.describe()}"
    assert len(records) == 1, f"stage {outcome.stage} left {len(records)} records\n{outcome.describe()}"
    rel, front, text = records[0]
    assert (outcome.project / rel).read_bytes() == support.at_head(outcome.project, rel), \
        f"{rel} is not committed as it stands"
    assert isinstance(front.get("id"), str) and support.RECORD_ID_RE.match(front["id"]), \
        f"{rel}: the id is not a record id ({front.get('id')!r})"
    assert front.get("type") == "evidence", f"{rel}: type is not 'evidence'"
    assert front.get("state_class") == "EVIDENCE", f"{rel}: state_class is not EVIDENCE"
    assert isinstance(front.get("status"), str) and front["status"], f"{rel}: no status"
    return rel, front, text


def gate_conditions(outcome, rel, front):
    found = conditions(front)
    assert found, f"{rel}: the record gives no condition in W2-02's form (name, source, state)\n{outcome.describe()}"
    for item in found:
        assert_condition_form(item, rel)
        assert any(source in item["source"] for source in CONDITION_SOURCES), \
            f"{rel}: the condition's source names neither of {CONDITION_SOURCES}: {item}"
    assert any(re.search(rf"\b{outcome.stage}\b", item["name"]) for item in found), \
        f"{rel}: no condition's name names the gate {outcome.stage}: {found}"
    assert not [item for item in found if item["state"] == "accepted"], \
        f"{rel}: the gate accepts a condition; only the owner accepts an exception (CAP-44.h, DEC-741 F): {found}"
    return found


def assert_passed(outcome):
    """The gate passed: the envelope says so, and its record, its own stage, gives conditions all met."""
    assert_stage_taken(outcome)
    envelope = base.assert_envelope(outcome.run, support.base.load_interface(REPO_ROOT), command="adopt")
    assert envelope["ok"] is True, f"stage {outcome.stage} did not pass\n{outcome.describe()}"
    result = envelope["result"]
    assert result.get("stage") == outcome.stage, f"the result does not name the stage {outcome.stage}"
    assert_only_its_own_record(outcome)
    rel, front, text = the_record(outcome)
    assert result.get("record") == rel, f"the result's record {result.get('record')!r} is not {rel}"
    found = gate_conditions(outcome, rel, front)
    unmet = [item for item in found if item["state"] != "met"]
    assert not unmet, f"{rel}: the gate passed with conditions not met: {unmet}"
    return rel, front, text


def _said(outcome, record_text=""):
    return (outcome.run.stdout + "\n" + record_text).lower()


def _assert_names(outcome, said, names, any_of):
    for name in names:
        assert name.lower() in said, f"stage {outcome.stage}: neither the answer nor the record names {name!r}\n" \
                                     f"{outcome.describe()}"
    if any_of:
        assert any(name.lower() in said for name in any_of), \
            f"stage {outcome.stage}: neither the answer nor the record names any of {list(any_of)}\n" \
            f"{outcome.describe()}"


def assert_failing_record(outcome, *names, any_of=()):
    """Failure line: the gate failed and wrote a failing record, committed in the run's own folder, whose
    conditions a verdict cannot read as healthy; the answer or the record names ``names``."""
    assert_stage_taken(outcome)
    base.assert_envelope(outcome.run, support.base.load_interface(REPO_ROOT), command="adopt")
    assert_only_its_own_record(outcome)
    rel, front, text = the_record(outcome)
    found = gate_conditions(outcome, rel, front)
    assert [item for item in found if item["state"] == "not met"], \
        f"{rel}: a failing gate's record gives no condition 'not met': {found}\n{outcome.describe()}"
    assert lite_verdict(found) != "ADOPTED_HEALTHY", f"{rel}: a verdict reading {found} would be healthy"
    _assert_names(outcome, _said(outcome, text), names, any_of)
    return rel, front, text


def assert_never_passes(outcome, *names, any_of=()):
    """The gate does not pass: it refuses (``ok: false``, exit code 1, 3 or 4, nothing written) or writes a failing
    record; either way the answer or the record names ``names``, and no record of the gate says 'met' alone."""
    assert_stage_taken(outcome)
    envelope = base.assert_envelope(outcome.run, support.base.load_interface(REPO_ROOT), command="adopt")
    if outcome.records():
        return assert_failing_record(outcome, *names, any_of=any_of)
    assert envelope["ok"] is False, f"stage {outcome.stage} reports success but left no record\n" \
                                    f"{outcome.describe()}"
    assert outcome.run.returncode in support.REFUSAL_EXIT_CODES, \
        f"a refusal ends with one of {support.REFUSAL_EXIT_CODES}\n{outcome.describe()}"
    assert outcome.before == outcome.after, f"a refusal wrote something\n{outcome.describe()}"
    _assert_names(outcome, _said(outcome), names, any_of)
    return None


def assert_names_wave_3(rel, text, gate):
    """The record names what of the gate stays for Wave 3 (CAP-44.k; CIT-P §3.2)."""
    lowered = text.lower()
    assert "wave 3" in lowered or re.search(r"\bw3\b", lowered), f"{rel}: the record does not name Wave 3"
    missing = [item for item in WAVE_3[gate] if not re.search(rf"\b{re.escape(item.lower())}\b", lowered)]
    assert not missing, f"{rel}: the record does not name what stays for Wave 3: {missing}"


def rebuild_digest(adoption):
    """``gov rebuild --json`` in the temporary project: the digest of the derived state rebuilt from git."""
    run = adoption.gov("rebuild", "--json")
    envelope = run.envelope()
    assert envelope.get("ok") is True, f"the rebuild failed\n{run.describe()}"
    digest = (envelope.get("result") or {}).get("digest")
    assert isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest), f"no digest\n{run.describe()}"
    return digest


def remove_derived_state(project):
    """Delete the temporary project's derived state (CAP-20: delete derived, rebuild from git)."""
    shutil.rmtree(Path(project) / ".gov-runtime", ignore_errors=True)
