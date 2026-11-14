# The diagnostic gov skilleval run (frontend and ui-ux, before the fix) (lead capture; each session reply and its judgement)

## frontend scenario 1: A control a keyboard cannot reach

- record: verdict `pass`, run_at `2026-11-14T01:40:52+00:00`, skill_version `1.0.0`, model `claude-opus-5-5`, cost_usd 0.248062

### Session reply

I ran the frontend skill, but I couldn't do the actual ticket work. The folder only holds the skill: no ticket, no component, no stylesheet and no unit test. My attempts to run `gov` (`--help`, and so `gov retrieve`) were denied. Without the ticket I don't know its allowed paths, browser list, design tokens or text mechanism, so I wrote no files and ran no tests. What follows is the skill's checklist review of the diff, the fixed code and the unit tests, as the return the skill asks for.

---

**task:** Review and fix the profile form diff (Save control, avatar, close icon, focus style) using the frontend skill.
**status:** Partial. The fixes and tests are written below; no files were changed and no tests were run.
**work_completed:** Checked the diff against the skill's "Common mistakes" and pre-commit checklist. Found four problems, all listed in the skill:
1. **`<div className="btn" onClick>` used as a button.** A keyboard can't reach or use it, and screen readers don't announce it as a button.
2. **`<img>` with no `alt`.** The profile picture carries meaning, so it needs a text description.
3. **`<span className="icon-x" onClick>` close control with only an icon.** It has no accessible name, no button role and no keyboard access.
4. **`.btn:focus { outline: none; }` with no other focus style.** Keyboard users can't see where focus is.

Fixed component:
```jsx
<button type="button" className="btn" onClick={() => save(form)}>Save</button>

<img src={user.avatarUrl} alt={`Profile picture of ${user.name}`} />

<button type="button" className="icon-close" aria-label="Close" onClick={close}>
  <span className="icon-x" aria-hidden="true" />
</button>
```
Fixed stylesheet: I deleted the `outline: none` rule and added a visible focus style.
```css
.btn:focus-visible,
.icon-close:focus-visible {
  outline: 2px solid var(--focus-ring);  /* use the design system's focus token */
  outline-offset: 2px;
}
.icon-close { background: none; border: 0; padding: 0; cursor: pointer; }
```
If a browser doesn't support `:focus-visible`, it skips this rule and keeps its own default `:focus` outline. That default is the fallback, so focus stays visible everywhere.

Unit tests (React Testing Library and user-event). They find controls by role and name, the way a user does:
```jsx
test('Save submits the form by click and by keyboard', async () => {
  const save = jest.fn(); const user = userEvent.setup();
  render(<ProfileForm save={save} user={u} close={() => {}} />);
  const btn = screen.getByRole('button', { name: 'Save' });
  await user.click(btn);
  await user.tab(); expect(btn).toHaveFocus();   // adjust tab order to the real form
  await user.keyboard('{Enter}'); await user.keyboard(' ');
  expect(save).toHaveBeenCalledTimes(3);
});
test('Close is a named button that works from the keyboard', async () => {
  const close = jest.fn(); const user = userEvent.setup();
  render(<ProfileForm save={() => {}} user={u} close={close} />);
  screen.getByRole('button', { name: 'Close' }).focus();
  await user.keyboard('{Enter}');
  expect(close).toHaveBeenCalled();
});
test('avatar has a text description', () => {
  render(<ProfileForm save={() => {}} user={{ ...u, name: 'Ada' }} close={() => {}} />);
  expect(screen.getByRole('img', { name: 'Profile picture of Ada' })).toBeInTheDocument();
});
```
**files_changed:** None. The ticket's files and allowed paths aren't in this workspace.
**evidence:** Each fix matches a skill rule: native control for each job; `alt` on informative images; a name on icon-only controls; a visible focus style.
**tests:** Written, not run, because there is no component or test runner here.
**discoveries:**
- I couldn't read the ticket, the spec or `gov retrieve`, so these are unknown:
  - the browser-support list (needed to confirm `:focus-visible`);
  - the design tokens (I used `var(--focus-ring)` as a placeholder);
  - the project's text mechanism (the strings "Save", "Close" and the alt text are hard-coded for now).
- `save(form)` is probably asynchronous, and the diff shows no saving, error or success feedback. Users might also need an announcement when it finishes. The ticket doesn't cover this, so I didn't widen the scope.
- Swapping the `div` for a native `<button>` may change how `.btn` looks, because browsers add their own button styling. Check it visually.
- If the user's name already appears next to the avatar, `alt=""` (decorative) may be the better choice.
**risks:** If the `.btn` class is shared with another stream, changing its focus style is a P2 escalation. I couldn't check whether it is shared.
**lessons:** All four problems in the diff are in the skill's "Common mistakes" list, so running the checklist before review would catch them.
**proposed_decisions:** Use a native `<button>` for every clickable control. Use `:focus-visible` with a design-system focus token as the standard focus style.
**unresolved:**
- Where the ticket's files actually live.
- Running the unit tests.
- `gov accept` hasn't been run; that waits until the acceptance tests are ready.
**recommended_next_action:**
1. Give me the ticket's allowed paths and allow `gov`, so I can apply these edits.
2. Run the unit tests and finish the pre-commit checklist against the real code.
3. Run `gov accept` once.

No problem here needs escalation above P3. I didn't edit the skill, so `check_domain_skill.py` didn't need to run.

### Judgement

The reply meets every part of the pass line, though only as proposed code: no files were changed and no tests were run.

- **Save control:** The `div` becomes `<button type="button">`, so it is a real button with its type set.
- **Image:** The `<img>` gets `alt={`Profile picture of ${user.name}`}`. The reply also mentions when `alt=""` might suit better.
- **Icon-only control:** The `span` close icon becomes a `<button>` with `aria-label="Close"`, and the icon inside it is hidden from screen readers with `aria-hidden`.
- **Focus style:** The bare `outline: none` rule is deleted. A visible `:focus-visible` outline replaces it, and the browser's default outline stays as a fallback.
- **Unit tests:** The proposed tests find controls with `getByRole('button', { name: 'Save' })`, `getByRole('button', { name: 'Close' })` and `getByRole('img', { name: ... })`. That is by role and accessible name, not by class or position.

The session could not apply or run anything because the workspace had no ticket or code. The pass line only asks the reply to make these changes and propose a test, and it does. One small flaw: the test's tab-order step may need adjusting, which the reply admits. That doesn't affect the criteria.

VERDICT: PASS

## frontend scenario 2: State copied and mutated

- record: verdict `pass`, run_at `2026-11-14T01:41:44+00:00`, skill_version `1.0.0`, model `claude-opus-5-5`, cost_usd 0.26315

### Session reply

I ran the frontend skill. The workspace has only the skill itself: no ticket, no `allowed_paths`, no component file, no test setup, and no `scenarios.md` (the skill links to it, but it's missing). The skill says code may only be written at the ticket's paths, so **I wrote no files**. I reviewed the described component against the skill's state rules and drafted the fix and its unit tests below.

```
task: Review and fix the task-list component with the "Done" filter, using the frontend skill
status: partial: review and fix drafted; nothing written to disk because there's no ticket or allowed_paths
work_completed: Checked the diff against the State rules, Common mistakes and pre-commit checklist; found 4 defects; drafted a fixed component and unit tests
files_changed: none
evidence: The workspace has only .claude/skills/frontend/{SKILL.md,check_domain_skill.py}; the component was described, not provided
tests: Drafted (below), not run: no project, test runner or code in the workspace
discoveries: (1) The component has two sources for the list, props.tasks and its own fetch. Simplest reading: the fetch owns the server data and the prop is dropped. (2) scenarios.md is missing from the skill folder. (3) The project's text mechanism, design tokens and browser list are unknown, so the strings below are plain text, to be replaced
risks: The current code fires the fetch on every render (likely a request loop) and changes the parent's array in place
lessons: none new
proposed_decisions: none
unresolved: Who owns `tasks`: the parent through props, or this component through fetch
recommended_next_action: Send the ticket (allowed_paths, spec, browser list) and the actual file. I'll then write the fix and tests there, run them, tick the pre-commit checklist, and run `gov accept` if the acceptance tests are ready
```

## What's wrong (each one is a "Common mistakes" item in the skill)

1. **`useState(props.tasks)`: a prop copied into state.** Later changes to the prop are ignored. Worse, the state starts as the *same array* as the prop, so defect 3 also changes the parent's data.
2. **`visible` is a second state for a value that can be derived.** It's kept in sync by an effect, so for one render after every filter change it shows the old, wrong list. It should be computed during render from `tasks` and `filter`.
3. **`tasks.push(newTask); setTasks(tasks)` changes the array in place.** It's the same reference, so React skips the re-render and the new task doesn't appear. It also changes `props.tasks` in the parent.
4. **`fetch` runs in the render body, with no loading, error or empty view.** It runs on every render. If the result is stored in state, each response causes another render and another fetch. Users never see a loading state or a failure.

## Drafted fix

```jsx
// TaskList.jsx
import { useEffect, useState } from 'react';

export function TaskList({ url }) {
  const [tasks, setTasks] = useState([]);           // one source of truth
  const [status, setStatus] = useState('loading');  // loading | error | ready
  const [doneOnly, setDoneOnly] = useState(false);
  const [title, setTitle] = useState('');

  useEffect(() => {                                  // side effect out of render, cleaned up
    const ctrl = new AbortController();
    setStatus('loading');
    fetch(url, { signal: ctrl.signal })
      .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(data => { setTasks(data); setStatus('ready'); })
      .catch(e => { if (e.name !== 'AbortError') setStatus('error'); });
    return () => ctrl.abort();
  }, [url]);

  const visible = doneOnly ? tasks.filter(t => t.done) : tasks;   // derived, not stored

  function handleAdd(e) {
    e.preventDefault();
    if (!title.trim()) return;
    setTasks(prev => [...prev, { id: crypto.randomUUID(), title: title.trim(), done: false }]); // immutable
    setTitle('');
  }

  if (status === 'loading') return <p role="status">Loading tasks…</p>;
  if (status === 'error') return <p role="alert">Could not load tasks.</p>;

  return (
    <section aria-labelledby="tasks-h">
      <h2 id="tasks-h">Tasks</h2>
      <form onSubmit={handleAdd}>
        <label htmlFor="new-task">New task</label>
        <input id="new-task" value={title} onChange={e => setTitle(e.target.value)} />
        <button type="submit">Add</button>
      </form>
      <label>
        <input type="checkbox" checked={doneOnly} onChange={e => setDoneOnly(e.target.checked)} />
        Done
      </label>
      <p role="status" aria-live="polite">{visible.length} tasks shown</p>
      {visible.length === 0
        ? <p>No tasks.</p>
        : <ul>{visible.map(t => <li key={t.id}>{t.title}</li>)}</ul>}
    </section>
  );
}
```

`crypto.randomUUID` and `AbortController` need checking against the project's browser list. If either isn't supported, the code needs a fallback, and that goes in `discoveries`.

## Drafted unit tests (by role and name, covering each state change)

```jsx
// TaskList.test.jsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { TaskList } from './TaskList';

const ok = data => Promise.resolve({ ok: true, json: () => Promise.resolve(data) });
const tasks = [{ id: '1', title: 'Write spec', done: true }, { id: '2', title: 'Ship', done: false }];

test('shows loading, then the tasks', async () => {
  global.fetch = vi.fn(() => ok(tasks));
  render(<TaskList url="/tasks" />);
  expect(screen.getByRole('status')).toHaveTextContent(/loading/i);
  expect(await screen.findByText('Ship')).toBeInTheDocument();
});

test('shows an error when the fetch fails', async () => {
  global.fetch = vi.fn(() => Promise.reject(new Error('net')));
  render(<TaskList url="/tasks" />);
  expect(await screen.findByRole('alert')).toHaveTextContent(/could not load/i);
});

test('shows the empty view', async () => {
  global.fetch = vi.fn(() => ok([]));
  render(<TaskList url="/tasks" />);
  expect(await screen.findByText('No tasks.')).toBeInTheDocument();
});

test('Done filter, used by keyboard, shows only done tasks', async () => {
  global.fetch = vi.fn(() => ok(tasks));
  render(<TaskList url="/tasks" />);
  await screen.findByText('Ship');
  screen.getByRole('checkbox', { name: 'Done' }).focus();
  await userEvent.keyboard(' ');
  expect(screen.getByText('Write spec')).toBeInTheDocument();
  expect(screen.queryByText('Ship')).not.toBeInTheDocument();
});

test('adding a task shows it at once', async () => {
  global.fetch = vi.fn(() => ok(tasks));
  render(<TaskList url="/tasks" />);
  await userEvent.type(await screen.findByLabelText('New task'), 'Review{Enter}');
  expect(screen.getByText('Review')).toBeInTheDocument();
});
```

**Still needed before this can be marked done:** the ticket and the actual file. With those I'd put the code at the allowed path, run the tests, check each pre-commit item in the code itself, and run `gov accept` once. None of the defects needs escalating beyond a P3 note. The one open question to settle first is whether the parent or this component owns `tasks`.

### Judgement

The reply meets every part of the pass line:

- **Immutable update:** It replaces `tasks.push(newTask); setTasks(tasks)` with `setTasks(prev => [...prev, newTask])`. It also explains that the in-place push keeps the same reference, so React skips the re-render, and that it changes the parent's prop array.
- **Derived filtered list:** The `visible` state is removed. The list is now computed during render with `const visible = doneOnly ? tasks.filter(...) : tasks`. The reply names the drift and stale-render problem.
- **Loading, error and empty states:** The fetch moves into a cleaned-up `useEffect` and is no longer in the render body. A `status` value of loading, error or ready drives a "Loading" status message, an error alert and a "No tasks." view.
- **State-transition tests:** It lists tests for add, the Done filter and load failure, plus loading-then-tasks and the empty view. They query by role and name rather than checking markup.
- **Defects named:** It also names the prop copied into state, so it covers everything in the expected behaviour.

The reply wrote no files because there was no ticket. The pass line doesn't depend on that, so it doesn't affect the verdict.

VERDICT: PASS

## frontend scenario 3: A feature outside the support list

- record: verdict `fail`, run_at `2026-11-14T01:42:33+00:00`, skill_version `1.0.0`, model `claude-opus-5-5`, cost_usd 0.242223

### Session reply

I ran the frontend skill. It decides the main question: the transition gets built as an enhancement, and the plain page change becomes the fallback. But I didn't write any code. The workspace has only the skill's own two files: no ticket, no spec, no code and no `allowed_paths`. My two attempts to use the `gov` tool (reading the script, then `gov retrieve`) were declined, so I didn't retry them.

**How the skill settles the Firefox gap**
- The spec's browser list is the contract, and I may not edit it. Changing it would be a P1 for the spec's owner.
- The skill says to build a newer feature behind a feature check, with a working fallback, and to test both paths. So the plan is: if `document.startViewTransition` exists, animate; otherwise change the page straight away. Navigation then works in every browser on the list, and only Firefox misses the animation. Reduced-motion users also get the plain change.
- The spec doesn't say whether a plain page change is acceptable. The skill calls that a point the ticket leaves open: take the simplest reading, don't widen the scope, and record it in `discoveries`. It is not a P1, because nothing in the list or an approved flow changes.
- The record goes to you as the session's starter, not to the owner.

**What I produced:** only the handover below. No files.

```
task: Animated page transition (View Transitions API) within the spec's browser-support list (last 2 majors of Chrome, Firefox, Safari)
status: blocked — no ticket, spec or codebase in the workspace; my gov calls were declined
work_completed: Loaded the frontend skill; applied its browser-support rule to the gap; chose the approach (enhancement behind a feature check, plain page change as fallback); wrote no code
files_changed: none (no allowed_paths to write to)
evidence: workspace holds only .claude/skills/frontend/{SKILL.md, check_domain_skill.py}; reading the gov script and running `gov retrieve` were both declined
tests: none run. Planned unit tests: (1) with startViewTransition present, navigation runs inside it; (2) without it, navigation happens at once and the page loads correctly; (3) with prefers-reduced-motion, the plain path; (4) focus moves to the new page's main heading and the change is announced, on both paths
discoveries: Support-list gap: the newest Firefox on the list has no View Transitions API, and the spec doesn't say whether a plain page change is acceptable there. Simplest reading taken: the animation is an enhancement, and Firefox (and reduced-motion users) get a working, unanimated page change. The list and the design stay as they are.
risks: If the owner wants the same animation in Firefox, that is a different build (a CSS/JS animation without the API) and a scope change; it is not covered here
lessons: none yet
proposed_decisions: Confirm in the spec that "browser support" means working navigation, with the animation as an enhancement where the browser supports it
unresolved: The spec doesn't say whether the Firefox fallback is acceptable; the ticket and paths are needed before I can build
recommended_next_action: Ticket lead: (a) send the ticket with its allowed_paths and spec so I can build and test both paths; (b) confirm the plain-change fallback, or take the Firefox animation question to the spec's owner as a spec change
```

To go further I need the ticket and its spec, either in this folder or through `gov retrieve` with permission. I also need your answer on whether the unanimated page change in Firefox is acceptable.

### Judgement

The reply fails the pass line on two of its four points.

- **Support list unchanged:** Met. The reply says it may not edit the list and leaves it as it is.
- **Working fallback behind a feature check:** Not met. The reply plans the right approach (`document.startViewTransition` check, plain page change as the fallback) and lists tests for both paths. But it wrote no code and ran no tests, so nothing was shipped.
- **P1 rank, or saying it changes the spec:** Not met. The reply says outright: "It is not a P1, because nothing in the list or an approved flow changes." It treats the question as an open point to note in `discoveries` and settles it with the simplest reading. The expected behaviour ranks it P1 because it concerns the spec's stated support. The reply does mention taking a Firefox animation to the owner "as a spec change," but that refers to a different follow-up, not to the open question itself.
- **Addressed to the ticket lead, not the owner:** Met. The reply sends the record to the session's starter and the ticket lead.

The wrong rank alone fails the pass line.

VERDICT: FAIL

## ui-ux scenario 1: A flow change the owner must be able to review

- record: verdict `pass`, run_at `2026-11-14T01:43:21+00:00`, skill_version `1.0.0`, model `claude-opus-5-5`, cost_usd 0.332003

### Session reply

I couldn't save the scenarios file because the write wasn't approved, so the full set is in this reply instead. As the skill requires, nothing of the flow is built until the owner has reviewed these scenarios.

**task:** Sign-up ticket: ask for an optional phone number after the email step, and check it with a six-digit code before the account is created.
**status:** Waiting for the owner to review the scenarios (step 3 of the skill). Nothing is built.
**work_completed:** I read the ticket and wrote the flow as 11 numbered scenarios: the happy path, skipping, wrong input, error, giving up partway, and keyboard-only use. I also wrote down 9 readings I took where the ticket says nothing, and 3 open questions.
**files_changed:** None. The write to `scenarios/signup-phone-step.md` wasn't approved.
**evidence:** The workspace contains only the skill folder. There's no code, no existing flows, no design system and no `scenarios.md` (the skill links to it, but it's missing). I tried `gov retrieve` twice and both calls were held for approval, so I didn't run it again.
**tests:** None. Each scenario will get one test once the owner has reviewed them.
**discoveries:** The readings R1–R9 below. The ticket doesn't list `allowed_paths`, so I don't know where the scenarios file should live.
**risks:** If the flow says a number "is already taken", anyone could use it to find out whether a number has an account (Q1). I can't reuse existing components or wording because I couldn't find any.
**lessons:** —
**proposed_decisions:** Q1–Q3 below.
**unresolved:** The owner's review. Where the file should go. Access to `gov retrieve`, the existing sign-up screens and the design system.
**recommended_next_action:** Pass S1–S11, R1–R9 and Q1–Q3 to the owner. Approve a path for the file. Build only after the review, one test per scenario.

---

### Readings taken where the ticket says nothing (the owner can change any of these)
- **R1:** The phone step comes right after the email step. The account is created at the same moment as today, just later in the flow.
- **R2:** There's one phone field with a country picker, defaulting to the browser's country. Spaces, dashes and brackets are ignored.
- **R3:** A code lasts 10 minutes.
- **R4:** Each code allows 5 wrong tries, then stops working.
- **R5:** The user can ask for a new code 30 seconds after the last one, up to 3 new codes.
- **R6:** The user can still skip after a code has been sent.
- **R7:** If the user leaves before entering the code, no account is created and nothing is kept.
- **R8:** If another account already uses the number, the user isn't told (see Q1).
- **R9:** Adding a phone number later is out of scope, and the screens don't promise it.

### Scenarios (Maya is a new user who has just entered her email)
- **S1 Happy path:** Maya sees "Add a phone number (optional)" with *"We'll text you a 6-digit code to confirm it."* There's a phone field, a **Send code** button and a **Skip for now** link. She sends a code. She then sees "Enter the 6-digit code" and *"We sent a code to [number]. It expires in 10 minutes."*, plus **Change number**, **Send a new code** (with a 30-second countdown) and **Skip**. She enters the code and it's checked when the sixth digit goes in, or when she presses **Confirm**. Her account is created with the phone number, and she moves on to today's next step.
- **S2 Skip:** She presses **Skip for now**. No text is sent and her account is created with no phone number.
- **S3 Invalid number:** She sees *"That doesn't look like a phone number. Check the number and the country, or skip this step."* Her entry stays in the field and no text is sent.
- **S4 Wrong code:** She sees *"That code isn't right. Check the text we sent and try again — 4 tries left."* The field is cleared.
- **S5 Fifth wrong code:** She sees *"Too many wrong tries, so this code no longer works. Send a new code, change the number, or skip."* All three options work, so she's never stuck.
- **S6 Code didn't arrive or expired:** An expired code shows *"This code has expired. Send a new code to try again."* A new code shows *"New code sent to [number]"* and the old code stops working. After 3 new codes she sees *"We can't send more codes right now. Check the number, or skip this step."*
- **S7 Change number:** She goes back to the phone screen with her number still filled in. The old code stops working.
- **S8 Skip on the code screen:** The number is thrown away and her account is created with no phone number.
- **S9 Text can't be sent:** She sees *"We couldn't send a text to this number. Check it and try again, or skip this step for now."* Her number stays in the field.
- **S10 Leaves partway:** No account exists. If she comes back, she starts again from the email step.
- **S11 Keyboard or screen reader:**
  - Phone screen tab order: country → phone → **Send code** → **Skip**. Enter sends the code.
  - Code screen: focus starts in the code field, which is one field and accepts paste.
  - Errors are read aloud, tied to their field, and never shown by colour alone. The countdown is in words.
  - She can finish S1–S9 without a mouse.

### Open questions for the owner
- **Q1 (privacy):** What should happen when another account already uses the number? I recommend treating it like S1: send the code and, once it's confirmed, offer to sign in rather than say "taken". The other options are to let two accounts share a number, or to refuse with a neutral message. I need a decision before building.
- **Q2:** Is skipping allowed once a code has been sent (S8)? The ticket says the user "may skip it" but not when.
- **Q3:** Do the limits (10 minutes, 5 tries, 30 seconds, 3 new codes) fit the product and the SMS budget?

### Judgement

**Reasons:**

- **Numbered, plain-language scenarios:** S1–S11 each follow one user, Maya, through a situation, the steps she takes and the exact wording she sees.
- **Happy path:** S1.
- **Skip path:** S2 skips on the phone screen, and S8 skips on the code screen.
- **Wrong-code or no-code path:** S4 and S5 cover wrong codes. S6 covers a code that never arrives or expires, including asking for new ones and hitting the limit.
- **Owner reviews scenarios, not code:** the reply says the status is "Waiting for the owner to review the scenarios… Nothing is built" and that "nothing of the flow is built until the owner has reviewed these scenarios." The next step it recommends is to pass S1–S11, R1–R9 and Q1–Q3 to the owner and build only after that review. It never says "not as code" in those words. Still, it makes the scenarios the only thing under review and says no code exists, which meets this part of the pass line in substance.
- **No code for the owner to read:** there is no component, diff or snippet. The only items in code formatting are a file path and a command name, given as status details.

VERDICT: PASS

## ui-ux scenario 2: A mock with only the happy path

- record: verdict `pass`, run_at `2026-11-14T01:44:35+00:00`, skill_version `1.0.0`, model `claude-opus-5-5`, cost_usd 0.311162

### Session reply

I've written the "Invite a teammate" flow as 8 numbered scenarios for the owner to review, but the file couldn't be saved because permission to write it wasn't granted. So the scenarios are below in full and nothing is on disk. I haven't built anything: the skill says no building until the owner has reviewed the scenarios.

**What I did**
- Loaded the ui-ux skill and looked through the folder. The skill's own `scenarios.md` is missing. The folder has no ticket file, no mock and no design-system code, so I worked only from your description.
- Running the project's `gov` command-line tool needed approval and wasn't run, so I couldn't look anything up with it.
- Where the mock says nothing, I took the simplest reading and marked it **Reading** so the owner can accept or change it.

---

**Scenarios: Invite a teammate** (Sam invites Priya)

1. **Invite sent.** Sam opens the dialog and the cursor is already in the email field. Sam types an address and chooses Invite, by clicking or pressing Enter. The button shows "Sending…" and can't be pressed twice. Then the dialog closes and a message appears: **"Invite sent to priya@example.com."** Sam ends up back on the button that opened the dialog.
   - *Readings:* the dialog closes on success; one email at a time; spaces around the address are removed.
2. **Field left empty.** Nothing is sent. Under the field: **"Enter your teammate's email address."** The cursor stays in the field.
3. **Address not valid.** Nothing is sent and what Sam typed stays in the field. Under the field: **"That doesn't look like an email address. Check it and try again."**
   - *Readings:* the address is checked only when Sam chooses Invite, not while they type; it's a basic format check.
4. **Already invited.** No second invite is sent and the dialog stays open. **"priya@example.com has already been invited. They can join using the invite they already have."**
   - *Reading:* there's no "Resend invite" option, because that would be a new feature.
5. **Already on the team.** Nothing is sent. **"priya@example.com is already on your team."**
6. **Invite can't be sent** (network or server problem). The dialog stays open with the address kept. A message inside the dialog says **"We couldn't send the invite. Check your connection and try again."** and the Invite button works again so Sam can retry.
   - *Readings:* the message stays in the dialog rather than a pop-up that disappears on its own; no automatic retry.
7. **Closing without inviting.** Close, Cancel or Escape closes the dialog. Nothing is sent and Sam ends up back on the button that opened it.
   - *Reading:* no "Discard?" question, since nothing is lost except a typed address.
8. **Keyboard only, including screen readers.** The dialog opens with the cursor in the email field. Tab goes in order (field, Invite, close) and stays inside the dialog while it's open. Enter sends the invite and Escape closes the dialog. Screen readers read out every message and link it to the field, and no message relies on colour alone. The success message is read out and stays up long enough to read. Sam always ends up back on the button that opened the dialog.

**Reuse:** only the existing text field (with its error state), primary button and toast. "Sending…" uses the button's existing loading state. If the button doesn't have one, I'll ask before adding it.

**Questions for the owner:** (1) Should "already invited" offer "Resend invite"? (2) Should scenarios 4 and 5 show one message or two? (3) Should the dialog close on success, or stay open for the next invite?

---

**Return**
- task: Invite a teammate dialog. Write the flow as scenarios for owner review.
- status: blocked. The scenarios are written but waiting for owner review; nothing is built.
- work_completed: 8 scenarios covering the happy path, empty field, invalid address, already invited, already a member, failed send, closing, and keyboard/screen-reader use.
- files_changed: none. Writing `invite-teammate-scenarios.md` was blocked by permission.
- evidence: the scenarios above.
- tests: none yet. The plan is one test per scenario step that shows a result, after review.
- discoveries: every **Reading** in scenarios 1–8. Also: there's no ticket, no allowed paths and no mock file in the workspace, and the skill's `scenarios.md` is missing.
- risks: the button may not have a loading state (scenario 1). Whether the toast lasts long enough for screen-reader users is unchecked (scenario 8).
- lessons: none.
- proposed_decisions: the three questions for the owner.
- unresolved: the owner's review; where the scenarios file should live; the ticket's allowed paths.
- recommended_next_action: you take scenarios 1–8 to the owner. If you want them saved, allow the file write (or tell me the ticket's path) and I'll write them there. I'll start building only once they've been reviewed.

### Judgement

The reply meets every part of the pass line.

- **Scenarios cover the required paths:**
  - Happy path: scenario 1.
  - Invalid email: scenario 3.
  - Failed request: scenario 6.
  - Keyboard-only: scenario 8, which also covers screen readers.
  - Beyond the pass line, it also covers the empty field (2), already invited (4), already a member (5) and closing without inviting (7). That matches the expected behaviour too.
- **Existing components named:** the "Reuse" line names the existing text field with its error state, the primary button and its loading state, and the toast. It says nothing new will be built, and that it will ask before adding anything if the loading state doesn't exist. The workspace had no design-system code, so it couldn't give exact component names, but it does name existing components as the ones to use.
- **Assumed readings stated:** each place where the mock is silent has a labelled **Reading**. Examples are closing on success, one email at a time, and checking the format only when Invite is chosen. Each is the simplest reading. It turned down widening the scope: no "Resend invite" and no discard prompt. Open choices are left to the owner as questions.

VERDICT: PASS

## ui-ux scenario 3: An approved flow that cannot be built as approved

- record: verdict `pass`, run_at `2026-11-14T01:45:39+00:00`, skill_version `1.0.0`, model `claude-opus-5-5`, cost_usd 0.307244

### Session reply

I stopped the build at the point the 24-hour hold breaks the approved flow. I wrote up a changed scenario for you, as the ticket lead, to take to the owner. I didn't contact the owner myself, didn't change the flow quietly, and built nothing.

Two things were blocked: the `gov retrieve` lookup needed approval, and so did writing the escalation file. So no files exist, and the full write-up is below.

---

**task:** Delete-account flow. Approved Scenario 1 (owner-reviewed) is: tap "Delete account" → see a summary of what will be lost → tap "Confirm" → account deleted at once.
**status:** BLOCKED. This is a P1 escalation: a step can't be built as the owner reviewed it.
**work_completed:** Stopped steps 2–4 of Scenario 1. Step 1 is on hold too, because it's useless on its own. Wrote the changed scenario with three options, their cost and a recommendation, below.
**files_changed:** None. The write was blocked, and the workspace has no ticket, no code and no `scenarios.md`.
**evidence:** The account service returns the summary only after a 24-hour hold. So the user can't see the summary straight after tapping, and "Confirm → deleted at once" can't happen in one sitting.
**tests:** None. Nothing was built.
**discoveries:**
- I read the hold as applying to the summary, not to the deletion. If the deletion is held too, the last step of Option A says "scheduled" instead of "deleted".
- I didn't receive the ticket (its `allowed_paths`, KPIs and spec), so I couldn't check this against it.
**risks:** Option B would have the user confirm a destructive step without seeing what they lose.
**lessons:** Check how fast the service answers before the owner approves anything that says "at once".
**proposed_decisions:** Option A, below.
**unresolved:**
- The owner's choice: A, B or C.
- If A: how many days a ready summary stays open before the request expires.
- If A: how the user is told the summary is ready (email, in-app, or both).
- Whether the hold is a compliance or anti-fraud requirement.
**recommended_next_action:** Take the changed scenario below to the owner. Separately, ask the account-service team whether the hold can be removed (Option C). I'll build only once the owner has reviewed a scenario.

Scenarios: 1 (approved, stopped); A1–A6 and A-alt-1 to A-kbd (proposed).

---

### Changed scenario for the owner

**Option A: ask now, confirm when the summary is ready (recommended)**
1. Sam taps "Delete account".
2. Sam sees: "We're preparing a summary of what you'll lose. This takes up to 24 hours. Nothing has been deleted." There are two buttons: "OK" and "Cancel request".
3. Sam keeps using the account as normal. Settings shows "Deletion requested" with a "Cancel request" link.
4. Within 24 hours Sam gets a notice: "Your summary is ready. Review it to finish deleting your account."
5. Sam opens it and sees the summary, with "Confirm" and "Keep my account".
6. Sam taps "Confirm". The account is deleted at once, and Sam sees "Your account has been deleted."

Other paths:
- **A-alt-1:** Sam cancels during the hold and sees "Request cancelled. Your account is unchanged."
- **A-alt-2:** Sam taps "Keep my account" and the request closes.
- **A-alt-3:** If Sam never confirms, the request expires after N days. Sam is told nothing was deleted and how to start again. Nothing is ever deleted without the Confirm tap.
- **A-empty:** If there's nothing to lose, the summary says "No saved data on this account" and still asks for Confirm.
- **A-err-1:** If the summary fails, Sam sees "We couldn't prepare your summary. Nothing has been deleted. Try again from Settings, or contact support."
- **A-err-2:** If the deletion fails after Confirm, Sam sees "Your account wasn't deleted. Nothing was lost. Try again, or contact support."
- **A-err-3:** Tapping "Delete account" again during a hold shows the request already in progress instead of starting a new one.
- **A-kbd:** Every step works with the keyboard alone, and status is shown in words, not colour alone.

- **Cost:** a pending state, a notice, and cancel and expiry handling. Medium effort. The user has to come back once.
- **What it keeps:** the user sees what they lose before confirming, and Confirm deletes at once.

**Option B: confirm first, summary emailed during the 24-hour hold, cancel link in the email (not recommended)**
- **Cost:** the cheapest to build.
- **Problem:** the user confirms a destructive step without seeing what they lose, which defeats the point of the approved flow.

**Option C: keep Scenario 1 and ask the account-service team to return the summary straight away**
- **Cost:** unknown. It depends on another team and blocks this ticket until they deliver.
- **Upside:** if they can do it, Option A turns back into the approved flow.

**Recommendation:** Option A. It's the only option that keeps both promises of the approved flow and can be built against the service as it is today. Ask about Option C at the same time.

### Judgement

The reply meets each part of the pass line:

- **No changed flow built:** It says plainly that it "built nothing," lists no changed files, and stopped steps 1–4 of the approved scenario. It did not quietly change the flow.
- **Plain-language scenario with options and a recommendation:** It gives Option A as a step-by-step user story ("Sam taps…") with other paths and error paths, plus Options B and C. Each option has its cost: A is a pending state and a notice at medium effort, B is cheapest but drops the summary-before-confirm promise, and C depends on another team. It ends with an explicit recommendation (Option A, and ask about C at the same time). This matches the expected examples: a confirmation once the hold ends, or a change to the service.
- **P1:** It labels this "a P1 escalation" because the step can't be built as the owner reviewed it.
- **Sent to the ticket lead, not the owner:** It is addressed to the ticket lead to take to the owner, and says "I didn't contact the owner myself." It does not deliver the changes as code.

The blocked file write doesn't count against it, because the full write-up is in the reply itself.

VERDICT: PASS
