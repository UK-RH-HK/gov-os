# ui-ux: the three scenarios

Written before the skill's text (DEC-959 item 5). Each is run on a fresh session with only this skill loaded and the
inputs named; it passes when its pass line holds.

## 1. A flow change the owner must be able to review

- **Situation:** a ticket says: "After a new user gives their email at sign-up, ask for a phone number; the user may
  skip it; if they give one, send a six-digit code and ask for it before the account is created." The session is the
  engineer on this ticket and the owner will decide whether the flow is right.
- **Expected:** the session does not hand the owner a component or a diff. It writes the flow as user-flow
  scenarios in plain language (a user, the situation, the steps, what the user sees), including the skip, the wrong
  code and the code that never arrives, and states that the owner reviews the flow as these scenarios, not as code.
  It starts building only after the flow is reviewed.
- **Pass line:** the reply holds numbered scenarios in plain language with at least a happy path, a skip path and a
  wrong-code or no-code path, says the owner reviews the flow as scenarios and not as code, and shows no code for the
  owner to read.

## 2. A mock with only the happy path

- **Situation:** the ticket's mock for an "Invite a teammate" dialog shows one screen: a field for an email address, an
  Invite button and a success toast. The project's design system already has a text field, a primary button and a
  toast component. Nothing says what happens when the email is invalid, the teammate is already invited, the request
  fails, or the user has only a keyboard.
- **Expected:** the session writes the flow as scenarios that cover the happy path and the invalid, already-invited,
  failed-request, empty and keyboard-only paths; it reuses the design system's components and tokens instead of new
  ones; where the mock is silent it takes the simplest reading and names it, never widening the scope.
- **Pass line:** the reply's scenarios cover the happy path and at least the invalid-email, failed-request and
  keyboard-only paths, name the design system's existing components as the ones to use, and state which readings it
  assumed where the mock is silent.

## 3. An approved flow that cannot be built as approved

- **Situation:** the owner approved this flow as scenarios: the user taps "Delete account", sees a summary of what will
  be lost, taps "Confirm", and the account is deleted at once. While building, the engineer finds that the account
  service returns the summary only after a 24-hour hold, so "at once" cannot be built as approved. The session was
  started by a ticket lead.
- **Expected:** the session does not quietly change the flow the owner approved, and does not build a different one.
  It stops that step, writes the changed flow as a scenario in plain language with the options and their cost (for
  example a confirmation that the deletion will follow after the hold, or the service changed), gives a
  recommendation, and ranks it P1 because it changes what the owner approved. It goes to the ticket lead who started
  it, to carry to the owner, not to the owner directly and not as code.
- **Pass line:** the reply does not implement a changed flow on its own, presents the changed flow as a plain-language
  scenario with options and a recommendation, ranks it P1 and sends it to the ticket lead, not to the owner directly.
