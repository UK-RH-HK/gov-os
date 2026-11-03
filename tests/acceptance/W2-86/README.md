# W2-86 (DAEO-jsg1) acceptance tests

The kernel template is embedded as the path map means it (DEC-952 item 1, DEC-388 DP-8, DEC-381, DEC-694).
Written by the independent test designer (MR-3) before the implementation, from the ticket's KPI lines.

## How the tests find what they test

- The repository is the one the test file sits in: `Path(__file__).resolve().parents[3]`. No worktree path is
  written in the tests. Tracked files come from `git ls-files` run there. The path map is that repository's
  `governance/project/path-map.yaml`, read with `gov.config.loader.load_config`.
- `gov` is imported from `PYTHONPATH`, set per command to the same repository's `src/`. Every selection checks
  that `gov.__file__` lies under `<repository>/src` and fails if it does not:
  `PYTHONPATH=<repository>/src python3 -m pytest tests/acceptance/W2-86 -q -p no:cacheprovider`.
- The selection is the semantic route's own, `semantic._wanted(root, connection)`. It is given a chunk table built
  with `lexical.SCHEMA` in pytest's temporary folder, one chunk per tracked path. No embedder, rebuild, network
  or store is used, and nothing is written in the repository.

## Cases

| Case | KPI lines |
|---|---|
| 1 `test_template_in_one_namespace_each_and_embedded_except_vendored_and_generated` | success 1 (the files' selection; the vector counts from the clone's store belong to the lead's measure record); success 2; success 3 (every tracked path under `template/` in exactly one namespace); failure 1; failure 3 (no namespace or two) |
| 2 `test_every_namespace_states_one_of_the_two_values` | success 3 (the two values only; `semantic.EMBEDDED` is still the one exact value); failure 3 (another value); failure 4 (a free-text exception that stays in the map fails here) |
| 3 `test_guard_outside_template_every_verdict_as_at_the_base` | success 4 (each file outside `template/` keeps its verdict); failure 2 |

These tests leave four things out:
- the unchanged indexer code in success 3 and failure 4, which the close's diff shows (the ticket's
  `allowed_paths` hold no `src/`);
- the store comparison in success 4;
- success 5 and failure 5, W2-61's re-measure;
- the vector counts in success 1.

The last three need the embedder and the built stores. They go in `docs/research/W2-86-memory-measure.md`.

Case 1 sorts the files into sets:
- **Vendored:** `template/governance/kernel/vendor/**`, `template/governance/kernel/bin/**`, and every file in a
  folder below `template/governance/kernel/skills/superpowers/`.
- **Generated:** `template/.rulesync/**`.
- **Embedded:** every other tracked file under `template/`, `superpowers/vendored.yaml` among them.

The case also checks that the vendored, generated, role, hook and kernel-skill sets each hold at least one file,
so it cannot pass with an empty set.

## Red at the base `9dc5288161c4` (the path map before the change)

- **Case 1 fails** because the selection embeds none of the 93 kernel-template files it should. `kernel-template`
  (`template/**`) says `embedded, except vendored code`, and DEC-388 reads that as not embedded. At the base,
  every path under `template/` is in exactly one namespace, so the failure comes from the selection.
- **Case 2 fails** with `{'kernel-template': 'embedded, except vendored code'}`.
- **Case 3 is a guard.** It passes at the base and must still pass after the change. It compares the selection's
  verdict for every tracked path outside `template/` under the repository's path map with the verdict under the
  base's path map, which it reads with `git show 9dc5288161c4:governance/project/path-map.yaml` into a temporary root.

## KPI map after D-4's cut (DEC-1061)

Regenerated in round 2 of the cut (DEC-1061; the review's F3, F4): each line of the ticket's `kpis:` is placed
by its own words (or by the designer, or by part A's row for that line), never by the README's layout; each
case named here runs in the full run, with every row of a class the line names; tier 2's cap then cut only
the rest. The rest stay built: `breadth` (`tests/optin-lifted*breadth*.txt`, `--optin=breadth`) and, for the
switched-off features, `lifted` (the other `tests/optin-lifted*.txt`, `--optin=lifted`). The placement is data
(`placement.json`, with the designer's `overrides.json`), checked by code against the default collection.

Cases: 3 in the full run, 0 in `breadth`, 0 in `lifted`.

| KPI line | case(s) in the full run (rows in the full run of the function's rows) | placed by |
|---|---|---|
| S1: After a rebuild with the embedder, the kernel's own files under template/ have vectors: every role file (template/governance/kernel/roles/*.md)... | `test_w2_86_kernel_template_embedding.py::test_template_in_one_namespace_each_and_embedded_except_vendored_and_generated` | the ticket's words |
| S2: Vendored code has no vector: template/governance/kernel/vendor/**, the kernel's copies of the vendored skills (template/governance/kernel/skill... | `test_w2_86_kernel_template_embedding.py::test_template_in_one_namespace_each_and_embedded_except_vendored_and_generated` | the ticket's words |
| S3: The path map states it in its two valid values only: kernel-template says embedded, each new namespace says not embedded, and no namespace stat... | `test_w2_86_kernel_template_embedding.py::test_every_namespace_states_one_of_the_two_values`, `test_w2_86_kernel_template_embedding.py::test_template_in_one_namespace_each_and_embedded_except_vendored_and_generated` | the ticket's words |
| S4: Nothing else moves: for every tracked path outside template/ the indexer's embedding verdict is the same at the head as at the ticket's base; b... | `test_w2_86_kernel_template_embedding.py::test_template_in_one_namespace_each_and_embedded_except_vendored_and_generated`, `test_w2_86_kernel_template_embedding.py::test_guard_outside_template_every_verdict_as_at_the_base` | the ticket's words |
| S5: W2-61's measure is re-run after the change on the visible half, on a clone at the branch head with stores built by the pinned gov, and on a clo... | none: the measure's research record line (docs/research/W2-86-memory-measure.md) | designer |
| F1: A vendored file, or a generated adapter copy, embedded. | `test_w2_86_kernel_template_embedding.py::test_template_in_one_namespace_each_and_embedded_except_vendored_and_generated` | the ticket's words |
| F2: A file outside template/ gains or loses its embedding. | `test_w2_86_kernel_template_embedding.py::test_template_in_one_namespace_each_and_embedded_except_vendored_and_generated`, `test_w2_86_kernel_template_embedding.py::test_guard_outside_template_every_verdict_as_at_the_base` | the ticket's words |
| F3: A namespace states a value other than embedded or not embedded, or a tracked path under template/ falls in no namespace or in two. | `test_w2_86_kernel_template_embedding.py::test_template_in_one_namespace_each_and_embedded_except_vendored_and_generated`, `test_w2_86_kernel_template_embedding.py::test_every_namespace_states_one_of_the_two_values` | the ticket's words |
| F4: The indexer changed to honour a free-text exception (DEC-694's two values stay). | `test_w2_86_kernel_template_embedding.py::test_every_namespace_states_one_of_the_two_values` | the ticket's words |
| F5: A figure of the measure reported without the other, or the hidden half read or run. | none: the measure's research record line | designer |
