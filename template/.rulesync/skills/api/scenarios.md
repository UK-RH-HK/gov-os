# api: the three scenarios

Written before the skill's text (DEC-959 item 5). Each is run on a fresh session with only this skill loaded and the
inputs named; it passes when its pass line holds.

## 1. A new endpoint with no contract

- **Situation:** a STANDARD ticket asks for `POST /v1/exports`, which starts an export job and returns its id. The
  repository has an OpenAPI file for the other endpoints, and the ticket's paths hold that file, the handler and its
  tests. The session has not yet written anything.
- **Expected:** the session writes the endpoint's contract in the OpenAPI file first (request, responses with their
  error codes, status codes), derives its unit tests from the contract, and writes the handler last, checking the handler
  against the contract.
- **Pass line:** the reply puts the contract change before the handler in its order of work and says the unit tests
  follow the contract.

## 2. A rename in a published response

- **Situation:** the ticket asks that `GET /v1/orders/{id}` return `total_cents` where it returns `total` today.
  Mobile apps that cannot be forced to update read `total`, and the ticket says nothing about them.
- **Expected:** the session keeps `total` and adds `total_cents` (an additive change), marks `total` as deprecated in
  the contract, adds a test that an old client's request still gets the old shape, and notes that removing `total`
  needs a new version.
- **Pass line:** the reply does not remove or rename `total` in v1, and names a backward-compatibility test for the old
  shape.

## 3. A contract that is silent on one error

- **Situation:** the contract for the ticket's endpoint says "409 when the name is taken" but gives no body for it.
  Every other error in the contract uses the body `{"error": {"code": "...", "message": "..."}}`. Asking the owner would
  stop the ticket for a day.
- **Expected:** the session takes the simplest reading (the same error body as the others), adds it to the contract, tests
  it, and names the point in `discoveries`; this is a P3 (reversible, inside the ticket, no change to a KPI), decided
  and logged without stopping the work.
- **Pass line:** the reply uses the shared error body, ranks the point P3, and does not stop the work or send the
  question to the owner.
