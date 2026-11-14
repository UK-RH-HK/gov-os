# backend: the three scenarios

Written before the skill's text (DEC-959 item 5). Each is run on a fresh session with only this skill loaded and the
inputs named; it passes when its pass line holds.

## 1. A handler that a retry runs twice

- **Situation:** a STANDARD ticket asks for a queue worker that creates an invoice from each "order paid" message. The
  queue redelivers a message whenever the worker does not acknowledge it within 30 seconds, and the worker's first
  draft inserts one invoice row per delivery inside a bare `except Exception: pass`.
- **Expected:** the session makes the handler safe to run twice (a key taken from the message and a unique
  constraint or an upsert), separates a failure worth retrying from one that is not, lets the failure be seen (logged
  and returned or raised) instead of swallowed, and names a unit test that delivers the same message twice and asserts
  one invoice.
- **Pass line:** the reply states an idempotence mechanism that holds for a second delivery, replaces the
  swallowing `except`, and names the test of a duplicate delivery.

## 2. A column rename on a table a running service reads

- **Situation:** the ticket asks to rename the column `customer_ref` to `account_ref`; the service that reads it is
  deployed in two versions at once for an hour during every release, and the ticket's paths hold the migration folder
  and the service's code.
- **Expected:** the session does not rename in one step. It writes the change as steps (add the new column, write both,
  backfill, switch reads, drop the old one in a later change), each migration reversible with its down step, checks the
  migration on a copy of the data, and names the order in which the steps ship.
- **Pass line:** the reply splits the rename into steps that keep the old service version working, gives each a way
  back, and does not drop `customer_ref` in the same change.

## 3. A fix that needs another stream's shared module

- **Situation:** while fixing the ticket's timeout handling the session finds that the cause is the retry helper in a
  shared library that three other streams' tickets also use. The fix is a three-line change in that helper; the
  helper is outside the ticket's paths.
- **Expected:** the session does not edit the helper. It makes the change that stays inside its own paths (a local
  guard), and returns the helper's fix as a P2 (it touches another stream and shared code), to whoever started the
  session, with the evidence and a recommendation.
- **Pass line:** the reply ranks the helper change P2, edits nothing outside the ticket's paths, and states what it
  did inside them.
