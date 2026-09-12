CREATE TABLE messages (id INTEGER PRIMARY KEY, role TEXT, content TEXT, ts TEXT);
INSERT INTO messages VALUES (1, 'user', 'Should we cap retries?', '2025-03-09');
INSERT INTO messages VALUES (2, 'assistant', 'Decision: we will cap gateway retries at 5 because the new gateway tolerates it. Policy: never retry on 4xx.', '2025-03-09');
INSERT INTO messages VALUES (3, 'assistant', 'Lesson learned: the stale vector index caused the agent to cite the 2024 retry rule; root cause was indexing before the path migration.', '2025-04-02');
INSERT INTO messages VALUES (4, 'user', 'here is the key for the gateway: sk_live_CHAT_LEAKED_KEY_zz99yy88xx77ww66vv55uu44', '2025-04-03');
INSERT INTO messages VALUES (5, 'assistant', 'Decision: quotes are cached for 10 minutes (agreed to keep gateway load low).', '2025-04-10');
