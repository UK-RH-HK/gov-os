# Decisions log (legacy, 2024-2025)

## Decision: cache quotes for 10 minutes
We decided to cache quotes for 10 minutes to reduce gateway load.

## Decision: retries limited to 3 (superseded)
Superseded by the 2025 requirement of 5 retries; kept for history.

## Lesson: gateway timeouts
Lesson learned: gateway timeouts spike at month end; root cause was missing connection pooling.
