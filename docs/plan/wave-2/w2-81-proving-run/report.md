# W2-81 proving ground: NOT_READY

Seed 7429927; mode read; hidden half present and asked in 6 of 6 repositories.
Release 0.1.4; sessions: adopter claude-sonnet-5-5, reader claude-sonnet-5-5, grader claude-sonnet-5-5.

- python-app: python-app.misleading-name.live-under-old-name is NOT_BUILT
- python-app: python-app.misleading-name.dead-under-current-name is NOT_BUILT
- python-app: python-app.orphaned-test.module-removed is NOT_BUILT
- python-app: python-app.superseded-plan.names-it is NOT_BUILT
- python-app: python-app.stale-spec.newer-version is NOT_BUILT
- python-app: hidden variant #1 (f01) is NOT_BUILT
- python-app: stage VERDICT is NOT_BUILT
- python-app: stage findings is NOT_BUILT
- python-app: the end-to-end figure is 80.9524, below its bar of 95
- rust-workspace: rust-workspace.orphaned-test.function-removed is NOT_BUILT
- rust-workspace: rust-workspace.superseded-plan.by-version is NOT_BUILT
- rust-workspace: rust-workspace.stale-spec.newer-rfc is NOT_BUILT
- rust-workspace: hidden variant #2 (f02) is NOT_BUILT
- rust-workspace: hidden variant #3 (f03) is NOT_BUILT
- rust-workspace: hidden variant #4 (f04) is NOT_BUILT
- rust-workspace: rust-workspace.control.current-spec-looks-old is FLAGGED
- rust-workspace: rust-workspace.control.live-file-in-legacy-folder is FLAGGED
- rust-workspace: stage A10 is ABSENT
- rust-workspace: stage VERDICT is NOT_BUILT
- rust-workspace: stage findings is NOT_BUILT
- rust-workspace: the end-to-end figure is 75, below its bar of 95
- typescript-monorepo: typescript-monorepo.misleading-name.live-under-old-name is NOT_BUILT
- typescript-monorepo: typescript-monorepo.misleading-name.dead-under-current-name is NOT_BUILT
- typescript-monorepo: typescript-monorepo.secret.token-in-script is NOT_BUILT
- typescript-monorepo: typescript-monorepo.orphaned-test.file-removed is NOT_BUILT
- typescript-monorepo: typescript-monorepo.stale-spec.newer-adr is NOT_BUILT
- typescript-monorepo: hidden variant #5 (f05) is NOT_BUILT
- typescript-monorepo: stage VERDICT is NOT_BUILT
- typescript-monorepo: stage findings is NOT_BUILT
- typescript-monorepo: the end-to-end figure is 60, below its bar of 95
- legacy-docs: legacy-docs.legacy-document.extract is NOT_BUILT
- legacy-docs: legacy-docs.legacy-document.retire is NOT_BUILT
- legacy-docs: legacy-docs.large-file.dataset is MISSED
- legacy-docs: legacy-docs.large-file.media is MISSED
- legacy-docs: legacy-docs.superseded-plan.names-it is NOT_BUILT
- legacy-docs: hidden variant #7 (f07) is NOT_BUILT
- legacy-docs: hidden variant #8 (f08) is NOT_BUILT
- legacy-docs: hidden variant #9 (f09) is NOT_BUILT
- legacy-docs: hidden variant #10 (f10) is NOT_BUILT
- legacy-docs: legacy-docs.control.current-spec-looks-old is FLAGGED
- legacy-docs: legacy-docs.control.live-file-in-legacy-folder is FLAGGED
- legacy-docs: stage VERDICT is NOT_BUILT
- legacy-docs: stage findings is NOT_BUILT
- legacy-docs: the end-to-end figure is 60, below its bar of 95
- secret-history: secret-history.misleading-name.live-under-old-name is NOT_BUILT
- secret-history: secret-history.misleading-name.dead-under-current-name is NOT_BUILT
- secret-history: secret-history.secret.key-in-config is NOT_BUILT
- secret-history: hidden variant #11 (f11) is NOT_BUILT
- secret-history: hidden variant #12 (f12) is NOT_BUILT
- secret-history: hidden variant #13 (f13) is NOT_BUILT
- secret-history: secret-history.control.current-spec-looks-old is FLAGGED
- secret-history: secret-history.control.live-file-in-legacy-folder is FLAGGED
- secret-history: stage VERDICT is NOT_BUILT
- secret-history: stage findings is NOT_BUILT
- secret-history: the end-to-end figure is 80, below its bar of 95
- python-app-clean: stage VERDICT is NOT_BUILT
- python-app-clean: stage findings is NOT_BUILT
- python-app: gov queue pa-smko ended with exit 3
- rust-workspace: gov queue rw-vyk3 ended with exit 3
- typescript-monorepo: gov queue tm-4kpa ended with exit 3
- legacy-docs: gov queue ld-mj6i ended with exit 3
- secret-history: gov queue sh-e15w ended with exit 3
- python-app-clean: gov queue pac-73p5 ended with exit 3

## python-app

End-to-end figure 80.95238095238095 (bar 95; 17 of 21 questions judged right); diagnostic, never a bar: hit@5 57.1, stacked share 66.7; gov queue: {'run': True, 'ticket': 'pa-smko', 'exit': 3}; not built: A2-content-class, VERDICT, findings; hidden half: present and asked (10 hidden questions asked, at least 10 needed)

| Planted problem | Status | Evidence |
|---|---|---|
| `python-app.misleading-name.live-under-old-name` | NOT_BUILT | A2-content-class (CAP-44.b): A2 classes by path-map namespace only and reads no content: no class current, historical, superseded, live or dead, no successor or newer source, is recorded |
| `python-app.misleading-name.dead-under-current-name` | NOT_BUILT | A2-content-class (CAP-44.b): A2 classes by path-map namespace only and reads no content: no class current, historical, superseded, live or dead, no successor or newer source, is recorded |
| `python-app.orphaned-test.module-removed` | NOT_BUILT | findings (CAP-44.g): finding states and human gates: no stage scans the history for secrets or records a finding (a secret, an orphaned test, drift) with a state and a gate |
| `python-app.superseded-plan.names-it` | NOT_BUILT | A2-content-class (CAP-44.b): A2 classes by path-map namespace only and reads no content: no class current, historical, superseded, live or dead, no successor or newer source, is recorded |
| `python-app.stale-spec.newer-version` | NOT_BUILT | A2-content-class (CAP-44.b): A2 classes by path-map namespace only and reads no content: no class current, historical, superseded, live or dead, no successor or newer source, is recorded |
| `hidden variant #1 (f01)` | NOT_BUILT | withheld: a hidden variant |


| Control | Status |
|---|---|
| `python-app.control.current-spec-looks-old` | CLEAN |
| `python-app.control.live-file-in-legacy-folder` | CLEAN |

## rust-workspace

End-to-end figure 75.0 (bar 95; 15 of 20 questions judged right); diagnostic, never a bar: hit@5 55.0, stacked share 70.0; gov queue: {'run': True, 'ticket': 'rw-vyk3', 'exit': 3}; not built: A2-content-class, A8-documents, VERDICT, findings; hidden half: present and asked (10 hidden questions asked, at least 10 needed)

| Planted problem | Status | Evidence |
|---|---|---|
| `rust-workspace.orphaned-test.function-removed` | NOT_BUILT | findings (CAP-44.g): finding states and human gates: no stage scans the history for secrets or records a finding (a secret, an orphaned test, drift) with a state and a gate |
| `rust-workspace.superseded-plan.by-version` | NOT_BUILT | A2-content-class (CAP-44.b): A2 classes by path-map namespace only and reads no content: no class current, historical, superseded, live or dead, no successor or newer source, is recorded |
| `rust-workspace.stale-spec.newer-rfc` | NOT_BUILT | A2-content-class (CAP-44.b): A2 classes by path-map namespace only and reads no content: no class current, historical, superseded, live or dead, no successor or newer source, is recorded |
| `hidden variant #2 (f02)` | NOT_BUILT | withheld: a hidden variant |
| `hidden variant #3 (f03)` | NOT_BUILT | withheld: a hidden variant |
| `hidden variant #4 (f04)` | NOT_BUILT | withheld: a hidden variant |


| Control | Status |
|---|---|
| `rust-workspace.control.current-spec-looks-old` | FLAGGED |
| `rust-workspace.control.live-file-in-legacy-folder` | FLAGGED |

## typescript-monorepo

End-to-end figure 60.0 (bar 95; 12 of 20 questions judged right); diagnostic, never a bar: hit@5 40.0, stacked share 50.0; gov queue: {'run': True, 'ticket': 'tm-4kpa', 'exit': 3}; not built: A2-content-class, VERDICT, findings; hidden half: present and asked (10 hidden questions asked, at least 10 needed)

| Planted problem | Status | Evidence |
|---|---|---|
| `typescript-monorepo.misleading-name.live-under-old-name` | NOT_BUILT | A2-content-class (CAP-44.b): A2 classes by path-map namespace only and reads no content: no class current, historical, superseded, live or dead, no successor or newer source, is recorded |
| `typescript-monorepo.misleading-name.dead-under-current-name` | NOT_BUILT | A2-content-class (CAP-44.b): A2 classes by path-map namespace only and reads no content: no class current, historical, superseded, live or dead, no successor or newer source, is recorded |
| `typescript-monorepo.secret.token-in-script` | NOT_BUILT | findings (CAP-44.g): finding states and human gates: no stage scans the history for secrets or records a finding (a secret, an orphaned test, drift) with a state and a gate |
| `typescript-monorepo.orphaned-test.file-removed` | NOT_BUILT | findings (CAP-44.g): finding states and human gates: no stage scans the history for secrets or records a finding (a secret, an orphaned test, drift) with a state and a gate |
| `typescript-monorepo.stale-spec.newer-adr` | NOT_BUILT | A2-content-class (CAP-44.b): A2 classes by path-map namespace only and reads no content: no class current, historical, superseded, live or dead, no successor or newer source, is recorded |
| `hidden variant #5 (f05)` | NOT_BUILT | withheld: a hidden variant |
| `hidden variant #6 (f06)` | FOUND_AND_HANDLED | withheld: a hidden variant |


| Control | Status |
|---|---|
| `typescript-monorepo.control.current-spec-looks-old` | CLEAN |
| `typescript-monorepo.control.live-file-in-legacy-folder` | CLEAN |

## legacy-docs

End-to-end figure 60.0 (bar 95; 12 of 20 questions judged right); diagnostic, never a bar: hit@5 55.0, stacked share 55.0; gov queue: {'run': True, 'ticket': 'ld-mj6i', 'exit': 3}; not built: A2-content-class, A8-documents, VERDICT, findings; hidden half: present and asked (10 hidden questions asked, at least 10 needed)

| Planted problem | Status | Evidence |
|---|---|---|
| `legacy-docs.legacy-document.extract` | NOT_BUILT | A8-documents (CAP-44.e): A8 retires rule files, memory stores and chat databases only (legacy.KINDS); it extracts or retires no legacy document |
| `legacy-docs.legacy-document.retire` | NOT_BUILT | A8-documents (CAP-44.e): A8 retires rule files, memory stores and chat databases only (legacy.KINDS); it extracts or retires no legacy document |
| `legacy-docs.large-file.dataset` | MISSED | data/rostering-2009.bin is not classed |
| `legacy-docs.large-file.media` | MISSED | media/payroll-briefing-2009.wav is not classed |
| `legacy-docs.superseded-plan.names-it` | NOT_BUILT | A2-content-class (CAP-44.b): A2 classes by path-map namespace only and reads no content: no class current, historical, superseded, live or dead, no successor or newer source, is recorded |
| `hidden variant #7 (f07)` | NOT_BUILT | withheld: a hidden variant |
| `hidden variant #8 (f08)` | NOT_BUILT | withheld: a hidden variant |
| `hidden variant #9 (f09)` | NOT_BUILT | withheld: a hidden variant |
| `hidden variant #10 (f10)` | NOT_BUILT | withheld: a hidden variant |

Not measured: large-file: `within the budget`: no budget for the index is stated in the path map (its schema has no such field), in the index's records or in the Contract, so the judge has none to read; the clause is not measured today

| Control | Status |
|---|---|
| `legacy-docs.control.current-spec-looks-old` | FLAGGED |
| `legacy-docs.control.live-file-in-legacy-folder` | FLAGGED |

## secret-history

End-to-end figure 80.0 (bar 95; 16 of 20 questions judged right); diagnostic, never a bar: hit@5 70.0, stacked share 75.0; gov queue: {'run': True, 'ticket': 'sh-e15w', 'exit': 3}; not built: A2-content-class, VERDICT, findings; hidden half: present and asked (10 hidden questions asked, at least 10 needed)

| Planted problem | Status | Evidence |
|---|---|---|
| `secret-history.misleading-name.live-under-old-name` | NOT_BUILT | A2-content-class (CAP-44.b): A2 classes by path-map namespace only and reads no content: no class current, historical, superseded, live or dead, no successor or newer source, is recorded |
| `secret-history.misleading-name.dead-under-current-name` | NOT_BUILT | A2-content-class (CAP-44.b): A2 classes by path-map namespace only and reads no content: no class current, historical, superseded, live or dead, no successor or newer source, is recorded |
| `secret-history.secret.key-in-config` | NOT_BUILT | findings (CAP-44.g): finding states and human gates: no stage scans the history for secrets or records a finding (a secret, an orphaned test, drift) with a state and a gate |
| `hidden variant #11 (f11)` | NOT_BUILT | withheld: a hidden variant |
| `hidden variant #12 (f12)` | NOT_BUILT | withheld: a hidden variant |
| `hidden variant #13 (f13)` | NOT_BUILT | withheld: a hidden variant |


| Control | Status |
|---|---|
| `secret-history.control.current-spec-looks-old` | FLAGGED |
| `secret-history.control.live-file-in-legacy-folder` | FLAGGED |

## python-app-clean

End-to-end figure 95.0 (bar 95; 19 of 20 questions judged right); diagnostic, never a bar: hit@5 80.0, stacked share 85.0; gov queue: {'run': True, 'ticket': 'pac-73p5', 'exit': 3}; not built: VERDICT, findings; hidden half: present and asked (10 hidden questions asked, at least 10 needed)

| Planted problem | Status | Evidence |
|---|---|---|


| Control | Status |
|---|---|
| `python-app-clean.control.current-spec-looks-old` | CLEAN |
| `python-app-clean.control.live-file-in-legacy-folder` | CLEAN |
