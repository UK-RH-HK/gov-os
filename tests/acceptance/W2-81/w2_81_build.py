"""The five builders of the W2-81 proving ground, and the clean variant (DEC-941, DEC-936 item 3.6).

``build_all(run_folder, seed, large_size)`` builds, under ``<run>/repos/``, six
git repositories of their own, file by file and commit by commit, and writes
each one's manifest under ``<run>/manifests/`` (outside every repository):

- ``python-app``: a Python application with drifted specs and plans;
- ``rust-workspace``: a Rust workspace of three crates;
- ``typescript-monorepo``: a TypeScript monorepo of three packages;
- ``legacy-docs``: legacy documents and large files (generated here, never tracked in this repository);
- ``secret-history``: a Go service with a secret in its history;
- ``python-app-clean``: the Python shape with nothing planted, its controls only.

Names, places, wording, numbers, authors and dates come from the seed
(``w2_81_words``). The secrets are built from parts (``w2_81_secret``) and
returned in memory only, never written in a manifest.
"""

from __future__ import annotations

import random
import re
import shutil
import struct
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path

import w2_81_manifest as manifest_form
from w2_81_git import Repo, blob, tree
from w2_81_secret import FORMS, make_secret
from w2_81_words import (CURRENT_WORDS, DEFAULT_SEED, HELPERS, LEGACY_FOLDERS, OLD_WORDS, PRODUCTS, REVIEW_WORDS,
                         STATUS_LINES, TOPICS, Draw)

SELF_TEST_LARGE = 300_000          # bytes: the self-tests stay fast
REAL_RUN_LARGE = 48 * 1024 * 1024  # bytes: the real run's large files


def fill(template, **values):
    """``<<name>>`` replaced by its value: templates of Rust, TypeScript and Go keep their braces as they are."""
    for key, value in values.items():
        template = template.replace(f"<<{key}>>", str(value))
    assert "<<" not in template, template
    return template


@dataclass
class Built:
    name: str
    root: Path
    manifest: dict
    manifest_path: Path
    secrets: list = field(default_factory=list)  # Held values, in memory only; never written


class _Build:
    """One repository being built: its folder, its seeded stream, its manifest."""

    def __init__(self, root, seed, name, shape, clean=False):
        self.repo = Repo(root)
        self.draw = Draw(seed, name)
        self.manifest = manifest_form.Manifest(seed, name, shape, clean=clean)
        self.secrets = []

    def commit(self, message, files=(), remove=()):
        for rel, text in dict(files).items():
            self.repo.write(rel, text)
        for rel in remove:
            self.repo.remove(rel)
        return self.repo.commit(message, self.draw.author(), self.draw.tick())

    def facts(self, **named):
        """The seeded names and paths the question sets refer to (no secret, no hidden material)."""
        self.manifest.data["facts"] = {key: value for key, value in named.items() if value is not None}

    def finish(self, run_folder):
        data = self.manifest.close([c for c, _ in self.repo.commits])
        path = manifest_form.write(data, run_folder, self.repo.root)
        return Built(data["repository"], self.repo.root, data, path, self.secrets)


def _spec(title, status, review_word, reviewed, lines, note=""):
    body = "\n".join(f"- {line}" for line in lines)
    return f"# {title}\n\n{status}\n{review_word}: {reviewed}\n\n## Values\n\n{body}\n{note}"


# --------------------------------------------------------------------------
# 1. The Python application with drifted specs and plans
# --------------------------------------------------------------------------

def build_python(root, seed, run_folder, planted=True, name="python-app"):
    b = _Build(root, seed, name, "python-application", clean=not planted)
    d = b.draw
    pkg, topic = d.pick(PRODUCTS), d.pick(TOPICS)
    other = d.pick([t for t in TOPICS if t != topic])
    helper = d.pick(HELPERS)
    specdir = d.pick(("docs/specs", "specs", "docs/design"))
    plandir = d.pick(("docs/plans", "plans", "docs/roadmap"))
    const = d.pick(("TIMEOUT_SECONDS", "UPSTREAM_TIMEOUT", "REQUEST_TIMEOUT_S"))
    label = d.pick(("Upstream timeout (seconds)", "Request timeout, in seconds", "Timeout for upstream calls (s)"))
    old_v = d.pick((15, 20, 30))
    new_v = old_v + d.pick((10, 15, 25))
    status, review = d.pick(STATUS_LINES), d.pick(REVIEW_WORDS)
    old_word, cur_word, folder = d.pick(OLD_WORDS), d.pick(CURRENT_WORDS), d.pick(LEGACY_FOLDERS)
    adapter = d.pick(("adapter", "client", "gateway", "bridge"))
    exporter = d.pick(("exporter", "formatter", "renderer", "summary"))
    plan = d.pick(("rollout-plan", "delivery-plan", "launch-plan", "cutover-plan"))
    code_len = d.number(6, 12)
    src = f"src/{pkg}"
    live_mod = f"{old_word}_{adapter}" if planted else adapter
    dead_mod = f"{cur_word}_{exporter}"
    codes_mod = f"{other}_codes"
    stale, governing = f"{specdir}/{topic}.md", f"{specdir}/{topic}-v2.md"
    control_spec = f"{specdir}/draft-{other}-codes.md"
    plan_old, plan_new = f"{plandir}/{plan}.md", f"{plandir}/{plan}-2.md"
    topic_code = f"{src}/{topic}.py"

    def topic_py(value, with_helper):
        head = f"from {pkg}.{helper} import {helper}_value\n\n" if with_helper else ""
        use = f"{helper}_value(amount)" if with_helper else "round(amount, 2)"
        return (f'"""The {topic} service: calls upstream and records the result."""\n\n{head}'
                f"{const} = {value}\n\n\ndef settle(amount):\n    return {use}\n\n\n"
                f"def timeout():\n    return {const}\n")

    def app_py():
        return (f'"""Entry point of {pkg}."""\n\nfrom {pkg} import {topic}, {live_mod}\n'
                f"from {pkg}.{folder} import {codes_mod}\n\n\ndef main():\n"
                f"    client = {live_mod}.connect(timeout={topic}.timeout())\n"
                f"    return client, {codes_mod}.CODE_LENGTH\n\n\nif __name__ == \"__main__\":\n    main()\n")

    first = b.commit("Initial layout of the service", {
        "README.md": f"# {pkg}\n\nThe {topic} service of {pkg}.\n\nRun it with `python -m {pkg}.app`.\n",
        "pyproject.toml": f'[project]\nname = "{pkg}"\nversion = "0.1.0"\nrequires-python = ">=3.10"\n',
        ".gitignore": "__pycache__/\n*.pyc\n.venv/\n",
        f"{src}/__init__.py": f'"""{pkg}."""\n',
        topic_code: topic_py(old_v, False),
        f"tests/test_{topic}.py": f"from {pkg} import {topic}\n\n\ndef test_settle_rounds():\n"
                                  f"    assert {topic}.settle(1.005) >= 1.0\n",
        stale if planted else governing: _spec(f"The {topic} service", status, review, d.day(), [f"{label}: {old_v}"]),
    })
    b.commit(f"Add the {helper} helper", {
        f"{src}/{helper}.py": f'"""The {helper} helper."""\n\n\ndef {helper}_value(amount):\n'
                              f"    return round(amount, 2)\n",
        f"tests/test_{helper}.py": f"from {pkg}.{helper} import {helper}_value\n\n\ndef test_{helper}_value():\n"
                                   f"    assert {helper}_value(2.5) == 2.5\n",
        topic_code: topic_py(old_v, True),
    })
    adapters = b.commit(f"Wire the upstream {adapter} and the {other} codes", {
        f"{src}/{live_mod}.py": f'"""The upstream {adapter}."""\n\n\ndef connect(timeout):\n'
                                f"    return {{'timeout': timeout}}\n",
        f"{src}/{folder}/__init__.py": "",
        f"{src}/{folder}/{codes_mod}.py": f'"""The {other} codes, still read by the service."""\n\n'
                                          f"CODE_LENGTH = {code_len}\n",
        f"{src}/app.py": app_py(),
        control_spec: _spec(f"Draft: the {other} codes", "Status: Current", "Dated", d.old_day(),
                            [f"Code length: {code_len}"], "\nThis is the governing description of the codes.\n"),
        plan_old if planted else plan_new: f"# The {plan.replace('-', ' ')}\n\n1. Ship the {topic} service.\n"
                                           f"2. Move the {adapter} to the new upstream.\n",
    })
    b.manifest.control("current-spec-looks-old", [control_spec], why="it agrees with the code and nothing replaces "
                       "it; only its date and its name look old", code=f"{src}/{folder}/{codes_mod}.py",
                       claim_line=f"- Code length: {code_len}", code_line=f"CODE_LENGTH = {code_len}")
    b.manifest.control("live-file-in-legacy-folder", [f"{src}/{folder}/{codes_mod}.py"], why="the entry point "
                       "imports it", token=codes_mod, referenced_by=[f"{src}/app.py"])
    value = new_v if planted else old_v
    b.facts(product=pkg, topic=topic, other=other, const=const, app=f"{src}/app.py", topic_code=topic_code,
            topic_test=f"tests/test_{topic}.py", adapter=adapter, adapter_module=f"{src}/{live_mod}.py",
            codes_module=f"{src}/{folder}/{codes_mod}.py", control_spec=control_spec,
            code_len_line=f"- Code length: {code_len}", code_len_code=f"CODE_LENGTH = {code_len}",
            governing=governing, spec_line=f"- {label}: {value}", value_line=f"{const} = {value}",
            plan=plan_new, plan_title=plan.replace("-", " "), stale=stale if planted else None,
            plan_old=plan_old if planted else None, dead_module=f"{src}/{dead_mod}.py" if planted else None,
            run_line=f"python -m {pkg}.app")
    if not planted:
        b.commit(f"Note the {adapter} in the README", {"README.md": f"# {pkg}\n\nThe {topic} service of {pkg}.\n\nRun it with `python -m {pkg}.app`.\n\n"
                 f"Governing specs: `{governing}`, `{control_spec}`. Plan: `{plan_new}`.\n"})
        return b.finish(run_folder)
    dead = b.commit(f"Add the {cur_word} {exporter}", {
        f"{src}/{dead_mod}.py": f'"""The {cur_word} {exporter} of {topic} results."""\n\n'
                                f"{const} = {old_v}\n\n\ndef export(rows):\n    return [r for r in rows]\n"})
    b.manifest.plant("misleading-name", "live-under-old-name", [f"{src}/{live_mod}.py"], [adapters],
                     token=live_mod, referenced_by=[f"{src}/app.py"], live=True)
    b.manifest.plant("misleading-name", "dead-under-current-name", [f"{src}/{dead_mod}.py"], [dead],
                     token=dead_mod, referenced_by=[], live=False)
    raised = b.commit(f"Raise the {topic} timeout to {new_v} s", {
        topic_code: topic_py(new_v, True),
        governing: _spec(f"The {topic} service, version 2", status, review, d.day(), [f"{label}: {new_v}"],
                         f"\nThis version replaces `{stale}`.\n")})
    removed = b.commit(f"Inline the {helper} helper", {topic_code: topic_py(new_v, False)},
                       remove=[f"{src}/{helper}.py"])
    b.manifest.plant("orphaned-test", "module-removed", [f"tests/test_{helper}.py", f"{src}/{helper}.py"],
                     [removed], test=f"tests/test_{helper}.py", subject=f"{src}/{helper}.py",
                     definition=f"def {helper}_value", used_as=f"from {pkg}.{helper} import {helper}_value",
                     removed_in=removed[:12])
    successor = b.commit(f"Revise the {plan.replace('-', ' ')}", {
        plan_new: f"# The {plan.replace('-', ' ')}, second edition\n\nThis plan supersedes `{plan_old}`.\n\n"
                  f"1. Ship the {topic} service with the {new_v} s timeout.\n2. Retire the old upstream.\n"})
    b.manifest.plant("superseded-plan", "names-it", [plan_old, plan_new], [adapters, successor], plan=plan_old,
                     successor=plan_new, link="names-it")
    b.draw.tick()
    reviewed = d.day(-d.number(0, 3))
    touched = b.commit(f"Review the {topic} specs", {
        stale: _spec(f"The {topic} service", status, review, reviewed, [f"{label}: {old_v}"]),
        "README.md": f"# {pkg}\n\nThe {topic} service of {pkg}.\n\nRun it with `python -m {pkg}.app`.\n\nGoverning specs: `{governing}`, "
                     f"`{control_spec}`. Plan: `{plan_new}`.\n"})
    b.manifest.plant("stale-spec", "newer-version", [stale, governing], [first, raised, touched], stale=stale,
                     governing=governing, code=topic_code, status_line=status, reviewed=reviewed, review_line=f"{review}: {reviewed}",
                     claim_line=f"- {label}: {old_v}", governing_line=f"- {label}: {new_v}",
                     code_line=f"{const} = {new_v}", names=stale)
    return b.finish(run_folder)


# --------------------------------------------------------------------------
# 2. The Rust workspace of three crates
# --------------------------------------------------------------------------

_CRATE_TOML = '[package]\nname = "<<name>>"\nversion = "0.3.0"\nedition = "2021"\n\n[dependencies]\n<<deps>>'
_FRAME_LIB = """//! Framing of the <<topic>> stream.

pub const MAX_FRAME_BYTES: usize = <<value>>;

pub fn frame_len(payload: &[u8]) -> usize {
    payload.len().min(MAX_FRAME_BYTES)
}
<<extra>>"""
_REMOVED_FN = """
pub fn <<fn>>(payload: &[u8]) -> u32 {
    payload.iter().map(|b| *b as u32).sum()
}
"""


def build_rust(root, seed, run_folder, name="rust-workspace"):
    b = _Build(root, seed, name, "rust-workspace")
    d = b.draw
    product, topic = d.pick(PRODUCTS), d.pick(TOPICS)
    other = d.pick([t for t in TOPICS if t != topic])
    a, c2, c3 = d.sample(("framing", "store", "wire", "codec", "sched", "relay", "catalog"), 3)
    folder = d.pick(LEGACY_FOLDERS)
    fn = d.pick(("checksum", "digest", "parity", "tally"))
    old_v = d.pick((4096, 8192, 16384))
    new_v = old_v * d.pick((2, 4))
    status, review = d.pick(STATUS_LINES), d.pick(REVIEW_WORDS)
    rfcdir = d.pick(("docs/rfcs", "rfcs", "docs/rfc"))
    n_old = d.number(1, 4)
    n_new = n_old + d.number(3, 6)
    stale, governing = f"{rfcdir}/{n_old:04d}-{topic}-framing.md", f"{rfcdir}/{n_new:04d}-{topic}-framing-revised.md"
    control_spec = f"{rfcdir}/draft-0000-{other}-table.md"
    plandir = d.pick(("plans", "docs/plans", "planning", "docs/roadmap"))
    plan_id = d.pick(("roadmap", "release-plan", "migration-plan", "delivery-plan", "platform-plan", "stabilisation-plan"))
    plan_v1, plan_v2 = f"{plandir}/{plan_id}.v1.md", f"{plandir}/{plan_id}.v2.md"
    width = d.number(8, 40)
    crate = lambda word: f"{product}-{word}"  # noqa: E731
    ident = lambda word: f"{product}_{word}"  # noqa: E731
    lib_a = f"crates/{a}/src/lib.rs"
    table = f"{other}_table"
    test_rel = f"crates/{a}/tests/{fn}_test.rs"

    first = b.commit("Workspace with three crates", {
        "Cargo.toml": f'[workspace]\nmembers = ["crates/{a}", "crates/{c2}", "crates/{c3}"]\nresolver = "2"\n',
        ".gitignore": "/target\n",
        "README.md": f"# {product}\n\nA Rust workspace: `{a}`, `{c2}` and the `{c3}` binary.\n",
        f"crates/{a}/Cargo.toml": fill(_CRATE_TOML, name=crate(a), deps=""),
        lib_a: fill(_FRAME_LIB, topic=topic, value=old_v, extra=fill(_REMOVED_FN, fn=fn)),
        f"crates/{c2}/Cargo.toml": fill(_CRATE_TOML, name=crate(c2), deps=""),
        f"crates/{c2}/src/lib.rs": f"//! The {c2} crate.\n\nmod {folder};\n\npub use {folder}::{table};\n",
        f"crates/{c2}/src/{folder}/mod.rs": f"//! The {other} table, still read by the binary.\n\n"
                                            f"pub const RECORD_WIDTH: usize = {width};\n\n"
                                            f"pub fn {table}() -> usize {{\n    RECORD_WIDTH\n}}\n",
        f"crates/{c3}/Cargo.toml": fill(_CRATE_TOML, name=crate(c3),
                                        deps=f'{crate(a)} = {{ path = "../{a}" }}\n'
                                             f'{crate(c2)} = {{ path = "../{c2}" }}\n'),
        f"crates/{c3}/src/main.rs": f"fn main() {{\n    let n = {ident(a)}::frame_len(b\"hello\");\n"
                                    f"    let w = {ident(c2)}::{table}();\n    println!(\"{{}} {{}}\", n, w);\n}}\n",
        stale: _spec(f"RFC {n_old}: {topic} framing", status, review, d.day(), [f"Maximum frame: {old_v} bytes"]),
        control_spec: _spec(f"Draft RFC 0: the {other} table", "Status: Accepted", "Dated", d.old_day(),
                            [f"Record width: {width}"], "\nThe table's governing description.\n"),
    })
    b.manifest.control("current-spec-looks-old", [control_spec], why="it agrees with the code and nothing replaces "
                       "it; only its date and its name look old", code=f"crates/{c2}/src/{folder}/mod.rs",
                       claim_line=f"- Record width: {width}", code_line=f"RECORD_WIDTH: usize = {width}")
    b.manifest.control("live-file-in-legacy-folder", [f"crates/{c2}/src/{folder}/mod.rs"], why="its crate's "
                       "lib.rs declares it and the binary calls it", token=table,
                       referenced_by=[f"crates/{c2}/src/lib.rs", f"crates/{c3}/src/main.rs"])
    b.facts(product=product, topic=topic, other=other, crate_a=a, crate_store=c2, crate_bin=c3, lib_a=lib_a,
            bin_main=f"crates/{c3}/src/main.rs", store_lib=f"crates/{c2}/src/lib.rs",
            table_module=f"crates/{c2}/src/{folder}/mod.rs", table=table, control_spec=control_spec,
            width_line=f"- Record width: {width}", width_code=f"RECORD_WIDTH: usize = {width}",
            governing=governing, stale=stale, spec_line=f"- Maximum frame: {new_v} bytes",
            frame_code=f"MAX_FRAME_BYTES: usize = {new_v}", plan=plan_v2, plan_old=plan_v1, plan_id=plan_id,
            members_line=f'members = ["crates/{a}", "crates/{c2}", "crates/{c3}"]', fn=fn, orphan=test_rel)
    b.commit(f"Test the {fn}", {test_rel: f"use {ident(a)}::{fn};\n\n#[test]\nfn {fn}_of_bytes() {{\n"
                                          f"    assert_eq!({fn}(&[1, 2, 3]), 6);\n}}\n"})
    v1 = b.commit(f"The {plan_id.replace('-', ' ')}, version 1", {
        plan_v1: f"---\nplan: {plan_id}\nversion: 1\n---\n# {plan_id.replace('-', ' ').title()}\n\n"
                 f"- Q1: stabilise `{a}`.\n- Q2: ship `{c3}` 1.0.\n"})
    raised = b.commit(f"Raise the maximum frame to {new_v} bytes", {
        lib_a: fill(_FRAME_LIB, topic=topic, value=new_v, extra=fill(_REMOVED_FN, fn=fn)),
        governing: _spec(f"RFC {n_new}: {topic} framing, revised", status, review, d.day(),
                         [f"Maximum frame: {new_v} bytes"], f"\nReplaces RFC {n_old} (`{stale}`).\n")})
    removed = b.commit(f"Drop the {fn}: framing no longer needs it", {
        lib_a: fill(_FRAME_LIB, topic=topic, value=new_v, extra="")})
    b.manifest.plant("orphaned-test", "function-removed", [test_rel, lib_a], [removed], test=test_rel,
                     subject=f"{lib_a}::{fn}", definition=f"pub fn {fn}", used_as=f"use {ident(a)}::{fn};",
                     removed_in=removed[:12])
    v2 = b.commit(f"The {plan_id.replace('-', ' ')}, version 2", {
        plan_v2: f"---\nplan: {plan_id}\nversion: 2\nsupersedes: version 1\n---\n"
                 f"# {plan_id.replace('-', ' ').title()}\n\n- Q3: frames of {new_v} bytes.\n- Q4: `{c3}` 2.0.\n"})
    b.manifest.plant("superseded-plan", "by-version", [plan_v1, plan_v2], [v1, v2], plan=plan_v1, successor=plan_v2,
                     link="by-version", plan_id=plan_id, version=1)
    b.draw.tick()
    reviewed = d.day(-d.number(0, 3))
    touched = b.commit(f"Review RFC {n_old}", {
        stale: _spec(f"RFC {n_old}: {topic} framing", status, review, reviewed, [f"Maximum frame: {old_v} bytes"])})
    b.manifest.plant("stale-spec", "newer-rfc", [stale, governing], [first, raised, touched], stale=stale,
                     governing=governing, code=lib_a, status_line=status, reviewed=reviewed, review_line=f"{review}: {reviewed}",
                     claim_line=f"- Maximum frame: {old_v} bytes", governing_line=f"- Maximum frame: {new_v} bytes",
                     code_line=f"MAX_FRAME_BYTES: usize = {new_v}", names=f"RFC {n_old}")
    return b.finish(run_folder)


# --------------------------------------------------------------------------
# 3. The TypeScript monorepo of three packages (a token in a script's history)
# --------------------------------------------------------------------------

def build_typescript(root, seed, run_folder, name="typescript-monorepo"):
    b = _Build(root, seed, name, "typescript-monorepo")
    d = b.draw
    product, topic = d.pick(PRODUCTS), d.pick(TOPICS)
    other = d.pick([t for t in TOPICS if t != topic])
    p1, p2, p3 = d.sample(("api", "web", "shared", "ui", "sdk", "worker", "cli"), 3)
    helper = d.pick(HELPERS)
    old_word, cur_word, folder = d.pick(OLD_WORDS), d.pick(CURRENT_WORDS), d.pick(LEGACY_FOLDERS)
    adapter = d.pick(("client", "transport", "fetcher", "session"))
    exporter = d.pick(("exporter", "formatter", "printer", "serializer"))
    old_v = d.pick((20, 25, 50))
    new_v = old_v * d.pick((2, 4))
    status, review = d.pick(STATUS_LINES), d.pick(REVIEW_WORDS)
    adrdir = d.pick(("docs/adr", "docs/decisions", "adr"))
    n_old = d.number(2, 5)
    n_new = n_old + d.number(2, 7)
    stale, governing = f"{adrdir}/{n_old:04d}-{topic}-paging.md", f"{adrdir}/{n_new:04d}-{topic}-paging.md"
    control_spec = f"{adrdir}/draft-0001-{other}-records.md"
    width = d.number(16, 64)
    script = f"scripts/{d.pick(('publish', 'release', 'deploy'))}.sh"
    live_rel = f"packages/{p1}/src/{old_word}-{adapter}.ts"
    dead_rel = f"packages/{p3}/src/{exporter}.{cur_word}.ts"
    codes_rel = f"packages/{p1}/src/{folder}/{other}-records.ts"
    index2 = f"packages/{p2}/src/index.ts"
    helper_rel, test_rel = f"packages/{p2}/src/{helper}.ts", f"packages/{p2}/test/{helper}.test.ts"
    token = make_secret("forge-token", seed, name)
    b.secrets.append(token)

    def pkg(p):
        return (f'{{\n  "name": "@{product}/{p}",\n  "version": "1.2.0",\n  "main": "dist/index.js",\n'
                f'  "scripts": {{ "build": "tsc -p .", "test": "vitest run" }}\n}}\n')

    def index2_ts(value, with_helper):
        head = f'import {{ {helper} }} from "./{helper}";\n\n' if with_helper else ""
        use = f"{helper}(items)" if with_helper else "items"
        return (f"{head}export const PAGE_SIZE = {value};\n\nexport function page<T>(items: T[]): T[] {{\n"
                f"  return {use}.slice(0, PAGE_SIZE);\n}}\n")

    first = b.commit("Monorepo with three packages", {
        "package.json": f'{{\n  "name": "{product}",\n  "private": true,\n  "workspaces": ["packages/*"]\n}}\n',
        "tsconfig.base.json": '{\n  "compilerOptions": { "strict": true, "target": "ES2022", "module": "ESNext" }\n}\n',
        ".gitignore": "node_modules/\ndist/\n",
        "README.md": f"# {product}\n\nPackages: `{p1}`, `{p2}`, `{p3}`.\n",
        f"docs/plans/{p1}-release.md": f"# Releasing `{p1}`\n\n1. Publish `{p2}` first.\n2. Then `{p1}` and "
                                       f"`{p3}` together.\n",
        f"packages/{p1}/package.json": pkg(p1), f"packages/{p2}/package.json": pkg(p2),
        f"packages/{p3}/package.json": pkg(p3),
        index2: index2_ts(old_v, False),
        f"packages/{p3}/src/index.ts": f'export const name = "{p3}";\n',
        stale: _spec(f"ADR {n_old}: paging of {topic}", status, review, d.day(), [f"Page size: {old_v}"]),
    })
    secret_in = b.commit("Add the publish script", {
        script: token.line("#!/bin/sh\nset -eu\nexport GITHUB_TOKEN={value}\nnpm publish --workspaces\n")})
    wired = b.commit(f"The {p1} package: {adapter} and {other} records", {
        live_rel: f"export function connect(url: string) {{\n  return {{ url, open: true }};\n}}\n",
        codes_rel: f"export const RECORD_WIDTH = {width};\n",
        f"packages/{p1}/src/index.ts": f'import {{ connect }} from "./{old_word}-{adapter}";\n'
                                       f'import {{ RECORD_WIDTH }} from "./{folder}/{other}-records";\n\n'
                                       f"export const session = connect(\"https://{p1}.example.invalid\");\n"
                                       f"export const width = RECORD_WIDTH;\n",
        control_spec: _spec(f"Draft ADR 1: {other} records", "Status: Accepted", "Dated", d.old_day(),
                            [f"Record width: {width}"], "\nStill the governing description of the records.\n"),
    })
    b.manifest.control("current-spec-looks-old", [control_spec], why="it agrees with the code and nothing replaces "
                       "it; only its date and its name look old", code=codes_rel,
                       claim_line=f"- Record width: {width}", code_line=f"RECORD_WIDTH = {width}")
    b.manifest.control("live-file-in-legacy-folder", [codes_rel], why="its package's index imports it",
                       token=f"{folder}/{other}-records", referenced_by=[f"packages/{p1}/src/index.ts"])
    b.manifest.plant("misleading-name", "live-under-old-name", [live_rel], [wired], token=f"{old_word}-{adapter}",
                     referenced_by=[f"packages/{p1}/src/index.ts"], live=True)
    b.facts(product=product, topic=topic, other=other, p1=p1, p2=p2, p3=p3, paging=index2,
            page_code=f"PAGE_SIZE = {new_v}", governing=governing, stale=stale,
            spec_line=f"- Page size: {new_v}", script=script, records_module=codes_rel,
            width_line=f"- Record width: {width}", width_code=f"RECORD_WIDTH = {width}",
            control_spec=control_spec, client_module=live_rel, p1_index=f"packages/{p1}/src/index.ts",
            release_plan=f"docs/plans/{p1}-release.md", dead_module=dead_rel, orphan=test_rel,
            p1_package=f"packages/{p1}/package.json", p1_name=f"@{product}/{p1}")
    helped = b.commit(f"The {helper} helper and its test", {
        helper_rel: f"export function {helper}<T>(items: T[]): T[] {{\n  return [...items];\n}}\n",
        test_rel: f'import {{ {helper} }} from "../src/{helper}";\n\ntest("{helper} copies", () => {{\n'
                  f"  expect({helper}([1, 2])).toEqual([1, 2]);\n}});\n",
        index2: index2_ts(old_v, True)})
    dead = b.commit(f"Add the {cur_word} {exporter}", {
        dead_rel: f"// The {cur_word} {exporter} of {topic} pages.\nexport const PAGE_SIZE = {old_v};\n"
                  f"export function {exporter}Rows(rows: string[]): string {{\n  return rows.join(\"\\n\");\n}}\n"})
    b.manifest.plant("misleading-name", "dead-under-current-name", [dead_rel], [dead],
                     token=f"{exporter}.{cur_word}", referenced_by=[], live=False)
    cleaned = b.commit("Read the publish token from the environment", {
        script: '#!/bin/sh\nset -eu\n: "${GITHUB_TOKEN:?set GITHUB_TOKEN in the environment}"\n'
                "npm publish --workspaces\n"})
    b.manifest.plant("secret", "token-in-script", [script], [secret_in, cleaned], path=script,
                     added_in=secret_in[:12], removed_in=cleaned[:12], rule=FORMS["forge-token"]["rule"],
                     form="forge-token")
    raised = b.commit(f"Page {topic} by {new_v}", {
        index2: index2_ts(new_v, True),
        governing: _spec(f"ADR {n_new}: paging of {topic}", status, review, d.day(), [f"Page size: {new_v}"],
                         f"\nSupersedes ADR {n_old} (`{stale}`).\n")})
    removed = b.commit(f"Inline the {helper} helper", {index2: index2_ts(new_v, False)}, remove=[helper_rel])
    b.manifest.plant("orphaned-test", "file-removed", [test_rel, helper_rel], [helped, removed], test=test_rel,
                     subject=helper_rel, definition=f"export function {helper}", used_as=f'from "../src/{helper}"',
                     removed_in=removed[:12])
    b.draw.tick()
    reviewed = d.day(-d.number(0, 3))
    touched = b.commit(f"Review ADR {n_old}", {
        stale: _spec(f"ADR {n_old}: paging of {topic}", status, review, reviewed, [f"Page size: {old_v}"])})
    b.manifest.plant("stale-spec", "newer-adr", [stale, governing], [first, raised, touched], stale=stale,
                     governing=governing, code=index2, status_line=status, reviewed=reviewed, review_line=f"{review}: {reviewed}",
                     claim_line=f"- Page size: {old_v}", governing_line=f"- Page size: {new_v}",
                     code_line=f"PAGE_SIZE = {new_v}", names=f"ADR {n_old}")
    return b.finish(run_folder)


# --------------------------------------------------------------------------
# 4. Legacy documents and large files
# --------------------------------------------------------------------------

def _large(size, seed, salt, header=b""):
    """Incompressible bytes of exactly ``size``, drawn from the seed (generated here, never tracked)."""
    body = random.Random(f"w2-81:{seed}:{salt}").randbytes(max(0, size - len(header)))
    return (header + body)[:size]


def build_legacy(root, seed, run_folder, large_size=SELF_TEST_LARGE, name="legacy-docs"):
    b = _Build(root, seed, name, "legacy-documents")
    d = b.draw
    product, topic = d.pick(PRODUCTS), d.pick(TOPICS)
    other = d.pick([t for t in TOPICS if t != topic])
    folder = d.pick(LEGACY_FOLDERS)
    tool = d.pick(("convert_records", "export_ledger", "load_codes", "split_batches", "merge_ledgers", "index_scans", "rebuild_codes", "check_totals"))
    system = d.pick(("Mainframe", "Tandem", "AS-400", "Unisys", "VAX", "Wang", "Burroughs", "ICL"))
    year = d.number(2004, 2013)
    width = d.number(40, 132)
    plandir = d.pick(("plans", "docs/plans", "project/plans"))
    plan = d.pick(("migration", "archive-move", "records-cleanup", "digitisation"))
    plan_old, plan_new = f"{plandir}/{plan}-plan.md", f"{plandir}/{plan}-plan-revised.md"
    extract_doc = f"docs/legacy/{topic}-procedure-{year}.txt"
    retire_doc = f"docs/legacy/{system.lower()}-operations-manual-{year - 3}.rtf"
    control_spec = f"docs/specs/draft-{other}-record-format.md"
    tool_rel = f"{folder}/{tool}.py"
    dataset = f"data/{other}-{year}.bin"
    media = f"media/{topic}-briefing-{year}.wav"
    wav = b"RIFF" + struct.pack("<I", max(0, large_size - 8)) + b"WAVEfmt "

    b.commit("Records repository", {
        "README.md": f"# {product} records\n\nThe {topic} records of {product} and the tools that read them.\n"
                     f"Run `make records` to convert them.\n",
        "Makefile": f"records:\n\tpython3 {tool_rel} data/\n",
        ".gitattributes": "*.bin binary\n*.wav binary\n",
    })
    tooled = b.commit(f"The {tool} tool and the record format", {
        tool_rel: f'"""Convert the {other} records (fixed width)."""\n\nimport sys\n\nRECORD_WIDTH = {width}\n\n\n'
                  f"def main(folder):\n    return folder, RECORD_WIDTH\n\n\nif __name__ == \"__main__\":\n"
                  f"    main(sys.argv[1])\n",
        control_spec: _spec(f"Draft: the {other} record format", "Status: Current", "Dated", d.old_day(),
                            [f"Record width: {width}"], "\nThe governing description of the format.\n"),
        f"tests/test_{tool}.py": f'import runpy\n\n\ndef test_record_width():\n'
                                 f'    assert runpy.run_path("{tool_rel}")["RECORD_WIDTH"] == {width}\n',
    })
    b.manifest.control("current-spec-looks-old", [control_spec], why="it agrees with the tool and nothing replaces "
                       "it; only its date and its name look old", code=tool_rel,
                       claim_line=f"- Record width: {width}", code_line=f"RECORD_WIDTH = {width}")
    b.manifest.control("live-file-in-legacy-folder", [tool_rel], why="the Makefile runs it", token=tool_rel,
                       referenced_by=["Makefile"])
    b.facts(product=product, topic=topic, other=other, tool=tool_rel, tool_test=f"tests/test_{tool}.py",
            control_spec=control_spec, width_line=f"- Record width: {width}",
            width_code=f"RECORD_WIDTH = {width}", procedure=extract_doc, manual=retire_doc, system=system,
            plan=plan_new, plan_old=plan_old, plan_title=plan.replace("-", " "), dataset=dataset, media=media,
            make_line=f"python3 {tool_rel} data/")
    docs = b.commit("Scanned documents from the old share", {
        extract_doc: f"{topic.upper()} RECONCILIATION PROCEDURE ({year})\n\n1. Each night, total the {topic} "
                     f"batches.\n2. A batch whose total differs is held for the {other} desk.\n3. Held batches "
                     f"are released only by two signatures.\nThis is still how the desk works.\n",
        retire_doc: "{\\rtf1\\ansi " + f"{system} OPERATIONS MANUAL. Mount tape volume 3 before the night run. "
                    f"The {system} was switched off in {year + 2}." + "}\n",
    })
    b.manifest.plant("legacy-document", "extract", [extract_doc], [docs], path=extract_doc, handling="extract",
                     reason="the procedure is still followed; its knowledge is extracted into a record")
    b.manifest.plant("legacy-document", "retire", [retire_doc], [docs], path=retire_doc, handling="retire",
                     reason=f"it describes the {system}, switched off; it is retired, kept in history")
    big = b.commit("Add the archived dataset and the briefing recording", {
        dataset: _large(large_size, seed, "dataset"), media: _large(large_size, seed, "media", wav)})
    b.manifest.plant("large-file", "dataset", [dataset], [big], path=dataset, size=large_size)
    b.manifest.plant("large-file", "media", [media], [big], path=media, size=large_size)
    old = b.commit(f"The {plan} plan", {
        plan_old: f"# The {plan.replace('-', ' ')} plan\n\n1. Scan the share.\n2. Move the records to tape.\n"})
    new = b.commit(f"Revise the {plan} plan", {
        plan_new: f"# The {plan.replace('-', ' ')} plan, revised\n\nThis revision replaces `{plan_old}` in full.\n\n"
                  f"1. Scan the share.\n2. Keep the records in the repository; tape is gone.\n"})
    b.manifest.plant("superseded-plan", "names-it", [plan_old, plan_new], [old, new], plan=plan_old,
                     successor=plan_new, link="names-it")
    return b.finish(run_folder)


# --------------------------------------------------------------------------
# 5. A Go service with a secret in its history
# --------------------------------------------------------------------------

_MAIN_GO = """package main

import (
\t"fmt"

\t"example.invalid/<<product>>/internal/<<pkg>>"
\t"example.invalid/<<product>>/internal/<<folder>>"
)

func main() {
\tfmt.Println(<<pkg>>.Routes(), <<folder>>.StatusText(200), <<pkg>>.RetryLimit)
}
"""


def build_go(root, seed, run_folder, name="secret-history"):
    b = _Build(root, seed, name, "go-service")
    d = b.draw
    product, other = d.pick(PRODUCTS), d.pick(TOPICS)
    old_word, cur_word, folder = d.pick(OLD_WORDS), d.pick(CURRENT_WORDS), d.pick(LEGACY_FOLDERS)
    config = d.pick(("config/settings.ini", "config/storage.ini", "deploy/app.ini"))
    retries = d.number(2, 9)
    dead_fn = f"{cur_word.title()}Routes"
    pkg = d.pick(("handlers", "routes", "web", "httpapi", "server"))
    mux = d.pick(("router", "routes", "mux", "dispatch", "table"))
    live_rel = f"internal/{pkg}/{old_word}_{mux}.go"
    dead_rel = f"internal/{pkg}/{cur_word}_{mux}.go"
    codes_rel = f"internal/{folder}/codes.go"
    control_spec = f"docs/specs/draft-{other}-retries.md"
    key = make_secret("cloud-access-key", seed, name)
    b.secrets.append(key)

    b.commit("A Go service", {
        "go.mod": f"module example.invalid/{product}\n\ngo 1.22\n",
        "README.md": f"# {product}\n\nThe {other} service. `go run ./cmd/{product}`.\n",
        ".gitignore": "/bin\n",
        live_rel: f"package {pkg}\n\n// RetryLimit is the number of upstream retries.\nconst RetryLimit = {retries}\n\n"
                  f"// Routes is the routing table.\nfunc Routes() []string {{\n\treturn []string{{\"/{other}\", "
                  f"\"/health\"}}\n}}\n",
        f"internal/{pkg}/{mux}_test.go": f"package {pkg}\n\nimport \"testing\"\n\nfunc TestRoutes(t *testing.T) "
                                            "{\n\tif len(Routes()) == 0 {\n\t\tt.Fatal(\"no routes\")\n\t}\n}\n",
        codes_rel: f"package {folder}\n\nimport \"fmt\"\n\n// StatusText names a status code.\n"
                   f"func StatusText(code int) string {{\n\treturn fmt.Sprint(code)\n}}\n",
        f"cmd/{product}/main.go": fill(_MAIN_GO, product=product, folder=folder, pkg=pkg),
    })
    secret_in = b.commit("Storage settings", {
        config: key.line("[storage]\nregion = eu-west-1\nbucket = " + f"{product}-{other}\naccess_key_id = {{value}}\n")})
    b.commit(f"Document the {other} retries", {
        control_spec: _spec(f"Draft: {other} retries", "Status: Current", "Dated", d.old_day(),
                            [f"Retry limit: {retries}"], "\nThe governing description of the retries.\n"),
        "docs/plans/next-quarter.md": f"# Next quarter\n\n1. Serve `/{other}` from two regions.\n"
                                      f"2. Alert on retries above {retries}.\n"})
    b.manifest.control("current-spec-looks-old", [control_spec], why="it agrees with the code and nothing replaces "
                       "it; only its date and its name look old", code=live_rel,
                       claim_line=f"- Retry limit: {retries}", code_line=f"RetryLimit = {retries}")
    b.manifest.control("live-file-in-legacy-folder", [codes_rel], why="the entry point imports its package and "
                       "calls it", token="StatusText", referenced_by=[f"cmd/{product}/main.go"])
    b.manifest.plant("misleading-name", "live-under-old-name", [live_rel], [b.repo.commits[0][0]], token="Routes()",
                     referenced_by=[f"cmd/{product}/main.go"], live=True)
    b.facts(product=product, other=other, main=f"cmd/{product}/main.go", router=live_rel, package=pkg,
            codes=codes_rel, config=config, control_spec=control_spec, retries_line=f"- Retry limit: {retries}",
            retries_code=f"RetryLimit = {retries}", plan="docs/plans/next-quarter.md",
            router_test=f"internal/{pkg}/{mux}_test.go", module_line=f"module example.invalid/{product}",
            dead_module=dead_rel)
    dead = b.commit(f"Draft the {cur_word} routing table", {
        dead_rel: f"package {pkg}\n\n// {dead_fn} is the {cur_word} routing table.\nfunc {dead_fn}() []string {{\n"
                  f"\treturn []string{{\"/v0/{other}\"}}\n}}\n"})
    b.manifest.plant("misleading-name", "dead-under-current-name", [dead_rel], [dead], token=dead_fn,
                     referenced_by=[], live=False)
    cleaned = b.commit("Read the storage credentials from the environment", {
        config: f"[storage]\nregion = eu-west-1\nbucket = {product}-{other}\n# credentials: from the environment\n"})
    b.manifest.plant("secret", "key-in-config", [config], [secret_in, cleaned], path=config,
                     added_in=secret_in[:12], removed_in=cleaned[:12], rule=FORMS["cloud-access-key"]["rule"],
                     form="cloud-access-key")
    b.commit("Note the configuration in the README", {
        "README.md": f"# {product}\n\nThe {other} service. `go run ./cmd/{product}`.\n\nSettings: `{config}`; "
                     f"credentials come from the environment.\n"})
    return b.finish(run_folder)


# --------------------------------------------------------------------------
# The whole proving ground
# --------------------------------------------------------------------------

SHAPES = ("python-app", "rust-workspace", "typescript-monorepo", "legacy-docs", "secret-history")
CLEAN = "python-app-clean"


def build_all(run_folder, seed=DEFAULT_SEED, large_size=SELF_TEST_LARGE, manifests_root=None, variants=()):
    """Build the five repositories and the clean variant under ``<run>/repos/``, their manifests under
    ``<manifests_root or run>/manifests/``, and the hidden half's ``variants`` (when given) on top."""
    run_folder = Path(run_folder)
    repos, beside = run_folder / "repos", Path(manifests_root) if manifests_root else run_folder
    built = {
        "python-app": build_python(repos / "python-app", seed, beside),
        "rust-workspace": build_rust(repos / "rust-workspace", seed, beside),
        "typescript-monorepo": build_typescript(repos / "typescript-monorepo", seed, beside),
        "legacy-docs": build_legacy(repos / "legacy-docs", seed, beside, large_size),
        "secret-history": build_go(repos / "secret-history", seed, beside),
        CLEAN: build_python(repos / CLEAN, seed, beside, planted=False, name=CLEAN),
    }
    if variants:
        apply_variants(built, variants, seed, beside)
    return built


# --------------------------------------------------------------------------
# The hidden half's planted-problem variants (README, "The hidden half"): built here, described there
# --------------------------------------------------------------------------

_PLACE = re.compile(r"\{(commit|fact):([A-Za-z0-9_-]+)\}")
VARIANT_KEYS = ("id", "repository", "kind", "variant", "paths", "steps", "evidence")


def _put(value, hashes, facts, where):
    """``{commit:N}`` (step N's commit, 12 digits) and ``{fact:name}`` filled in a string, a list or a mapping."""
    if isinstance(value, dict):
        return {k: _put(v, hashes, facts, where) for k, v in value.items()}
    if isinstance(value, list):
        return [_put(v, hashes, facts, where) for v in value]
    if not isinstance(value, str):
        return value

    def one(match):
        kind, key = match.groups()
        try:
            return hashes[int(key) - 1][:12] if kind == "commit" else str(facts[key])
        except (ValueError, IndexError, KeyError):
            raise AssertionError(f"variant {where}: {match.group(0)} names no step or fact") from None
    return _PLACE.sub(one, value)


class VariantError(AssertionError):
    """A hidden variant that cannot be built. Its message names the variant by its number and id only: never its
    texts, paths or values (they are the hidden half's)."""


def _ident(variant):
    ident = variant.get("id") if isinstance(variant, dict) else None
    return str(ident) if isinstance(ident, (str, int)) and len(str(ident)) <= 40 else "?"


def apply_variants(built, variants, seed, manifests_root):
    """Each variant built by ``_apply_one``; any failure is a VariantError naming its number and id only."""
    for number, variant in enumerate(variants, 1):
        try:
            _apply_one(built, number, variant, seed, manifests_root)
        except Exception:  # noqa: BLE001 - whatever stops it, the message holds nothing of the variant's content
            raise VariantError(f"hidden variant #{number} ({_ident(variant)}) cannot be built") from None


def _apply_one(built, number, variant, seed, manifests_root):
    """Append each variant to its repository as commits of its own, plant it in the manifest, rewrite the manifest.

    A variant is ``{id, repository, kind, variant, paths, steps, evidence}``: ``steps`` are the commits, each
    ``{message, write: {path: text}, remove: [path]}``; ``evidence`` is the kind's evidence as the manifest holds it.
    Texts and evidence may name ``{commit:N}`` and ``{fact:name}``; a secret's step texts name ``{value}``, its
    evidence names ``form``, and its value is drawn from the seed here and held in memory only.
    """
    from w2_81_git import outside_this_repository, run_git
    from w2_81_secret import assert_absent

    where = f"#{number}"
    if not isinstance(variant, dict) or set(VARIANT_KEYS) - set(variant):
        raise AssertionError(f"variant {where}: it needs {', '.join(VARIANT_KEYS)}")
    if variant["kind"] not in manifest_form.KINDS + manifest_form.LEGACY_KINDS:
        raise AssertionError(f"variant {where}: kind {variant['kind']!r} is not a planted kind")
    if variant["repository"] not in built:
        raise AssertionError(f"variant {where}: no repository {variant['repository']!r}")
    target = built[variant["repository"]]
    data, facts = target.manifest, target.manifest.get("facts") or {}
    draw = Draw(seed, f"{target.name}:hidden:{variant['id']}")
    draw.clock = datetime.fromisoformat(run_git(target.root, "log", "-1", "--format=%cI").strip())
    held = None
    if variant["kind"] == "secret":
        form = variant["evidence"].get("form")
        if form not in FORMS:
            raise AssertionError(f"variant {where}: a secret names its form, one of {', '.join(FORMS)}")
        held = make_secret(form, seed, f"{target.name}:hidden:{variant['id']}")
    hashes, touched = [], set()
    for step in variant["steps"]:
        for rel, content in (step.get("write") or {}).items():
            rel = _put(str(rel), hashes, facts, where)
            touched.add(rel)
            content = _put(str(content), hashes, facts, where)
            content = held.line(content) if held is not None else content
            place = outside_this_repository(target.root / rel)
            place.parent.mkdir(parents=True, exist_ok=True)
            place.write_text(content, encoding="utf-8")
        for rel in step.get("remove") or []:
            rel = _put(str(rel), hashes, facts, where)
            touched.add(rel)
            (target.root / rel).unlink()
        run_git(target.root, "add", "-A")
        run_git(target.root, "commit", "-q", "-m", str(step.get("message") or f"Change {number}"),
                author=draw.author(), date=draw.tick())
        hashes.append(run_git(target.root, "rev-parse", "HEAD").strip())
    evidence = _put(variant["evidence"], hashes, facts, where)
    if held is not None:
        evidence = {**evidence, "rule": FORMS[evidence["form"]]["rule"],
                    "salt": f"{target.name}:hidden:{variant['id']}"}
        if not held.found_in(blob(target.root, evidence["added_in"], evidence["path"])):
            raise AssertionError(f"variant {where}: the secret is not at its added_in")
        for rel in tree(target.root):
            assert_absent(held, blob(target.root, "HEAD", rel), f"variant {where}: a file at HEAD")
        target.secrets.append(held)
    data["planted"].append({
        "id": f"{target.name}.{variant['kind']}.hidden-{variant['id']}", "kind": variant["kind"],
        "variant": str(variant["variant"]), "shape": data["shape"], "hidden": True,
        "number": number, "hidden_id": _ident(variant),  # how the report names it (README, "The hidden half's form")
        "hidden_files": sorted(touched),  # its own files: a visible entry's evidence never names them
        "paths": _put(variant["paths"], hashes, facts, where), "commits": [h[:12] for h in hashes],
        "detectable_by": manifest_form.DETECTABLE_BY[variant["kind"]],
        "correct_handling": manifest_form.CORRECT_HANDLING[variant["kind"]], "evidence": evidence})
    commits = run_git(target.root, "rev-list", "--reverse", "HEAD").split()
    data["clean"] = False
    data["commits"], data["head"] = [c[:12] for c in commits], commits[-1][:12]
    target.manifest_path = manifest_form.write(data, manifests_root, target.root)


def remove(run_folder):
    """Remove a run folder's built repositories and manifests (never a folder of this repository)."""
    from w2_81_git import outside_this_repository

    shutil.rmtree(outside_this_repository(run_folder), ignore_errors=False)
