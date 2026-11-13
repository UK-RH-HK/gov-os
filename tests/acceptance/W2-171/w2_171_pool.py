"""Planting a regression pool (Interface 4): ``fixtures/evaluation/memory-pool/hidden/<audit>-<qid>.yaml``, flat, with
the planted ``gov``'s ranks for each question (the first ``hit5`` at rank 1, the next up to ``full`` at rank 8, the rest
nowhere: hit@5 = ``hit5``, full evidence = ``full``)."""

from __future__ import annotations

import json
import random
import shutil

import yaml

import w2_171_scenario as S
import w2_171_world as W


def plant_pool(world, n: int, hit5: int, full: int, *, prefix: str = W.EARLIER, word: str = "") -> dict[str, str]:
    """Replace the pool by ``n`` questions named ``<prefix>-p<k>.yaml``; returns ``{stem: question text}``."""
    shutil.rmtree(world.pool, ignore_errors=True)
    world.pool.mkdir(parents=True)
    plan = json.loads((world.state / "gov_plan.json").read_text())
    stems = {}
    for k in range(1, n + 1):
        stem, text = f"{prefix}-p{k:04d}", f"Pool question {k:04d} text {word}.".replace(" .", ".")
        path = f"docs/plan/p{(k % 4) + 11}.md"
        doc = {"id": f"p{k:04d}", "question": text, "gold_answer": f"The pool answer {k}.",
               "sources": [{"path": path}], "commit": world.audit_commit, "category": "plan", "drawn": "sample"}
        (world.pool / f"{stem}.yaml").write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
        rank = 1 if k <= hit5 else (8 if k <= full else None)
        plan["questions"][text] = {"gold": [[path, 1, 3]], "calls": S.calls_for(rank)}
        stems[stem] = text
    (world.state / "gov_plan.json").write_text(json.dumps(plan))
    return stems


def rank_of(stem: str, hit5: int, full: int):
    k = int(stem.rsplit("-p", 1)[1])
    return 1 if k <= hit5 else (8 if k <= full else None)


def expected_draw(audit: str, stems, seed: int, k: int = 400) -> list[str]:
    """Item 4 (3): ``ids = sorted(stems)``, ``random.Random(seed).sample(ids, 400)``."""
    return random.Random(seed).sample(sorted(stems), k)


def default_seed(audit: str, digest: str) -> int:
    return int(W.sha_bytes(f"{audit}\n{digest}".encode())[:15], 16)


def pool_asked(world, stems: dict[str, str], offset: int = 0) -> list[str]:
    """The stems of the pool questions the planted gov was asked from call ``offset`` on, in order."""
    by_text = {text: stem for stem, text in stems.items()}
    return [by_text[c["q"]] for c in world.gov_calls()[offset:] if c["q"] in by_text]
