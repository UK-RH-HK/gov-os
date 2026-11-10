
## cost components by source ($)
1 CTO session {'read': 62.1, 'write5m': 0.0, 'write1h': 37.2, 'output': 10.4, 'input': 0.0, 'think_tok': 96614, 'out_tok': 521701}
2 CTO helpers {'read': 256.0, 'write5m': 117.0, 'write1h': 0.0, 'output': 92.5, 'input': 0.0, 'think_tok': 1547826, 'out_tok': 4623265}
3 launched workers {'read': 254.2, 'write5m': 1.4, 'write1h': 225.7, 'output': 204.6, 'input': 0.1, 'think_tok': 5241198, 'out_tok': 10230423}
4 experiments (writer) {'read': 0.0, 'write5m': 0.0, 'write1h': 3.2, 'output': 0.0, 'input': 0.0, 'think_tok': 0, 'out_tok': 7}
5 sentinel {'haiku/all': 3.1}
6 dead-man pushes {'haiku/all': 0.0}
8 operator folder session {'read': 2.5, 'write5m': 0.0, 'write1h': 4.9, 'output': 0.6, 'input': 0.0, 'think_tok': 10430, 'out_tok': 32087}
9 live tests (pytest) {'haiku/all': 0.4}
total {'read': 574.8, 'write5m': 118.4, 'write1h': 271.0, 'output': 308.1, 'input': 0.1, 'think_tok': 6896068.0, 'out_tok': 15407483.0, 'haiku/all': 3.5}

## by role and effort ($)
('CTO helpers', 'general-purpose') 265.98 2834 calls 18 transcripts
('launched workers', 'test designer') 241.07 3134 calls 73 transcripts
('launched workers', 'independent-auditor') 224.01 2744 calls 64 transcripts
('launched workers', 'engineer/other') 217.33 2822 calls 53 transcripts
('CTO helpers', 'orchestrator') 126.58 1314 calls 6 transcripts
('CTO session', '-') 109.69 630 calls 1 transcripts
('CTO helpers', 'research') 39.69 460 calls 8 transcripts
('CTO helpers', 'independent-auditor') 23.22 320 calls 7 transcripts
('CTO helpers', 'product-spec') 10.06 182 calls 5 transcripts
('operator folder session', '-') 8.09 70 calls 1 transcripts
('launched workers', "worker's helper") 3.59 41 calls 1 transcripts
('experiments (writer)', '-') 3.24 1 calls 1 transcripts
('sentinel', '-') 3.14 122 calls 1 transcripts
('live tests (pytest)', '-') 0.4 194 calls 90 transcripts
('dead-man pushes', '-') 0.01 6 calls 2 transcripts
effort ('launched workers', 'high') 485.02
effort ('CTO helpers', 'high') 465.53
effort ('launched workers', 'max') 153.58
effort ('CTO session', 'high') 109.69
effort ('launched workers', 'medium') 25.86
effort ('launched workers', 'xhigh') 20.8
effort ('operator folder session', 'high') 8.09
effort ('experiments (writer)', 'high') 3.24
effort ('sentinel', 'medium') 3.14
effort ('launched workers', 'low') 0.73
effort ('live tests (pytest)', 'medium') 0.4
effort ('dead-man pushes', 'medium') 0.01

## first-call context (k tokens) by source: median, p90; and calls per transcript median
1 CTO session 1 358 358 calls med 630
2 CTO helpers 44 11 32 calls med 79.0
3 launched workers 190 49 52 calls med 41.0
3w workers' helpers 1 37 37 calls med 41
4 experiments (writer) 1 432 432 calls med 1
5 sentinel 1 101 101 calls med 122
6 dead-man pushes 2 23 23 calls med 3.0
8 operator folder session 1 131 131 calls med 70
9 live tests (pytest) 90 28 42 calls med 2.0

## cache expiries: calls whose cache write > 60k (a cold or near-cold prompt), by source
1 CTO session cold calls 7 their write $26.7 mean gap before 233 min | gaps>5m: 76 of 629, >60m: 7
2 CTO helpers cold calls 36 their write $58.7 mean gap before 63 min | gaps>5m: 38 of 5066, >60m: 4
5 sentinel cold calls 26 their write $0.5 mean gap before 108 min | gaps>5m: 35 of 121, >60m: 26
8 operator folder session cold calls 2 their write $2.6 mean gap before 123 min | gaps>5m: 9 of 69, >60m: 3

## workers 1h->5m cache: now $685.99, with 5m $633.97, saving $52.02

## context cap counterfactual (saving $, restarts)
limit 150k handover 60k: total $211 {'CTO session': (51, 7), 'CTO helpers': (134, 79), 'launched workers': (26, 149), 'experiments (writer)': (0, 1), 'operator folder session': (0, 2)}
limit 200k handover 60k: total $207 {'CTO session': (50, 5), 'CTO helpers': (122, 46), 'launched workers': (35, 69), 'experiments (writer)': (0, 1), 'operator folder session': (0, 1)}
limit 300k handover 80k: total $142 {'CTO session': (46, 3), 'CTO helpers': (85, 19), 'launched workers': (12, 20), 'experiments (writer)': (-1, 1), 'operator folder session': (0, 0)}

## the meter: cumulative fit pct = k * X (through the origin) at each reading since the reset
$ list incl. fresh-80: one point = 27.5; RMSE 0.52 pt, max miss 1.6 pt, R2 0.9990
$ list, transcripts only: one point = 24.4; RMSE 2.41 pt, max miss 4.9 pt, R2 0.9791
output tokens: one point = 2.93e+05; RMSE 2.75 pt, max miss 5.7 pt, R2 0.9728
cache-read tokens: one point = 5.52e+07; RMSE 2.63 pt, max miss 5.1 pt, R2 0.9750
all tokens (in+out+cr+cw): one point = 5.67e+07; RMSE 2.62 pt, max miss 5.0 pt, R2 0.9754
in+out+cw (no cache read): one point = 1.49e+06; RMSE 2.11 pt, max miss 4.3 pt, R2 0.9840
API calls: one point = 284; RMSE 3.12 pt, max miss 5.5 pt, R2 0.9648

## CTO wakes: {'text': 25, 'task-notification': 100, 'pasted': 9} human turns 134 compactions 1 tools {'Bash': 485, 'SendMessage': 66, 'Agent': 38, 'Read': 22, 'Edit': 13, 'Write': 10, 'PushNotification': 6, 'ToolSearch': 3}
sentinel wakes: {'task-notification': 36} 122 calls 2026-11-08T09:07:06.244Z 2026-11-10T10:57:29.360Z

## top 10 detail
(CTO)  $109.69: read $62.1 write $37.2 out $10.4 (thinking 19%); calls 630; ctx first 358k med 457k last 415k max 966k; 50.0 h 11-08T09:32..11-10T11:33; Bash 485, tool-result 0.6M chars; reads 22/21; tools 643; desc 
D-10 orchestrator $67.87: read $51.5 write $8.4 out $8.0 (thinking 23%); calls 606; ctx first 10k med 439k last 768k max 768k; 12.4 h 11-09T23:09..11-10T11:34; Bash 611, tool-result 0.7M chars; reads 5/5; tools 669; desc D-10 red-fix list, open items
D-5 general-purpose $57.44: read $36.4 write $14.0 out $7.0 (thinking 22%); calls 491; ctx first 32k med 388k last 666k max 666k; 15.5 h 11-09T18:51..11-10T10:20; Bash 487, tool-result 0.6M chars; reads 3/3; tools 538; desc D-5: the templates
W2-121 general-purpose $44.10: read $27.4 write $10.9 out $5.8 (thinking 19%); calls 396; ctx first 33k med 372k last 614k max 614k; 15.9 h 11-09T00:27..11-09T16:22; Bash 387, tool-result 0.6M chars; reads 1/1; tools 447; desc Item 8: tickets, tests first
ACT-OPERATOR-1 general-purpose $24.86: read $10.9 write $9.6 out $4.3 (thinking 39%); calls 164; ctx first 32k med 383k last 531k max 531k; 1.9 h 11-09T17:12..11-09T19:04; Bash 138, tool-result 0.6M chars; reads 9/9; tools 163; desc Prepare ACT-OPERATOR-1
D-6 general-purpose $22.92: read $14.6 write $4.6 out $3.8 (thinking 18%); calls 299; ctx first 32k med 255k last 408k max 408k; 4.3 h 11-09T18:51..11-09T23:11; Bash 299, tool-result 0.4M chars; reads 0/0; tools 327; desc D-6 part 2 and its rows
W2-146 general-purpose $22.44: read $6.3 write $13.6 out $2.5 (thinking 23%); calls 172; ctx first 32k med 201k last 335k max 335k; 3.5 h 11-09T13:43..11-09T17:12; Bash 130, tool-result 0.4M chars; reads 15/12; tools 160; desc Operator agent: ticket and tests
W2-149 orchestrator $22.14: read $12.5 write $5.7 out $3.9 (thinking 33%); calls 208; ctx first 12k med 322k last 460k max 460k; 10.7 h 11-10T00:52..11-10T11:35; Bash 186, tool-result 0.6M chars; reads 20/17; tools 240; desc Set-up A wiring in W2-149
W2-149 orchestrator $21.99: read $15.3 write $2.5 out $4.2 (thinking 29%); calls 242; ctx first 11k med 349k last 497k max 497k; 1.7 h 11-09T23:09..11-10T00:51; Bash 224, tool-result 0.6M chars; reads 8/8; tools 250; desc W2-149 F11, install ACT, OPERATOR-2
W2-149 general-purpose $15.61: read $9.4 write $2.1 out $4.1 (thinking 38%); calls 169; ctx first 32k med 296k last 443k max 443k; 1.9 h 11-09T20:56..11-09T22:53; Bash 137, tool-result 0.4M chars; reads 9/5; tools 183; desc Prepare the sets globs ACT
