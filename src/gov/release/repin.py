"""The general re-pin of the machine's ``gov`` (W2-209, RELEASE-ON-BEHALF "Re-pin and its rollback"; DEC-1223).

``repin(repo, version, home)`` is ``docs/emergency-2/release-0.1.4/repin.sh`` made general: the version is read from
the tag ``v<version>``, none is written in. Each of these stops before the switch, changing neither the link
``<home>/.local/bin/gov`` nor the pin folders (a folder made for the new pin is removed): the version is not burned;
the tag is annotated and its commit's only parent is C; only the record's files differ between C and the tag; the
manifest matches its hash and names the version and C; the wheel built twice from C equals the record's sha256; the
environment ``pin-<C12>`` is made beside the live one and its ``gov --version`` says the release.

The switch is one rename of the link. Then the post-pin checks run through the new link: ``gov --help``,
``gov launch --help``, a search of the memory store with both facets, the five hook programs of the repository's
settings with an empty event, and ``gov doctor`` (no part unhealthy that was healthy before the switch). A pass commits
the registry entry, writes ``repin.json`` and ``rollback.sh`` and makes the release push; a failure renames the link back,
writes ``repin.json`` as ``rolled_back``, burns the release (``burned``, one version a line; its tag and record stay) and
makes the failure push. Nothing here contacts a remote: the one thing that leaves the machine is the push command the
caller names, run once and detached as ``gov.dispatch.runtime.push`` runs it.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

from gov import release
from gov.release import gates, patch

SHARE_REL, BIN_REL = ".local/share/gov-os", ".local/bin"
REGISTRY_REL = "governance/project/tool-registry.yaml"
HOOKS_REL = "template/governance/kernel/hooks"
HOOKS = ("context_watch", "precompact", "sessionstart", "stop", "subagentstop")
PUSH_LIMIT = 190
ROLLBACK_LINE = "bash ~/.local/share/gov-os/rollback.sh"
CHECK_LIMIT = 120
QUESTION = "what decides a close"
_SHA = re.compile(r"[0-9a-f]{64}")


def _share(home) -> Path:
    return Path(home) / SHARE_REL


def burned(home) -> list[str]:
    """The releases marked burned in ``<home>/.local/share/gov-os/burned``, in file order (``[]`` without the file)."""
    try:
        text = (_share(home) / "burned").read_text(encoding="utf-8")
    except OSError:
        return []
    return [line.strip() for line in text.splitlines() if line.strip()]


def _burn(home, version: str) -> None:
    folder = _share(home)
    folder.mkdir(parents=True, exist_ok=True)
    if version not in burned(home):
        with open(folder / "burned", "a", encoding="utf-8") as handle:
            handle.write(f"{version}\n")


def push_text(version: str, fixes: int, head: str, verdict: str, kind: str = "patch") -> str:
    """The push of a pinned release: the version, the fixes, the suite and proving-run evidence, the rollback line."""
    noun = "fix" if fixes == 1 else "fixes"
    text = (f"Gov OS {version} released ({kind}, {fixes} {noun}). Suite green on {str(head)[:8]}, proving run "
            f"{verdict}, pin live. Roll back: {ROLLBACK_LINE}")
    return text[:PUSH_LIMIT]


def failure_text(version: str, check: str, kind: str = "patch") -> str:
    """The push of a failed re-pin, cut to 190 characters by shortening the check's text; version and ``burned`` stay."""
    following = "patch" if kind == "patch" else "release"

    def build(shown: str, tail: str = f" CTO cuts the next {following}.") -> str:
        return (f"Gov OS {version} NOT pinned: post-pin check failed ({shown}). Rolled back, old gov live, nothing "
                f"for you to do. Release burned;{tail}")
    check = " ".join(str(check).split())
    text = build(check)
    if len(text) > PUSH_LIMIT:
        room = PUSH_LIMIT - len(build("")) - 1
        text = build(check[:room].rstrip() + "…" if room > 0 else "")
    if len(text) > PUSH_LIMIT:
        text = build("", tail="")
    return text[:PUSH_LIMIT] if "burned" in text[:PUSH_LIMIT] else text


def rollback_script(old_pin, home, version: str) -> str:
    """``rollback.sh``: plain shell, never ``gov`` (the new gov is the thing in doubt): the link back to the old pin by
    one rename, and the release added to ``burned``."""
    link = f"{Path(home) / BIN_REL}/gov"
    burned_file = _share(home) / "burned"
    return ("#!/usr/bin/env bash\n"
            f"# Puts the previous gov back (pin {Path(old_pin).name}) and marks release {version} burned. Plain shell: no gov.\n"
            f"ln -sfn {old_pin}/bin/gov {link}.new && mv -Tf {link}.new {link}; hash -r\n"
            f"grep -qxF {version} {burned_file} 2>/dev/null || echo {version} >> {burned_file}\n"
            f"echo \"rolled back: {link} -> $(readlink -f {link}); release {version} burned\"\n")


def note_text(version: str, n: str, fixes: list[str], chores: list[str], evidence: dict, repositories: list[str],
              approvals: list[dict] = ()) -> str:
    """``docs/releases/<version>/NOTE.md``: the version, each fix in plain words, an approved release's items with their
    decisions, the gate evidence, the rollback line and which repositories update next."""
    title = "Patch" if evidence["kind"] == "patch" else "Approved"
    lines = [f"# Gov OS {version}", "", f"{title} release from {n}: {len(fixes)} fixes, {len(chores)} chores.", "",
             "## What changed", ""]
    lines += [f"- Fix: {text}" for text in fixes] + [f"- Chore: {text}" for text in chores]
    if not fixes and not chores:
        lines.append("- nothing listed")
    if approvals:
        lines += ["", "## Approvals", ""]
        lines += [f"- {item['item']}: {', '.join(item['decisions'])}" for item in approvals]
    lines += ["", "## Gate evidence", "",
              f"- Suite record {evidence['record']}: green on {evidence['head']} (full, weekly tier included)",
              f"- Proving run (update rehearsal): {evidence['verdict']}",
              f"- Release rule: {evidence['kind']}", "",
              "## Roll back", "", f"`{ROLLBACK_LINE}`", "",
              "## Repositories that update next", ""]
    lines += [f"- {path}" for path in repositories] or ["- none listed"]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# the re-pin
# ---------------------------------------------------------------------------

def _git(repo: Path, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, input=stdin)


def _show(repo: Path, tag: str, rel: str) -> str | None:
    done = _git(repo, "show", f"{tag}:{rel}")
    return done.stdout if done.returncode == 0 else None


def _clean_env() -> dict:
    """The caller's environment without what makes a pin's ``gov`` import another ``gov``: the pin runs as it does
    from a plain terminal, from its own site-packages (``PYTHONPATH`` and ``PYTHONHOME`` out)."""
    return {key: value for key, value in os.environ.items() if key not in ("PYTHONPATH", "PYTHONHOME")}


def _run(argv, cwd, timeout=300, env=None, stdin=None) -> subprocess.CompletedProcess:
    env = _clean_env() if env is None else env
    feed = {"input": stdin} if stdin is not None else {"stdin": subprocess.DEVNULL}
    try:
        return subprocess.run([str(a) for a in argv], cwd=str(cwd), capture_output=True, text=True, timeout=timeout,
                              env=env, **feed)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return subprocess.CompletedProcess(argv, 124, "", f"{type(exc).__name__}: {exc}")


def _parts(stdout: str) -> dict[str, str] | None:
    """The doctor parts with their status: the maps with a ``status`` under ``result`` or, for ``DOCTOR_UNHEALTHY``,
    under ``error.details``; ``None`` when the output is no envelope."""
    try:
        envelope = json.loads(stdout)
        holder = envelope["result"] if envelope.get("ok") else envelope["error"]["details"]
    except (ValueError, KeyError, TypeError, AttributeError):
        return None
    if not isinstance(holder, dict):
        return None
    return {key: value["status"] for key, value in holder.items() if isinstance(value, dict) and "status" in value}


def _unhealthy(parts: dict[str, str]) -> set[str]:
    return {name for name, status in parts.items() if status in ("fail", "drift")}


def _registry(text: str, version: str, cli: str, c12: str, sha: str, old_pin: str, script: str, decision: str) -> str:
    """The ``- name: gov`` entry of the tool registry replaced in place (the other entries untouched)."""
    wheel = f"gov-{cli}-py3-none-any.whl"
    new = ('  - name: gov\n'
           f'    version: "{version}"\n'
           f'    sha256: "{sha}"\n'
           f'    install: "python3 -m venv --system-site-packages ~/.local/share/gov-os/pin-{c12} && ~/.local/share/gov-os/pin-{c12}/bin/python -m pip install --no-deps --no-index ~/.local/share/gov-os/wheels/{c12}/{wheel} && ln -s ~/.local/share/gov-os/pin-{c12}/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov"\n'
           f'    uninstall: "ln -s ~/.local/share/gov-os/{old_pin}/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov && rm -rf ~/.local/share/gov-os/pin-{c12}"\n'
           f'    date: "{datetime.date.today().isoformat()}"\n'
           f'    approved_by: "{decision}"\n'
           f'    note: "Re-pin from release {version} ({decision}, the owner\'s standing yes): the wheel of the numbered release {version}, tag v{version} on the record commit whose parent is {c12}; built twice from {c12} with SOURCE_DATE_EPOCH, equal to the record\'s sha256; its own environment ~/.local/share/gov-os/pin-{c12}; linked from ~/.local/bin/gov by an atomic rename (script sha256 {script}). Replaces the entry of {old_pin}, kept for a one-command rollback (the uninstall line)."\n')
    start = text.find("  - name: gov\n")
    if start < 0:
        return text + ("" if text.endswith("\n") else "\n") + new
    end = text.find("\n  - name: ", start + 1)
    end = len(text) if end == -1 else end + 1
    return text[:start] + new + text[end:]


def _decision(repo: Path) -> str:
    text = _show(repo, "HEAD", gates.AUTHORITY_REL)
    try:
        value = yaml.safe_load(text or "")
        decision = value.get("decision") if isinstance(value, dict) else None
    except yaml.YAMLError:
        decision = None
    return decision.strip() if isinstance(decision, str) and decision.strip() else "the owner's standing yes"


def _hooks(pin: Path, repo: Path) -> str | None:
    """Run the repository's five hook programs with an empty event through the pin's interpreter; the failing one or None."""
    env = {key: value for key, value in _clean_env().items() if key not in ("GOV_ROLE", "GOV_TICKET")}
    env["CLAUDE_PROJECT_DIR"] = str(repo)
    for hook in HOOKS:
        program = repo / HOOKS_REL / f"{hook}.py"
        done = _run([pin / "bin" / "python", "-E", program], repo, timeout=120, env=env, stdin="{}")
        output = f"{done.stdout}\n{done.stderr}"
        if "Traceback" in output:
            return f"{hook}: the hook crashed"
        if done.returncode == 0:
            continue
        if hook == "subagentstop" and done.returncode == 2 and "return contract incomplete" in output:
            continue
        return f"{hook}: the hook gave exit {done.returncode}"
    return None


def _post_pin(link: Path, pin: Path, repo: Path, before: dict[str, str]) -> tuple[str, str] | None:
    """The post-pin checks through the new link, in order; ``(name, detail)`` of the first failing, or None."""
    if _run([link, "--help"], repo).returncode != 0:
        return "help", "gov --help failed"
    if _run([link, "launch", "--help"], repo).returncode != 0:
        return "launch", "gov launch --help failed"
    found = _run([link, "retrieve", QUESTION, "--json"], repo)
    try:
        facets = json.loads(found.stdout)["result"]["facets"]
        both = found.returncode == 0 and all(facets[k]["available"] is True for k in ("lexical", "semantic"))
    except (ValueError, KeyError, TypeError):
        both = False
    if not both:
        return "search", "a search of the memory store failed or lost a facet"
    hook = _hooks(pin, repo)
    if hook:
        return "hooks", hook
    doctor = _parts(_run([link, "doctor", "--json"], repo).stdout)
    if doctor is None:
        return "doctor", "gov doctor gave no readable report"
    newly = sorted(_unhealthy(doctor) - _unhealthy(before))
    if newly:
        return "doctor", f"newly unhealthy: {', '.join(newly)}"
    return None


def _switch(link: Path, target: Path) -> None:
    """One rename of the link onto ``target``'s ``bin/gov``."""
    staged = link.with_name(link.name + ".new")
    if staged.is_symlink() or staged.exists():
        staged.unlink()
    os.symlink(target, staged)
    os.replace(staged, link)


def _blob(repo: Path, ref: str, rel: str) -> bytes | None:
    done = subprocess.run(["git", "-C", str(repo), "cat-file", "blob", f"{ref}:{rel}"], capture_output=True)
    return done.stdout if done.returncode == 0 else None


def _read_json(repo: Path, tag: str, rel: str) -> dict:
    try:
        value = json.loads(_show(repo, tag, rel) or "")
    except ValueError:
        return {}
    return value if isinstance(value, dict) else {}


def _pushed(push, text: str) -> str | None:
    """The push command run once, detached; the error if it could not be started."""
    if not push:
        return None
    from gov.dispatch import runtime

    try:
        runtime.push(push, text)
    except (OSError, ValueError) as exc:
        return f"{type(exc).__name__}: {exc}"
    return None


def _wheel_twice(repo: Path, commit: str) -> tuple[str, Path, Path] | None:
    """The wheel of ``commit`` built twice: ``(sha256, kept file, its folder)`` when both builds agree, else None."""
    folder = Path(tempfile.mkdtemp(prefix="gov-repin-"))
    try:
        (folder / "1").mkdir()
        (folder / "2").mkdir()
        first, second = release._wheel(repo, commit, keep=folder / "1"), release._wheel(repo, commit, keep=folder / "2")
    except release.ReleaseError:
        shutil.rmtree(folder, ignore_errors=True)
        return None
    if first["sha256"] != second["sha256"]:
        shutil.rmtree(folder, ignore_errors=True)
        return None
    return first["sha256"], Path(first["path"]), folder


def repin(repo, version: str, home, *, push=None, check=None) -> dict:
    """Make the machine's ``gov`` the release ``version``'s; see the module text. Raises nothing for a stop:
    ``{"status": "ok" | "rolled_back" | "stopped", "version", "commit", "step", "check", "pin", "old_pin",
    "push_text"}``."""
    repo, home = Path(repo), Path(home)
    share, bin_dir, tag = _share(home), home / BIN_REL, f"v{version}"
    link = bin_dir / "gov"
    answer = {"status": "stopped", "version": version, "commit": None, "step": None, "check": None, "pin": None,
              "old_pin": None, "push_text": None}
    made: list[Path] = []
    scratch: list[Path] = []
    state = {"switched": False}

    def stop(step: str, reason: str) -> dict:
        for folder in reversed(made):
            shutil.rmtree(folder, ignore_errors=True)
        answer.update(status="stopped", step=step, reason=reason)
        return answer

    try:
        if version in burned(home):
            return stop("burned", f"release {version} is burned: it is never pinned")
        live = Path(os.path.realpath(link)) if link.is_symlink() or link.exists() else None
        if live is None or live.parent.name != "bin" or not live.parent.parent.name.startswith("pin-"):
            return stop("live", f"{link} does not point into a pin")
        old_pin = live.parent.parent
        answer["old_pin"] = str(old_pin)
        # R. the tag, its record and C
        if _git(repo, "cat-file", "-t", f"refs/tags/{tag}").stdout.strip() != "tag":
            return stop("tag", f"{tag} is not an annotated tag")
        record = _git(repo, "rev-parse", f"{tag}^{{commit}}").stdout.strip()
        parents = _git(repo, "rev-list", "--parents", "-n", "1", record).stdout.split()[1:]
        if len(parents) != 1:
            return stop("tag", f"the commit of {tag} does not have C as its only parent")
        c = parents[0]
        c12 = c[:12]
        answer["commit"] = c
        folder_rel = f"{release.RELEASES_REL}/{version}"
        changed = [line for line in _git(repo, "diff", "--name-only", c, record).stdout.splitlines() if line]
        outside = [path for path in changed if not path.startswith(folder_rel + "/")]
        if outside or not changed:
            return stop("record", f"between C ({c12}) and {tag} more than the record changed: {', '.join(outside[:10])}")
        data = _blob(repo, record, f"{folder_rel}/{release.MANIFEST_NAME}")
        stated = _blob(repo, record, f"{folder_rel}/{release.HASH_NAME}")
        stated_hash = (stated.decode("utf-8", "replace").split() or [""])[0] if stated is not None else None
        if data is None or stated_hash is None or hashlib.sha256(data).hexdigest() != stated_hash:
            return stop("manifest", f"{release.MANIFEST_NAME} does not match the sha256 in {release.HASH_NAME}")
        try:
            manifest = json.loads(data)
            wheel_info = manifest.get("wheel") or {}
            cli = manifest.get("cli_version")
            named = (manifest.get("version") == version and manifest.get("commit") == c
                     and isinstance(cli, str) and wheel_info.get("name") == f"gov-{cli}-py3-none-any.whl"
                     and bool(_SHA.fullmatch(str(wheel_info.get("sha256")))))
        except (ValueError, AttributeError):
            named = False
        if not named:
            return stop("manifest", f"the manifest does not name version {version}, commit {c} and a wheel with its sha256")
        sha = wheel_info["sha256"]
        kind = _read_json(repo, record, f"{folder_rel}/kind.json")
        released = "approved" if kind.get("kind") == "approved" else "patch"
        # A. the wheel of C, built twice, checked against the record
        built = _wheel_twice(repo, c)
        if built is None:
            return stop("wheel", "the wheel of C could not be built twice to the same bytes")
        scratch.append(built[2])
        if built[0] != sha:
            return stop("wheel", f"the wheel built from C ({built[0][:16]}) is not the record's ({sha[:16]})")
        pin = share / f"pin-{c12}"
        answer["pin"] = str(pin)
        if pin.exists():
            return stop("exists", f"{pin} already exists (an earlier run): remove it first if it is not live")
        wheels = share / "wheels" / c12
        wheel_file = wheels / built[1].name
        for folder in (share / "wheels", wheels):  # made now, so removed on a stop; never one that was there
            if not folder.exists():
                made.append(folder)
        wheels.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(built[1], wheel_file)
        made.append(pin)
        made_venv = _run([sys.executable, "-m", "venv", "--system-site-packages", pin], repo, timeout=600)
        installed = _run([pin / "bin" / "python", "-m", "pip", "install", "-q", "--no-deps", "--no-index", wheel_file],
                         repo, timeout=600) if made_venv.returncode == 0 else made_venv
        said = _run([pin / "bin" / "gov", "--version"], repo) if installed.returncode == 0 else installed
        said_line = ((said.stdout or "") + (said.stderr or "")).strip().splitlines()[:1]
        if said.returncode != 0 or version not in (said_line[0] if said_line else ""):
            return stop("version", f"the new pin's gov --version says {said_line[0] if said_line else 'nothing'!r}, "
                                   f"not {version}")
        # before the switch: the reading the doctor check compares with
        before: dict[str, str] = {}
        if check is None:
            before_parts = _parts(_run([link, "doctor", "--json"], repo).stdout)
            if before_parts is None:
                return stop("doctor", "gov doctor through the live link gave no readable report before the switch")
            before = before_parts
        # D. the switch (one rename), then the checks through the link
        _switch(link, pin / "bin" / "gov")
        state["switched"] = True
        failing = None
        if os.path.realpath(link) != os.path.realpath(pin / "bin" / "gov"):
            failing = ("link", f"{link} does not name {pin.name}")
        else:
            # the new entry is in the working tree before the checks, so gov doctor's tools part reads the new pin
            failing = _write_registry(repo, version, cli, c12, sha, old_pin.name, pin, state)
        if failing is not None:
            pass
        elif check is not None:
            name = check(link)
            failing = (str(name), f"the check {name} failed") if name else None
        else:
            failing = _post_pin(link, pin, repo, before)
        if failing is None:
            # E. the registry entry, committed as the orchestrator under the owner's standing yes
            failing = _commit_registry(repo, version, c12, old_pin.name, state)
        if failing is not None:
            _restore_registry(repo, state)
            made.clear()
            return _roll_back(answer, link, share, home, push, failing, released)
        gates_json = _read_json(repo, record, f"{folder_rel}/gates.json")
        fixes = patch.count_fixes(repo, kind["from"], c) if isinstance(kind.get("from"), str) else 0
        head = (gates_json.get("suite") or {}).get("head") or c
        verdict = (gates_json.get("proving") or {}).get("verdict") or "unknown"
        text = push_text(version, fixes, head, verdict, released)
        _write_json(share / "repin.json", {"status": "ok", "version": version, "commit": c, "pin": str(pin),
                                          "old_pin": str(old_pin), "check": None, "at": _now()})
        (share / "rollback.sh").write_text(rollback_script(old_pin, home, version), encoding="utf-8")
        (share / "rollback.sh").chmod(0o755)
        answer.update(status="ok", push_text=text)
        error = _pushed(push, text)
        if error:
            answer["push_error"] = error
        made.clear()
        return answer
    except Exception as exc:  # before the switch: a stop, nothing switched; after it: the link goes back
        if state["switched"]:
            _restore_registry(repo, state)
            made.clear()
            return _roll_back(answer, link, share, home, push, ("error", f"{type(exc).__name__}: {exc}"), released)
        return stop("error", f"{type(exc).__name__}: {exc}")
    finally:
        for folder in scratch:
            shutil.rmtree(folder, ignore_errors=True)


def _roll_back(answer: dict, link: Path, share: Path, home: Path, push, failing: tuple[str, str], kind: str) -> dict:
    """The link back onto the old pin by one rename, the release burned, ``repin.json`` and the failure push."""
    version, old_pin = answer["version"], Path(answer["old_pin"])
    _switch(link, old_pin / "bin" / "gov")
    _burn(home, version)
    text = failure_text(version, failing[0], kind)
    _write_json(share / "repin.json", {"status": "rolled_back", "version": version, "commit": answer["commit"],
                                      "pin": answer["pin"], "old_pin": answer["old_pin"], "check": failing[0],
                                      "detail": failing[1], "at": _now()})
    answer.update(status="rolled_back", check=failing[0], detail=failing[1], push_text=text)
    error = _pushed(push, text)
    if error:
        answer["push_error"] = error
    return answer


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def _write_registry(repo: Path, version: str, cli: str, c12: str, sha: str, old_name: str, pin: Path,
                    state: dict) -> tuple[str, str] | None:
    """Write the registry's new gov entry into the working tree (not committed), keeping the original bytes."""
    try:
        decision = _decision(repo)
        script = hashlib.sha256((pin / "bin" / "gov").read_bytes()).hexdigest()
        path = repo / REGISTRY_REL
        original = path.read_bytes()
        state["registry_original"] = original
        state["decision"] = decision
        path.write_text(_registry(original.decode("utf-8"), version, cli, c12, sha, old_name, script, decision),
                        encoding="utf-8")
    except (OSError, ValueError) as exc:
        return "registry", f"the registry entry could not be written: {exc}"
    return None


def _restore_registry(repo: Path, state: dict) -> None:
    """Put the original registry bytes back and unstage the file, so the working tree and HEAD read as before."""
    original = state.pop("registry_original", None)
    if original is None:
        return
    try:
        _git(repo, "reset", "-q", "--", REGISTRY_REL)
    except Exception:
        pass
    try:
        (repo / REGISTRY_REL).write_bytes(original)
    except OSError:
        pass


def _commit_registry(repo: Path, version: str, c12: str, old_name: str, state: dict) -> tuple[str, str] | None:
    """Commit the written registry entry alone; ``(check, detail)`` when that cannot be done."""
    decision = state["decision"]
    message = (f"Re-pin from release {version}: gov from the release's wheel (tag v{version}, commit {c12})\n\n"
               f"The wheel built twice from {c12} equals the release record's sha256; {old_name} kept for the "
               f"rollback.\n\nRole: orchestrator\nDecided-by: owner (standing, {decision})\nTask: release\n")
    done = _git(repo, "-c", "commit.gpgSign=false", "commit", "-q", "-F", "-", "--", REGISTRY_REL, stdin=message)
    if done.returncode:
        return "registry", f"the registry commit failed: {(done.stderr or done.stdout).strip()[:200]}"
    state.pop("registry_original", None)
    return None
