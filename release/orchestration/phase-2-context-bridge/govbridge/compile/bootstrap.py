#!/usr/bin/env python3
"""The canonical worker bootstrap: ``govbridge bootstrap <task-spec>`` (ARCHITECTURE.md section 7.5).

**ADAPT provenance.** Adapted from
``release/orchestration/phase-2/tools/worker_bootstrap.py`` at commit
``6e7a2a3495a8d3619759a95b7ed055da9c848618`` (read with
``git show 6e7a2a3495a8d3619759a95b7ed055da9c848618:release/orchestration/phase-2/tools/worker_bootstrap.py``).
Never edit that original; this file is a copy, changed exactly as ARCHITECTURE.md section 7.5 specifies:

* **kept, verbatim:** the verbatim-quote discipline (an excerpt always carries its own path/commit/line range); the
  ``CONVENTIONS`` blocks below (copied from the source unchanged); the checkpoint protocol and completion
  semantics (``CHECKPOINT_PROTOCOL`` below, copied unchanged).
* **changed (the two things ARCHITECTURE.md section 7.5 names):**
  1. ``phase_state()``'s hard-coded text (the source's SO-01 baked-in ``cap2-candidate-1``/``GATE-P2-REPAIR-2``
     strings) becomes ``where_you_are()``: structured state lookups (``govbridge.authority.state.get``) WITH
     provenance, over a fixed, generic set of top-level state-file fields -- never a hard-coded value, so this
     output always reflects whatever this run's own state file currently says.
  2. the fixed ``DECISIONS`` dictionary becomes the resolver's own section A, rendered by
     ``govbridge.compile.packet`` and included here verbatim as part of the compiled packet (A-J) -- output is
     "the bootstrap prelude, followed by the packet A-J and then the receipt instructions" (section 7.5).

One canon, one text, model-neutral: a provider-specific wrapper, if one is ever needed, stays a thin adapter around
this same output (the owner rule V8.3 section 2.3 records).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

import yaml

from govbridge.authority import state as statemod
from govbridge.compile import packet as packetmod
from govbridge.compile import section_i as section_i_mod
from govbridge.core.yamlutil import load_yaml_file

ADAPT_SOURCE = ("release/orchestration/phase-2/tools/worker_bootstrap.py"
                "@6e7a2a3495a8d3619759a95b7ed055da9c848618")

# --------------------------------------------------------------------------------------------------------------
# Kept verbatim from the ADAPT source (ARCHITECTURE.md section 7.5: "its conventions blocks").
# --------------------------------------------------------------------------------------------------------------
CONVENTIONS = {
"rust": """**Rust layout.** The product is `runtime/` (library, `gov_runtime`) plus `cli/` (the `gov` binary). Modules are
files or directories under `runtime/src/`; a new module needs its `pub mod` line in the parent `mod.rs` or `lib.rs`.
Unit tests live in a `#[cfg(test)] mod tests` block at the foot of the file they test. Build with
`cargo build --release`; the binary is `target/release/gov`. Keep `cargo fmt` clean on files you touch and leave the
release build at **0 warnings** -- a warning is treated as a defect here.""",
"tests": """**Tests.** Certification tests live in `tests/certification/<name>.rs` and must be declared with a `mod <name>;`
line in `tests/certification/main.rs`, or they never run. Test names are load-bearing: the governed evidence map names
tests by exact path, so renaming, removing or `#[ignore]`-ing an existing test breaks `gov contract verify`, the
contract-binding test and `release build`. Add tests; never rename or delete one. A test that merely asserts a struct
field or a constant is not evidence of behaviour -- drive the real code path and assert the observable result.""",
"cli": """**Adding or changing a command.** Every subcommand must be classified or G0 refuses it: add the arm in
`cli/src/main.rs`, the `g0_label` mapping, and an entry in `COMMAND_GUARDS` in `runtime/src/orchestration/control.rs`
declaring its authority class and whether it reads or writes. An unclassified command fails closed by design.""",
"schemas": """**Schemas and versions.** Record schemas live in `framework/schemas/*.json`. If you change a schema you must
bump its version and mirror that version in `framework/KERNEL.yaml`'s `schema_versions`, or the release build and the
kernel-consistency tests refuse the tree.""",
"governed-records": """**Governed records and sealing.** Records the OS writes (gates, decisions, CIT state, tasks, the
plugin registry, health results) are sealed T2 state: a record written by hand is `UNSEALED`/`BROKEN` and is never
honoured. Write through the existing governed path rather than writing files directly, and never add a code path that
blesses a hand-written record. Project-editable files under `governance/project/**` are *requests*, not grants.""",
"health": """**Health and the availability rule.** Checks are declared in `runtime/src/scheduler/catalogue.rs` with their
tiers, severities and remedies. A block refuses only what it protects, its listed remedy stays available, no block
refuses its own remedy, and every refusal is typed and names its scope and subjects.""",
"policy": """**Policy precedence.** Kernel policy outranks project overlay. A project overlay may narrow what it grants
itself; an attempt to widen must be refused, left without effect and reported through
`policy_precedence::evaluate_overlay` and `gov policy overrides`.""",
"adoption": """**Adoption.** `gov adopt` runs stages A0-A11 in order on an existing repository; each stage is executable
and evidenced, and a stage may not be skipped to make a later one pass. The brownfield fixture under `fixtures/` is the
tree the acceptance evidence uses -- do not edit a fixture to make adoption succeed.""",
}

CHECKPOINT_PROTOCOL = """## Context and checkpoint protocol

Your context is a working surface, not a place to accumulate everything you have read.

- **Checkpoint early and often.** Call `checkpoint` after each material step: what the objective is, what you have
  completed, files changed, checks run with outcomes, what you discovered, what is unresolved, decisions and
  assumptions you have made, and the **exact next action**. The adapter also checkpoints automatically before it
  renews your context and before the run ends.
- **A checkpoint is a handover.** Write it so that a different worker could continue from it alone, without replaying
  your exploration. Name files and symbols exactly.
- **Context renewal is normal.** When history becomes mostly exploration noise the adapter rebuilds a fresh bounded
  context from your latest checkpoint (`govbridge renew --checkpoint`). Nothing is lost that you put in the
  checkpoint; anything you left only in the conversation is lost. Re-read an authoritative file when you need it
  again rather than keeping it in view.
- **Large outputs are externalised.** A big command result or search is written to a scratch file and you get a
  summary plus its path; read the part you need with `read_scratch`.
- **Reaching a context target never fails your task.** Budgets are guidance; the orchestrator raises or lowers them.
  What matters is useful progress: edits that make the requirement true, and checks that show it.

## Completion semantics

- `REPAIRED_CLAIMED` -- the requirement is now true, you made it observable with a test you added, and the relevant
  checks pass. This is a *claim*: an independent verifier grades it later. Never describe it as accepted or verified.
- `PARTIAL` -- some items are true and observable, others are not. Name precisely which, and what remains.
- `OWNER_DECISION_REQUIRED` -- closing an item needs a choice the accepted sources do not make. State the choice, the
  options and the consequence; do the rest.
- `INCOMPLETE` -- you could not land the work. Say exactly where you stopped and what the next worker should do.

An honest `PARTIAL` with evidence is worth more than a `REPAIRED_CLAIMED` you cannot show. Do not report a figure you
did not observe, and never weaken a test, check, schema or policy to make something pass."""

# a small, generic lookup for whatever completion_vocabulary a task spec declares (ANSWERED/PARTIAL/BLOCKED for a
# demonstration task, REPAIRED_CLAIMED/... for a builder, ...); an unrecognised word still renders, generically.
COMPLETION_MEANINGS = {
    "ANSWERED": "the objective is fully addressed, with evidence.",
    "PARTIAL": "some items are true and observable, others are not -- name precisely which, and what remains.",
    "BLOCKED": "a required input or check could not be satisfied; say exactly which and why.",
    "REPAIRED_CLAIMED": "the requirement is now true, made observable with an added test, and the relevant checks "
                         "pass -- a CLAIM: an independent verifier grades it later, never accepted or verified by "
                         "you.",
    "OWNER_DECISION_REQUIRED": "closing this needs a choice the accepted sources do not make -- state the choice, "
                                "the options and the consequence; do the rest.",
    "INCOMPLETE": "you could not land the work -- say exactly where you stopped and what the next worker should do.",
}

# the bridge's own orchestrator state (release/orchestration/phase-2-context-bridge/ORCHESTRATOR_STATE.yaml) --
# generic across any lifecycle this domain ever runs, never a particular lifecycle's content (OC-BR-02).
STATE_ALIAS = "bridge"
WHERE_YOU_ARE_KEYS = ("lifecycle_id", "lifecycle_name", "lifecycle_state", "loop_status", "acceptance_token")


def where_you_are(view_path: Optional[str] = None, repo: Optional[str] = None) -> str:
    """ARCHITECTURE.md section 7.5: ``phase_state()``'s hard-coded text becomes structured state lookups WITH
    PROVENANCE. Generic over any state file matching this domain's own schema: it looks up a fixed set of
    universal top-level field NAMES, never a particular value -- whatever this state file's CURRENT values are is
    what gets rendered, each with the exact ``(path, commit, lines)`` that backs it."""
    lines = []
    for key in WHERE_YOU_ARE_KEYS:
        try:
            r = statemod.get(STATE_ALIAS, key, repo=repo, view_path=view_path)
        except (KeyError, ValueError, FileNotFoundError) as e:
            lines.append(f"- `{key}`: not available in this state file ({e})")
            continue
        lines.append(f"- `{key}`: {r.value!r}  "
                     f"(source: `{r.path}@{r.commit[:10]}:{r.line_start}-{r.line_end}`, seal {r.seal_status})")
    return "\n".join(lines)


def compile_brief(task_spec: dict, routes=None, repo: Optional[str] = None, registry_path: Optional[str] = None,
                   budgets_path: Optional[str] = None, packet_out: Optional[str] = None) -> tuple:
    """Returns ``(brief_text, compile_result)``. ``compile_result`` is ``govbridge.compile.packet.compile_packet``'s
    own return value, enriched by ``section_i.with_task_inputs_in_section_i`` (OBS-BR-07) -- the caller can inspect
    ``compile_result["status"]``/``["manifest"]`` without recompiling.

    ``packet_out`` (REPAIR_PLAN.md section 6, RC-9: "the bootstrap inlines the whole packet -- run-1's bootstrap
    was 282,782 bytes"): when given, the directory this SAME packet was (or will be) written to by the caller --
    the brief then REFERENCES it by path/id/hash instead of embedding ``result["rendered"]``. When omitted, the
    brief still never inlines the packet; it tells the reader to compile it themselves (deterministic: the same
    task spec always reproduces the identical ``packet_sha256``) and verify what they hold against the hash named
    here."""
    result = packetmod.compile_packet(task_spec, routes=routes or packetmod.FAKE_ROUTES, repo=repo,
                                       registry_path=registry_path, budgets_path=budgets_path)
    result = section_i_mod.with_task_inputs_in_section_i(result, task_spec, repo=repo)

    out = [f"# Worker bootstrap -- {task_spec.get('task_id', '?')}\n"]
    out.append(
        "You are a **governed worker**. This bootstrap is your operating context: it carries the rules, the "
        "authority model, the requirement you must satisfy and the conventions of this repository. Do not infer "
        "these by exploring; they are here because they are authoritative. Where you need more, issue a live "
        "`govbridge` query -- every read you make outside this packet must be declared in your receipt's "
        "`external_reads`.\n"
    )

    out.append("## Where you are\n\n" + where_you_are(view_path=result["view_path"], repo=repo) + "\n")

    out.append(
        f"## Your role and authority\n\n"
        f"- Role: **{task_spec.get('role', '?')}**.\n"
        f"- Objective: {task_spec.get('objective', '?')}\n"
        f"- You produce **claims**, never acceptances, and you grade nobody's work, including your own.\n"
        f"- You may write only the paths named in section I of the packet below. The adapter refuses every other "
        f"write.\n"
    )

    picked = [k for k in (task_spec.get("conventions") or CONVENTIONS) if k in CONVENTIONS]
    if picked:
        out.append("## How this repository works\n\n" + "\n\n".join(CONVENTIONS[k] for k in picked) + "\n")

    # REPAIR_PLAN.md section 6 (RC-9/OBS-BR-07): reference the packet by id and hash -- NEVER inline it (run-1's
    # bootstrap was 282,782 bytes and contained the whole packet). Section I of the packet itself now also carries
    # the instantiated query set and the answers/receipt schemas verbatim and by hash (section_i.py above), so
    # nothing about the task's own inputs is lost by not embedding the packet text here.
    packet_ref = [
        "## Your context packet (sections A-J)\n",
        f"- packet_id: `{result.get('packet_id')}`",
        f"- packet_sha256: `{result.get('packet_sha256')}`",
        f"- manifest_sha256: `{result['manifest'].get('manifest_sha256')}`",
    ]
    if packet_out:
        packet_ref.append(f"- compiled at: `{packet_out}` -- read `packet.md`/`manifest.json` there directly.")
    else:
        packet_ref.append(
            "- NOT inlined here. Compile it yourself with `govbridge compile <task-spec> --out <dir>` "
            "(compilation is deterministic: the same task spec always reproduces the identical packet_sha256 "
            "above) and confirm you hold the SAME packet with `govbridge packet verify <dir>`.")
    out.append("\n".join(packet_ref) + "\n")

    out.append(CHECKPOINT_PROTOCOL + "\n")

    vocab = task_spec.get("completion_vocabulary") or []
    if vocab:
        out.append("## Completion semantics\n\n" + "\n".join(
            f"- `{w}` -- {COMPLETION_MEANINGS.get(w, 'task-defined completion state; see the task contract (section I).')}"
            for w in vocab) + "\n")

    out.append(
        "## Your receipt\n\n"
        "Before you finish, produce a `govbridge-receipt/1` document (`schemas/receipt.yaml`) naming this packet's "
        f"hash (`{result['packet_sha256']}`), every section read token you reached, every section-A item's "
        "`content_sha256`, every `item_id` you relied on, and every external read. Run `govbridge receipt check` "
        "yourself before reporting completion.\n"
    )

    return "\n".join(out), result


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.compile.bootstrap")
    p.add_argument("task_spec")
    p.add_argument("--fake-routes", action="store_true",
                    help="use the all-empty RouteSet; the DEFAULT is the real B2/B3/B4 routes, matching "
                         "govbridge.compile.packet's own CLI default.")
    p.add_argument("--registry")
    p.add_argument("--budgets")
    p.add_argument("--repo", help="the repository to read Git objects from; defaults to the repository containing "
                                   "the current working directory (see govbridge.cli's own cmd_search for why "
                                   "this is worth passing explicitly rather than relying on cwd).")
    p.add_argument("--out", help="also write the compiled packet directory here (manifest.json/packet.md/"
                                  "task_spec.yaml/meta.json, the same shape `govbridge compile --out` writes) -- "
                                  "the brief text REFERENCES it by id/hash instead of inlining it (REPAIR_PLAN.md "
                                  "section 6)")
    args = p.parse_args(argv)

    task_spec = load_yaml_file(args.task_spec)
    routes = packetmod.FAKE_ROUTES if args.fake_routes else packetmod.real_routes_for(
        task_spec, registry_path=args.registry, repo=args.repo)
    brief, result = compile_brief(task_spec, routes=routes, repo=args.repo, registry_path=args.registry,
                                   budgets_path=args.budgets, packet_out=args.out)
    if args.out:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "packet.md").write_text(result["rendered"], encoding="utf-8")
        (out_dir / "manifest.json").write_text(json.dumps(result["manifest"], indent=1, sort_keys=True),
                                                encoding="utf-8")
        (out_dir / "task_spec.yaml").write_text(yaml.safe_dump(task_spec, sort_keys=False), encoding="utf-8")
        meta = {
            "packet_kind": "main", "status": result["status"], "packet_id": result.get("packet_id"),
            "packet_sha256": result.get("packet_sha256"), "manifest_sha256": result.get("manifest_sha256"),
            "registry_path": result.get("registry_path"), "excluded_hits": result.get("excluded_hits"),
            # BR-DAG-AMEND-R1-10 (reopening): mirrors cmd_compile's own meta.json field, so a LATER `packet
            # verify`/`receipt check` on this directory can recompose an oversize item's expected body exactly.
            "budgets_path": args.budgets,
        }
        (out_dir / "meta.json").write_text(json.dumps(meta, indent=1, sort_keys=True), encoding="utf-8")
    sys.stdout.write(brief)
    return 0 if result["status"] == packetmod.STATUS_OK else 1


if __name__ == "__main__":
    sys.exit(main())
