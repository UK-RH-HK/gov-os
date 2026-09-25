"""ARCHITECTURE.md section 5.3 rule 6: "With every index deleted, compilation must produce a byte-identical section
A." Section A depends only on the resolver, which reads Git objects directly (never ``govbridge.core.store``'s
SQLite index) -- so moving the store aside must not change A at all, even though other sections that DO consult the
store (C, via ``govbridge.graph.traverse``) may legitimately have less to say.
"""
from govbridge.compile import packet as packetmod
from govbridge.core import store as storemod
from govbridge.route.router import RouteSet


def test_outage_a_identical(fixture_repo, view_path, registry_path, task_spec_factory, monkeypatch, tmp_path):
    task_spec = task_spec_factory(view_path, seeds=["CX-0001"])

    # a normal compile, with a real (empty-but-present) store.
    store_root = tmp_path / "store-present"
    monkeypatch.setenv("GOVBRIDGE_STORE", str(store_root))
    storemod.open_db()  # ensure the store directory + schema exist
    result_present = packetmod.compile_packet(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                                registry_path=registry_path)
    assert result_present["status"] == packetmod.STATUS_OK

    # move the store aside (never delete -- rm is denied to every bridge role), then compile again.
    moved = storemod.move_store_aside()
    assert moved is not None
    result_outage = packetmod.compile_packet(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                               registry_path=registry_path)
    assert result_outage["status"] == packetmod.STATUS_OK

    a_present = [(it["unit"]["id"], it["content_sha256"], it["source"])
                 for it in result_present["manifest"]["sections"]["A"]["items"]]
    a_outage = [(it["unit"]["id"], it["content_sha256"], it["source"])
                for it in result_outage["manifest"]["sections"]["A"]["items"]]
    assert a_present == a_outage
    assert a_present, "the fixture must resolve at least one A item for this test to be meaningful"

    # the rendered section A text itself (not just the manifest rows) is byte-identical too.
    def _section_a_text(rendered: str) -> str:
        start = rendered.index("## A.")
        end = rendered.index("## B.")
        return rendered[start:end]

    assert _section_a_text(result_present["rendered"]) == _section_a_text(result_outage["rendered"])
