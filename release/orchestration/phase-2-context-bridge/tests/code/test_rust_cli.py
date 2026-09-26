"""``govbridge.code.rust_cli`` (BR-AR-0019 reopening, Gap 2): Rust clap-derive CLI dispatch, TESTS edges from a
Rust integration test that spawns the product binary through a CARGO_BIN_EXE helper, direct or through one
resolved wrapper function. Every fixture here is synthetic (OC-BR-02): no Review-8/Phase-2/product symbol or
file name.
"""
from __future__ import annotations

from govbridge.code import rust_cli as RC
from govbridge.graph import edges as E

MAIN_RS = """
use clap::{Parser, Subcommand};

#[derive(Parser)]
struct Cli {
    #[command(subcommand)]
    cmd: Cmd,
}

#[derive(Subcommand)]
enum Cmd {
    Version,
    CancelAgents {
        reason: Option<String>,
    },
    Research {
        #[command(subcommand)]
        op: ResearchCmd,
    },
    #[command(name = "override-name")]
    Weird,
    Adopt {
        #[command(subcommand)]
        stage: AdoptCmd,
    },
}

#[derive(Subcommand)]
enum ResearchCmd {
    Record { fields: String },
    Show { id: String },
}

#[derive(Subcommand)]
enum AdoptCmd {
    A0,
}

fn dispatch(cli: &Cli) {
    match &cli.cmd {
        Cmd::Version => print_version(),
        Cmd::CancelAgents { reason } => {
            let p = setup();
            cancel(&p, reason)
        }
        Cmd::Research { op } => match op {
            ResearchCmd::Record { fields } => research::record(fields),
            ResearchCmd::Show { id } => research::show(id),
        },
        Cmd::Weird => weird_handler(),
        Cmd::Adopt { stage } => match stage {
            AdoptCmd::A0 => a0_handler(),
        },
    }
}
"""

TEST_RS_DIRECT = """
use std::process::Command;

fn my_bin() -> std::path::PathBuf {
    std::path::PathBuf::from(env!("CARGO_BIN_EXE_mybin"))
}

#[test]
fn test_direct_command_new() {
    let out = Command::new(my_bin())
        .args(["cancel-agents", "--reason", "x"])
        .output()
        .unwrap();
}

#[test]
fn test_nested_subcommand() {
    let out = Command::new(my_bin()).args(["research", "record"]).output().unwrap();
}

#[test]
fn test_unresolvable_outer_arm() {
    // "adopt" has a nested enum (AdoptCmd), but the test gives no second token -- outer arm only.
    let out = Command::new(my_bin()).args(["adopt"]).output().unwrap();
}

#[test]
fn test_unknown_subcommand_is_skipped_not_crashed() {
    let out = Command::new(my_bin()).args(["not-a-real-subcommand"]).output().unwrap();
}
"""

TEST_RS_WRAPPER = """
use std::process::Command;

fn my_bin() -> std::path::PathBuf {
    std::path::PathBuf::from(env!("CARGO_BIN_EXE_mybin"))
}

fn run_wrapped(session: &str, args: &[&str]) -> Vec<u8> {
    let mut c = Command::new(my_bin());
    c.arg("--session").arg(session).args(args);
    c.output().unwrap().stdout
}

#[test]
fn test_via_one_level_wrapper() {
    let out = run_wrapped("S-1", &["research", "show", "id-1"]);
}
"""


def _build(text: str) -> dict:
    return RC.build_dispatch_map(text)


def test_build_dispatch_map_kebab_cases_and_records_override():
    dispatch = _build(MAIN_RS)
    assert dispatch[("Cmd", "CancelAgents")]["subcommand"] == "cancel-agents"
    assert dispatch[("Cmd", "Weird")]["subcommand"] == "override-name"


def test_build_dispatch_map_records_nested_subcommand_field():
    dispatch = _build(MAIN_RS)
    entry = dispatch[("Cmd", "Research")]
    assert entry["nested_enum"] == "ResearchCmd"
    assert entry["nested_field"] == "op"
    entry_adopt = dispatch[("Cmd", "Adopt")]
    assert entry_adopt["nested_enum"] == "AdoptCmd"


def test_resolve_dispatch_direct_handler():
    dispatch = _build(MAIN_RS)
    r = RC.resolve_dispatch(dispatch, "Cmd", ["version"])
    assert r == {"handler": "print_version", "label": "inner", "enum_name": "Cmd", "variant_name": "Version",
                 "matched_tokens": 1}


def test_resolve_dispatch_unwraps_block_tail_call():
    """BR-AR-0019 reopening's own worked example shape: a block doing setup before its real dispatch call."""
    dispatch = _build(MAIN_RS)
    r = RC.resolve_dispatch(dispatch, "Cmd", ["cancel-agents"])
    assert r["handler"] == "cancel"
    assert r["label"] == "inner"


def test_resolve_dispatch_nested_two_levels():
    dispatch = _build(MAIN_RS)
    r = RC.resolve_dispatch(dispatch, "Cmd", ["research", "record"])
    assert r["handler"] == "research::record"
    assert r["label"] == "inner"
    assert r["enum_name"] == "ResearchCmd"
    assert r["matched_tokens"] == 2


def test_resolve_dispatch_falls_back_to_outer_arm_when_not_determinable():
    dispatch = _build(MAIN_RS)
    r = RC.resolve_dispatch(dispatch, "Cmd", ["adopt"])  # no second token -- cannot walk into AdoptCmd
    assert r["label"] == "outer"
    assert r["enum_name"] == "Cmd"
    assert r["variant_name"] == "Adopt"


def test_resolve_dispatch_unknown_token_returns_none():
    dispatch = _build(MAIN_RS)
    assert RC.resolve_dispatch(dispatch, "Cmd", ["not-a-subcommand"]) is None


def test_find_cargo_bin_exe_helpers():
    helpers = RC.find_cargo_bin_exe_helpers(TEST_RS_DIRECT)
    assert helpers == {"my_bin"}


def test_find_wrapper_functions_direct():
    helpers = {"my_bin"}
    wrappers = RC.find_wrapper_functions(TEST_RS_WRAPPER, helpers)
    assert wrappers["run_wrapped"]["kind"] == "direct"
    assert wrappers["run_wrapped"]["param_index"] == 1


def test_rust_cli_dispatch_tests_edges_direct_and_nested():
    dispatch = _build(MAIN_RS)
    helpers = RC.find_cargo_bin_exe_helpers(TEST_RS_DIRECT)
    wrappers = RC.find_wrapper_functions(TEST_RS_DIRECT, helpers)
    edges, unresolved = RC.rust_cli_dispatch_tests_edges(TEST_RS_DIRECT, "tests/fixtures/test_direct.rs",
                                                          "deadbeef", dispatch, helpers, wrappers)
    assert unresolved == []
    by_test = {e.src: e for e in edges}
    assert by_test["test_direct_command_new"].dst == "cancel"
    assert by_test["test_direct_command_new"].derivation == E.EXACT_RUST_CLI_DISPATCH
    assert by_test["test_nested_subcommand"].dst == "research::record"
    assert by_test["test_nested_subcommand"].derivation == E.EXACT_RUST_CLI_DISPATCH
    assert by_test["test_unresolvable_outer_arm"].dst == "Cmd::Adopt"
    assert by_test["test_unresolvable_outer_arm"].derivation == E.HEURISTIC_RUST_CLI_DISPATCH_OUTER_ARM
    assert "test_unknown_subcommand_is_skipped_not_crashed" not in by_test


def test_rust_cli_dispatch_tests_edges_one_level_wrapper_indirection():
    """BR-AR-0019 reopening's own bound: 'allow bounded wrapper indirection, one level at least'."""
    dispatch = _build(MAIN_RS)
    helpers = RC.find_cargo_bin_exe_helpers(TEST_RS_WRAPPER)
    wrappers = RC.find_wrapper_functions(TEST_RS_WRAPPER, helpers)
    edges, unresolved = RC.rust_cli_dispatch_tests_edges(TEST_RS_WRAPPER, "tests/fixtures/test_wrapper.rs",
                                                          "deadbeef", dispatch, helpers, wrappers)
    assert unresolved == []
    assert len(edges) == 1
    assert edges[0].src == "test_via_one_level_wrapper"
    assert edges[0].dst == "research::show"
    assert edges[0].derivation == E.EXACT_RUST_CLI_DISPATCH


def test_rust_cli_dispatch_tests_edges_empty_without_helpers_or_dispatch():
    assert RC.rust_cli_dispatch_tests_edges(TEST_RS_DIRECT, "x.rs", "deadbeef", {}, set(), {}) == ([], [])
    dispatch = _build(MAIN_RS)
    assert RC.rust_cli_dispatch_tests_edges(TEST_RS_DIRECT, "x.rs", "deadbeef", dispatch, set(), {}) == ([], [])


def test_resolve_wrapper_chain_bounded():
    """A forward chain longer than MAX_WRAPPER_CHAIN fails closed (None), never crashes or loops forever."""
    wrappers = {}
    n = RC.MAX_WRAPPER_CHAIN + 3
    for i in range(n):
        target = f"w{i + 1}" if i + 1 < n else None
        kind = "forward" if target else "direct"
        wrappers[f"w{i}"] = {"param_name": "args", "param_index": 0, "kind": kind, "target": target}
    assert RC.resolve_wrapper_chain(wrappers, "w0") is None  # chain too long to resolve within the bound
    # a chain that fits within the bound DOES resolve
    short = {
        "outer": {"param_name": "args", "param_index": 0, "kind": "forward", "target": "inner"},
        "inner": {"param_name": "args", "param_index": 0, "kind": "direct", "target": None},
    }
    assert RC.resolve_wrapper_chain(short, "outer") is not None


# --- BR-AR-0019 reopening (third pass), Defect B: the harness-METHOD shape (<receiver>.ok(&[...])) -------------

TEST_RS_HARNESS = """
use std::process::Command;

fn my_bin() -> std::path::PathBuf {
    std::path::PathBuf::from(env!("CARGO_BIN_EXE_mybin"))
}

struct Harness { session: String }

impl Harness {
    fn new() -> Self { Harness { session: "s".into() } }

    fn ok(&self, args: &[&str]) -> Vec<u8> {
        Command::new(my_bin()).args(args).output().unwrap().stdout
    }

    fn ok_via_forward(&self, args: &[&str]) -> Vec<u8> {
        self.ok(args)
    }
}

#[test]
fn test_harness_declared_type() {
    let h = Harness::new();
    let out = h.ok(&["research", "show", "id-1"]);
}

#[test]
fn test_harness_forward_method() {
    let h: Harness = Harness::new();
    let out = h.ok_via_forward(&["version"]);
}

#[test]
fn test_harness_dedup_same_handler_twice() {
    let h = Harness::new();
    let a = h.ok(&["version"]);
    let b = h.ok(&["version"]);
}
"""

TEST_RS_HARNESS_UNTYPED = """
fn my_bin() -> std::path::PathBuf {
    std::path::PathBuf::from(env!("CARGO_BIN_EXE_mybin"))
}

fn make_harness() -> Harness2 { Harness2 {} }

struct Harness2;

impl Harness2 {
    fn ok(&self, args: &[&str]) -> Vec<u8> {
        Command::new(my_bin()).args(args).output().unwrap().stdout
    }
}

#[test]
fn test_harness_unique_name_fallback() {
    // `make_harness()` is not a `let <var>: Type = ...`/`let <var> = Type::ctor()` binding this scan follows,
    // so the receiver's type is undetermined -- resolved only because "ok" is unique across every harness type.
    let out = make_harness().ok(&["research", "show", "id-2"]);
}
"""

TEST_RS_HARNESS_AMBIGUOUS = """
fn my_bin() -> std::path::PathBuf {
    std::path::PathBuf::from(env!("CARGO_BIN_EXE_mybin"))
}

struct Alpha;
impl Alpha {
    fn ok(&self, args: &[&str]) -> Vec<u8> {
        Command::new(my_bin()).args(args).output().unwrap().stdout
    }
}
struct Beta;
impl Beta {
    fn ok(&self, args: &[&str]) -> Vec<u8> {
        Command::new(my_bin()).args(args).output().unwrap().stdout
    }
}

#[test]
fn test_ambiguous_harness_method() {
    let out = make_either().ok(&["version"]);
}
"""


def test_find_impl_wrapper_methods_direct_and_forward():
    helpers = {"my_bin"}
    wrappers = RC.find_impl_wrapper_methods(TEST_RS_HARNESS, helpers)
    assert wrappers["Harness::ok"]["kind"] == "direct"
    assert wrappers["Harness::ok"]["param_index"] == 0
    assert wrappers["Harness::ok_via_forward"] == {
        "param_name": "args", "param_index": 0, "kind": "forward", "target": "Harness::ok",
    }


def test_impl_wrapper_candidate_prefilter():
    assert RC.impl_wrapper_candidate(TEST_RS_HARNESS) is True
    assert RC.impl_wrapper_candidate("fn plain() {}") is False


def test_rust_cli_dispatch_tests_edges_harness_declared_type():
    dispatch = _build(MAIN_RS)
    helpers = RC.find_cargo_bin_exe_helpers(TEST_RS_HARNESS)
    wrappers = RC.find_impl_wrapper_methods(TEST_RS_HARNESS, helpers)
    edges, unresolved = RC.rust_cli_dispatch_tests_edges(TEST_RS_HARNESS, "tests/fixtures/test_harness.rs",
                                                          "deadbeef", dispatch, helpers, wrappers)
    assert unresolved == []
    by_test = {e.src: e for e in edges}
    assert by_test["test_harness_declared_type"].dst == "research::show"
    assert by_test["test_harness_declared_type"].derivation == E.EXACT_RUST_CLI_DISPATCH
    # a forward through a SECOND harness method (self.ok(args)) resolves too, one level of chaining
    assert by_test["test_harness_forward_method"].dst == "print_version"
    assert by_test["test_harness_forward_method"].derivation == E.EXACT_RUST_CLI_DISPATCH


def test_rust_cli_dispatch_tests_edges_harness_dedup_per_test_and_handler():
    dispatch = _build(MAIN_RS)
    helpers = RC.find_cargo_bin_exe_helpers(TEST_RS_HARNESS)
    wrappers = RC.find_impl_wrapper_methods(TEST_RS_HARNESS, helpers)
    edges, _ = RC.rust_cli_dispatch_tests_edges(TEST_RS_HARNESS, "tests/fixtures/test_harness.rs", "deadbeef",
                                                 dispatch, helpers, wrappers)
    dedup_edges = [e for e in edges if e.src == "test_harness_dedup_same_handler_twice"]
    assert len(dedup_edges) == 1  # two identical `h.ok(&["version"])` calls -> ONE edge, not two


def test_rust_cli_dispatch_tests_edges_harness_unique_name_fallback():
    dispatch = _build(MAIN_RS)
    helpers = RC.find_cargo_bin_exe_helpers(TEST_RS_HARNESS_UNTYPED)
    wrappers = RC.find_impl_wrapper_methods(TEST_RS_HARNESS_UNTYPED, helpers)
    edges, unresolved = RC.rust_cli_dispatch_tests_edges(TEST_RS_HARNESS_UNTYPED, "tests/fixtures/test_h2.rs",
                                                          "deadbeef", dispatch, helpers, wrappers)
    assert unresolved == []
    assert len(edges) == 1
    assert edges[0].dst == "research::show"
    assert edges[0].derivation == E.HEURISTIC_RUST_CLI_HARNESS_UNIQUE_METHOD
    assert "unique_name" in edges[0].note


def test_rust_cli_dispatch_tests_edges_ambiguous_harness_method_is_recorded_not_dropped():
    dispatch = _build(MAIN_RS)
    helpers = RC.find_cargo_bin_exe_helpers(TEST_RS_HARNESS_AMBIGUOUS)
    wrappers = RC.find_impl_wrapper_methods(TEST_RS_HARNESS_AMBIGUOUS, helpers)
    assert "Alpha::ok" in wrappers and "Beta::ok" in wrappers
    edges, unresolved = RC.rust_cli_dispatch_tests_edges(TEST_RS_HARNESS_AMBIGUOUS, "tests/fixtures/test_amb.rs",
                                                          "deadbeef", dispatch, helpers, wrappers)
    assert edges == []  # never guess between Alpha::ok and Beta::ok
    assert len(unresolved) == 1
    assert unresolved[0]["form"] == "rust_harness_method"
    assert unresolved[0]["candidate"] == "ok"
    assert "ambiguous method name" in unresolved[0]["reason"]
    assert "2 candidates" in unresolved[0]["reason"]


def test_resolve_dispatch_bounded_depth():
    """A resolution deeper than MAX_DISPATCH_DEPTH degrades to an "outer" answer at whatever depth the bound was
    hit -- never an infinite recursion, and never a hard failure that loses the citation entirely (the same
    never-silently-drop spirit as Gap 1's own fix)."""
    dispatch = {}
    for i in range(RC.MAX_DISPATCH_DEPTH + 3):
        enum_name = f"E{i}"
        next_enum = f"E{i + 1}"
        dispatch[(enum_name, "Next")] = {"subcommand": "next", "nested_enum": next_enum, "nested_field": "op",
                                          "arm_value_type": "match_expression", "arm_match_scrutinee": "op"}
    tokens = ["next"] * (RC.MAX_DISPATCH_DEPTH + 3)
    result = RC.resolve_dispatch(dispatch, "E0", tokens)
    assert result is not None
    assert result["label"] == "outer"
    assert result["matched_tokens"] <= RC.MAX_DISPATCH_DEPTH + 1

    # tokens that do not even reach the bound still resolve normally
    short_tokens = ["next"] * (RC.MAX_DISPATCH_DEPTH - 1)
    short_result = RC.resolve_dispatch(dispatch, "E0", short_tokens)
    assert short_result is not None
    assert short_result["matched_tokens"] == RC.MAX_DISPATCH_DEPTH - 1
