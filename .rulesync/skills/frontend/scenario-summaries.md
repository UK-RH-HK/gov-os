# Scenario summaries: frontend

These are the summaries of the `gov skilleval` runs of the frontend skill recorded in `scenario-records.yaml` beside
this file, one entry per record entry, in the records' order. The replies are taken from the lead's capture of the
same run, because the `--json` envelope carries no reply text. Run 1 had no capture: its entries give only what the
record holds. The diagnostic run, the final run and run 3 (after the L1 change, skill version 1.2.0) have a capture;
the skill version changed between them (1.0.0 to 1.1.0, then to 1.2.0). The harness leaves this file out of the
session's copy, so the summaries are written by hand.

### Run 1, scenario 1: A control a keyboard cannot reach

- **Scenario:** 1
- **Verdict:** pass
- **run_at:** 2026-11-14T01:29:23+00:00
- **Skill version:** 1.0.0
- **Summary:**
  - No transcript was captured for this run, so the session's reply cannot be summarised.
  - The record's verdict is pass.
  - The record's cause is null; it holds no reason beyond the verdict.

### Run 1, scenario 2: State copied and mutated

- **Scenario:** 2
- **Verdict:** pass
- **run_at:** 2026-11-14T01:30:07+00:00
- **Skill version:** 1.0.0
- **Summary:**
  - No transcript was captured for this run, so the session's reply cannot be summarised.
  - The record's verdict is pass.
  - The record's cause is null; it holds no reason beyond the verdict.

### Run 1, scenario 3: A feature outside the support list

- **Scenario:** 3
- **Verdict:** fail
- **run_at:** 2026-11-14T01:31:06+00:00
- **Skill version:** 1.0.0
- **Summary:**
  - No transcript was captured for this run, so the session's reply cannot be summarised.
  - The record's verdict is fail.
  - The record's cause is "judged FAIL against the pass line"; the record does not say which part failed.

### Diagnostic run, scenario 1: A control a keyboard cannot reach

- **Scenario:** 1
- **Verdict:** pass
- **run_at:** 2026-11-14T01:40:52+00:00
- **Skill version:** 1.0.0
- **Summary:**
  - The workspace held only the skill, so the reply wrote no files and ran no tests; it reviewed the four diff lines against the skill's mistakes list and wrote the fixes and tests in the reply.
  - It proposed a native `<button type="button">` for Save, an `alt` built from the user's name, a `<button>` with `aria-label="Close"` for the icon, and a `:focus-visible` outline in place of `outline: none`, with unit tests that find controls by role and name.
  - The judgement passed it because each part of the pass line is met as a proposed fix and test; it noted the missing files do not matter and that the test's tab-order step may need adjusting.

### Diagnostic run, scenario 2: State copied and mutated

- **Scenario:** 2
- **Verdict:** pass
- **run_at:** 2026-11-14T01:41:44+00:00
- **Skill version:** 1.0.0
- **Summary:**
  - The reply wrote no files because there was no ticket or allowed path, and named four defects: a prop copied into state, a stored `visible` that can be derived, an in-place `push`, and a fetch in the render body with no loading, error or empty view.
  - It drafted a fixed component (the fetch in a cancelled `useEffect`, one `tasks` state, `visible` derived in render, `setTasks(prev => [...prev, newTask])`) and five unit tests found by role and name.
  - The judgement passed it because the immutable update, the derived list, the loading, error and empty views and the state-transition tests are all present; it left open who owns `tasks`.

### Diagnostic run, scenario 3: A feature outside the support list

- **Scenario:** 3
- **Verdict:** fail
- **run_at:** 2026-11-14T01:42:33+00:00
- **Skill version:** 1.0.0
- **Summary:**
  - The reply chose to animate behind a `document.startViewTransition` check with a plain page change as the fallback and left the browser list alone, but it wrote no code and sent the plan to the session's starter.
  - It said outright that the question is "not a P1" and put the Firefox gap in `discoveries` as a simplest-reading point.
  - The judgement failed it on the wrong rank, which alone fails the pass line, and also found no fallback code shown.

### Final run, scenario 1: A control a keyboard cannot reach

- **Scenario:** 1
- **Verdict:** pass
- **run_at:** 2026-11-14T01:49:43+00:00
- **Skill version:** 1.1.0
- **Summary:**
  - The reply said it was blocked because the ticket and component were not in the workspace, so it wrote no files and ran nothing, and gave a table of fixes for the four added lines with the component, stylesheet and tests.
  - It replaced the `div` with `<button type="button">`, gave the image an `alt` (or `alt=""` if the name sits beside it), named the icon button with `aria-label`, and deleted the `outline: none` rule, adding a `:focus-visible` ring only if the style guide has a token.
  - The judgement passed it because every part of the pass line is met and its tests find controls by role and name; it treated the open points as P3.

### Final run, scenario 2: State copied and mutated

- **Scenario:** 2
- **Verdict:** pass
- **run_at:** 2026-11-14T01:50:28+00:00
- **Skill version:** 1.1.0
- **Summary:**
  - The reply rewrote the component and wrote ten tests but saved nothing, because the write and `gov` permissions were not granted, and it said so plainly.
  - It removed the copied prop and the second `visible` state, derived the filtered list in render, used `setTasks(prev => [...prev, newTask])`, and moved the fetch into a cancelled `useEffect` with loading, error (with retry) and empty views.
  - The judgement passed it because the immutable update, the derived list, the three views and the state-transition tests are all present; it judged what the reply contains, not whether it ran.

### Final run, scenario 3: A feature outside the support list

- **Scenario:** 3
- **Verdict:** pass
- **run_at:** 2026-11-14T01:51:39+00:00
- **Skill version:** 1.1.0
- **Summary:**
  - The reply wrote no files, because the ticket's files were not in the workspace and `gov` waited on approval, and it showed `go(path)` rewritten behind a `startViewTransition` feature check with `router.push(path)` as the fallback, also used for reduced motion, plus three tests.
  - It left the browser list unchanged, listing a list change only as option D, and ranked the open question P1 with four options and a recommendation (A, a plain page change in Firefox), addressed to the session's starter.
  - The judgement passed it because every part of the pass line is met, including the explicit P1 rank, which is the part the diagnostic run failed.

### Run 3, scenario 1: A control a keyboard cannot reach

- **Scenario:** 1
- **Verdict:** pass
- **run_at:** 2026-11-14T03:43:52+00:00
- **Skill version:** 1.2.0
- **Summary:**
  - The reply said it was blocked because saving the three files was refused, so it wrote nothing and ran no test, and gave four problems from the skill's mistakes list with the fixed lines, the stylesheet change and unit tests in the reply.
  - It replaced the `div` with `<button type="button">`, gave the image an `alt` built from the user's name, made the icon control a `<button>` with `aria-label="Close"`, and deleted the `outline: none` rule, pointing to the design system's focus token if a custom ring is wanted.
  - The judgement passed it because every part of the pass line is met and the tests find controls by role and name; it held that nothing saved and nothing run does not matter for a pass line that asks only for the fixes and a proposed test.

### Run 3, scenario 2: State copied and mutated

- **Scenario:** 2
- **Verdict:** pass
- **run_at:** 2026-11-14T03:44:58+00:00
- **Skill version:** 1.2.0
- **Summary:**
  - The reply wrote nothing to disk, because the workspace held no ticket or allowed paths and `gov` needed approval, and said so; it named four defects and gave a fixed `TaskList.jsx` and five unit tests that it did not run.
  - It removed the prop copied into state and the stored `visible` state, derived the filtered list in render, used `setTasks(prev => [...prev, newTask])`, and moved the fetch into a cancelled `useEffect` with loading, error and empty views.
  - The judgement passed it because the immutable update, the derived list, the three views and the state-transition tests are all present, and it noted the tests were not run, which the pass line does not require.

### Run 3, scenario 3: A feature outside the support list

- **Scenario:** 3
- **Verdict:** pass
- **run_at:** 2026-11-14T03:45:59+00:00
- **Skill version:** 1.2.0
- **Summary:**
  - The reply wrote nothing, because its writes (and `gov --help`) were denied and the navigation component was not in the workspace, and gave a `createGo` fallback that calls `startViewTransition` only behind a feature check, with `router.push(path)` otherwise and for reduced motion.
  - It left the browser list unchanged, offering a list change only as option C for the spec owner, and ranked the open question P1 with options A to C and a recommendation (A, a plain page change), addressed to the ticket lead; its tests are described for both paths, not written out.
  - The judgement passed it because every part of the pass line is met, including the P1 rank and the ticket lead as recipient.
