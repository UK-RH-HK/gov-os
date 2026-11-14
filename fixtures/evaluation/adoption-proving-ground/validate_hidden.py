"""The automatic check of W2-81's hidden half (W2-93; DEC-1010 item 4, DEC-1143 (4) C6, DEC-1144 (6)).

    python3 fixtures/evaluation/adoption-proving-ground/validate_hidden.py --sets-root <root> [--seed <n>]

The hidden half is read from ``<root>/fixtures/evaluation/adoption-proving-ground/hidden/`` and nowhere else: one
``<repository>.yaml`` for each of the six synthetic repositories and ``variants.yaml``. The check builds the six
repositories with W2-81's own builders (the hidden variants applied) in a fresh temporary folder, removes that folder
when it ends, and proves, on the built copy:

- the form and count of the questions (at least 10 per repository, every field, unique ids);
- every gold source's text is at the built HEAD, and every fact a gold answer names exists (the gold answer is held);
- every forbidden ("must not cite") citation names a file at the built HEAD;
- the variants build, and every kind of planted problem the visible builders do not plant in a repository has at least
  one hidden variant there (and each of the seven kinds has one where the visible builders lack it); the clean twin
  takes none.

It prints counts and ids only: never a question, an answer, a template, a fact's value, a path's content or a secret's
value. It fails closed: a file it cannot read, a symbolic link, an entry it does not expect, any exception ends as a
``refused:`` line, never a traceback, and every refusal exits 2. It writes nothing outside its own temporary folder,
reads W2-81's modules from the checkout it sits in (read-only, no bytecode written) and nothing of the hidden half
beyond the eight files above.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True  # importing W2-81's modules never writes a __pycache__ in the repository

CHECKOUT = Path(__file__).resolve().parents[3]
SUITE = CHECKOUT / "tests" / "acceptance" / "W2-81"
sys.path.insert(0, str(SUITE))

HIDDEN_UNDER_SETS_ROOT = "fixtures/evaluation/adoption-proving-ground/hidden"
NEEDED = 10          # hidden questions per repository (W2-93's first KPI line)
BUILD_LARGE = 4096   # the built copy's large files: small, the check reads no size
MAX_BYTES = 8 * 1024 * 1024
SAFE = re.compile(r"^[A-Za-z0-9_.-]{1,40}$")
QUESTION_FIELDS = ("id", "category", "question", "gold_answer")


class _Unreadable(Exception):
    """A hidden file that cannot be read; ``reason`` holds a fixed phrase, never the file's content."""

    def __init__(self, reason):
        super().__init__(reason)
        self.reason = reason


def _name(text):
    """A file name as it may be printed: plain characters only, bounded."""
    return re.sub(r"[^A-Za-z0-9_.+@ -]", "?", str(text))[:60]


def _ident(value):
    """A variant's or question's id as it may be printed (plain, short), else ``?``."""
    return str(value) if isinstance(value, (str, int)) and not isinstance(value, bool) \
        and SAFE.match(str(value)) else "?"


def _read_yaml(path):
    """A hidden file's YAML, read strictly: never through a symbolic link, only a regular file, bounded, UTF-8."""
    import yaml

    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, "rb") as handle:
            if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
                raise _Unreadable("is not a regular file")
            raw = handle.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise _Unreadable("is too large")
        return yaml.safe_load(raw.decode("utf-8"))
    except _Unreadable:
        raise
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        raise _Unreadable("cannot be read") from None


def _entries(folder, expected, refuse):
    """The hidden folder's files by name: every entry other than the seven expected files is refused by its name."""
    found = {}
    with os.scandir(folder) as scan:
        for entry in sorted(scan, key=lambda e: e.name):
            label = _name(entry.name)
            if entry.is_symlink():
                refuse(label, "is a symbolic link")
            elif entry.is_dir(follow_symlinks=False):
                refuse(label, "is a folder: the hidden half holds only its eight files")
            elif entry.name not in expected:
                refuse(label, "is not part of the hidden half (the six question files and variants.yaml)")
            elif not entry.is_file(follow_symlinks=False):
                refuse(label, "is not a regular file")
            else:
                found[entry.name] = entry.path
    return found


def _check_questions(repository, data, refuse):
    """S1: the form and the fields of one repository's question set. Returns (count, the well-formed questions)."""
    from w2_81_questions import FORM

    name = f"{repository}.yaml"
    if not isinstance(data, dict) or data.get("form") != FORM or not isinstance(data.get("questions"), list):
        refuse(name, f"is not of the form {FORM}")
        return None, []
    if data.get("repository") != repository:
        refuse(name, "names another repository")
        return None, []
    item_id = re.compile(rf"^{re.escape(repository)}-h\d{{2,}}$")
    seen, good = set(), []
    for number, item in enumerate(data["questions"], 1):
        place = f"{repository} question #{number}"
        if not isinstance(item, dict):
            refuse(place, "is not a mapping")
            continue
        raw = item.get("id")
        label = raw if isinstance(raw, str) and SAFE.match(raw) else place
        problems = []
        for key in QUESTION_FIELDS:
            if key not in item:
                problems.append(f"missing field {key}")
            elif not isinstance(item[key], str) or not item[key].strip():
                problems.append(f"field {key} has the wrong type or is empty")
        if isinstance(raw, str) and raw.strip():
            if not item_id.match(raw):
                problems.append(f"the id is not {repository}-h<nn>")
            elif raw in seen:
                problems.append("the id is given twice")
            seen.add(raw)
        if "sources" not in item:
            problems.append("missing field sources")
        elif not isinstance(item["sources"], list) or not item["sources"]:
            problems.append("field sources has the wrong type or is empty")
        elif not all(isinstance(s, dict) and all(isinstance(s.get(k), str) and s[k].strip() for k in ("path", "holds"))
                     for s in item["sources"]):
            problems.append("a source is not a mapping of path and holds")
        # ``forbidden`` may be left out, as the visible half and W2-81's resolver leave it out where nothing is planted
        # (the clean twin's questions): absent means none. When it is there it is a list of paths.
        if "forbidden" in item and (not isinstance(item["forbidden"], list)
                                    or not all(isinstance(f, str) and f.strip() for f in item["forbidden"])):
            problems.append("field forbidden has the wrong type")
        for problem in problems:
            refuse(label, problem)
        if not problems:
            good.append(item)
    if len(data["questions"]) < NEEDED:
        refuse(repository, f"{len(data['questions'])} hidden questions, at least {NEEDED} needed")
    return len(data["questions"]), good


def _check_variants(data, refuse):
    """S2, the file's form: ``variants:`` a list of mappings with unique ids. Returns the list, or None."""
    if not isinstance(data, dict) or not isinstance(data.get("variants"), list):
        refuse("variants.yaml", "holds no list `variants`")
        return None
    clean, seen = True, set()
    for number, variant in enumerate(data["variants"], 1):
        if not isinstance(variant, dict):
            refuse(f"hidden variant #{number} (?)", "is not a mapping")
            clean = False
            continue
        raw = variant.get("id")
        if not isinstance(raw, (str, int)) or isinstance(raw, bool) or not str(raw).strip():
            refuse(f"hidden variant #{number} (?)", "has no id")
            clean = False
        elif str(raw) in seen:
            refuse(f"hidden variant #{number} ({_ident(raw)})", "the id is given twice")
            clean = False
        else:
            seen.add(str(raw))
    return data["variants"] if clean else None


def _scratch():
    """A fresh temporary folder under $TMPDIR, outside this repository and outside any git work tree."""
    import w2_81_git as gitlib

    folder = Path(tempfile.mkdtemp(prefix="validate-hidden-"))
    try:
        gitlib.outside_this_repository(folder)
        inside = subprocess.run(["git", "-C", str(folder), "rev-parse", "--show-toplevel"], capture_output=True,
                                text=True, env=gitlib.git_env(folder))
        if inside.returncode == 0:
            raise _Unreadable("the temporary folder lies in a git work tree")
    except BaseException:
        shutil.rmtree(folder, ignore_errors=True)
        raise
    return folder


def _planted_kinds(built):
    """Repository -> the kinds the visible builders plant there (the manifest's entries that are not hidden)."""
    return {name: {e["kind"] for e in b.manifest["planted"] if not e.get("hidden")} for name, b in built.items()}


def _number_of(refused):
    match = re.search(r"#(\d+)", str(refused))
    return int(match.group(1)) if match else None


def _resolve_all(repositories, built, good, refuse):
    """S4, S5: each question resolved on the built copy, one by one, so each failure names its own id."""
    import w2_81_git as gitlib
    import w2_81_questions as questions

    for repository in repositories:
        copy, items = built[repository], good.get(repository, [])
        files = gitlib.tree(copy.root, copy.manifest["head"])
        for item in items:
            qid = item["id"]
            try:
                resolved = questions.resolve({"questions": [item]}, copy.manifest, copy.root, "hidden")
            except questions.QuestionError as refused:
                said = str(refused)
                refuse(qid, said[len(qid) + 2:] if said.startswith(f"{qid}: ") and len(said) < 200
                       else "cannot be resolved on the built copy")
                continue
            if any(path not in files for path in resolved[0].forbidden):
                refuse(qid, "a forbidden citation names no file of the built repository")


def _kind_checks(variants, visible, planted, kinds, core, refuse):
    """S2, the kinds: what the hidden variants must cover where the visible builders plant nothing."""
    counts = {}
    for variant in variants:
        if isinstance(variant, dict) and isinstance(variant.get("repository"), str) \
                and isinstance(variant.get("kind"), str):
            key = (variant["repository"], variant["kind"])
            counts[key] = counts.get(key, 0) + 1
    for repository in planted:
        for kind in core:
            if kind not in visible[repository] and not counts.get((repository, kind)):
                refuse(repository, f"no hidden variant of kind {kind}")
    for kind in kinds:
        if not any(counts.get((repository, kind)) for repository in planted if kind not in visible[repository]):
            refuse(f"kind {kind}", "no hidden variant where the visible builders do not plant it")
    return counts


def validate(sets_root, seed):
    """The check: (lines to print, exit code). Refusals are lines ``refused: ...``; a valid half prints its counts."""
    import w2_81_build as build
    import w2_81_manifest as manifest_form

    repositories, planted = (*build.SHAPES, build.CLEAN), build.SHAPES
    kinds, core = manifest_form.KINDS + manifest_form.LEGACY_KINDS, manifest_form.KINDS
    refusals = []

    def refuse(label, reason):
        refusals.append(f"refused: {label}: {reason}")

    folder = Path(sets_root).expanduser() / HIDDEN_UNDER_SETS_ROOT
    if folder.is_symlink():
        return [f"refused: {HIDDEN_UNDER_SETS_ROOT}: is a symbolic link"], 2
    if not folder.is_dir():
        return [f"refused: no hidden half under the sets root: {HIDDEN_UNDER_SETS_ROOT}"], 2

    expected = {f"{r}.yaml" for r in repositories} | {"variants.yaml"}
    try:
        files = _entries(folder, expected, refuse)
    except OSError:
        return [*refusals, "refused: the hidden folder: cannot be listed"], 2

    counts, good, loaded = {}, {}, {}
    for repository in repositories:
        name = f"{repository}.yaml"
        if name not in files:
            if not any(r.startswith(f"refused: {name}:") for r in refusals):
                refuse(repository, "no question file")
            continue
        try:
            loaded[repository] = _read_yaml(files[name])
        except _Unreadable as unreadable:
            refuse(name, unreadable.reason)
        except Exception as exc:  # noqa: BLE001 - whatever stops the read is named by its class only
            refuse(name, type(exc).__name__)
    for repository, data in loaded.items():
        try:
            counts[repository], good[repository] = _check_questions(repository, data, refuse)
        except Exception as exc:  # noqa: BLE001
            refuse(f"{repository}.yaml", type(exc).__name__)

    variants = None
    if "variants.yaml" not in files:
        if not any(r.startswith("refused: variants.yaml:") for r in refusals):
            refuse("variants.yaml", "missing")
    else:
        try:
            variants = _check_variants(_read_yaml(files["variants.yaml"]), refuse)
        except _Unreadable as unreadable:
            refuse("variants.yaml", unreadable.reason)
        except Exception as exc:  # noqa: BLE001
            refuse("variants.yaml", type(exc).__name__)

    # a variant in the clean twin is refused naming its number and id (S2 (c))
    for number, variant in enumerate(variants or [], 1):
        if isinstance(variant, dict) and variant.get("repository") == build.CLEAN:
            refuse(f"hidden variant #{number} ({_ident(variant.get('id'))})",
                   f"the clean twin {build.CLEAN} takes no variant")

    try:
        scratch = _scratch()
    except _Unreadable as unreadable:
        return [*refusals, f"refused: the check: {unreadable.reason}"], 2
    held, built, visible, kind_counts = [], None, None, {}
    try:
        if variants is not None:
            try:
                built = build.build_all(scratch / "hidden-built", seed, BUILD_LARGE, variants=variants)
            except build.VariantError as refused:
                number = _number_of(refused)
                variant = variants[number - 1] if number and number <= len(variants) else None
                refuse(f"hidden variant #{number} ({_ident(variant.get('id') if isinstance(variant, dict) else None)})"
                       if number else "hidden variants", "cannot be built")
            if built is not None:
                visible = _planted_kinds(built)
            else:
                visible = _planted_kinds(build.build_all(scratch / "visible-built", seed, BUILD_LARGE))
            for b in (built or {}).values():
                held += list(b.secrets)
            kind_counts = _kind_checks(variants, visible, planted, kinds, core, refuse)
        if built is not None:
            _resolve_all(repositories, built, good, refuse)
        elif any(good.values()):
            refuse("questions", "not checked on a built copy: the hidden variants could not be built or read")
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    if refusals:
        lines, code = refusals, 2
    else:
        lines = [f"{r}: {counts[r]} hidden questions" for r in repositories]
        for repository in planted:
            lacking = [k for k in kinds if k not in visible[repository]]
            lines.append(f"{repository}: hidden variants " + (", ".join(f"{k}={kind_counts.get((repository, k), 0)}"
                                                                    for k in lacking) or "none"))
        lines.append(f"valid: {sum(counts.values())} hidden questions in {len(repositories)} repositories, "
                     f"{len(variants)} hidden variants (seed {seed})")
        code = 0
    if any(h.found_in("\n".join(lines)) for h in held):  # belt and braces: no secret's value in the output
        return ["refused: the check: the output would hold a secret's value"], 2
    return lines, code


def main(argv=None):
    parser = argparse.ArgumentParser(prog="validate_hidden.py", description="the check of W2-81's hidden half")
    parser.add_argument("--sets-root", dest="sets_root", required=True)
    parser.add_argument("--seed", type=int, default=None)
    options = parser.parse_args(argv)
    try:
        from w2_81_words import DEFAULT_SEED

        lines, code = validate(options.sets_root, DEFAULT_SEED if options.seed is None else options.seed)
    except Exception as exc:  # noqa: BLE001 - never a traceback, never an exception's message
        lines, code = [f"refused: the check: {type(exc).__name__}"], 2
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    sys.exit(main())
