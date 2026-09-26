import sys
import yaml

D = "release/orchestration/phase-2-context-bridge"


def S(*paths):
    return [f"{D}/{p}" for p in paths]


def chk(cmd, expect):
    return {"cmd": cmd, "expect": expect}


dag = {
    "schema": "govbridge-implementation-dag/1",
    "run_id": "BR-AR-0016",
    "title": "REPAIR-1 -- generic repair of the Context/Retrieval Bridge after the run-1 DEMONSTRATION_FAIL",
    "status": "PROPOSED (for the orchestrator; nothing has been built)",
    "reads_with": "REPAIR_PLAN.md (sections cited per node), CAUSE_ANALYSIS.md (root causes RC-1..RC-11), ARCHITECTURE.md, "
                  "DEMONSTRATION_DESIGN.md, GATES/OWNER-DIRECTION-BR-0005-*, GATES/OWNER-DIRECTION-BR-0006-*",
    "conventions": {
        "domain": D,
        "paths": "every mutation_scope glob is relative to the repository root and lies inside the domain",
        "run_records": f"the orchestrator appends {D}/AGENT_RUNS/<RUN_ID>.* to each node's mutation_scope at dispatch "
                       "(typed report + schema-2 checkpoint, OD-BR-04 A)",
        "python": f"PY=$HOME/.cache/gov-bridge/venv/bin/python; D={D}; commands run from the repository root of the node's "
                  "worktree with PYTHONPATH=$D and GOVBRIDGE_STORE=$HOME/.cache/gov-bridge/store-<RUN_ID>",
        "generic_rule": "no code, config, facet, scope or test may name a Review-8 item, an F-finding, a Phase-2 file or a "
                        "symbol of the Review-8 chains (OC-BR-02). Builders must NOT use the public demonstration query "
                        "texts, the run-1 answers or any oracle as acceptance input; they use fixtures and CONTROL-A only "
                        "(REPAIR_PLAN.md section 9)",
        "unrelated_controls": "real-view subjects chosen by the orchestrator: evidence spanning >= 3 top-level directories, "
                              ">= 1 decision record and >= 1 test file involved, not a Review-8 subject, not a CTRL-1..3 "
                              "subject. CONTROL-A is written by R1-CTRL before any builder starts and is the real-view "
                              "acceptance subject of every builder node and of R1-INT. CONTROL-B is chosen by the "
                              "orchestrator only at R1-MB dispatch and is never shown to builders, so the OD-BR-05 s9 "
                              "demonstration cannot have been tuned for",
        "shared_files": "govbridge/cli.py is edited in sequence RX -> GA1 -> RS -> RA; govbridge/compile/packet.py in "
                        "sequence RX -> RM -> GA3; govbridge/compile/{receipt,validate}.py in sequence RM -> RS; never "
                        "co-edited",
        "tests": "never pipe without set -o pipefail; every wait bounded with a timeout action; no rm",
        "size_limit": "no committed file over 5 MB; stores, venvs and models live under $HOME/.cache/gov-bridge/",
        "model_pinning": "every dispatched role is spawned with an explicit model (routing below); unpinned roles are not "
                         "accepted",
    },
    "build_node_count": 10,
    "build_node_count_rationale": "RX, RN, RL, RM, RG, GA1, GA2, GA3, RS, RA -- one node per disjoint scope. Gather is "
                                  "split in three (core / follow-up and merge / compile integration) because each part is "
                                  "L-sized and they are strictly sequential. RN stays its own node because GA3 and the "
                                  "verifier both consume its schema. Protocol nodes (CTRL, DEC, TA2, INT, MB, D2, DEMO2, "
                                  "GRADE2) are not builders.",
    "parallel_groups": {
        "R1-PG0": ["R1-CTRL", "R1-DEC", "R1-RN"],
        "R1-PG1": ["R1-RX", "R1-RL", "R1-RG", "R1-TA2"],
        "R1-PG2": ["R1-RM", "R1-GA1"],
        "R1-PG3": ["R1-GA2", "R1-RS"],
        "R1-PG4": ["R1-GA3", "R1-RA"],
        "R1-PG5": ["R1-INT"],
        "R1-PG6": ["R1-MB"],
        "R1-PG7": ["R1-D2"],
        "R1-PG8": ["R1-DEMO2"],
        "R1-PG9": ["R1-GRADE2"],
    },
    "traceability": {
        "OD-BR-05": {
            "s1_query_decomposition": ["R1-GA1"],
            "s2_parallel_retrieval": ["R1-GA1"],
            "s3_sequential_adaptive": ["R1-GA2"],
            "s4_retrieval_continuation": ["R1-RL", "R1-GA1"],
            "s5_completeness_criterion_stop_reason": ["R1-GA1"],
            "s6_merge_before_compilation": ["R1-GA2", "R1-GA3"],
            "s7_hierarchical_synthesis": ["R1-RN", "R1-GA3"],
            "s8_mandatory_inputs_separate": ["R1-RM", "R1-GA3"],
            "s9_demonstration": ["R1-MB"],
        },
        "OD-BR-06": {
            "s2_retrieval_completeness": ["R1-GA1", "R1-GA2", "R1-GA3"],
            "s3_parallel_plus_sequential": ["R1-GA1", "R1-GA2"],
            "s4_evidence_larger_than_packet": ["R1-RN", "R1-GA3", "R1-RS"],
        },
        "observations": {"OBS-BR-05": ["R1-RG"], "OBS-BR-06": ["R1-RS"], "OBS-BR-07": ["R1-RS"], "OBS-BR-08": ["R1-RX"],
                         "OBS-BR-09": ["R1-RG"], "OBS-BR-10": ["R1-TA2"]},
        "grader_defects": {"GD-1": ["R1-RG"], "GD-2": ["R1-RG"], "GD-3": ["R1-RG"], "GD-4": ["R1-RG"], "GD-5": ["R1-RG"],
                           "GD-6": ["R1-DEC", "R1-RG"], "GD-7": ["R1-DEC", "R1-RG"], "GD-8": ["R1-DEC", "R1-RG"],
                           "GD-9": ["R1-DEC", "R1-RG"], "GD-10": ["R1-RG"]},
        "root_causes": {"RC-1": ["R1-RM"], "RC-2": ["R1-GA1"], "RC-3": ["R1-GA1", "R1-GA2", "R1-RL"], "RC-4": ["R1-GA3"],
                        "RC-5": ["R1-GA3"], "RC-6": ["R1-RS"], "RC-7": ["R1-RL", "R1-GA2"], "RC-8": ["R1-RX"],
                        "RC-9": ["R1-RS"], "RC-10": ["R1-DEC", "R1-RG"], "RC-11": ["R1-RA", "R1-DEMO2"]},
    },
    "nodes": [],
}

N = dag["nodes"]

N.append({
    "id": "R1-CTRL",
    "title": "unrelated real-view control CONTROL-A (orchestrator-chosen) and its baseline on the unrepaired bridge",
    "capabilities": ["OC-BR-02 control subject"],
    "depends_on": [],
    "mutation_scope": S("tests/fixtures/controls/**"),
    "deliverables": [
        "tests/fixtures/controls/control-a/{task-spec.yaml, queries.yaml, SELECTION.md}: a subject meeting "
        "conventions.unrelated_controls, with the orchestrator's evidence (exact greps and paths) that it spans >= 3 "
        "top-level directories and involves >= 1 decision record and >= 1 test file",
        "tests/fixtures/controls/control-a/baseline/: compile, packet verify and a manifest summary on the UNREPAIRED "
        "bridge, so that every node can show a before/after comparison on the same subject",
    ],
    "acceptance_checks": [
        chk("$PY -m govbridge compile $D/tests/fixtures/controls/control-a/task-spec.yaml --out /tmp/ca0 && "
            "$PY -m govbridge packet verify /tmp/ca0",
            "PASS on the unrepaired bridge; the baseline is recorded"),
        chk("grep -nE 'P2-AR-0097|REVIEW-8|OD-P2-10' $D/tests/fixtures/controls/control-a/*.yaml", "no match"),
    ],
    "routing": "orchestrator (deterministic)",
    "size": "S",
    "parallel_group": "R1-PG0",
})

N.append({
    "id": "R1-DEC",
    "title": "grading-rule decisions D-1..D-5: whole-document vs sectioned anchors; must_state binding; AUTH gating; "
             "reads of run metadata; G7 packet-byte accounting",
    "capabilities": ["demonstration grading rules"],
    "depends_on": [],
    "mutation_scope": S("ARCHITECTURE/REPAIR-1/DECISIONS/**", "ARCHITECTURE/DEMONSTRATION_DESIGN.md"),
    "deliverables": [
        "ARCHITECTURE/REPAIR-1/DECISIONS/GRADING-RULES.md recording D-1..D-5 (REPAIR_PLAN.md section 8.1), each with its "
        "approver (the orchestrator; the owner where a gate's meaning changes) and its date",
        "a dated amendment section appended to DEMONSTRATION_DESIGN.md section 4 (G3, G4, G5, G7) that quotes D-1..D-5; "
        "the existing text is not rewritten",
    ],
    "acceptance_checks": [
        chk("grep -cE '^\\| D-[1-5] ' $D/ARCHITECTURE/REPAIR-1/DECISIONS/GRADING-RULES.md", "5"),
        chk("grep -c 'APPROVED' $D/ARCHITECTURE/REPAIR-1/DECISIONS/GRADING-RULES.md",
            ">= 5, and each row names its approver"),
        chk("git diff <base> -- $D/ARCHITECTURE/DEMONSTRATION_DESIGN.md | grep -c '^-[^-]'",
            "0 (the amendment only appends)"),
    ],
    "routing": "orchestrator (the owner is consulted for D-2 and D-3)",
    "size": "S",
    "parallel_group": "R1-PG0",
})

N.append({
    "id": "R1-RN",
    "title": "hierarchical evidence notes: schema, validator and CLI (OD-BR-05 s7, OD-BR-06 s4)",
    "capabilities": ["derived evidence notes with claim-to-source lineage"],
    "depends_on": [],
    "mutation_scope": S("govbridge/notes/**", "config/notes-schema.yaml", "tests/notes/**"),
    "deliverables": [
        "config/notes-schema.yaml: note_id; class DERIVED_NOTE; claims[] with sources[] {item_id, path, commit, blob, "
        "lines, content_sha256}; unresolved[]; built_from_sha256",
        "govbridge/notes/{build,validate}.py and `govbridge notes validate <file>`; DERIVED_NOTE is non-ladder and never "
        "admissible in A",
    ],
    "acceptance_checks": [
        chk("cd $D && $PY -m pytest tests/notes -q",
            "exit 0. Refused: a claim with no source, a source that does not resolve, a note placed in A, and a "
            "built_from_sha256 mismatch. Accepted: a note rebuilt twice from the same sources, with an identical hash. "
            "unresolved[] is mandatory and may be empty"),
    ],
    "routing": "sonnet",
    "size": "S",
    "parallel_group": "R1-PG0",
})

N.append({
    "id": "R1-RX",
    "title": "task context: retrieval_exclusions applied automatically by every route, every CLI query command and "
             "every compile call site (OBS-BR-08, OD-BR-03 item 1)",
    "capabilities": ["task-scoped retrieval exclusions"],
    "depends_on": ["R1-CTRL"],
    "mutation_scope": S("govbridge/core/taskctx.py", "govbridge/cli.py", "govbridge/route/real_routes.py",
                        "govbridge/compile/packet.py", "govbridge/graph/why.py", "govbridge/graph/impact.py",
                        "govbridge/graph/history.py", "govbridge/authority/state.py", "govbridge/core/exact.py",
                        "tests/route/test_task_exclusions.py", "tests/fixtures/route/exclusions/**"),
    "deliverables": [
        "govbridge/core/taskctx.py: a TaskContext loaded from --task <spec> or GOVBRIDGE_TASK, with one exclusion "
        "predicate used everywhere",
        "every CLI query command (search, why, impact, history, exact, state), and the compiler's seed code route and D.2 "
        "templates, apply the context; every output carries excluded_hits, a count, so the exclusion is disclosed",
    ],
    "acceptance_checks": [
        chk("cd $D && $PY -m pytest tests/route/test_task_exclusions.py -q",
            "exit 0. In a fixture repo whose excluded directory holds the best lexical and semantic match, every command "
            "and compile (seed route and D.2 included) return 0 excluded occurrences and a non-zero excluded_hits "
            "disclosure"),
        chk("grep -n 'routes.run(' $D/govbridge/compile/packet.py",
            "every call passes the task context's exclusions; no call omits them"),
        chk("python3 $D/ARCHITECTURE/REPAIR-1/evidence/tools/exclusion_probe.py <CONTROL-A task spec> (adapted to --task)",
            "totals.cli_default_no_exclude == 0 once the task context is set"),
    ],
    "routing": "sonnet",
    "size": "S",
    "parallel_group": "R1-PG1",
})

N.append({
    "id": "R1-RL",
    "title": "graph and lineage additions: tests beyond names, code->data and code->requirement edges, addressable "
             "state records, symbol introduction history, paging primitives",
    "capabilities": ["code/test lineage", "data dependencies", "requirement lineage", "structured-record identity",
                     "continuation"],
    "depends_on": ["R1-CTRL"],
    "mutation_scope": S("govbridge/code/**", "govbridge/graph/derive.py", "govbridge/graph/code_bridge.py",
                        "govbridge/graph/edges.py", "govbridge/graph/symbol_history.py", "govbridge/authority/records.py",
                        "config/id-grammar.yaml", "tests/code/**", "tests/graph/**",
                        "tests/authority/test_state_records.py", "tests/fixtures/code/**", "tests/fixtures/graph/**"),
    "deliverables": [
        "TESTS edges from (a) direct calls inside test functions, (b) tests that run the product binary with a "
        "subcommand, mapped through the CLI dispatch table to its handler, and (c) test registries recognised by path "
        "class and schema; each edge is labelled with its derivation",
        "DEPENDS_ON_DATA edges from string literals and joined path fragments that resolve to tracked repository paths",
        "CITES_REQUIREMENT edges from requirement citations in code comments (<document>:<line>, section references), "
        "resolved to the cited section",
        "record_def rows for the nested YAML keys and id-bearing list items of state files, so that `exact id` resolves "
        "them",
        "symbol INTRODUCED_IN / DELETED_IN over the indexed history layer, bounded by configuration, as a "
        "`symbol-history` query",
        "paging (cursor, page_size) for callers, tests_of and reads_key_of; a capped list returns a continuation handle",
        "every addition registered as a store layer with a digest (ARCHITECTURE.md section 8)",
    ],
    "acceptance_checks": [
        chk("cd $D && $PY -m pytest tests/code tests/graph tests/authority/test_state_records.py -q",
            "exit 0. Fixtures prove each edge kind with its label: a process-level test reaches its handler; a joined "
            "path literal reaches its data file; a comment citation reaches the cited section; a nested YAML key is "
            "resolved by `exact id`; a symbol's introducing commit is found; and a 50-caller symbol paged 8 at a time "
            "gives the same union as the unpaged query"),
        chk("$PY -m govbridge.core.freshness rebuild --from-clean (twice, into two fresh stores)",
            "identical digests for every new layer; freshness NOOP afterwards"),
        chk("$PY -m govbridge.code.symbols callers <a CONTROL-A symbol with more callers than the profile cap> "
            "--page-size 6",
            "a continuation handle; following it to exhaustion returns every call site that the unpaged query returns"),
    ],
    "routing": "sonnet",
    "size": "L",
    "parallel_group": "R1-PG1",
})

N.append({
    "id": "R1-RG",
    "title": "deterministic grader repair: GD-1..GD-10 and OBS-BR-05, each with a regression test (implements "
             "D-1..D-5)",
    "capabilities": ["demonstration grading"],
    "depends_on": ["R1-DEC"],
    "mutation_scope": S("govbridge/demo/**", "tests/integration/test_demo_grade.py",
                        "tests/integration/test_demo_grade_regressions.py", "tests/integration/test_extract_reads.py",
                        "tests/fixtures/demo/**"),
    "deliverables": [
        "the fixes of REPAIR_PLAN.md section 8.2: GD-1 line forms; GD-2 answer selection by the both-ways query id; GD-3 "
        "record by id OR section; GD-4 a generic withdrawn marker; GD-5 the enforcement-point rule; GD-6 read-extraction "
        "scope and govbridge argument parsing; GD-7 byte accounting per D-5; GD-8 per D-1; GD-9 [R] ingestion and AUTH "
        "per D-3; GD-10 enclosing-symbol matching; OBS-BR-05, the 1% check always on, over main plus supplementary "
        "packets",
        "one synthetic fixture set (oracle, answers, receipt, transcript) per defect, with no Review-8 content",
    ],
    "acceptance_checks": [
        chk("cd $D && $PY -m pytest tests/integration/test_demo_grade.py tests/integration/test_demo_grade_regressions.py "
            "tests/integration/test_extract_reads.py -q",
            "exit 0; one named regression test per GD-1..GD-10 and OBS-BR-05. Each fails when run against the pre-repair "
            "commit and passes after the repair"),
        chk("(orchestrator only, quarantined) $PY -m govbridge demo grade over run-1 with the run-1 oracle",
            "no crash; G6 is graded on the both-ways answer; the per-item [D] results equal BR-AR-0012's design-rule "
            "results except for the items that D-1 or GD-10 re-rule, each of which is listed. The orchestrator records "
            "the comparison without oracle values"),
    ],
    "routing": "sonnet (fixtures reviewed by the orchestrator)",
    "size": "M",
    "parallel_group": "R1-PG1",
})

N.append({
    "id": "R1-TA2",
    "title": "fresh test-author for run-2: a fresh oracle, sealed at an unrecorded location, with D-2 fact binding",
    "capabilities": ["demonstration oracle"],
    "depends_on": ["R1-DEC"],
    "mutation_scope": S("DEMONSTRATION/oracle-commitment-run-2.yaml", "DEMONSTRATION/oracle-tools/**"),
    "deliverables": [
        "a fresh oracle (schema govbridge-oracle/1 plus a per-fact binding, stage or chain, per D-2), written from "
        "primary sources only, in an orchestrator-created 0700 directory whose path is recorded in NO committed file, "
        "state entry or brief (OBS-BR-04, OBS-BR-10)",
        "DEMONSTRATION/oracle-commitment-run-2.yaml {oracle_sha256, author_run, author_model, written_at, schema}",
        "oracle-tools/check_oracle.py extended for the binding field",
    ],
    "acceptance_checks": [
        chk("python3 $D/DEMONSTRATION/oracle-tools/check_oracle.py <sealed path>",
            "exit 0; every must_state fact carries a binding; one enforcement stage per chain; one authority row per "
            "mandatory item"),
        chk("git grep -n '<sealed directory name>' -- . (run by the orchestrator)", "no match anywhere in the repository"),
        chk("sha256sum <sealed path>", "equals oracle-commitment-run-2.yaml"),
    ],
    "routing": "opus (fresh: not the run-1 test-author, not a builder, not BR-AR-0016)",
    "size": "M",
    "parallel_group": "R1-PG1",
    "notes": "reads primary sources at the view commits only; never builder branches, run-1 answers, REPAIR-1/** or "
             "bridge/grade-0012",
})

N.append({
    "id": "R1-RM",
    "title": "mandatory-input fidelity: no silent truncation; declared selectors honoured; directory items expanded; "
             "the receipt acknowledges what was delivered (RC-1)",
    "capabilities": ["mandatory-authoritative-input resolution", "bounded context compilation"],
    "depends_on": ["R1-RX"],
    "mutation_scope": S("govbridge/authority/resolver.py", "govbridge/compile/packet.py", "govbridge/compile/budgets.py",
                        "govbridge/compile/render.py", "govbridge/compile/receipt.py", "govbridge/compile/validate.py",
                        "govbridge/compile/sectionmap.py", "tests/compile/test_mandatory_fidelity.py",
                        "tests/fixtures/compile/mandatory/**"),
    "deliverables": [
        "item_from_mandatory never cuts text. An item over the per-item cap is delivered as a section map (headings or "
        "keys, with line ranges and hashes) plus facet-selected sections plus a by-reference remainder, with the J "
        "notice MANDATORY_PARTIAL_DELIVERY listing every undelivered range (REPAIR_PLAN.md section 3)",
        "the resolver honours `entries` (an id range), `keys` (YAML keys) and multiple `paths`; an unresolvable selector "
        "fails closed with a J notice",
        "a by-reference directory is expanded to a member manifest (path, blob, size, class)",
        "the receipt and manifest carry delivered_sha256 and source_sha256 separately; packet verify checks both",
    ],
    "acceptance_checks": [
        chk("cd $D && $PY -m pytest tests/compile/test_mandatory_fidelity.py tests/compile -q",
            "exit 0, with the whole compile suite still green. Fixtures: an oversize item never ends mid-content without "
            "the notice; an id-range selector delivers exactly those entries; a key selector exactly those keys; a "
            "two-path item both paths; a directory item a member manifest; section A is never dropped"),
        chk("grep -n 'max_chars' $D/govbridge/compile/packet.py",
            "no truncation of mandatory items; any remaining cap applies only to RETRIEVED or DERIVED excerpts and is "
            "disclosed"),
        chk("$PY -m govbridge compile <CONTROL-A task spec with >= 1 oversize mandatory item and >= 1 selector> --out "
            "/tmp/rm && $PY -m govbridge packet verify /tmp/rm",
            "PASS; every A item has delivered_bytes == source_bytes, or a MANDATORY_PARTIAL_DELIVERY notice with its "
            "ranges"),
    ],
    "routing": "sonnet",
    "size": "M",
    "parallel_group": "R1-PG2",
})

N.append({
    "id": "R1-GA1",
    "title": "govbridge gather, core: query instantiation, facet registry, deterministic parallel facet retrieval, "
             "paging and continuation with a configurable batch size, stopping reasons, telemetry (OD-BR-05 s1, s2, s4, "
             "s5, s9 telemetry)",
    "capabilities": ["multi-facet, multi-batch retrieval"],
    "depends_on": ["R1-RX", "R1-RL"],
    "mutation_scope": S("govbridge/gather/__init__.py", "govbridge/gather/instantiate.py", "govbridge/gather/facets.py",
                        "govbridge/gather/engine.py", "govbridge/gather/telemetry.py", "config/facets.yaml",
                        "config/budgets.yaml", "govbridge/route/real_routes.py", "govbridge/route/router.py",
                        "govbridge/lexical/query.py", "govbridge/semantic/search.py", "govbridge/semantic/vectors.py",
                        "govbridge/cli.py", "tests/gather/test_engine.py", "tests/gather/test_instantiate.py",
                        "tests/fixtures/gather/**"),
    "deliverables": [
        "instantiation of {class, subject} entries from the query file's own tables; a query that cannot be made "
        "executable is the compile error QUERY_NOT_EXECUTABLE and is never skipped (RC-2)",
        "config/facets.yaml: generic facets (REPAIR_PLAN.md section 2.2) with routes, path-class scopes, query builders, "
        "batch size and minimum share; a class -> facet mapping; no instance-specific names",
        "the engine: rounds; the facets of a round run concurrently with a deterministic merge order; per-facet cursors "
        "(lexical and semantic offset, code paging from R1-RL); batch_size from configuration (no hard-coded 8); stop "
        "reasons from the fixed vocabulary",
        "telemetry per gather: rounds, per round and facet the candidates (items, bytes), deduplication counts, final "
        "bytes, stop reason, unresolved identifiers",
        "`govbridge gather --task <spec> --query <id|text> [--batch-size N] [--max-rounds N] [--threads N]`",
    ],
    "acceptance_checks": [
        chk("cd $D && $PY -m pytest tests/gather/test_engine.py tests/gather/test_instantiate.py -q",
            "exit 0. A fixture query file with class x subject entries yields one executable query per entry; a "
            "malformed entry raises QUERY_NOT_EXECUTABLE; a fixture subject whose evidence spans 5 directories and "
            "exceeds one batch is covered after more than one round; stop_reason is one of FACETS_COVERED, "
            "NO_UNRESOLVED_IDENTIFIERS, MARGINAL_GAIN_ONLY_DUPLICATES, MAX_ROUNDS, BUDGET_REACHED_WITH_UNRESOLVED"),
        chk("$PY -m govbridge gather --task <CONTROL-A spec> --query <CONTROL-A query> with --threads 1, 4 and 16",
            "a byte-identical merged result (equal sha256) across thread counts"),
        chk("the same query with --batch-size 2 and with --batch-size 16",
            "an identical merged evidence set; more rounds for the smaller batch; a telemetry row for every round"),
        chk("grep -rnE 'k: int = 8|DEFAULT_K = 8|k=8\\b' $D/govbridge/",
            "no match outside the configuration-default loader; 8 survives only as configuration"),
    ],
    "routing": "sonnet",
    "size": "L",
    "parallel_group": "R1-PG2",
})

N.append({
    "id": "R1-GA2",
    "title": "gather, adaptive follow-up and merge: identifier extraction and resolution, triggered rounds, "
             "provenance-preserving deduplication, occurrence collapse, version reconciliation, authority and lifecycle "
             "filtering (OD-BR-05 s3, s6)",
    "capabilities": ["sequential and adaptive multi-hop retrieval", "provenance-preserving merge",
                     "version reconciliation"],
    "depends_on": ["R1-GA1", "R1-RL"],
    "mutation_scope": S("govbridge/gather/followup.py", "govbridge/gather/identifiers.py", "govbridge/gather/merge.py",
                        "govbridge/gather/versions.py", "tests/gather/test_followup.py", "tests/gather/test_merge.py",
                        "tests/fixtures/gather/followup/**"),
    "deliverables": [
        "identifier extractors for id-grammar ids, symbol-shaped tokens, path literals and joined fragments, test names, "
        "commit hashes and requirement citations; resolvers via exact id, code definitions, callers and tests, path "
        "resolution, and the sections of a known document",
        "follow-up rounds with a visited set; every follow-up item records its trigger (the identifier and its source "
        "item)",
        "merge: deduplication by (blob, line span); a provenance list per item (routes, facets, rounds, triggers); "
        "occurrences collapsed to the canonical occurrence plus a per-ref identity summary; a `versions` facet reporting "
        "per-path blob identity across the view's refs and the canonical ref; authority and lifecycle filtering "
        "unchanged (A only from the resolver)",
    ],
    "acceptance_checks": [
        chk("cd $D && $PY -m pytest tests/gather/test_followup.py tests/gather/test_merge.py -q",
            "exit 0. In the fixture, a record citing an id defined elsewhere, a function whose tests live in another "
            "directory, a joined path literal and a comment requirement citation are each reached within 3 rounds, with "
            "the trigger recorded. The same item found by three routes is one merged item with three provenance entries. "
            "A 3-ref fixture reports identical or different per ref. A superseded item is filtered to E with its banner"),
        chk("$PY -m govbridge gather --task <CONTROL-A spec> --query <CONTROL-A query> --json | jq '.telemetry'",
            ">= 1 round whose trigger is an identifier first seen in an earlier round; merged items carry provenance; no "
            "search hit lists more than one occurrence row plus a ref summary"),
    ],
    "routing": "sonnet",
    "size": "L",
    "parallel_group": "R1-PG3",
})

N.append({
    "id": "R1-RS",
    "title": "supplementary packets for every query command; occurrence collapse; bootstrap by reference; task inputs "
             "in section I (OBS-BR-06, OBS-BR-07)",
    "capabilities": ["budgeted supplementary retrieval output with manifests"],
    "depends_on": ["R1-GA1", "R1-RM"],
    "mutation_scope": S("govbridge/compile/supplementary.py", "govbridge/compile/bootstrap.py",
                        "govbridge/compile/receipt.py", "govbridge/compile/validate.py", "govbridge/compile/section_i.py",
                        "govbridge/cli.py", "tests/compile/test_supplementary.py",
                        "tests/compile/test_section_i_and_bootstrap.py", "tests/fixtures/compile/supplementary/**"),
    "deliverables": [
        "every query command (search, why, impact, history, exact, state, gather) writes a supplementary packet "
        "directory (manifest.json, packet.md, meta.json, packet hash, read tokens) under --out. Each is budgeted by a "
        "per-command profile and deduplicated, by item id, against the main packet and earlier supplementary packets. "
        "Raw JSON is available only behind --raw",
        "`packet verify` and `receipt check` cover the main packet and every supplementary packet",
        "section I carries the task's instantiated query set and the answers and receipt schemas, verbatim and by hash",
        "the bootstrap references the packet by id and hash and does not inline it",
    ],
    "acceptance_checks": [
        chk("cd $D && $PY -m pytest tests/compile/test_supplementary.py tests/compile/test_section_i_and_bootstrap.py -q",
            "exit 0. A fixture search writes a verifiable supplementary packet; a hit already in the main packet appears "
            "only by reference; no hit carries more than one occurrence row plus a ref summary; a receipt that omits a "
            "supplementary packet fails"),
        chk("$PY -m govbridge search --task <CONTROL-A spec> '<CONTROL-A query>' --out /tmp/s1 && "
            "$PY -m govbridge packet verify /tmp/s1",
            "PASS; bytes within the command profile; meta.json carries packet_sha256"),
        chk("$PY -m govbridge bootstrap <CONTROL-A spec> | wc -c",
            "well under the packet size, because the packet is referenced, not inlined"),
    ],
    "routing": "sonnet",
    "size": "M",
    "parallel_group": "R1-PG3",
})

N.append({
    "id": "R1-GA3",
    "title": "compile from gather: facet quotas and a facet-aware drop order; content slices instead of pointers; "
             "per-item query and facet tags; overflow to evidence notes and supplementary packets; D.2 via gather (RC-4, "
             "RC-5; OD-BR-05 s6-s8)",
    "capabilities": ["bounded context compilation over multi-round evidence"],
    "depends_on": ["R1-GA2", "R1-RS", "R1-RN", "R1-RM"],
    "mutation_scope": S("govbridge/compile/packet.py", "govbridge/compile/budgets.py", "govbridge/compile/render.py",
                        "govbridge/compile/codesurfaces.py", "govbridge/compile/overflow.py", "config/budgets.yaml",
                        "tests/compile/test_facet_quotas.py", "tests/compile/test_content_slices.py",
                        "tests/compile/test_overflow_notes.py", "tests/fixtures/compile/gather/**"),
    "deliverables": [
        "the compiler builds sections B-H from gather results for every task query (instantiated), with per-item query "
        "ids and facets",
        "facet quotas (a minimum share for every requested facet that has candidates) and a drop order that is "
        "round-robin across facets; a resolution label is never a global sort key; per-facet drops are disclosed with "
        "continuation handles",
        "code and test items carry their definition body slice (max_slice_chars, larger for a facet's top items); "
        "semantic items carry chunk text; content already present is cited by item id",
        "when merged evidence exceeds the profile: evidence notes (the R1-RN schema) plus supplementary packets (R1-RS). "
        "The main packet keeps the mandatory sources, the notes and each facet's top items; nothing is silently "
        "discarded",
        "D.2 both-ways evidence is produced by gather with the task context's exclusions",
    ],
    "acceptance_checks": [
        chk("cd $D && $PY -m pytest tests/compile -q",
            "exit 0. Fixtures: a facet with 40 heuristic-label candidates beside 300 exact-label candidates of another "
            "facet keeps at least its minimum share; no symbol or semantic item has a 0-byte body; an over-budget fixture "
            "produces notes that pass `govbridge notes validate` and supplementary packets that pass `packet verify`; "
            "quotas leave section A unchanged"),
        chk("$PY -m govbridge compile <CONTROL-A spec> --out /tmp/c1 (twice) && $PY -m govbridge packet verify /tmp/c1",
            "byte-identical packets; PASS; every requested facet of every query is present, or disclosed as MISSING or "
            "BUDGET with a handle; the main packet is within the profile total"),
    ],
    "routing": "sonnet",
    "size": "L",
    "parallel_group": "R1-PG4",
})

N.append({
    "id": "R1-RA",
    "title": "answer-side aids: govbridge cite and govbridge answers lint (RC-11)",
    "capabilities": ["citation resolution", "answer completeness lint"],
    "depends_on": ["R1-GA2", "R1-RS"],
    "mutation_scope": S("govbridge/answers/**", "govbridge/cli.py", "tests/answers/**", "tests/fixtures/answers/**"),
    "deliverables": [
        "`govbridge cite <identifier> [--commit C]` returns an exact (path, commit, lines, symbol if any), or AMBIGUOUS "
        "with every candidate",
        "`govbridge answers lint <answers> --packet DIR [--supplementary DIR...]` reports four kinds of finding: "
        "NAMED_NOT_CITED (an identifier in a claim that resolves in the index and has no citation), DOC_LEVEL_CITATION (a "
        "whole-document citation of a document that has a section map), CROSS_ANSWER_REFERENCE and NOT_SELF_CONTAINED. "
        "Output is machine-readable; exit 1 on findings unless they are waived",
    ],
    "acceptance_checks": [
        chk("cd $D && $PY -m pytest tests/answers -q",
            "exit 0. A fixture answer that names three tests and cites one yields two NAMED_NOT_CITED; a whole-document "
            "citation of a sectioned fixture document yields DOC_LEVEL_CITATION with the suggested section anchor; `cite` "
            "resolves a test name to its definition span"),
    ],
    "routing": "sonnet",
    "size": "M",
    "parallel_group": "R1-PG4",
})

N.append({
    "id": "R1-INT",
    "title": "integration I2: whole suite, store rebuild from clean, determinism, generic-rule audit, CONTROL-A before "
             "and after, observation closure",
    "capabilities": ["integration proof"],
    "depends_on": ["R1-RG", "R1-GA3", "R1-RA", "R1-RN", "R1-RL", "R1-RX", "R1-RM", "R1-RS"],
    "mutation_scope": S("tests/integration/test_repair1_integration.py", "EVIDENCE/repair-1/**"),
    "deliverables": [
        "EVIDENCE/repair-1/int-*.out: the suite, rebuild digests, determinism, the audit, CONTROL-A compile and gather "
        "telemetry, and the before/after comparison against tests/fixtures/controls/control-a/baseline/",
    ],
    "acceptance_checks": [
        chk("cd $D && $PY -m pytest tests -q",
            "exit 0; every pre-existing test is still green, plus all REPAIR-1 tests"),
        chk("$PY -m govbridge.core.freshness rebuild --from-clean into two fresh stores",
            "identical build-manifest digests; freshness NOOP; coverage unclassified 0"),
        chk("grep -rnE 'P2-AR-0097|Review[- ]?8|REVIEW-8' $D/govbridge $D/config $D/tests --include=*.py --include=*.yaml, "
            "excluding fixture data files and the demonstration query file",
            "no match (the generic-rule audit, OC-BR-02)"),
        chk("$PY -m govbridge compile <CONTROL-A spec> --out /tmp/i1 && $PY -m govbridge packet verify /tmp/i1 && "
            "$PY -m govbridge gather --task <CONTROL-A spec> --query <CONTROL-A query> --json",
            "PASS; stop_reason recorded; every requested facet covered or disclosed; main plus supplementary bytes under "
            "1% of the corpus; wall time within the configured gather budget; before/after shows no facet lost relative "
            "to the baseline"),
        chk("python3 $D/tools/check_state.py verify", "STATE_CONSISTENT"),
    ],
    "routing": "sonnet",
    "size": "M",
    "parallel_group": "R1-PG5",
})

N.append({
    "id": "R1-MB",
    "title": "OD-BR-05 s9 multi-batch demonstration: a CONTROL-B query plus one further unrelated control, a fresh "
             "agent, telemetry acceptance",
    "capabilities": ["demonstrated multi-batch and multi-hop retrieval"],
    "depends_on": ["R1-INT"],
    "mutation_scope": S("DEMONSTRATION/mb-1/**"),
    "deliverables": [
        "DEMONSTRATION/mb-1/{task spec, packet, supplementary packets, telemetry, answers, receipt, grade.yaml}, for a "
        "CONTROL-B query chosen by the orchestrator at dispatch (conventions.unrelated_controls) and one further "
        "unrelated control query",
    ],
    "acceptance_checks": [
        chk("jq over the DEMONSTRATION/mb-1 telemetry",
            "for the query AND for the control: rounds >= 2; >= 1 round with >= 2 facets retrieved concurrently; >= 1 "
            "follow-up round whose trigger identifier was first seen in an earlier round; candidate bytes greater than "
            "the configured batch_size bytes; merged evidence from >= 3 distinct top-level directories; every merged "
            "item has provenance; every requested facet is covered, or MISSING with a reason; stop_reason is in the "
            "fixed vocabulary"),
        chk("$PY -m govbridge packet verify on the main packet and every supplementary packet; "
            "$PY -m govbridge receipt check", "PASS"),
        chk("$PY -m govbridge answers lint DEMONSTRATION/mb-1/answers.yaml --packet ... --supplementary ...",
            "no unwaived finding"),
        chk("a fresh grader (opus) confirms the telemetry checks and that every claim cites a merged item",
            "MB_PASS recorded in grade.yaml"),
    ],
    "routing": "the orchestrator dispatches a fresh opus demonstration agent and a fresh opus grader",
    "size": "M",
    "parallel_group": "R1-PG6",
})

N.append({
    "id": "R1-D2",
    "title": "run-2 store build at the frozen, repaired bridge tip (freeze per OBS-BR-03)",
    "capabilities": ["demonstration view"],
    "depends_on": ["R1-MB"],
    "mutation_scope": S("DEMONSTRATION/run-2/build/**"),
    "deliverables": [
        "a store $HOME/.cache/gov-bridge/store-<RUN_ID>, built from clean at the frozen tip; coverage and freshness outputs "
        "committed",
    ],
    "acceptance_checks": [
        chk("$PY -m govbridge coverage --view $D/config/canonical-view.yaml", "unclassified 0 for every view ref"),
        chk("$PY -m govbridge freshness", "NOOP"),
    ],
    "routing": "orchestrator (deterministic)",
    "size": "S",
    "parallel_group": "R1-PG7",
})

N.append({
    "id": "R1-DEMO2",
    "title": "run-2 demonstration: a fresh opus agent, the same public queries, the repaired bridge, lint required",
    "capabilities": ["demonstration"],
    "depends_on": ["R1-D2", "R1-TA2"],
    "mutation_scope": S("DEMONSTRATION/run-2/**"),
    "deliverables": [
        "run-2 bootstrap; main packet (section I carries the task inputs); supplementary packets only, with no raw "
        "dumps; answers.yaml; receipt.yaml covering every packet; answers-lint output with justified waivers; "
        "reads.json; a secrecy and consumption audit",
    ],
    "acceptance_checks": [
        chk("$PY -m govbridge receipt check --packet <main> --receipt receipt.yaml (with every supplementary packet)",
            "PASS"),
        chk("a transcript audit (orchestrator) for the sealed path, .authoring, oracle files, excluded paths, REPAIR-1/** "
            "and bridge/grade-0012", "0 accesses"),
    ],
    "routing": "opus (fresh; no prior chat; not a builder, not TA2, not BR-AR-0016)",
    "size": "M",
    "parallel_group": "R1-PG8",
})

N.append({
    "id": "R1-GRADE2",
    "title": "run-2 grading: the repaired deterministic grader, then a fresh opus rubric grader under D-1..D-5",
    "capabilities": ["demonstration grading"],
    "depends_on": ["R1-DEMO2", "R1-RG"],
    "mutation_scope": S("DEMONSTRATION/grading-run-2/**", "DEMONSTRATION/oracle-run-2/**"),
    "deliverables": [
        "the unsealed run-2 oracle copy (sha256 equal to the commitment), the deterministic grade, the rubric grade, and "
        "a grading report per schemas/grading-report.yaml with G1..G8 and a per-gate reason list",
    ],
    "acceptance_checks": [
        chk("sha256sum DEMONSTRATION/oracle-run-2/oracle.yaml", "equals DEMONSTRATION/oracle-commitment-run-2.yaml"),
        chk("$PY -m govbridge demo grade ... (repaired)",
            "exit 0 or 1 according to the verdict, never a crash; G1 and G2 cover every supplementary packet; G7 applies "
            "the 1% check"),
    ],
    "routing": "the deterministic tool, then opus (fresh)",
    "size": "M",
    "parallel_group": "R1-PG9",
})

header = ("# REPAIR-1 implementation DAG (BR-AR-0016). Same node format as ARCHITECTURE/IMPLEMENTATION_DAG.yaml: id, title,\n"
          "# depends_on, mutation_scope (inside the domain), deliverables, acceptance_checks (cmd + expect), routing, size,\n"
          "# parallel_group. PROPOSED; no node has been dispatched. Generated from a checked data structure (ordering and\n"
          "# scope disjointness verified; see AGENT_RUNS/BR-AR-0016.checkpoint.yaml).\n")
out = sys.argv[1]
with open(out, "w") as fh:
    fh.write(header)
    yaml.safe_dump(dag, fh, sort_keys=False, width=118, allow_unicode=True, default_flow_style=False)
print("written", out)
