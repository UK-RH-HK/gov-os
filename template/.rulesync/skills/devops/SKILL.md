---
name: devops
version: "1.1.0"
description: "The engineer's skill for build and release tickets: hermetic builds, pinned versions and rollback, with a pre-commit checklist and the unit-test focus. Use beside the engineer role when a ticket changes a build, image or pipeline file."
output: "<allowed_path>/** (one entry of the ticket's allowed_paths)"
metadata:
  version: "1.1.0"
---

# DevOps

The engineer's skill for a ticket that changes how the code is built, packaged or released: a build file, an image
definition, a pipeline file, a release script (DEC-957 Q5, DEC-959 item 4). An engineer loads it beside the engineer
role. The guard, the launcher and the role file decide what a session may do; this skill is a method only and grants
nothing (CAP-24.b). Its three scenarios: [scenarios.md](scenarios.md); its check: `check_domain_skill.py`, in this
folder.

## When / not when

- Use it when the ticket's paths hold a build, image, pipeline or release file, or the scripts they call.
- Not for application code: use the skill of its area. Not for the guard, the launcher or the governance tools
  themselves: those are changed under their own tickets.

## Inputs

Read first, before anything else:

- the ticket: its KPI lines and `allowed_paths`, and the spec it cites;
- the build, image and pipeline files as they are, with their lockfiles and the last release they produced;
- the project's own values: `<the project's pipeline layout and naming>`, `<the project's release and rollback
  procedure>`, `<the project's secret store>`;
- what else it needs to know, through `gov retrieve` first (DEC-836).

## Steps

Copy this checklist into your notes and tick each step as you go.

- [ ] 1. Read the files and lockfiles; list every input of the build (base image, packages, tools, downloads) and
  every step of the release.
- [ ] 2. Write the unit test or check for the change first (the test-driven-development skill): a script test, a
  lint of the file, a dry run that needs no network.
- [ ] 3. Make the change by the conventions and the three points below: hermetic builds, pinned versions, rollback.
- [ ] 4. Run your checks locally, then go through the pre-commit checklist.
- [ ] 5. Run the acceptance tests only through `gov accept`, once they are ready; you see pass or fail, never the
  tests (the engineer role).

You write and test the files; you never run a deploy or trigger a pipeline: those classes stay denied to the engineer
(the engineer role).

**Conventions:**

- Files, jobs and stages are named and laid out as `<the project's pipeline layout and naming>`: one job, one
  purpose; each stage's inputs and outputs named.
- A build is a script in the repository, run by the pipeline; the pipeline file only calls it.
- A value that differs by environment is a named input; a secret comes from `<the project's secret store>`, never
  from the file.
- Every release has a version that never changes once made; every step that can fail says how it is known to have
  failed.

**Hermetic builds:** the same inputs build the same output, with no network at build time beyond a declared, pinned
fetch. Every input is declared and versioned: base image, system packages, language packages (installed from the
lockfile), tools. No download piped into a shell; a vendored or checksummed one instead. No clock, host name or
unstated environment variable shapes the output.

**Pinned versions:** every base image, package, tool and action is pinned to an exact version, an image also to its
digest (`<digest>`); never `latest`, never a range. A bump is its own change, with its reason, and it updates the
lockfile with it.

**Rollback:** a release can be undone as easily as it was made. Each release has an immutable version; the previous
one is recorded before the change and kept; a health check decides success; a rollback step is written and tried in a
dry run. A change that cannot be undone, such as a column drop, is split: the old version keeps working until a later
release removes what it needed.

**Unit-test focus:** what runs without the network or a real deploy: the build script's logic and its failure paths; the
pipeline file's validity and that its pins are present; the rollback step on a dry run; that a missing input or a failed
health check stops the release. Not a live deploy.

**Common mistakes:**

- `latest` or a floating tag as a base image, a package or an action.
- `npm install` or the like where the lockfile's install belongs; system packages with no version.
- A download piped into a shell; a download with no checksum.
- A deploy step with no recorded previous version, no health check and no rollback step.
- A migration that drops what the running version still reads, in the same release.
- A secret written into a pipeline file, a script or an image layer.
- A build that passes only with the network, or only on one host.

**Pre-commit checklist:**

- [ ] Every base image, package, tool and action is pinned to an exact version; images also by digest.
- [ ] Language packages are installed from the lockfile, and the lockfile changed with the pin.
- [ ] No download piped into a shell; every fetched file is versioned and checksummed or vendored.
- [ ] The build needs no network beyond its declared, pinned fetches, and the same inputs give the same output.
- [ ] Each release has an immutable version, a recorded previous version, a health check and a rollback step.
- [ ] No change in the release that the previous version cannot run beside.
- [ ] No secret in any file; secrets come from the secret store.
- [ ] Only the ticket's paths changed; nothing was deployed or triggered.

## Done when

- [ ] The pre-commit checklist is ticked, each item checked in the files, not remembered.
- [ ] The checks pass without the network; the acceptance tests, if ready, were run once through `gov accept`.
- [ ] `python3 <skill folder>/check_domain_skill.py <SKILL.md>` prints PASS, when this skill itself changed.

If any is false: fix, then check again.

## Output and handover

- The build, image, pipeline or release files and their checks, written only at the ticket's paths.
- The return starts with the twelve fields, each a labelled line (task, status, work_completed, files_changed,
  evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action); refused
  twice for the same call, stop and return; an authentication error returns `AUTH_REQUIRED` (the orchestration
  skill's briefs-and-returns.md).
- Each pin, each rollback step and each release blocker found goes in `discoveries`, with the file and line.

## Escalation

**When to escalate:** ranked by the escalation rubric (P3, P2, P1, Emergency; DEC-1219 (2)), to whoever started the session,
never to the owner directly.

- P3: a naming or layout choice inside the ticket's paths that changes no KPI; note it in `discoveries`.
- P2: a pipeline or image shared with another stream; a change to the ticket's scope or KPIs within the approved spec;
  a bump of a pinned version that another stream's build also uses.
- P1: a new tool, package or paid service (an install, a cost); a change that cannot be rolled back; any change to
  how secrets, access or production are handled; a release that needs a deploy, a pipeline run or the network to be
  tested; anything that fails open.
- Emergency: a secret found in a file, a log or an image; a risk of losing data; the disk below its floor; the guard
  failing open. Stop the affected work at once, never copy or use the secret, then go up as a P1.

## Never

Reminders only: the guard decides.

- This skill changes no role's reads or writes. Work that needs other writes goes back as a package for the role that
  holds them, never routed round (DEC-995, DEC-996).
- Run a deploy, trigger a pipeline, install a tool or reach the network to make a build pass.
- Use `latest`, a floating tag or a range, or pipe a download into a shell.
- Write a secret into a file, or print one in a note or a return.
- Ship a change with no way back, or a migration the previous version cannot run beside.

## Sources

DEC-957 (Q5 and the escalation rubric), DEC-959 (items 4 and 5), DEC-995, DEC-996, DEC-836, DEC-616, DEC-645,
DEC-315, DEC-1112 (3), CAP-24.b, ROLES-RESEARCH-1 §2.7 (SRE release engineering).
