"""S3 (success-3), S4 (success-4), F2 (failure-2), F3 (failure-3, digests half); I3, I4, I6: A9 lite on a planted adoption.

A planted adoption is run through A0..A8 (W2-124's driver, MA before A3 where the head offers it), then
``gov adopt --lite --stage A9 --out <folder>``: the record's per-store blocks, every tracked file indexed or refused with
its reason, a store the path map calls for and a file in neither list making the stage not ok, the four digests, and two
runs on one commit giving equal first three digests.
"""

from __future__ import annotations

import subprocess
import sys
import time

import pytest

import w2_88_support as W

HOLDER = W.ACCEPT / "W2-76" / "w2_76_holder.py"


def stores_of(record):
    stores = record.get("stores")
    assert isinstance(stores, dict) and set(stores) == set(W.STORES), f"stores holds {sorted(stores or {})}, I3 names {W.STORES}"
    return stores


def count(value):
    return len(value) if isinstance(value, list) else value


def test_s3_the_stage_ends_ok_and_commits_its_record_under_governance_adoption(worlds):
    nine = worlds.a9("default")
    nine.need_a9()
    record_path = nine.run.result.get("record")
    assert nine.run.returncode == 0 and nine.run.envelope().get("ok") is True, nine.run.describe()
    assert isinstance(record_path, str) and record_path.startswith("governance/adoption/"), f"record: {record_path!r}"
    assert W.git(nine.project, "status", "--porcelain") == "", "A9 left the tree dirty"
    assert (nine.out / "memory-audit").is_dir(), "A9 wrote no memory-audit/ under --out"


def test_s3_the_record_holds_per_store_every_field(worlds):
    stores = stores_of(worlds.a9("default").record())
    for name, block in stores.items():
        assert set(W.STORE_FIELDS) <= set(block), f"stores.{name} lacks {sorted(set(W.STORE_FIELDS) - set(block))}"
        for key in ("chunks", "vectors", "nodes", "edges", "seconds", "peak_rss_bytes"):
            assert isinstance(block[key], (int, float)) and block[key] >= 0, f"stores.{name}.{key}: {block[key]!r}"
        assert isinstance(block["refused"], list)
        assert isinstance(count(block["judged"]), int) and isinstance(count(block["indexed"]), int)
    assert stores["vectors"]["vectors"] > 0 and stores["vectors"]["chunks"] > 0, "the embedded namespace left no vectors"
    assert stores["record"]["nodes"] > 0, "the record store holds no node"


def test_s3_every_store_judges_what_it_indexed_or_refused_with_a_reason(worlds):
    stores = stores_of(worlds.a9("default").record())
    for name, block in stores.items():
        for item in block["refused"]:
            assert isinstance(item, dict) and isinstance(item.get("path"), str) and item.get("reason") in W.REFUSE_REASONS, \
                f"stores.{name}.refused: {item!r} (reasons: {W.REFUSE_REASONS})"
        assert count(block["judged"]) == count(block["indexed"]) + len(block["refused"]), \
            f"stores.{name}: judged {count(block['judged'])} != indexed {count(block['indexed'])} + refused {len(block['refused'])}"


def test_s3_the_planted_refusals_carry_their_reasons(worlds):
    """The tracked secret is refused ``secrets`` and the note of a namespace that is not embedded ``not-embedded`` by the vectors. The
    tracked binary (RV1-4, revised: DEC-1157 (12)) is either refused ``binary`` by a store that did not take it, or held (indexed and
    named in ``binary_held``) by a store that did: never both for one store (the next cases)."""
    stores = stores_of(worlds.a9("default").record())
    refused = [(n, i["path"], i["reason"]) for n, b in stores.items() for i in b["refused"]]
    assert any(p == "config/settings.env" and r == "secrets" for _, p, r in refused), f"the tracked secret is not refused as secrets: {refused}"
    assert any(n == "vectors" and p == "archive/old.md" and r == "not-embedded" for n, p, r in refused), \
        f"a note of a namespace that is not embedded is not refused by the vectors as not-embedded: {refused}"
    seen = False
    for name, block in stores.items():
        held = "assets/logo.bin" in (block.get("binary_held") or [])
        refused_binary = any(i["path"] == "assets/logo.bin" and i["reason"] == "binary" for i in block["refused"])
        assert not (held and refused_binary), f"stores.{name}: the tracked binary is both held and refused as binary"
        seen = seen or held or refused_binary
    assert seen, "no store names the tracked binary, held (binary_held) or refused as binary"
    indexed = stores["vectors"]["indexed"]
    if isinstance(indexed, list):
        assert any("docs/guide.md" in str(item) for item in indexed), "docs/guide.md is not in the vectors' indexed list"


def chunked_paths(project, query) -> set:
    """Paths the store the stage built holds rows for (``query`` selects one column of paths), read from the planted
    adoption's own ``.gov-runtime/store.db`` (a file the child wrote; read only here)."""
    import sqlite3
    conn = sqlite3.connect(f"file:{project / '.gov-runtime/store.db'}?mode=ro", uri=True)
    try:
        return {row[0] for row in conn.execute(query)}
    finally:
        conn.close()


def test_s3_a_tracked_binary_the_lexical_index_chunked_is_indexed_and_named_held_never_refused(worlds):
    """RV1-4: a file is never in a store's ``refused`` while that store holds it. The lexical index chunks a tracked binary
    (the planted ``assets/logo.bin``: it reads every file the secrets filter lets through): it is in ``stores.lexical.indexed``, named
    in the block's ``binary_held: [paths]``, and in no ``refused`` list; ``binary`` stays only for a binary the store did not take."""
    nine = worlds.a9("default")
    record = nine.record()
    stores = stores_of(record)
    path = "assets/logo.bin"
    held = chunked_paths(nine.project, "SELECT DISTINCT path FROM lexical_chunk")
    assert path in held, f"the plant did not take: the lexical index holds no chunk of {path} (chunked: {sorted(held)[:6]}...)"
    lexical = stores["lexical"]
    assert path in lexical["indexed"], f"stores.lexical.indexed does not hold {path}, which the lexical store chunked"
    assert path in (lexical.get("binary_held") or []), f"stores.lexical.binary_held does not name {path}: {lexical.get('binary_held')!r}"
    for name, block in stores.items():
        assert not [i for i in block["refused"] if i["path"] == path and path in (block["indexed"] if isinstance(block["indexed"], list) else [])], \
            f"stores.{name} names {path} both indexed and refused"
    assert not [i for i in lexical["refused"] if i["path"] == path], f"stores.lexical.refused holds {path} while the store holds it"


def test_s3_no_store_names_a_file_in_refused_while_the_store_holds_it(worlds):
    """RV1-4 as a rule, judged on the stores themselves: every path the lexical store holds chunks for is in ``lexical.indexed`` and
    in no ``lexical.refused`` item; every path that has a vector (a chunk with a stored vector) is in ``vectors.indexed`` and not in
    ``vectors.refused``; a path named in ``binary_held`` is in that store's ``indexed`` list, never its ``refused`` list."""
    nine = worlds.a9("default")
    stores = stores_of(nine.record())
    in_lexical = chunked_paths(nine.project, "SELECT DISTINCT path FROM lexical_chunk")
    in_vectors = chunked_paths(nine.project, "SELECT DISTINCT c.path FROM lexical_chunk c JOIN semantic_vector v ON v.chunk_id = c.chunk_id")
    assert in_lexical, "the lexical store holds no chunk: the plant did not take"
    for name, held in (("lexical", in_lexical), ("vectors", in_vectors)):
        block = stores[name]
        indexed = set(block["indexed"]) if isinstance(block["indexed"], list) else set()
        refused = {i["path"] for i in block["refused"]}
        assert not held & refused, f"stores.{name}.refused names files the store holds: {sorted(held & refused)}"
        if isinstance(block["indexed"], list):
            assert held <= indexed, f"stores.{name}.indexed lacks files the store holds: {sorted(held - indexed)}"
    for name, block in stores.items():
        named = set(block.get("binary_held") or [])
        indexed = set(block["indexed"]) if isinstance(block["indexed"], list) else named
        assert named <= indexed and not named & {i["path"] for i in block["refused"]}, f"stores.{name}.binary_held {sorted(named)} is not held"


def test_s3_a_store_the_path_map_calls_for_and_not_built_is_never_ok(worlds):
    """F2: the path map asks for code intelligence; no code-graph tool is on PATH (W2-124's way to plant it), so the
    codegraph store is not built: the stage is not ok and never prints ok."""
    nine = worlds.a9("no-code-graph", plant_options={"code_intelligence": True})
    run = nine.need_a9()
    W.assert_refused(run, "FABRIC_INCOMPLETE", "A9 with the code graph called for and not built")


# ---- F2, "a tracked file in neither list": the unit seam fabric.check_coverage(record, tracked) (P-4 (a), DEC-1157 (3)) ----
#
# ``record`` is the A9 record's data (``stores``: each ``{judged, indexed: [paths], refused: [{path, reason}], ...}``);
# ``tracked`` any iterable of tracked paths. It returns None, or raises ``GovError("FABRIC_INCOMPLETE", ..., {"missing":
# [<sorted paths>]})`` for a tracked file in neither the indexed nor the refused list of a store that judges it (the
# lexical store judges every tracked file). The run-2 case that deleted store rows after a rebuild is replaced by these:
# no store row is deleted anywhere.

TRACKED = ("README.md", "docs/guide.md", "lib/util.py", "assets/logo.bin", "config/settings.env", "archive/old.md")
LEFT_OUT = {"assets/logo.bin": "binary", "config/settings.env": "secrets"}


def coverage_record(*, lexical_leaves_out=(), lexical_refuses=()):
    """An A9 record's ``stores`` in which every store lists every tracked path (indexed, or refused with a reason of
    I3's list and ``not-indexed``), so a store's own judging rule cannot leave a path out; ``lexical_leaves_out`` are removed
    from the lexical store's two lists, ``lexical_refuses`` moved from its indexed list to its refused list."""
    stores = {}
    for name in W.STORES:
        indexed, refused = [], []
        for path in TRACKED:
            if path in LEFT_OUT:
                refused.append({"path": path, "reason": LEFT_OUT[path]})
            elif name == "vectors" and path == "archive/old.md":
                refused.append({"path": path, "reason": "not-embedded"})
            elif name == "codegraph" and not path.endswith(".py"):
                refused.append({"path": path, "reason": "unsupported-language"})
            elif name == "lexical" and path in lexical_refuses:
                refused.append({"path": path, "reason": "not-indexed"})
            else:
                indexed.append(path)
        judged = len(indexed) + len(refused)                  # the store judged them all, whatever it then listed
        if name == "lexical":
            indexed = [p for p in indexed if p not in lexical_leaves_out]
            refused = [r for r in refused if r["path"] not in lexical_leaves_out]
        stores[name] = {"judged": judged, "indexed": indexed, "refused": refused, "chunks": 0,
                        "vectors": 0, "nodes": 0, "edges": 0, "seconds": 0.0, "peak_rss_bytes": 0}
    return {"stores": stores}


def test_s3_f2_check_coverage_passes_a_record_that_leaves_no_tracked_path_out():
    from gov.adopt import fabric
    assert fabric.check_coverage(coverage_record(), TRACKED) is None, "a complete record: no refusal, and None"
    assert fabric.check_coverage(coverage_record(), iter(TRACKED)) is None, "tracked is any iterable (a generator here)"


@pytest.mark.parametrize("path", ["docs/guide.md", "lib/util.py"])
def test_s3_f2_check_coverage_names_a_tracked_path_that_no_list_of_the_lexical_store_holds(path):
    from gov.adopt import fabric
    from gov.cli.errors import GovError
    with pytest.raises(GovError) as raised:
        fabric.check_coverage(coverage_record(lexical_leaves_out=(path,)), TRACKED)
    assert raised.value.code == "FABRIC_INCOMPLETE", f"{raised.value.code} for a tracked file ({path}) in neither list"
    assert raised.value.details.get("missing") == [path], f"details['missing'] is {raised.value.details.get('missing')!r}, not [{path!r}]"


def test_s3_f2_check_coverage_lists_every_missing_path_sorted():
    from gov.adopt import fabric
    from gov.cli.errors import GovError
    gone = ("lib/util.py", "README.md", "docs/guide.md")                  # left out in one order, tracked given in the reverse
    with pytest.raises(GovError) as raised:
        fabric.check_coverage(coverage_record(lexical_leaves_out=gone), iter(reversed(TRACKED)))
    assert raised.value.code == "FABRIC_INCOMPLETE"
    assert raised.value.details.get("missing") == sorted(gone), f"missing: {raised.value.details.get('missing')!r}"


def test_s3_f2_a_path_named_in_the_refused_list_alone_is_covered():
    """A path in a store's refused list with a reason (``not-indexed`` is the reason added for a namespace whose lexical
    policy keeps it out) and in no indexed list is named, so it is no gap."""
    from gov.adopt import fabric
    assert fabric.check_coverage(coverage_record(lexical_refuses=("archive/old.md",)), TRACKED) is None


def test_s3_f2_check_coverage_raises_for_a_store_that_was_not_built():
    """A store the path map calls for and the stage did not build: the lexical store judges every tracked file, so one that
    holds no list at all (an empty block, or no block) leaves every tracked path out."""
    from gov.adopt import fabric
    from gov.cli.errors import GovError
    empty = coverage_record()
    empty["stores"]["lexical"] = {"judged": 0, "indexed": [], "refused": []}
    with pytest.raises(GovError) as raised:
        fabric.check_coverage(empty, TRACKED)
    assert raised.value.code == "FABRIC_INCOMPLETE"
    assert raised.value.details.get("missing") == sorted(TRACKED), f"missing: {raised.value.details.get('missing')!r}"
    absent = coverage_record()
    del absent["stores"]["lexical"]
    with pytest.raises(GovError) as raised:
        fabric.check_coverage(absent, TRACKED)
    assert raised.value.code == "FABRIC_INCOMPLETE", f"a record with no lexical store: {raised.value.code}"


def test_s3_f2_check_coverage_raises_for_a_code_graph_that_could_not_be_read_naming_codegraph():
    """RV1-5 (the unit seam): a code graph that cannot be read makes ``stores.codegraph`` ``{"built": false, "error": "<reason>"}``;
    ``check_coverage`` raises ``FABRIC_INCOMPLETE`` with ``codegraph`` in ``details["not_built"]`` (never nodes 0 and edges 0 with ok).
    The same record with the graph built passes."""
    from gov.adopt import fabric
    from gov.cli.errors import GovError
    unread = coverage_record()
    unread["stores"]["codegraph"] = {**unread["stores"]["codegraph"], "built": False, "error": "x"}
    with pytest.raises(GovError) as raised:
        fabric.check_coverage(unread, TRACKED)
    assert raised.value.code == "FABRIC_INCOMPLETE", f"{raised.value.code} for a code graph that could not be read"
    assert "codegraph" in (raised.value.details.get("not_built") or []), f"details['not_built'] is {raised.value.details.get('not_built')!r}"
    built = coverage_record()
    built["stores"]["codegraph"] = {**built["stores"]["codegraph"], "built": True}
    assert fabric.check_coverage(built, TRACKED) is None, "a built code graph with its files listed is refused"


def test_s3_a_second_rebuild_waits_for_the_first_under_w2_76s_lock(worlds):
    """S3's "refused by W2-76's lock" reads "never two at once" (P-4 (a), DEC-1157 (3)): while another process holds the
    machine's rebuild lock (W2-76's holder), A9 does not build beside it, nor is it refused: it is still waiting after 8 s
    with no record committed (``gov.rebuild.watch.take`` blocks), and finishes ok, one after the other, once the lock is
    let go."""
    nine = worlds.a9("a8-for-forks", run_a9=False)
    nine.need_chain()
    adoption = W.fork(nine, "fork-lock")
    lock, release = adoption.box.lock, adoption.box.base / "release"
    holder = subprocess.Popen([sys.executable, str(HOLDER), str(lock), str(release), "120"], stdout=subprocess.PIPE, text=True)
    process = None
    try:
        assert holder.stdout.readline().startswith("held"), "the stand-in holder did not take the lock"
        process = subprocess.Popen([sys.executable, "-m", "gov.cli.main", "adopt", "--lite", "--stage", "A9", "--out",
                                    str(adoption.box.base / "lock-out"), "--json", "--session", W.SESSION],
                                   cwd=str(adoption.project), env=adoption.env(), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True, stdin=subprocess.DEVNULL)
        time.sleep(8)
        assert process.poll() is None, f"A9 ended while another rebuild held the lock (exit {process.returncode}): " \
                                       f"{process.stderr.read()[-600:]}"
        assert not [n for n in W.git(adoption.project, "log", "--format=%s").splitlines() if "A9" in n], "A9 committed under the held lock"
        release.write_text("go", encoding="utf-8")
        out, err = process.communicate(timeout=600)
        assert process.returncode == 0, f"A9 did not finish ok once the lock was free: {err[-600:]}"
    finally:
        release.write_text("go", encoding="utf-8")
        holder.wait(timeout=30)
        if process is not None and process.poll() is None:
            process.kill()


# ---- S4 / F3: four digests ------------------------------------------------------------------------------------

def test_s4_the_record_holds_the_four_digests(worlds):
    digests = worlds.a9("default").record().get("digests")
    assert isinstance(digests, dict) and set(W.DIGESTS) <= set(digests), f"digests: {digests!r}"
    for key in ("record", "lexical", "vectors"):
        assert isinstance(digests[key], str) and len(digests[key]) == 64, f"digests.{key}: {digests[key]!r}"
    assert digests["codegraph_bytes"] is not None, "the code graph's bytes are reported"


def test_s4_f3_check_digests_refuses_a_record_with_only_the_record_graphs_digest():
    from gov.adopt import fabric
    from gov.cli.errors import GovError
    whole = {"digests": {"record": "a" * 64, "lexical": "b" * 64, "vectors": "c" * 64, "codegraph_bytes": 1234}}
    fabric.check_digests(whole)        # four digests: no refusal
    for partial in ({"record": "a" * 64}, {"record": "a" * 64, "lexical": "b" * 64, "vectors": "c" * 64},
                    {"lexical": "b" * 64, "vectors": "c" * 64, "codegraph_bytes": 1}):
        with pytest.raises(GovError) as raised:
            fabric.check_digests({"digests": partial})
        assert raised.value.code == "DIGESTS_INCOMPLETE", f"{raised.value.code} for {sorted(partial)}"


def test_s4_two_a9_runs_on_one_commit_give_equal_first_three_digests(worlds):
    nine = worlds.a9("a8-for-forks", run_a9=False)
    nine.need_chain()
    got = []
    for name in ("twice-a", "twice-b"):
        adoption = W.fork(nine, name)
        run = adoption.a9(adoption.box.base / f"{name}-out")
        W.assert_offered(run, "A9")
        assert run.returncode == 0, run.describe()
        got.append(W.a9_record(adoption.project, run)["digests"])
    for key in ("record", "lexical", "vectors"):
        assert got[0][key] == got[1][key], f"digests.{key} differs between two A9 runs on one commit"
    assert got[0].get("codegraph_bytes") is not None and got[1].get("codegraph_bytes") is not None, "the code graph's bytes are reported"
