# frontend: the three scenarios

Written before the skill's text (DEC-959 item 5). Each is run on a fresh session with only this skill loaded and the
inputs named; it passes when its pass line holds.

## 1. A control a keyboard cannot reach

- **Situation:** a ticket adds a Save control to a profile form. The engineer's diff adds these lines to a React
  component: `<div className="btn" onClick={() => save(form)}>Save</div>`, then
  `<img src={user.avatarUrl} />` for the profile picture, then an icon-only close control
  `<span className="icon-x" onClick={close} />`, and in the stylesheet `.btn:focus { outline: none; }`. The ticket's
  paths hold the component, its stylesheet and its unit test.
- **Expected:** the session treats this as an accessibility fault before it commits: the Save control becomes a real
  `button` element (type set), the image gets an `alt` text, the icon-only control gets a real button and an
  accessible name, and a visible focus style stays. It writes or proposes a unit test that finds the controls by
  role and accessible name, not by class or text position.
- **Pass line:** the reply replaces the `div` Save control with a button element (or keeps the `div` only with a role,
  tab stop and key handling), gives the image an `alt`, names the icon-only control, removes the `outline: none`
  without a replacement focus style, and proposes a unit test that queries by role and name.

## 2. State copied and mutated

- **Situation:** a ticket adds a task list with a "Done" filter. The diff holds this component: it reads
  `const [tasks, setTasks] = useState(props.tasks)` (a copy of a prop), a second `const [visible, setVisible] =
  useState(props.tasks)` that is updated in an effect whenever the filter changes, an add handler that runs
  `tasks.push(newTask); setTasks(tasks)`, and a `fetch` for the list called directly in the render body with no
  loading or error display.
- **Expected:** the session names the copied prop state, the duplicate `visible` state that can drift from `tasks`,
  the in-place mutation that React will not see, and the fetch in render with no loading, error or empty state. It
  keeps one source of truth, derives the visible list from it, updates immutably, moves the fetch out of the render
  body, and shows loading, error and empty states. Its unit-test focus is the state transitions, not the markup.
- **Pass line:** the reply fixes the `push` to an immutable update, derives the filtered list instead of storing it a
  second time, covers loading, error and empty states, and lists state-transition tests (add, filter, load failure).

## 3. A feature outside the support list

- **Situation:** the spec's browser-support list is the last two major versions of Chrome, Firefox and Safari. The
  design asks for an animated page transition that the engineer would build with the View Transitions API. The
  newest Firefox in the list has no support for it, and no spec line says a plain page change is acceptable there.
  The session was started by a ticket lead.
- **Expected:** the session does not change the support list and does not ship a page that breaks on Firefox. It
  builds the transition as an enhancement behind a feature check, with a plain page change as the fallback, and
  tests both paths. Since the design's intent in Firefox is a question about the spec, it raises a package: the
  options with their cost, a recommendation, and its rank under the escalation rubric (P1, because it concerns the
  spec's stated support), to the ticket lead who started it, not to the owner.
- **Pass line:** the reply keeps the support list unchanged, ships a working fallback behind a feature check, ranks the
  open question P1 (or states it changes the spec) and addresses it to the ticket lead, not to the owner.
