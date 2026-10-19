# Exit package, part "what makes the hosted CI green" (owner note of 2026-10-09; classified under prompt section 11)

First real run on GitHub: run 37959334612, commit c7e5c3ed. Passed: setup, checkout, package install, the
gitleaks download with checksum verification, the gitleaks scan. Failed: `gov ci job`, the project tests,
the evidence record. Warning: actions/checkout on deprecated Node 20. All as W1-40's residuals said.

## 1. Runner tools for the owner to approve (DEC-083, DEC-497)

| Tool | Version | Checksum | Source of the figure |
|---|---|---|---|
| rulesync | 24.0.0 | sha256 64e8ad323ad4ef991b21c6a54548e6a2bb02f9facaf9c6cfe9e0782ac3297c71 (release binary rulesync-linux-x64) | tool registry, DEC-074 |
| openspec | 1.13.2 (npm @fission-ai/openspec, Node 22) | sha256 ca136f0e9fd4951dcf93d8ed729ebc97b2d97d3980cd9dc9d42fc80e32e797c6 (its entry script bin/openspec.js) | tool registry, DEC-074. For a runner install the npm tarball's own integrity value is the one to pin: NOT recorded yet |
| pytest | 9.0.3 (the version on this machine) | NOT recorded: pytest has no registry entry | to be taken from the package index when the owner approves; no agent downloads it |
| pytest-xdist | 3.8.0 | sha256 202ca578cfeb7370784a8c33d6d05bc6e13b4f25b5053c30a152269fd10f0b88 | tool registry, DEC-514; needed only if CI runs the tests in parallel |

The workflow installs gitleaks from the registry's archive with its checksum; the same form (archive +
archive checksum in the registry, verified before use) is the one to follow for the three. That is a change
of `.github/workflows/ci.yml` and its template: new work, see the classification.

## 2. Hooks and the notes ref

- `~/.local/bin/lefthook install` in this repository: the owner's step (never an agent's), at the exit, once
  the baseline is empty.
- With the hooks installed, `gov ci push <remote>` runs before each push and writes the evidence record as
  a git note on the head commit under `refs/notes/gov-evidence`.
- The notes ref must be pushed with each push: `git push <remote> refs/notes/gov-evidence` (or a push
  refspec for it in the remote's configuration, set once by the owner). No agent pushes (DEC-465).
- Until both are done, the workflow's "fetch the ref" and "evidence record" steps fail, correctly.

## 3. Declared checks: which can run on a hosted runner and which are local-only

My reading of the 20 declarations (to be confirmed when the work is done; today `gov ci job` runs them all
and a check that cannot run there fails or reads "unmeasured"):

- **Run in CI as they are (repository content only):** core-authority, core-claims, core-commands,
  core-graph, core-mutation, core-pathmap, core-schema, skill-regression-a, skill-regression-b1,
  skill-regression-orchestration.
- **Run in CI only with the full history** (the workflow checks out two commits): core-decision-citations,
  product-traceability-trailers. Needs `fetch-depth: 0` or they misjudge.
- **Run in CI only with an approved tool:** adapter-portability (rulesync); the openspec validation of the job.
- **Local-only** (need the local indexes, the runtime folder or the dev tiers): index-freshness,
  retrieval-regression, recovery-rebuild, context-reproducibility, fresh-agent-reconstruction,
  secrets-indexing, audit-reproducibility. To be reported by the job as "local-only", never as failed or
  green: this needs a declared field per check and a change of `gov ci job`: new work.
- The baseline reds end with this repository's adoption (DEC-522), not with CI work.
- The project tests: `python3 -m pytest tests` is every acceptance suite (about 50 minutes in the parallel
  form on this machine, with tools and local models the runner lacks). What CI runs of them is the Wave 2
  item "fast feedback at scale" (DEC-567: staged gates, the full suite on CI machines).

## 4. actions/checkout

The workflow pins actions/checkout at commit 11bd7190… (v4.2.2, Node 20). Bump to the current major that
runs on Node 24, pinned by commit id as now, in the workflow and in its template (the two are held
byte-identical by a W1-40 case). The new commit id is the owner's or operator's to supply: no agent reads
the network for it.

## Classification (prompt section 11)

- **No Wave 1 exit criterion names this repository's hosted CI.** WBS section 4 and W1-42's KPI lines ask
  for a CI step in the spec-first cycle on the a-dev and b-dev clones (criterion 1), for `gov check` with 17
  of 17 families, and for an empty baseline here.
- **Not a fail-open:** every failure of the run is red or "unmeasured", never falsely green.
- **One reading the owner must confirm:** criterion 1's "CI" on the clones. Read as the CI gate W1-40 built,
  run in the clone (`gov ci job`, the hooks and the evidence record, with the tools of this machine), it is
  met without any of the above. Read as a hosted run on GitHub for the clones, items 1 to 3 would be needed
  before W1-42 and would come as a package.
- **So:** items 1, 2 and 4 are owner actions in the exit package; the workflow changes of 1, 3 and 4 and the
  "local-only" reporting are Wave 2 list items (with "fast feedback at scale"), no round in Wave 1.

## Runner tool added 2026-10-10 (DEC-605)

- **gov 0.1.0**, this repository's own command line: an editable user-level install (python3 -m pip install --user --break-system-packages -e <the repository>), script ~/.local/bin/gov (sha256 0ef910b0ab1f6377d83f2e1f2d300a1e50c3d2b11a42a8f0edb479b81b7f4c80), in governance/project/tool-registry.yaml with approval DEC-605. An adopted project's hooks and check commands need it. A hosted runner needs the same: gov installed from a pinned commit of this repository before the gate runs. After DEC-603 the generated hook commands carry no PYTHONPATH prefix, so an installed gov is a requirement of every adopted project, to be stated in the adoption notes.
