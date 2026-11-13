"""KPI 2 and the failure line "parallel requests that change a vector": the determinism check embeds a fixed set
of texts with ``parallel`` requests in flight and compares each vector with the stored one, byte for byte at float32
(S5). Called in the pytest process against an in-thread stand-in embedder."""

from __future__ import annotations

import pytest

import w2_123_support as support

TEXTS = [f"chunk {index}: the shared embedding server serves several requests at once" for index in range(8)]
DELAY_S = 0.2   # each embedding takes this long, so requests sent at once are in flight together


def _references(texts=TEXTS):
    return [(text, support.stored(support.vector_of(text))) for text in texts]


def _check(ollama, endpoint, parallel, references=None):
    result = ollama.check_determinism(endpoint.host, references or _references(), parallel)
    assert isinstance(result, dict), f"check_determinism returned {result!r}, not an object"
    support.assert_keys(result, ("parallel", "checked", "differing", "verdict"), "the check's result")
    return result


@pytest.mark.parametrize("parallel", [1, 4])
def test_equal_vectors_are_accepted_with_that_many_requests_in_flight(ollama, stage, parallel):
    """Every vector equal: accepted. Each text goes in a request of its own with the store's model, and at most
    ``parallel`` (and, above one, more than one) are in flight at once."""
    endpoint = stage.embedder(delay=DELAY_S)

    result = _check(ollama, endpoint, parallel)

    assert result["verdict"] == "accepted" and list(result["differing"]) == [], result
    assert result["parallel"] == parallel and result["checked"] == len(TEXTS), result
    sent = endpoint.embed_requests()
    assert sorted(request["body"].get("input")[0] for request in sent) == sorted(TEXTS), sent
    assert all(request["route"] == "/api/embed" and request["body"].get("model") == support.MODEL
               and len(request["body"].get("input")) == 1 for request in sent), sent
    if parallel == 1:
        assert endpoint.in_flight_max == 1, f"{endpoint.in_flight_max} requests were in flight at once, not one"
    else:
        assert 2 <= endpoint.in_flight_max <= parallel, \
            f"{endpoint.in_flight_max} requests were in flight at once with parallel {parallel}"


def test_a_difference_below_the_stored_precision_is_not_a_difference(ollama, stage):
    """The comparison is at the stored precision (float32): a move of 1e-12 on every value is equal."""
    endpoint = stage.embedder(below_precision=True)

    result = _check(ollama, endpoint, 2)

    assert result["verdict"] == "accepted", result


def test_vectors_changed_by_parallel_requests_refuse_the_setting(ollama, stage):
    """Failure line: an embedder whose vector changes while another request is in flight refuses the setting."""
    endpoint = stage.embedder(delay=DELAY_S, perturb_parallel=True)

    result = _check(ollama, endpoint, 4)

    assert result["verdict"] == "refused", result
    assert len(result["differing"]) >= 1, result


def test_one_differing_vector_is_named_and_refuses(ollama, stage):
    """One vector differs (at any parallel setting): refused, and its index named."""
    endpoint = stage.embedder(differ={TEXTS[5]})

    result = _check(ollama, endpoint, 2)

    assert result["verdict"] == "refused" and list(result["differing"]) == [5], result


def test_a_missing_vector_refuses(ollama, stage):
    """A text answered without its vector refuses too, and its index is named."""
    endpoint = stage.embedder(missing={TEXTS[2]})

    result = _check(ollama, endpoint, 2)

    assert result["verdict"] == "refused" and 2 in list(result["differing"]), result
