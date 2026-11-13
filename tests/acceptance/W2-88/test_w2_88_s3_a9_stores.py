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
    stores = stores_of(worlds.a9("default").record())
    refused = [(n, i["path"], i["reason"]) for n, b in stores.items() for i in b["refused"]]
    assert any(p == "config/settings.env" and r == "secrets" for _, p, r in refused), f"the tracked secret is not refused as secrets: {refused}"
    assert any(p == "assets/logo.bin" and r == "binary" for _, p, r in refused), f"the tracked binary is not refused as binary: {refused}"
    assert any(n == "vectors" and p == "archive/old.md" and r == "not-embedded" for n, p, r in refused), \
        f"a note of a namespace that is not embedded is not refused by the vectors as not-embedded: {refused}"
    indexed = stores["vectors"]["indexed"]
    if isinstance(indexed, list):
        assert any("docs/guide.md" in str(item) for item in indexed), "docs/guide.md is not in the vectors' indexed list"


def test_s3_a_store_the_path_map_calls_for_and_not_built_is_never_ok(worlds):
    """F2: the path map asks for code intelligence; no code-graph tool is on PATH (W2-124's way to plant it), so the
    codegraph store is not built: the stage is not ok and never prints ok."""
    nine = worlds.a9("no-code-graph", plant_options={"code_intelligence": True})
    run = nine.need_a9()
    W.assert_refused(run, "FABRIC_INCOMPLETE", "A9 with the code graph called for and not built")


def test_s3_a_tracked_file_in_neither_list_makes_the_stage_not_ok(worlds):
    """F2: a tracked file that no list holds. Planted after the real rebuild (``a9_drop_file.py``: its rows removed from the
    lexical and semantic tables), so the file is judged, indexed nowhere and refused for no reason."""
    nine = worlds.a9("a8-for-forks", run_a9=False)
    nine.need_chain()
    adoption = W.fork(nine, "fork-neither")
    done = W.child_gov(adoption, "a9_drop_file.py", "docs/guide.md", "adopt", "--lite", "--stage", "A9", "--out",
                       adoption.box.base / "neither-out", "--json", "--session", W.SESSION)
    assert "invalid choice" not in done.stderr, "gov adopt --lite does not take --stage A9 on this head (argparse: invalid choice)"
    planted = [line for line in done.stderr.splitlines() if line.startswith("planted:")]
    assert planted and not planted[-1].endswith(" 0 rows"), f"the plant did not take (no row named docs/guide.md): {done.stderr[-400:]}"
    run = W.S124.Run(("adopt", "A9"), done.returncode, done.stdout, done.stderr, 0.0)
    W.assert_refused(run, "FABRIC_INCOMPLETE", "A9 with docs/guide.md in no list")


def test_s3_a_second_rebuild_waits_for_the_first_under_w2_76s_lock(worlds):
    """While another process holds the machine's rebuild lock (W2-76's holder), A9 does not build beside it: it is still
    waiting after 8 s with no record committed, and finishes ok once the lock is let go. (The ticket says the second is
    "refused"; W2-76's code makes it wait, one after the other: README, package P-4.)"""
    nine = worlds.a9("a8-for-forks", run_a9=False)
    nine.need_chain()
    adoption = W.fork(nine, "fork-lock")
    lock, release = adoption.box.lock, adoption.box.base / "release"
    holder = subprocess.Popen([sys.executable, str(HOLDER), str(lock), str(release), "120"], stdout=subprocess.PIPE, text=True)
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
        try:
            process.kill()
        except Exception:  # noqa: BLE001
            pass


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
