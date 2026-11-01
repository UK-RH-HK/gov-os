# W2-91 measure facts (lead's summary of the records; scores only)

- **control:** record `/home/usain/gov-os-runs/W2-91/records/measure-memory-retrieval-visible-20261101T173426352951Z.json`; root `/home/usain/gov-os-runs/W2-91/base`; commit `f46b96537d74`; part `visible`; retriever `/home/usain/.local/share/gov-os/pin-5c401220/bin/gov` (gov 0.1.0 (commit unknown)); budget {'batch_size': 10, 'bundle_budget': 6000, 'stack_budget': 24000}; hit@5 7 of 20 (35.0 %, floor 85); full evidence 11 of 20 (55.0 %, target 99); in the bundle 13 of 20.
- **head:** record `/home/usain/gov-os-runs/W2-91/records/measure-memory-retrieval-visible-20261101T193515830840Z.json`; root `/home/usain/gov-os-runs/W2-91/head`; commit `b652fc96d2b5`; part `visible`; retriever `/home/usain/.local/share/gov-os/pin-5c401220/bin/gov` (gov 0.1.0 (commit unknown)); budget {'batch_size': 10, 'bundle_budget': 6000, 'stack_budget': 24000}; hit@5 7 of 20 (35.0 %, floor 85); full evidence 11 of 20 (55.0 %, target 99); in the bundle 13 of 20.

Per question: hit@5, first gold rank, in the bundle, full evidence (pieces found/needed), calls, stacked digest.

| Q | control | head |
|---|---|---|
| Q01 | yes, 1, yes, yes (1/1), 5, 4ca38be7a0c8468f | yes, 1, yes, yes (1/1), 5, 7051bcbff0ff19b6; compare: differs in stacked_digest |
| Q02 | yes, 1, yes, yes (1/1), 2, e71f57c4fd6cbf14 | yes, 1, yes, yes (1/1), 2, 1ecd0aa17d3a8ddb; compare: differs in stacked_digest |
| Q03 | no, 7, yes, yes (1/1), 2, 68c06fc9b0b031fa | no, 6, yes, yes (1/1), 2, b90d7731379d7f54; compare: differs in first_gold_rank, stacked_digest |
| Q04 | yes, 3, yes, yes (1/1), 2, deedab3b3835b5d6 | yes, 3, yes, yes (1/1), 2, 0e72ebbe70756e8d; compare: differs in stacked_digest |
| Q05 | yes, 4, yes, yes (1/1), 2, c90f20e1b5580ed8 | yes, 4, yes, yes (1/1), 2, 89a018337bad32a0; compare: differs in stacked_digest |
| Q06 | no, 8, yes, yes (2/2), 3, 765762823617e504 | no, 8, yes, yes (2/2), 3, b9f40db5cf05a5f8; compare: differs in stacked_digest |
| Q07 | no, 6, yes, yes (1/1), 5, 83d13ad05eb89d1e | no, 6, yes, yes (1/1), 5, d78981a216ad5092; compare: differs in stacked_digest |
| Q08 | no, 9, yes, yes (1/1), 2, 800de3a7f479a1b6 | no, 8, yes, yes (1/1), 2, 1c036db60d2fd1e6; compare: differs in first_gold_rank, stacked_digest |
| Q09 | no, 59, no, yes (1/1), 4, 190038d3c849190b | no, 59, no, yes (1/1), 4, 49cfccd70de2437e; compare: differs in stacked_digest |
| Q10 | no, 25, no, no (1/2), 2, a8962443057ef4a1 | no, 25, no, no (1/2), 2, 3098530010fcc7bf; compare: differs in stacked_digest |
| Q11 | yes, 4, yes, no (1/2), 2, c8ef3553bbda31c7 | yes, 4, yes, no (1/2), 2, c8ef3553bbda31c7; compare: same |
| Q12 | yes, 2, yes, yes (1/1), 2, 0a9672dea4602b5b | yes, 2, yes, yes (1/1), 2, 04a1ca5e91e28b58; compare: differs in stacked_digest |
| Q13 | no, 6, yes, no (1/2), 2, fadc483f653e1b82 | no, 6, yes, no (1/2), 2, 07660af5fc229776; compare: differs in stacked_digest |
| Q14 | no, 16, yes, no (4/9), 5, e4b6430169871a8b | no, 15, yes, no (4/9), 5, 4ccc531a4ba82da6; compare: differs in first_gold_rank, stacked_digest |
| Q15 | yes, 3, yes, yes (1/1), 2, 4cab476e49f285e6 | yes, 4, yes, yes (1/1), 2, 9e98dc8b6c2cb80c; compare: differs in first_gold_rank, stacked_digest |
| Q16 | no, none, no, no (0/1), 2, d0fc6ff1da9097a0 | no, none, no, no (0/1), 2, 6208aeaa2473ed79; compare: differs in stacked_digest |
| Q17 | no, 21, no, no (1/2), 2, 507549f4e9f29497 | no, 21, no, no (1/2), 2, 48e79f4c0dad0d8c; compare: differs in stacked_digest |
| Q18 | no, none, no, no (0/2), 2, cd3989c751a72242 | no, none, no, no (0/2), 2, cd3989c751a72242; compare: same |
| Q19 | no, none, no, no (0/1), 2, 78a9908482dfe8e8 | no, none, no, no (0/1), 2, fe416f68fcfc2c89; compare: differs in stacked_digest |
| Q20 | no, 21, no, no (1/2), 2, 726b8a89d997f8f9 | no, 21, no, no (1/2), 2, 726b8a89d997f8f9; compare: same |
