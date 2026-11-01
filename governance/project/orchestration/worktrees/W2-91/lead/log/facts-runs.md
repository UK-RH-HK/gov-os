# W2-91 run facts (lead)

## base
- clone: `/home/usain/gov-os-runs/W2-91/base` (`git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS`, detached at `f46b96537d74`)
- disk gate before the rebuild: disk gate open: 855 GiB free, 64598040 inodes free
- rebuild: pinned gov (`GOV_REBUILD_PYTHON=/home/usain/.local/share/gov-os/pin-5c401220/bin/python`, no PYTHONPATH, no GOV_TICKET) through `tools/rebuild_slot.sh` (a heavy-job slot and the clone's own lock, DEC-1001 (d)); script start 2026-11-01T16:01:30Z, end 2026-11-01T17:21:07Z, exit 0
- rebuild result: ok True; stores {'lexical': {'status': 'recreated'}, 'semantic': {'status': 'recreated'}, 'codeintel': {'status': 'recreated'}}; timing {'lexical_s': 278.9}
- digest (`result.digest`): `6de3fba99c6fed852b3e99428897af100ee28096e2575ff5ec7c436030ea96a4`
- sha256 after the rebuild:
```
473eba4c3a67683fcd286e477a4c012a2e8a9f9b0e776506464096aac47f1a9b  .gov-runtime/store.db
5e422adca9c8969ef5d3b6c50aec461cee58342191308cedb17ee104bd671764  .gov-runtime/codeintel/home/code.db
6881a590e961b4c4faff0180c79e87d6af9c34a9367e12cf28bbe2dbc4028cf8  .gov-runtime/codeintel/home/_config.db
```
- measure: start 2026-11-01T17:21:07Z, end 2026-11-01T17:34:26Z, exit 0, stderr empty

## head
- clone: `/home/usain/gov-os-runs/W2-91/head` (`git clone --no-hardlinks /home/usain/Dynamic-Agentic-Engineering-OS`, detached at `b652fc96d2b5`)
- disk gate before the rebuild: disk gate open: 853 GiB free, 64434966 inodes free
- rebuild: pinned gov (`GOV_REBUILD_PYTHON=/home/usain/.local/share/gov-os/pin-5c401220/bin/python`, no PYTHONPATH, no GOV_TICKET) through `tools/rebuild_slot.sh` (a heavy-job slot and the clone's own lock, DEC-1001 (d)); script start 2026-11-01T16:45:25Z, end 2026-11-01T18:40:14Z, exit 0
- rebuild result: ok True; stores {'lexical': {'status': 'recreated'}, 'semantic': {'status': 'recreated'}, 'codeintel': {'status': 'recreated'}}; timing {'lexical_s': 297.7}
- digest (`result.digest`): `6061a0dbebd18d2809bfbaf189f0bb6abcd7eb3f303803907690c86dfe9b8dfa`
- sha256 after the rebuild:
```
687afd8bbc57794482b3109db3af7a1ddc03e732e6d9503c8de7a9bdbaf02e04  .gov-runtime/store.db
78e750993574dd245478457feea5d51a5b4843dea2f93c963fec1a7e369a7062  .gov-runtime/codeintel/home/code.db
6881a590e961b4c4faff0180c79e87d6af9c34a9367e12cf28bbe2dbc4028cf8  .gov-runtime/codeintel/home/_config.db
```
- measure: start 2026-11-01T18:40:53Z, end 2026-11-01T19:35:16Z, exit 0, stderr empty

## Notes
- The base clone also serves as the measure's own clone: the measure's code (`src/gov/retrieval/measure.py`) and the visible set are read from it (`--sets-root`), at `f46b96537d74`, which was `w2/integrate`'s head when the ticket started.
- `git diff --stat f46b96537d74 b652fc96d2b5 -- src` is empty: the code is the same at base and head.
- The head (`b652fc96d2b5`) holds, besides the ticket's commits, the lead's merge of `w2/integrate` (`904bb3a0e7c6`) for the ticket's claim; it brought records, the merge queue's tool and its unit test, no code under `src/`.
- The head's rebuild script started at 16:45:25 but waited for a heavy-job slot until about 17:11 (all three slots were busy).
- The head's first measure was stopped by the lead before it wrote a record (its background task's two-hour limit was minutes away); the measure was then run alone on the same store (`measure_head_only.sh`). The store was not rebuilt again.
- The control's rebuild of the first attempt waited on the old machine-wide lock and was stopped before it started (never a running rebuild); the rebuilds above are the second attempt, in the new form.
