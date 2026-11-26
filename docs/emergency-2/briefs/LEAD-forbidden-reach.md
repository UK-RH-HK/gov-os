# Lead brief: forbidden-reach, the measure's own count of whether the forbidden sources an audit's misses cited are now outside default memory (DEC-1254 E-02's note; a fix under W2-204, DAEO-ma4q)

You are a fix lead (Sonnet, medium), started by the Gov OS CTO on 2026-11-26. **Read `docs/emergency-2/briefs/LEAD-COMMON.md`
first: every rule there applies.** Decide, never ask (I-10). Use `systematic-debugging`. Every `gov retrieve` you or a helper runs
takes `--root /home/usain/gov-os-worktrees/W2-00-store`. **Never open a hidden question-set root** (EXAMIN's or Gov OS's evaluation
root): every test plants its own sets root under a temporary folder. **Work steadily: if green early, this rides release 0.1.8.**

## Why
The owner (DEC-1254 E-02): "confirm EXAMIN's three stale citations leave default memory under the amended rule". EXAMIN's fresh 80 of
25 November (`/home/usain/gov-os-runs/W2-27/examin/docs/audits/wave0/memory/FRESH80-2026-11-25.md`, counts only) says 3 hidden-half
misses cited a forbidden (stale or superseded) source. Which sources sits only in the set's own rows inside the sets root, which no
session but the measure's own may read (DEC-1249 (2)). No `gov memaudit` command reports it: `figures` keeps only the count
(`src/gov/memaudit/figures.py:114-150`, `forbidden_cited`), `pool` re-runs retrieval scores with no forbidden check.

## What (a K-line as a `## Fix:` section in `.tickets/DAEO-ma4q.md`; the CTO approves it by this brief)
- **FR-1** `gov memaudit forbidden-reach --sets-root R --audit <name> [--repo D]` reads that audit's judged rows (where the judge
  records `forbidden_cited`, and the forbidden source each such answer cited; find where they are written), resolves each cited source
  against the repository's **current** memory policy (the path map's namespaces: `stale_class`, `lexical_policy`, `embedding_policy`;
  reuse `gov.retrieval` and D3's classifier where present, never a copy), and prints one line of counts only: sources cited, now outside
  default memory, still inside, and by the namespace or class that holds each (`archive: 2, docs: 1`), never a path, a question or an
  id. Exit 0 always on a readable audit; a missing audit or no judged rows names the reason and exits non-zero. It runs inside the
  measure's own process the same way `figures` does (the printer refusal of sets-root lines, `say.py`, stays in force).
  Verify: a planted sets root and repository whose audit has three misses citing forbidden sources in two namespaces, one stale-classed
  `not indexed`/`not embedded` and one live: the line says `3 cited, 2 outside, 1 inside` with the namespaces; the same after the live
  namespace gains the class says `3 outside`; the output holds no planted path, question or id (the test greps it).
- If D3's classifier is not on your base (`w2/integrate`; it is on `e2/bundle-a`), read the path map's policies directly and say so.

## Where
Worktree `/home/usain/gov-os-worktrees/E2-forbidden-reach`, branch `e2/forbidden-reach` from `w2/integrate`. Code area: a new module
in `src/gov/memaudit/` and its subcommand's registration (the smallest change to `src/gov/memaudit/__main__.py`; `e2/eval-roots`, held
in batch B, also changes that file, `command.py`, `driver.py`, `evalroots.py`, `judge.py` and `writerrun.py`: do not edit those others),
`tests/unit/memaudit/`, a **new** file `tests/acceptance/W2-204/test_w2_204_fr_forbidden_reach.py` with its rows in a **new section at the
end** of `tests/acceptance/W2-204/README.md` (the independent test designer only), `.tickets/DAEO-ma4q.md`.

## Green
FR-1 red on the base, green after; `gov accept W2-204` green; then exactly the impact-selected suites
(`PYTHONPATH=<worktree>/src python3 -m gov.cli.main queue DAEO-ma4q=e2/forbidden-reach --onto w2/integrate --select`) through the heavy
slot. Check the trailers (LEAD-COMMON).

## Return
Branch and head; where `forbidden_cited` and the cited source are recorded (file:line); FR-1 with tests and result; the exact command
line EXAMIN's driver runs; the selected run's summary; your retrieves (count, queries, records used).

## Your memory bundle (DEC-1249 (1); profile: code locations, conventions, earlier fixes and findings; uncut)
store: f61d30d937be (/home/usain/gov-os-worktrees/W2-00-store-b)
{
  "store": {
    "commit": "f61d30d937be8ccf7e70ff8531649879e51c2428",
    "head": "f61d30d937be8ccf7e70ff8531649879e51c2428",
    "stale": [],
    "root": "/home/usain/gov-os-worktrees/W2-00-store-b"
  },
  "stopping_reason": "BUDGET_EXHAUSTED_WITH_GAPS",
  "evidence": [
    {
      "id": "8dd5a2cd304188d7948fa27f",
      "sha256": "6db7876cc4cc56d1ee6003bc710ba1380af171359410389abcffd8abaaa1b3b6",
      "path": "src/gov/memaudit/matcher.py",
      "start_line": 111,
      "end_line": 114,
      "text": "def forbidden_cited(q: dict, citations) -> bool:\n    \"\"\"Whether any cited ``(path, first, last)`` names a path in the question's ``forbidden`` list (path equality, as\n    W2-81's ``cited`` matches; the lines do not matter).\"\"\"\n    return any(p in q[\"forbidden\"] for p, _, _ in citations)\n",
      "chunk_id": "8dd5a2cd304188d7948fa27f",
      "routes": [
        "lexical",
        "code"
      ],
      "batch": 1
    },
    {
      "id": "7a491287b2e34e4eab9dbe0c",
      "sha256": "600ebaf5087de42b89c436db7189b6bf80c97a47ae5788f3e880d0d5fbbf4f3f",
      "path": "src/gov/memaudit/matcher.py",
      "start_line": 117,
      "end_line": 120,
      "text": "def citation_right(repo, q: dict, citations) -> bool:\n    \"\"\"The strict rule (DEC-1227 D5 (a)): a cited place holds a gold line and no cited path is a forbidden one. An apart\n    question has no gold place, so its citation is never right.\"\"\"\n    return (not q[\"apart\"]) and cited(repo, q, citations) and not forbidden_cited(q, citations)\n",
      "chunk_id": "7a491287b2e34e4eab9dbe0c",
      "routes": [
        "lexical",
        "code"
      ],
      "batch": 1
    },
    {
      "id": "2471b4f2beac2ad024ef2547",
      "sha256": "7d8f809e6ed37326dc1707f13eef73a6d108553392d11a83f37189d8526b1a4a",
      "path": "src/gov/memaudit/judge.py",
      "start_line": 78,
      "end_line": 123,
      "text": "    def one(self, q: dict, first_result: dict) -> dict:\n        bundles = [prompts.items_of(first_result)]\n        attempts, final, verdict, searches = [], None, None, []\n        for k in range(1, prompts.CAP + 1):\n            meta, out = self.caller.call(READER, prompts.READER_SYS, prompts.READER_SCHEMA,\n                                         prompts.prompt_of(q[\"question\"], bundles), READER_BUDGET, f\"reader-{k}\",\n                                         q[\"id\"])\n            out = out if isinstance(out, dict) else None\n            attempts.append({\"attempt\": k, **meta, \"verdict\": (out or {}).get(\"verdict\"),\n                             \"answer\": (out or {}).get(\"answer\"), \"citations\": (out or {}).get(\"citations\")})\n            if not out or out.get(\"verdict\") not in (\"answer\", \"search_again\", \"not_found\"):\n                verdict = \"error\"\n                break\n            final, verdict = out, out[\"verdict\"]\n            if verdict != \"search_again\" or k == prompts.CAP:\n                break\n            result, ok, why, by = self.search(q[\"id\"], out.get(\"search\") or q[\"question\"])\n            searches.append({\"attempt\": k, \"ok\": ok, \"why\": why, \"rerank_by\": by})\n            bundles.append(prompts.items_of(result))\n        if verdict == \"search_again\":\n            verdict = \"not_found\"\n        grades = self.grade(q, verdict, final)\n        cites = []\n        for c in (final or {}).get(\"citations\") or []:\n            try:\n                cites.append((c.get(\"path\"), int(c.get(\"start_line\", 0)), int(c.get(\"end_line\", 0))))\n            except (TypeError, ValueError, AttributeError):\n                continue\n        got = [item for b in bundles for item in b]\n        outside = [c for c in cites if not any(pth == c[0] and s <= c[2] and c[1] <= e for pth, s, e, *_ in got)]\n        inside = [c for c in cites if c not in outside]\n        right_cite = matcher.citation_right(self.repo, q, cites)\n        right_inside = matcher.citation_right(self.repo, q, inside)\n        forbidden_cited = (not q[\"apart\"]) and matcher.forbidden_cited(q, cites)\n        row = {\"id\": q[\"id\"], \"kind\": \"audit\", \"apart\": q[\"apart\"], \"final_verdict\": verdict, \"attempts\": attempts,\n               \"answered_at\": len(attempts) if verdict == \"answer\" else None,\n               \"gold_in_bundle\": [any(matcher.hit(it, q) for it in b) for b in bundles],\n               \"citation_right\": right_cite, \"forbidden_cited\": forbidden_cited, \"grades\": grades, \"searches\": searches,\n               \"search_failures\": sum(1 for s in searches if not s[\"ok\"]), \"citations\": len(cites),\n               \"citations_outside\": len(outside), \"citation_right_only_outside\": right_cite and not right_inside,\n               \"calls_retried\": sum(1 for a in attempts if a.get(\"retried\"))\n                                + sum(1 for g in grades.values() if g.get(\"retried\")),\n               \"first_stopping_reason\": first_result.get(\"stopping_reason\"),\n               \"first_gaps_name_ids\": matcher.names_the_ids(first_result, q[\"question\"]) if q[\"apart\"] else None}\n        write_whole(self.reader, f\"{q['id']}.json\", row)\n        return row\n",
      "chunk_id": "2471b4f2beac2ad024ef2547",
      "routes": [
        "lexical",
        "code"
      ],
      "batch": 1
    },
    {
      "id": "a8e38945d7c01d638213ff97",
      "sha256": "75a11da44c802486bc6f65640aa48a730f0f684c5c07a42ba3cd1735eb3fb070",
      "path": "src/gov/memaudit/judge.py",
      "start_line": 137,
      "end_line": 138,
      "text": "\n\n",
      "chunk_id": "a8e38945d7c01d638213ff97",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "f22fb4f88d109cb0c9994c47",
      "sha256": "25bebb3e6b73b549b658e0c948990cc72d623e6f85e4d3625948ddc479927ab7",
      "path": "src/gov/memaudit/briefs/writer.py",
      "start_line": 108,
      "end_line": 121,
      "text": "   own words, with the facts only. Never copy a long passage.\n   **Forbidden sources.** Where a question has a stale, superseded or legacy source that a reader could wrongly cite,\n   name its repository path in `forbidden` (a list). A forbidden source is never also a gold source. Where none\n   exists, leave the field out.\n6. **The `nonexistent-id` question.** Ask about an id that exists nowhere (an id of one of the repository's own id\n   forms, past its highest number or outside its range). Its gold source is the line that settles the absence, and its\n   gold answer says \"none\".\n7. **Protected content.** Never write anything that looks like a secret: no key, token, password or credential, real or\n   realistic. A question about a secret names the place and never says what is in it. Skip a path that holds one.\n8. **Not about the audit.** No question is about this audit, the independent sessions or their briefs, the measure, the\n   question sets or the questions memory's search is tuned on. No question copies a question you have seen anywhere.\n\n## 6. Round 2\nYou have your set in `input/set/` and the checker's notes in `input/notes.md`. Each line of the notes gives a question's\n",
      "chunk_id": "f22fb4f88d109cb0c9994c47",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "DAEO-ma4q",
      "sha256": "e09cb5d06e3673b0693386a675728ace7998c53f021feceea2fc14f03ffbb07c",
      "path": ".tickets/DAEO-ma4q.md",
      "start_line": 217,
      "end_line": 245,
      "text": "## Fix: the strict forbidden-citation rule in the product's own grading (DEC-1227 D5 (a))\n\nFound in the 0.1.4 proving run (`docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md`, rows T7 and line 169): W2-81's\nscorer counts an answer wrong when it cites a forbidden (stale, superseded, legacy) source; the product's\n`judge.one` sets `citation_right` from gold alone and `prompts.outcome` has no forbidden concept, so 24 of the proving\nrun's 30 misses would have been graded right by the product. The owner (DEC-1227 D5 (a)) keeps W2-81's strict rule and\napplies it to the product's own measure, so EXAMIN's 95 % is graded the way the proving run is. Kind: a fix, no new\nticket; the ticket stays closed; `Fix:` trailer. The test designer's cases are red on the base first. Code is C3\n(`src/gov/memaudit/**`); every helper Sonnet (DEC-1225).\n\nW2-81's rule, which the product now follows: `citation_right = (a cited place holds a gold line) and (no cited path is a\nforbidden path)`; the answer is right only when the grade is `correct` and `citation_right` (a path matches a forbidden\npath by equality, as W2-81's `cited` does). Correct + gold + forbidden cited = wrong. `prompts.py` stays untouched (its\nhash is pinned by `test_prompts.py`): the rule lives in `judge.py`'s `citation_right`, which `prompts.outcome` reads.\n\n- **S1 A question may name forbidden sources.** A question file may hold `forbidden: [<repository path>, ...]` (a list of\n  non-empty path strings, W2-81's shape; absent = none). Verify: a set with and without the field both load and pass the\n  pre-flight; a malformed one (not a list, an empty list item, a non-string item) is `PF-FORM`, naming the question's id.\n- **S2 Citing a forbidden source makes the answer wrong,** whatever the grader says. Verify: planted grades through\n  `judge`: correct + gold cited = right; correct + forbidden cited = wrong; correct + gold and forbidden cited = wrong;\n  grade wrong = wrong; no forbidden list = as before. One function (`gov.memaudit.matcher`) holds the rule, and a\n  parity test pins it against W2-81's `judge_question` on the same planted cases.\n- **S3 The question writer is told to name the forbidden sources** where a stale or superseded source exists for a\n  question (the generated writer brief's form and rubric text; the checker's input form names the field). Verify: the\n  generated briefs hold the `forbidden` field and the instruction; kernel text is untouched.\n- **S4 The record says it.** `FIGURES.json` holds `forbidden_rule: \"strict\"` and `misses.forbidden_cited` (the\n  forbidden-cited misses counted apart, a subset of `misses.total`) (the five printed verdict lines are unchanged). Verify: a\n  planted run with a forbidden citation gives the count 1 and the key; with none, 0.\n\n",
      "chunk_id": "02e85df9d23d1ab4aa083ae2",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "f1750cbd9edc6b001ff68621",
      "sha256": "67d5006d2be43f94468208ee66bc9db464edae30862ba812539598f8a31100ac",
      "path": "docs/emergency-2/briefs/LEAD-d5-memaudit-strict.md",
      "start_line": 15,
      "end_line": 28,
      "text": "## The fix lines (failing test first; recorded in DAEO-ma4q's record as a fix, `Fix:` trailer)\n- **S1 A question may name forbidden sources.** The measure's question format (visible and hidden sets, the writer's\n  instructions and schema, `gov memaudit`'s steps) carries an optional list of forbidden sources per question, in the\n  same shape W2-81's sets use. Verify: a set with and without the field both load; a malformed one is refused by name.\n- **S2 Citing a forbidden source makes the answer wrong,** whatever the grader says of the answer, exactly as W2-81's\n  scorer rules it (one rule; if both can share one function, share it). Verify: planted grades: correct + gold cited =\n  right; correct + forbidden cited = wrong; correct + gold and forbidden cited = wrong (or as W2-81 rules it: match it\n  and say which); wrong = wrong.\n- **S3 The question writer is told to name the forbidden sources** where a stale or superseded source exists for a\n  question (prompt text in `src/gov/memaudit`; kernel text is not touched).\n- **S4 The record says it.** The measure's record names the rule (`forbidden_rule: strict`) and counts the\n  forbidden-cited misses apart, so a figure graded before this fix is never compared with one after without saying so.\n- Out of scope: the reader and grader models (lead `models-rubric` has them, R4); hit@k (a diagnostic only, EMERGENCY-2 5.2).\n\n",
      "chunk_id": "f1750cbd9edc6b001ff68621",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "8e4155b0adef43f64a72ff5b",
      "sha256": "320936df11b786ec5a8310d8287f7075798f8587096028a1cfc753a4e4acabe9",
      "path": "src/gov/memaudit/briefs/checker.py",
      "start_line": 27,
      "end_line": 44,
      "text": "  `id`, `question`, `gold_answer`, `sources`, `commit`, `category`, `drawn`, and optionally `keyword` and\n  `naive_answer` and `forbidden` (a list of repository paths of stale, superseded or legacy sources, never a gold\n  source). `input/selection.json` holds the lists the writer drew from: `changed` and `sample`.\n\n## 3. What you may read\n- `input/` and your own folder.\n- In `REPO`: every tracked file that \u00a74 does not name.\n\n## 4. What you must never read\nYour tree may hold some of these. Nothing but this brief stops you: leave them unread, and never list one as an `also`\nplace.\n\n| What | Why |\n|---|---|\n| Memory's own search and anything it produced: `gov retrieve`, a bundle, a ranked list, a measure record, a store, any run folder, the CTO's scratch | you judge the question, not its score |\n| Any earlier question set, notes or figures; the writer's folder | independence from the writer |\n| The paths the repository's configuration leaves out (`exclude`): {{exclude}} | they hold earlier questions, search results or the audit's own records |\n| Anything about this audit: any other brief, the sets root, another session's folder | the audit stays blind to itself |\n",
      "chunk_id": "8e4155b0adef43f64a72ff5b",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "9183a1b039df4cedfad56b97",
      "sha256": "1c2a3ddd5b06802bcfa4fc075a3ab2aaa6feb285659a7c8d33f5537f82dfb25f",
      "path": "src/gov/memaudit/figures.py",
      "start_line": 92,
      "end_line": 155,
      "text": "def build(audit: str, decl: dict, questions: list[dict], rows: dict, counting_folder, parsed: dict, control,\n          spend: dict, categories=None) -> tuple[dict, list[dict]]:\n    \"\"\"``(FIGURES, misses)`` for ``questions`` (the kept set, in file-name order) and their ``rows``. ``categories`` are\n    the repository's own (absent: those of the repository the process stands in); ``control`` is the counting attempt's\n    control event, or None when the configuration names no control (``FIGURES.json`` then holds a null control).\"\"\"\n    if categories is None:\n        categories = _config.current().quotas\n    by_line = {q[\"id\"]: q for q in parsed[\"questions\"]}\n    where = starts(parsed)\n    qids = [q[\"id\"] for q in questions]\n    o = {cut: {i: prompts.outcome(rows[i], cut) for i in qids} for cut in (1, 2, 3)}\n    right, wrong = (sum(o[2][i][k] for i in qids) for k in (\"right\", \"wrong\"))\n    bar = decl[\"bar\"]\n    n = len(qids)\n    lo, hi = scores.exact_interval(right, n)\n    apart = {q[\"id\"] for q in questions if q[\"apart\"]}\n    ret = scores.retrieval([x for x in parsed[\"questions\"] if x[\"id\"] in set(qids)], apart)\n    rt = {cut: [bool(o[cut][i][\"right\"]) for i in qids] for cut in (1, 2)}\n    gains, losses, p = prompts.mcnemar(rt[1], rt[2])\n    graded = [r for r in rows.values() if r.get(\"grades\")]\n    agree = sum(1 for r in graded if (r[\"grades\"].get(\"grader\") or {}).get(\"grade\")\n                == (r[\"grades\"].get(\"check\") or {}).get(\"grade\"))\n    misses, by_outcome, forbidden_cited = [], {k: 0 for k in OUTCOMES}, 0\n    by_rank, by_ns = {\"rank_1_5\": 0, \"rank_6_20\": 0, \"not_in_20\": 0}, {\"embedded\": 0, \"keyword_only\": 0}\n    by_cat, by_route = {c: 0 for c in categories}, {k: 0 for k in ROUTES}\n    for q in questions:\n        i = q[\"id\"]\n        if o[2][i][\"right\"]:\n            continue\n        row, line = rows[i], by_line.get(i) or {}\n        outcome = miss_outcome(row, o[2][i])\n        misses.append({\"id\": i, \"question\": q[\"question\"], \"gold_answer\": q[\"gold\"], \"gold_sources\": q[\"raw_sources\"],\n                       \"answer\": answer_shown(row), \"outcome\": outcome, \"evidence_in_bundle\": bool(line.get(\"bundle\"))})\n        by_outcome[outcome] += 1\n        forbidden_cited += 1 if row.get(\"forbidden_cited\") is True else 0  # rows from before the rule have no key\n        rank = line.get(\"rank\")\n        by_rank[\"rank_1_5\" if rank and rank <= 5 else \"rank_6_20\" if rank and rank <= 20 else \"not_in_20\"] += 1\n        by_ns[\"keyword_only\" if q[\"keyword\"] else \"embedded\"] += 1\n        if q[\"category\"] in by_cat:\n            by_cat[q[\"category\"]] += 1\n        by_route[first_route(counting_folder, q, *where[i]) if i in where else \"none\"] += 1\n    figures = {\n        \"audit\": audit, \"n\": n, \"n_gold\": ret[\"n\"], \"forbidden_rule\": \"strict\",\n        \"release\": release(), \"commit\": decl.get(\"audit_commit\"),\n        \"questions_with_forbidden\": sum(1 for q in questions if q.get(\"forbidden\")),\n        \"bar\": {k: bar[k] for k in (\"need_right\", \"max_wrong\", \"target_right\")},\n        \"verdict\": {\"right\": right, \"wrong\": wrong, \"passes\": right >= bar[\"need_right\"] and wrong <= bar[\"max_wrong\"],\n                    \"right_ok\": right >= bar[\"need_right\"], \"wrong_ok\": wrong <= bar[\"max_wrong\"],\n                    \"target_ok\": right >= bar[\"target_right\"], \"interval_exact\": [round(lo, 4), round(hi, 4)],\n                    \"not_run\": sum(1 for i in qids if i not in rows)},\n        \"beside\": {\"hit5\": ret[\"hit5\"], \"hit10\": ret[\"hit10\"], \"hit20\": ret[\"hit20\"], \"mrr\": ret[\"mrr\"],\n                   \"in_bundle\": ret[\"in_bundle\"], \"full_evidence\": ret[\"full\"],\n                   \"correct_citation_aside\": sum(o[2][i][\"correct\"] for i in qids),\n                   \"not_found\": sum(o[2][i][\"nf\"] for i in qids), \"a1_right\": sum(rt[1]),\n                   \"a3_right\": sum(o[3][i][\"right\"] for i in qids),\n                   \"mcnemar_a1_a2\": {\"gains\": gains, \"losses\": losses, \"p\": round(p, 6)},\n                   \"grader_agree\": agree, \"graded\": len(graded),\n                   \"search_failures\": sum(r.get(\"search_failures\", 0) for r in rows.values())},\n        \"misses\": {\"total\": len(misses), \"forbidden_cited\": forbidden_cited, \"by_outcome\": by_outcome, \"by_rank\": by_rank,\n                   \"by_namespace\": by_ns, \"by_category\": by_cat, \"by_route\": by_route},\n        \"control\": None if control is None else {k: control.get(k) for k in (\"hit5\", \"of\", \"last\", \"last_audit\")},\n        \"pool\": None, \"classes\": None, \"spend\": spend,\n    }\n    return figures, misses\n",
      "chunk_id": "9183a1b039df4cedfad56b97",
      "routes": [
        "lexical"
      ],
      "batch": 1
    },
    {
      "id": "e378bd1dc79e16987539f735",
      "sha256": "f543ab2a30d192142fb40ca0660260e185ed918f2d081f0d18b0ae0bc82f327f",
      "path": "docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md",
      "start_line": 170,
      "end_line": 176,
      "text": "## Fixes, in order\n\n| # | What | Where | Kind | Size |\n|---|---|---|---|---|\n| 1 | Grade the memory measure on Sonnet (reader and grader) and record the models in the measure's record | `src/gov/memaudit/judge.py:31`, its prompts and flags | fix under W2-201 (`DAEO-k1us`), R4 of `LEAD-models-rubric.md` | S |\n| 2 | The strict forbidden-citation rule in `gov memaudit`, recorded as `forbidden_rule: strict` | `memaudit/matcher.py`, `judge.py` | fix under W2-204 (`DAEO-ma4q`), brief `LEAD-d5-memaudit-strict.md` | M |\n| 3 | Role files: Sonnet at every class (C3 and C0) for every role except orchestrator and senior-engineer; promotion and probe no longer pick Opus; a limiter on the auditor's Opus exception; drop the dead Fable code | kit `roles/*.md` and regenerated copies; `criticality.yaml:6`; `launcher.py:706-745`; `role.py:278-342`; `model-exceptions.yaml`; `agent_model.py:30` | fix under W2-201, `e2/models-rubric` R1-R3 | M |\n",
      "chunk_id": "e378bd1dc79e16987539f735",
      "routes": [
        "semantic"
      ],
      "batch": 1
    },
    {
      "id": "be54f75cbb886c8fa82fbb9d",
      "sha256": "75a11da44c802486bc6f65640aa48a730f0f684c5c07a42ba3cd1735eb3fb070",
      "path": "src/gov/memaudit/judge.py",
      "start_line": 157,
      "end_line": 158,
      "text": "\n\n",
      "chunk_id": "be54f75cbb886c8fa82fbb9d",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "e3361ac4743c09cd1cebcbe3",
      "sha256": "75a11da44c802486bc6f65640aa48a730f0f684c5c07a42ba3cd1735eb3fb070",
      "path": "src/gov/memaudit/judge.py",
      "start_line": 165,
      "end_line": 166,
      "text": "\n\n",
      "chunk_id": "e3361ac4743c09cd1cebcbe3",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "fc454ef01956412f18cb2f68",
      "sha256": "75a11da44c802486bc6f65640aa48a730f0f684c5c07a42ba3cd1735eb3fb070",
      "path": "src/gov/memaudit/judge.py",
      "start_line": 148,
      "end_line": 149,
      "text": "\n\n",
      "chunk_id": "fc454ef01956412f18cb2f68",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "1913dfd669ed3a370c895db1",
      "sha256": "01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b",
      "path": "src/gov/memaudit/judge.py",
      "start_line": 124,
      "end_line": 124,
      "text": "\n",
      "chunk_id": "1913dfd669ed3a370c895db1",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "7e2629b3a027195b765f84e9",
      "sha256": "75a11da44c802486bc6f65640aa48a730f0f684c5c07a42ba3cd1735eb3fb070",
      "path": "src/gov/memaudit/judge.py",
      "start_line": 178,
      "end_line": 179,
      "text": "\n\n",
      "chunk_id": "7e2629b3a027195b765f84e9",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "989cc3aa7dede794250da7d4",
      "sha256": "6c3c5e6b550e1f4c5a47c9ed46fd02c09847a2bdd6557e35446510416de905bd",
      "path": "docs/emergency-2/briefs/LEAD-fix-dc-forbidden.md",
      "start_line": 1,
      "end_line": 18,
      "text": "# Lead brief: fix-dc-forbidden, `gov memaudit declare` notices (never refuses) a set with no forbidden list (a fix under W2-204, `DAEO-ma4q`)\n\nRead `docs/emergency-2/briefs/LEAD-COMMON.md` first and follow it (its test command, with node on PATH; the test\ndesigner's reading bounded). Name: `fix-dc-forbidden`; worktree `/home/usain/gov-os-worktrees/E2-fix-dc-forbidden`, branch\n`e2/fix-dc-forbidden` from `w2/integrate`. **Do not merge.** Every helper Sonnet; this lead runs medium. It blocks\nrelease 0.1.5: green **within about 45 minutes**.\n\n**The red** (the 0.1.5 full suite on `461c214a5`, weekly tier): 42 cases of `tests/acceptance/W2-187` fail. Cause:\n`fixes-015a` F15 made `src/gov/memaudit/declare.py` (about `:280`) append `DC-FORBIDDEN` and refuse when no hidden\nquestion carries a `forbidden` list. W2-187's standing measure plants sets with no forbidden lists, so every declare is\nrefused (`measure.out` reads `DC-FORBIDDEN`). The same would refuse EXAMIN's fresh 80 if its set held no stale source.\n\n**The CTO's ruling (P2, DEC-1242 T-1's level; F15 was the CTO's own brief line):** the strict rule stays strict, and a\nset with no forbidden list is a legitimate set. `declare` never refuses for it. Instead: the figure's stamp already\ncarries `questions_with_forbidden` (0 here); `declare` prints one notice line, exactly\n`NOTICE DC-FORBIDDEN-NONE: no question carries a forbidden list; the strict rule grades as the lenient rule would`, and\nthe declaration record carries `forbidden_lists: 0`. The verdict and exit code are unchanged by it.\n\n",
      "chunk_id": "989cc3aa7dede794250da7d4",
      "routes": [
        "semantic"
      ],
      "batch": 2
    },
    {
      "id": "62047d01946b5fbd9175c08b",
      "sha256": "472eec09a2d7da04205d14fd921e6709d64a7fbfd094f945f9a3ddd9dd122c39",
      "path": "src/gov/memaudit/judge.py",
      "start_line": 266,
      "end_line": 282,
      "text": "    spend = {\"usd\": round(caller.total, 6), \"projection\": proj, \"brake\": brake}\n    control = _control_of(run_dir, attempt_n) if cfg.control is not None else None\n    fig, misses = figures.build(audit, decl, qs, rows, counting, parsed, control, spend, cfg.quotas)\n    if not week:  # a standing run's questions leave nothing behind but its rows in this run folder (S4)\n        figures.write_misses(run_dir, misses)\n    # DEC-1225 (4): the models that answered and graded, so the figures compare only from the first fresh 80 on Sonnet\n    fig[\"models\"] = {\"reader\": READER, \"grader\": GRADER, \"checker\": CHECK}\n    fig[\"reader_model\"], fig[\"grader_models\"] = READER, [GRADER, CHECK]  # F15: the stamp's models\n    figures.write_figures(run_dir, fig)\n    v = fig[\"verdict\"]\n    events.append(run_dir, \"figures\", right=v[\"right\"], wrong=v[\"wrong\"], n=fig[\"n\"], passes=v[\"passes\"])\n    retried = sum(r.get(\"calls_retried\", 0) for r in rows.values())\n    for line in figures.verdict_lines(fig, retried):\n        emit(line)\n    failed = sorted(r[\"id\"] for r in rows.values() if r.get(\"search_failures\"))\n    if failed:\n        total = sum(r.get(\"search_failures\", 0) for r in rows.values())\n",
      "chunk_id": "62047d01946b5fbd9175c08b",
      "routes": [
        "lexical"
      ],
      "batch": 2
    },
    {
      "id": "1e9529ded0ebfed83964dd97",
      "sha256": "4a8b62cf12e2a2de2aaa7c4ad672e4319b521cd982634bfa5c044cc0ef11b245",
      "path": "src/gov/memaudit/figures.py",
      "start_line": 1,
      "end_line": 22,
      "text": "\"\"\"``FIGURES.json``, ``misses.jsonl`` and the printed verdict (Interface items 8, 9 and 10; S3, S5, S6, F1).\n\nCounts and fixed words only reach ``FIGURES.json`` and the screen. ``misses.jsonl`` holds the questions, gold answers, gold\nsources and answers of the misses, and with ``reader/`` it is the only place any of them is written (F1). The verdict is the\nreader run's A2 cut of ``outcome`` (the fresh 80's own), against the bar the declaration scaled to ``n``; hit@5, the first\nbundle, the citation aside and one search against two are beside it and never judged.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport json\nimport os\nfrom pathlib import Path\n\nfrom gov.memaudit import config as _config\nfrom gov.memaudit import fault, matcher, prompts, scores\nfrom gov.memaudit.common import write_whole\n\nCLASSES = (\"gold_wrong\", \"question_ambiguous\", \"out_of_scope\", \"retrieval_miss\", \"answer_wrong\")\nOUTCOMES = (\"wrong\", \"incomplete\", \"not_found\")\nROUTES = (\"lexical\", \"semantic\", \"both\", \"other\", \"none\")\nSTAMP_KEYS = (\"release\", \"commit\", \"reader_model\", \"grader_models\", \"forbidden_rule\", \"questions_with_forbidden\")\n",
      "chunk_id": "1e9529ded0ebfed83964dd97",
      "routes": [
        "lexical",
        "semantic"
      ],
      "batch": 2
    }
  ],
  "batches": [
    {
      "size": 10
    },
    {
      "size": 10
    }
  ],
  "merge": {
    "candidates": 20,
    "duplicates": 12,
    "dropped": [],
    "reranked": true
  },
  "rerank": {
    "by": "service",
    "device": "cuda:0",
    "reason": null
  },
  "expansions": [
    {
      "chunk_id": "2471b4f2beac2ad024ef2547",
      "parent_id": "5711c6e58223256fcff5a660",
      "path": "src/gov/memaudit/judge.py",
      "start_line": 78,
      "end_line": 123
    },
    {
      "chunk_id": "02e85df9d23d1ab4aa083ae2",
      "parent_id": "601983af19a523f8b172b92a",
      "path": ".tickets/DAEO-ma4q.md",
      "start_line": 217,
      "end_line": 245
    },
    {
      "chunk_id": "f1750cbd9edc6b001ff68621",
      "parent_id": "d2c083bcc62512810e0dc456",
      "path": "docs/emergency-2/briefs/LEAD-d5-memaudit-strict.md",
      "start_line": 15,
      "end_line": 28
    },
    {
      "chunk_id": "9183a1b039df4cedfad56b97",
      "parent_id": "0a949e97aa6634fc1df86f4e",
      "path": "src/gov/memaudit/figures.py",
      "start_line": 92,
      "end_line": 155
    },
    {
      "chunk_id": "989cc3aa7dede794250da7d4",
      "parent_id": "ef304529bffeecaea3c69783",
      "path": "docs/emergency-2/briefs/LEAD-fix-dc-forbidden.md",
      "start_line": 1,
      "end_line": 18
    }
  ],
  "repeats": [],
  "gaps": [
    {
      "path": "docs/emergency-2/briefs/LEAD-d5-memaudit-strict.md",
      "chunk_id": "84731b457d76f92583862272",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "290199afdd879cbc0a8614ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-ma4q.md",
      "chunk_id": "23af55bbaabb43c50dfb54f5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/checker.md",
      "chunk_id": "e12bd64afd6ea9759abc54d3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/checker.md",
      "chunk_id": "9425c7b642f3198921d2b6a8",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-d5-memaudit-strict.md",
      "chunk_id": "0ff109633ece143c8d6b8025",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/governance/kernel/skills/adopt/SKILL.md",
      "chunk_id": "49e55cbf78ec34f61ab27ba0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "50e6ce0240da0808eaf8c79e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "9be62cf54d7a0dd284a0c205",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/auditor.md",
      "chunk_id": "e4fd780f5a8146f7ca89c8ca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/auditor.md",
      "chunk_id": "43448fd2d961a56327e5f033",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/changes/W2-171-evidence.md",
      "chunk_id": "47e1efb3c0feec10980304ed",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".rulesync/skills/adopt/SKILL.md",
      "chunk_id": "2f107453311ce0ad9228ce09",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "template/.rulesync/skills/adopt/SKILL.md",
      "chunk_id": "9eb487425a5589a2fad62f7e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".claude/skills/adopt/SKILL.md",
      "chunk_id": "da9ee419868ac0f682dad6ee",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/memory-audit/auditor.md",
      "chunk_id": "463d508d0ceb02cef876cadc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-4-DETERMINISM.md",
      "chunk_id": "219ab11358e37b64683f963f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-cdoi/PR-DAEO-cdoi-round-DEC-694.md",
      "chunk_id": "7d2ff6ddd3f2f0f804983721",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-d3sr.md",
      "chunk_id": "9a366b23e8d5a0674bae78d3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-61vm.md",
      "chunk_id": "22baffa9005040664a6b1175",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-cdoi/PR-DAEO-cdoi-round-DEC-694.md",
      "chunk_id": "231d247989b5878535161400",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/08-register.md",
      "chunk_id": "f17af825cc490dec236791c9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-81-proving-run/report.json",
      "chunk_id": "07226482b1a62b2ec59d3f94",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-cdoi/PR-DAEO-cdoi-round-DEC-694.md",
      "chunk_id": "a0165c7c2c598f98153e3b53",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/memory-audit/checker.md",
      "chunk_id": "31ff0aac37b589b698b992d3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/audits/E2-AUDIT-1-DECISIONS.md",
      "chunk_id": "7efe5045ab828858001a6525",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1.md",
      "chunk_id": "c4fa50a2149024fd7df77892",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md",
      "chunk_id": "e8920543f1c8506d68525cfc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/README.md",
      "chunk_id": "4ccbebd5dce33eb01ac6908e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/figures.py",
      "chunk_id": "f7a19a0a8efab0be6ec98a2f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md",
      "chunk_id": "1710352ab93048ffb2c4c3b6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md",
      "chunk_id": "89148e05b97f18d532f1688d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-dc-forbidden.md",
      "chunk_id": "93c9d2018fcc2cfbfa939684",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/retrieval/semantic.py",
      "chunk_id": "e477ed6dc82364575c89d0cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/memory-audit/writer.md",
      "chunk_id": "c16965f82b1372dbb7c26bbe",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-cdoi/PR-DAEO-cdoi-round-DEC-694.md",
      "chunk_id": "36a271d953ed2cecce011fa9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-d3sr.md",
      "chunk_id": "ce26c674b606d1bef91aefb7",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md",
      "chunk_id": "f8b0997c719cbf085d895676",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/RECORDS-MAP.md",
      "chunk_id": "12f15e0f67508902ca324b7c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/README.md",
      "chunk_id": "fcec4a319ca4a79fc9dc0faf",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/memory-audit/writer.md",
      "chunk_id": "ccae5193ee7e40cb9aaccbac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/judge.py",
      "chunk_id": "1d17e9c246265ca33afd5363",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-5j8b.md",
      "chunk_id": "231d531b2fa02f640f6ba42c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-0cd2.md",
      "chunk_id": "69f303237d9dd1741f303e4b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-81-proving-run/report.json",
      "chunk_id": "482fc1ee67c5ccacb268f518",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md",
      "chunk_id": "a88629703af8ab20e11fb036",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/checker.md",
      "chunk_id": "fae9ada4a8dfbcc50f095b6c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md",
      "chunk_id": "6be3be29a9ecd9e29c1e21ea",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/auditor.md",
      "chunk_id": "d6f80dbfba802882e9e2784b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/say.py",
      "chunk_id": "e0bbbd95068d761442c9bcaa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md",
      "chunk_id": "f0dda0eaf6543b22139c5d2b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/retrieval/test_w2_91_full_embeddings.py",
      "chunk_id": "fbda53ef0d175e54f0ff9bc5",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/memory-audit/writer.md",
      "chunk_id": "762536e5374e9e7df3929090",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/HANDOVER.md",
      "chunk_id": "b2638aa81405517fad6bcea1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/FINDINGS.md",
      "chunk_id": "890b1dfb46b395fa19e0b4af",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/figures.py",
      "chunk_id": "e3e27e1362d96257ece3a608",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-61vm.md",
      "chunk_id": "6f5d324ce849f2016ebf676e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/judge.py",
      "chunk_id": "4db310555347d7a3fdd19cac",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-memaudit-launch.md",
      "chunk_id": "f9f65d1624f1bf44823c7f88",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-5j8b.md",
      "chunk_id": "13354322b57a293b9a8d3a0d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/README.md",
      "chunk_id": "0fbd1ee6bf91d59afbad1512",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fix-dc-forbidden.md",
      "chunk_id": "f828c563a0450d3e6dfb514b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/integration/TOOL-MAP.md",
      "chunk_id": "984ca2351c24dc0c6ebff27b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "7d3e502cc85a82e618e57483",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md",
      "chunk_id": "f821bc4dc46270e9d5d06534",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/_shipped/governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/auditor.md",
      "chunk_id": "3ffee09acadf70957e3787cb",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "chunk_id": "b8d59c8ff45f5a2abefd73bc",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/README.md",
      "chunk_id": "1a8963b9f46f878e514c6bdd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/releases/0.1.5/manifest.json",
      "chunk_id": "3b3f0d6d550d9628abcb700d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-memaudit-launch.md",
      "chunk_id": "efc3150ff31c33e6a2b54047",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-memaudit-launch.md",
      "chunk_id": "26908d1d90d0ec8e70210840",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "chunk_id": "0ba3d6865df682bc690e64ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/w2_81_score.py",
      "chunk_id": "1841f5bb0cc7e0f4839b3ff3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "src/gov/memaudit/briefs/writer.py",
      "chunk_id": "5275da5a2bbe3c8720097718",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/memory-audit/auditor.md",
      "chunk_id": "3901c2d42635d5072a39519b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/README.md",
      "chunk_id": "d7e01a2abf265bf1e20303cd",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-eval-roots.md",
      "chunk_id": "f489081e493e9401551c774d",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/memory-audit/checker.md",
      "chunk_id": "d1634e013f1867dfc6b1a53c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-memaudit-launch.md",
      "chunk_id": "085769ee4a2ddd4949edf99c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-memaudit-launch.md",
      "chunk_id": "60ab75ba2157044349aaaaa6",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/test_w2_204_fix_forbidden.py",
      "chunk_id": "9b422d32111a0d2b3cf9c2ab",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/indep-briefs/memory-audit/writer.md",
      "chunk_id": "bf75a4d9d9ec77fa1dff6c84",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/checker.md",
      "chunk_id": "6de80af8cf179106042c865b",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/emergency-2/briefs/LEAD-fixes-015a.md",
      "chunk_id": "147406c53cd1a3538855bcca",
      "reason": "NOT_GATHERED"
    },
    {
      "path": ".tickets/DAEO-p8tv.md",
      "chunk_id": "843136693a815716cfd119ae",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/plan/wave-2/w2-81-proving-run/report.json",
      "chunk_id": "0acd0f8d0cea95db3d5c1eaa",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "governance/project/orchestration/packages/MEMORY-AUDIT-1/briefs/writer.md",
      "chunk_id": "f01c2e27495dba1debf305c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/test_w2_81_score.py",
      "chunk_id": "73a4ca0c6a7f6450abaefb27",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-21/test_w1_21_no_hit_floor.py",
      "chunk_id": "f97488c48cbff9a6a87e7f94",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-cdoi/PR-DAEO-cdoi-round-DEC-694.md",
      "chunk_id": "618ace1a27bea51067a9e87f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/README.md",
      "chunk_id": "4c1fe3e7a19bef4dd100bf5f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/README.md",
      "chunk_id": "3887d319a05aff274ca32183",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-cdoi/PR-DAEO-cdoi-round-DEC-694.md",
      "chunk_id": "ee3c701dffd375be355937f0",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-91/w2_91_support.py",
      "chunk_id": "49ad411b7c802c4bff86f33c",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/probes/DAEO-l78m/PR-DAEO-l78m.md",
      "chunk_id": "8f922381c08d91540c0ff4be",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/test_w2_81_runner.py",
      "chunk_id": "40b02e57fd1439069a4f94ec",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-88/w2_88_support.py",
      "chunk_id": "ba4b979dc0010146143b6088",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "82e1c9db40fc685c6e5d3a57",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-41/README.md",
      "chunk_id": "3398405f3395fc56afd4f754",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/retrieval/test_w2_13_lexical_policy.py",
      "chunk_id": "c24fd176a8530735ed1479d3",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-41/README.md",
      "chunk_id": "866b52f2bbc49ed364436b17",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/README.md",
      "chunk_id": "ad383bd32441a8948fe30db9",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W1-41/README.md",
      "chunk_id": "349c80f46de7315eeecafb9f",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/audit/emergency-2026-11/permissions-audit.md",
      "chunk_id": "69f34e0dd89f0e79238bee54",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-204/test_w2_204_fix_forbidden.py",
      "chunk_id": "a79910c064478b144324493e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/unit/adopt/test_adopt.py",
      "chunk_id": "03a6b1e6fabc437da02a18c1",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "tests/acceptance/W2-81/w2_81_score.py",
      "chunk_id": "af6887f5e8191b00bf9f5f7e",
      "reason": "NOT_GATHERED"
    },
    {
      "path": "docs/assessment/2026-10/I1-guard-launcher-sandbox.md",
      "chunk_id": "55e97ccf9c9e22a9f77a8725",
      "reason": "NOT_GATHERED"
    }
  ],
  "facets": {
    "lexical": {
      "available": true,
      "reason": null
    },
    "semantic": {
      "available": true,
      "reason": null
    },
    "code": {
      "available": true,
      "reason": null
    }
  },
  "budget": {
    "bundle": {
      "limit": 6000,
      "used": 5489
    },
    "rounds": {
      "limit": 1,
      "used": 1
    }
  },
  "continuation": "eyJiYiI6bnVsbCwiYnMiOjEwLCJjIjpbWyJkb2NzL2VtZXJnZW5jeS0yL2F1ZGl0cy9FMi1BVURJVC0xLURFQ0lTSU9OUy5tZCIsMTcwLDE3NiwiZTM3OGJkMWRjNzllMTY5ODc1MzlmNzM1Il0sWyJzcmMvZ292L21lbWF1ZGl0L2JyaWVmcy9jaGVja2VyLnB5IiwyNyw0NCwiOGU0MTU1YjBhZGVmNDNmNjRhNzJmZjViIl0sWyJzcmMvZ292L21lbWF1ZGl0L2JyaWVmcy93cml0ZXIucHkiLDEwOCwxMjEsImYyMmZiNGY4OGQxMDljYjBjOTk5NGM0NyJdLFsic3JjL2dvdi9tZW1hdWRpdC9maWd1cmVzLnB5IiwxLDIyLCIxZTk1MjlkZWQwZWJmZWQ4Mzk2NGRkOTciXSxbInNyYy9nb3YvbWVtYXVkaXQvanVkZ2UucHkiLDc4LDk1LCIzZWM5MzI1MjdlOGNhM2Y2ZDA0MWYzMmIiXSxbInNyYy9nb3YvbWVtYXVkaXQvanVkZ2UucHkiLDk0LDExMiwiYjRhOTdkNGYxNTUxZTE0ZmQ5NDA5ZTQwIl0sWyJzcmMvZ292L21lbWF1ZGl0L2p1ZGdlLnB5IiwxMjQsMTI0LCIxOTEzZGZkNjY5ZWQzYTM3MGM4OTVkYjEiXSxbInNyYy9nb3YvbWVtYXVkaXQvanVkZ2UucHkiLDEzNywxMzgsImE4ZTM4OTQ1ZDdjMDFkNjM4MjEzZmY5NyJdLFsic3JjL2dvdi9tZW1hdWRpdC9qdWRnZS5weSIsMTQ4LDE0OSwiZmM0NTRlZjAxOTU2NDEyZjE4Y2IyZjY4Il0sWyJzcmMvZ292L21lbWF1ZGl0L2p1ZGdlLnB5IiwxNTcsMTU4LCJiZTU0Zjc1Y2JiODg2YzhmYTgyZmJiOWQiXSxbInNyYy9nb3YvbWVtYXVkaXQvanVkZ2UucHkiLDE2NSwxNjYsImUzMzYxYWM0NzQzYzA5Y2QxY2ViY2JlMyJdLFsic3JjL2dvdi9tZW1hdWRpdC9qdWRnZS5weSIsMTc4LDE3OSwiN2UyNjI5YjNhMDI3MTk1Yjc2NWY4NGU5Il0sWyJzcmMvZ292L21lbWF1ZGl0L2p1ZGdlLnB5IiwyNjYsMjgyLCI2MjA0N2QwMTk0NmI1ZmJkOTE3NWMwOGIiXSxbInNyYy9nb3YvbWVtYXVkaXQvbWF0Y2hlci5weSIsMTExLDExNCwiOGRkNWEyY2QzMDQxODhkNzk0OGZhMjdmIl0sWyJzcmMvZ292L21lbWF1ZGl0L21hdGNoZXIucHkiLDExNywxMjAsIjdhNDkxMjg3YjJlMzRlNGVhYjlkYmUwYyJdXSwiZiI6Ii9ob21lL3VzYWluL2dvdi1vcy13b3JrdHJlZXMvVzItMDAtc3RvcmUtYiIsImkiOltdLCJvIjoyMCwicCI6eyJiIjoic2VydmljZSIsImQiOiJjdWRhOjAiLCJoIjoiOTczMWEzOTAzYmVjYjA1YyIsIm8iOlswLDIsMzEsNiwxNyw1LDQsMTUsMjgsMzQsMzIsMzUsMzcsMjMsMzAsOSwyMSwzOSwxNCwxMSwxMyw4LDE2LDI5LDM2LDEsMTIsMyw3LDE5LDI2LDEwLDIyLDI0LDIwLDI1LDI3LDMzLDE4LDM4XX0sInEiOiJnb3YgbWVtYXVkaXQganVkZ2Ugcm93cyBmb3JiaWRkZW5fY2l0ZWQsIHRoZSBmb3JiaWRkZW4gc291cmNlIGEgcmVhZGVyIGNpdGVkLCBmaWd1cmVzIGNvdW50cyBvbmx5LCBzYXkucHkgcHJpbnRlciByZWZ1c2FsLCByZXRyaWV2YWwgbmFtZXNwYWNlIHBvbGljaWVzIGxleGljYWwgZW1iZWRkaW5nIHN0YWxlX2NsYXNzIiwiciI6MCwicyI6ImY2MWQzMGQ5MzdiZThjY2Y3ZTcwZmY4NTMxNjQ5ODc5ZTUxYzI0MjgiLCJ0IjpudWxsLCJ4IjpbIjBhOTQ5ZTk3YWE2NjM0ZmMxZGY4NmY0ZSIsIjU3MTFjNmU1ODIyMzI1NmZjZmY1YTY2MCIsIjYwMTk4M2FmMTlhNTIzZjhiMTcyYjkyYSIsImQyYzA4M2JjYzYyNTEyODEwZTBkYzQ1NiIsImVmMzA0NTI5YmZmZWVjYWVhM2M2OTc4MyJdfQ==",
  "routing": {
    "code": [
      "8dd5a2cd304188d7948fa27f",
      "7a491287b2e34e4eab9dbe0c"
    ],
    "named": [],
    "phrasings": [
      "gov memaudit judge rows forbidden_cited, the forbidden source a reader cited, figures counts only, say.py printer refusal, retrieval namespace policies lexical embedding stale_class",
      "gov memaudit judge rows forbidden_cited forbidden source reader cited figures counts only say.py printer refusal retrieval namespace policies lexical embedding stale_class"
    ]
  },
  "pool": {
    "settings": {
      "meaning_uncut": true,
      "route_depth": 60,
      "rerank_depth": 40,
      "per_file_first10": 2,
      "drop_nested": true
    },
    "reranked": 40,
    "order": "first",
    "nested": [
      {
        "chunk_id": "b4a97d4f1551e14fd9409e40",
        "path": "src/gov/memaudit/judge.py",
        "start_line": 94,
        "end_line": 112
      },
      {
        "chunk_id": "3ec932527e8ca3f6d041f32b",
        "path": "src/gov/memaudit/judge.py",
        "start_line": 78,
        "end_line": 95
      }
    ]
  }
}
