"""K5 (a rebuild without its semantic store fails) [DEC-1015 item 4, stricter-only].

``gov rebuild`` (seeded or not) exits non-zero when the semantic store was asked for and not recreated (the endpoint
unavailable, or failing part way): the error code ``REBUILD_FAILED``, its answer naming the semantic store and the
reason; never an ok answer over a partial store. Only ``--no-embeddings`` skips the semantic store and still answers
ok (on a planted repository only).
"""

from __future__ import annotations

import json

import w2_122_support as support

MANY = 40   # notes beside the base's: more texts than one embed request carries, so a failure can come part way


def _failed_naming_the_semantic_store(run):
    error = run.error
    assert run.returncode not in (0, None), \
        f"a rebuild whose semantic store was not recreated exited {run.returncode}\n{run.describe()}"
    assert run.envelope().get("ok") is False, f"a rebuild without its semantic store answered ok\n{run.describe()}"
    assert error.get("code") == "REBUILD_FAILED", f"the error is not REBUILD_FAILED: {error}\n{run.describe()}"
    text = json.dumps(error).lower()
    assert "semantic" in text, f"the error does not name the semantic store: {error}"
    message = str(error.get("message") or "")
    details = json.dumps(error.get("details") or {})
    assert len(message) + len(details) > len("semantic") + 20, f"the error gives no reason: {error}"


def test_a_rebuild_with_the_endpoint_down_fails_named(box):
    project = support.make_base(box)
    env = support.environment(box, support.closed_loopback_host())

    run = support.rebuild(project, env)

    _failed_naming_the_semantic_store(run)


def test_a_rebuild_whose_endpoint_fails_part_way_fails_named(box):
    project = support.make_base(box)
    for number in range(MANY):
        support.write(project / f"docs/many/n{number:03d}.md", support.note(f"entry{number:03d}word"))
    support.git(project, "add", "-A")
    support.git(project, "commit", "-q", "-m", "many notes")
    failing = support.OllamaStandIn(fail_after=1)
    try:
        run = support.rebuild(project, support.environment(box, failing.host))
        requests, answered = failing.embed_requests, len(failing.embedded)
    finally:
        failing.close()

    assert requests >= 2 and answered > 0, \
        f"the premise fails: the rebuild sent {requests} embed request(s), {answered} text(s) answered; the " \
        f"failure did not come part way"
    _failed_naming_the_semantic_store(run)


def test_a_seeded_rebuild_with_the_endpoint_down_fails_named(tree, base, box):
    env = support.environment(box, support.closed_loopback_host())

    run = support.rebuild(tree, env, "--seed", str(base))

    _failed_naming_the_semantic_store(run)


def test_without_embeddings_the_semantic_store_is_skipped_and_the_answer_is_ok(box):
    project = support.make_base(box)
    env = support.environment(box, support.closed_loopback_host())

    run = support.rebuild(project, env, "--no-embeddings")

    assert run.ok, f"a rebuild with --no-embeddings did not answer ok\n{run.describe()}"
    semantic = run.result.get("stores", {}).get("semantic", {})
    assert semantic.get("status") == "not_recreated" and semantic.get("requested") is False, \
        f"the semantic store is not given as not asked for: {semantic}"
