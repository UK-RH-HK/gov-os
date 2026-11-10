
## by source (transcripts)
| key | calls | input | output | cache read | cache write | $ list |
|---|---|---|---|---|---|---|
| 1 CTO session | 630 | 1,524 | 0.5 M | 310.4 M | 4.6 M | 109.69 |
| 2 CTO helpers | 5,134 | 10,636 | 4.6 M | 1,286.3 M | 23.4 M | 467.44 |
| 3 launched workers | 8,744 | 17,698 | 10.2 M | 1,271.5 M | 28.5 M | 686.30 |
| 4 experiments (writer) | 1 | 2 | 0.0 M | 0.0 M | 0.4 M | 3.24 |
| 5 sentinel | 122 | 312 | 0.0 M | 12.2 M | 2.5 M | 3.14 |
| 6 dead-man pushes | 6 | 12 | 0.0 M | 0.1 M | 0.0 M | 0.01 |
| 8 operator folder session | 70 | 164 | 0.0 M | 12.7 M | 0.6 M | 8.09 |
| 9 live tests (pytest) | 194 | 388 | 0.1 M | 4.5 M | 1.6 M | 0.40 |
| total | 14,901 | 30,736 | 15.5 M | 2,897.7 M | 61.8 M | 1,278.31 |

## by source and model
| key | calls | input | output | cache read | cache write | $ list |
|---|---|---|---|---|---|---|
| ('1 CTO session', 'opus-5-5') | 630 | 1,524 | 0.5 M | 310.4 M | 4.6 M | 109.69 |
| ('2 CTO helpers', 'opus-5-5') | 5,134 | 10,636 | 4.6 M | 1,286.3 M | 23.4 M | 467.44 |
| ('3 launched workers', 'opus-5-5') | 8,744 | 17,698 | 10.2 M | 1,271.5 M | 28.5 M | 686.30 |
| ('4 experiments (writer)', 'opus-5-5') | 1 | 2 | 0.0 M | 0.0 M | 0.4 M | 3.24 |
| ('5 sentinel', 'haiku-5-5') | 122 | 312 | 0.0 M | 12.2 M | 2.5 M | 3.14 |
| ('6 dead-man pushes', 'haiku-5-5') | 6 | 12 | 0.0 M | 0.1 M | 0.0 M | 0.01 |
| ('8 operator folder session', 'opus-5-5') | 70 | 164 | 0.0 M | 12.7 M | 0.6 M | 8.09 |
| ('9 live tests (pytest)', 'haiku-5-5') | 194 | 388 | 0.1 M | 4.5 M | 1.6 M | 0.40 |
| total | 14,901 | 30,736 | 15.5 M | 2,897.7 M | 61.8 M | 1,278.31 |
external: {'source': 'experiments', 'ticket': 'W2-88/K9 fresh 80', 'day': '2026-11-08', 'cost': 109.05, 'start': '2026-11-08T19:32', 'end': '2026-11-08T21:46', 'note': 'FRESH-80-RESULT.md cost table'}

## by ticket
| ticket | calls | $ | sources |
| W2-149 | 1531 | 157.05 | launched workers 95, CTO helpers 62 |
| (CTO) | 630 | 109.69 | CTO session 110 |
| W2-20 | 1208 | 95.01 | launched workers 95 |
| W2-148 | 982 | 92.55 | launched workers 79, CTO helpers 14 |
| W2-56 | 1160 | 83.30 | launched workers 64, CTO helpers 19, live tests (pytest) 0 |
| D-10 | 699 | 73.01 | CTO helpers 73 |
| D-5 | 491 | 57.44 | CTO helpers 57 |
| W2-141 | 719 | 52.74 | launched workers 46, CTO helpers 7 |
| W2-121 | 396 | 44.10 | CTO helpers 44 |
| W2-128 | 531 | 37.27 | launched workers 37 |
| ACT-OPERATOR-1 | 258 | 33.08 | CTO helpers 33 |
| W2-146 | 300 | 33.03 | CTO helpers 33 |
| D-6 | 430 | 31.79 | CTO helpers 23, launched workers 9 |
| W2-145 | 369 | 30.63 | launched workers 31 |
| W2-153 | 533 | 28.52 | launched workers 29 |
| W2-96 | 295 | 27.28 | launched workers 27 |
| W2-139 | 366 | 24.05 | launched workers 18, CTO helpers 6 |
| W2-92 | 352 | 22.07 | launched workers 22 |
| W2-150 | 325 | 21.37 | launched workers 21 |
| ACT-GUARD-SETS-1 | 213 | 18.71 | CTO helpers 19 |
| W2-152 | 232 | 17.48 | launched workers 17 |
| W2-55 | 288 | 14.46 | launched workers 14 |
| W2-05 | 180 | 14.22 | launched workers 14 |
| ACT-SELECT-FIXES-1 | 161 | 13.22 | CTO helpers 13 |
| ACT-STOP-IDLE-1 | 138 | 10.97 | CTO helpers 11 |
| W2-58 | 152 | 10.08 | launched workers 10 |
| W2-130 | 102 | 10.02 | CTO helpers 7, launched workers 3 |
| W2-66 | 129 | 9.75 | CTO helpers 5, launched workers 5 |
| ACT-INDEP-WALLS-1 | 74 | 8.76 | CTO helpers 9 |
| W2-129 | 142 | 8.72 | launched workers 9 |
| (operator folder session) | 70 | 8.09 | operator folder session 8 |
| W2-126 | 96 | 6.66 | launched workers 7 |
| W2-13 | 97 | 6.20 | launched workers 6 |
| D-4 | 85 | 5.72 | CTO helpers 6 |
| W2-116 | 86 | 5.52 | launched workers 6 |
| (helper, no id) | 55 | 5.30 | CTO helpers 5 |
| W2-147 | 75 | 5.30 | launched workers 5 |
| W2-140 | 46 | 5.24 | launched workers 5 |
| W2-138 | 80 | 4.79 | launched workers 5 |
| W2-142 | 75 | 4.11 | launched workers 4 |
| W2-1 | 60 | 3.43 | CTO helpers 3 |
| ACT-SANDBOX-SEAL-1 | 42 | 3.30 | CTO helpers 3 |
| W2-2 | 42 | 3.28 | CTO helpers 3 |
| (experiments (writer)) | 1 | 3.24 | experiments (writer) 3 |
| (sentinel) | 122 | 3.14 | sentinel 3 |
| W2-137 | 73 | 3.12 | CTO helpers 2, launched workers 2 |
| W2-136 | 58 | 2.20 | CTO helpers 2 |
| ACT-CLAUDE-COPIES-1 | 60 | 2.18 | CTO helpers 2 |
| W2-151 | 52 | 2.11 | launched workers 2 |
| ACT-CLAUDE-COPIES-2 | 55 | 1.75 | CTO helpers 2 |
| W2-88 | 23 | 1.52 | CTO helpers 2 |
| W2-03 | 40 | 1.51 | CTO helpers 2 |
| (live tests (pytest)) | 78 | 0.16 | live tests (pytest) 0 |
| W1-46/W2-153 | 38 | 0.07 | live tests (pytest) 0 |
| (dead-man pushes) | 6 | 0.01 | dead-man pushes 0 |

## by day (UTC)
| key | calls | input | output | cache read | cache write | $ list |
|---|---|---|---|---|---|---|
| 2026-11-08 | 160 | 374 | 0.1 M | 52.1 M | 2.5 M | 26.38 |
| 2026-11-09 | 10,647 | 21,976 | 11.0 M | 2,043.2 M | 43.6 M | 904.83 |
| 2026-11-10 | 4,094 | 8,386 | 4.5 M | 802.4 M | 15.7 M | 347.10 |
| total | 14,901 | 30,736 | 15.5 M | 2,897.7 M | 61.8 M | 1,278.31 |
2026-11-08 {'1 CTO session': 20.37, '2 CTO helpers': 1.99, '4 experiments (writer)': 3.24, '5 sentinel': 0.77}
2026-11-09 {'1 CTO session': 74.82, '2 CTO helpers': 342.86, '3 launched workers': 477.38, '5 sentinel': 1.53, '8 operator folder session': 8.09, '9 live tests (pytest)': 0.15}
2026-11-10 {'1 CTO session': 14.49, '2 CTO helpers': 122.59, '3 launched workers': 208.92, '5 sentinel': 0.84, '6 dead-man pushes': 0.01, '9 live tests (pytest)': 0.24}

## meter intervals
| from | to | pct | $ | $ incl. exp | out M | cr M | cw M | calls | $/pt |
| 11-08T09:00 | 11-08T09:23 | 0->0 | 0 | 0 | 0.0 | 0.4 | 0.0 | 4 | nan |
| 11-08T09:23 | 11-08T18:17 | 0->1 | 19 | 19 | 0.0 | 19.8 | 2.2 | 76 | 18.5 |
| 11-08T18:17 | 11-08T19:55 | 1->2 | 5 | 24 | 0.0 | 20.2 | 0.0 | 47 | 23.7 |
| 11-08T19:55 | 11-08T20:25 | 2->4 | 0 | 25 | 0.0 | 0.2 | 0.1 | 3 | 12.3 |
| 11-08T20:25 | 11-08T21:25 | 4->5 | 2 | 51 | 0.0 | 7.9 | 0.0 | 17 | 50.7 |
| 11-08T21:25 | 11-08T21:56 | 5->6 | 1 | 18 | 0.0 | 3.1 | 0.1 | 9 | 18.0 |
| 11-08T21:56 | 11-09T01:02 | 6->8 | 56 | 56 | 0.7 | 114.7 | 3.1 | 621 | 28.1 |
| 11-09T01:02 | 11-09T01:34 | 8->9 | 46 | 46 | 0.7 | 97.1 | 1.9 | 535 | 45.9 |
| 11-09T01:34 | 11-09T02:06 | 9->11 | 43 | 43 | 0.6 | 103.1 | 1.5 | 530 | 21.5 |
| 11-09T02:06 | 11-09T03:10 | 11->12 | 40 | 40 | 0.5 | 101.2 | 1.4 | 506 | 40.5 |
| 11-09T03:10 | 11-09T04:47 | 12->13 | 17 | 17 | 0.1 | 42.7 | 0.9 | 139 | 16.7 |
| 11-09T04:47 | 11-09T14:09 | 13->14 | 50 | 50 | 0.5 | 92.5 | 3.6 | 424 | 50.3 |
| 11-09T14:09 | 11-09T14:42 | 14->15 | 29 | 29 | 0.4 | 67.1 | 1.3 | 279 | 29.3 |
| 11-09T14:42 | 11-09T15:16 | 15->16 | 34 | 34 | 0.4 | 76.3 | 1.8 | 275 | 34.3 |
| 11-09T15:16 | 11-09T15:49 | 16->17 | 24 | 24 | 0.2 | 55.7 | 1.1 | 253 | 23.7 |
| 11-09T15:49 | 11-09T16:23 | 17->18 | 32 | 32 | 0.3 | 59.7 | 2.4 | 280 | 32.3 |
| 11-09T16:23 | 11-09T16:56 | 18->19 | 17 | 17 | 0.2 | 35.9 | 1.2 | 157 | 17.3 |
| 11-09T16:56 | 11-09T17:29 | 19->20 | 16 | 16 | 0.2 | 38.6 | 0.9 | 182 | 16.5 |
| 11-09T17:29 | 11-09T18:35 | 20->21 | 24 | 24 | 0.2 | 58.9 | 1.4 | 193 | 23.7 |
| 11-09T18:35 | 11-09T19:08 | 21->22 | 51 | 51 | 0.6 | 97.3 | 3.2 | 670 | 51.1 |
| 11-09T19:08 | 11-09T19:39 | 22->25 | 67 | 67 | 1.0 | 141.5 | 2.9 | 835 | 22.3 |
| 11-09T19:39 | 11-09T20:09 | 25->27 | 49 | 49 | 0.6 | 124.5 | 1.8 | 563 | 24.4 |
| 11-09T20:09 | 11-09T20:39 | 27->28 | 41 | 41 | 0.5 | 102.5 | 1.7 | 568 | 40.6 |
| 11-09T20:39 | 11-09T21:09 | 28->29 | 47 | 47 | 0.6 | 103.7 | 2.2 | 534 | 46.9 |
| 11-09T21:09 | 11-09T21:40 | 29->31 | 36 | 36 | 0.4 | 85.3 | 1.8 | 538 | 17.8 |
| 11-09T21:40 | 11-09T22:10 | 31->32 | 34 | 34 | 0.4 | 87.9 | 1.2 | 481 | 34.4 |
| 11-09T22:10 | 11-09T22:41 | 32->33 | 34 | 34 | 0.3 | 91.5 | 1.3 | 494 | 34.1 |
| 11-09T22:41 | 11-09T23:12 | 33->34 | 28 | 28 | 0.3 | 62.5 | 1.6 | 437 | 28.3 |
| 11-09T23:12 | 11-09T23:43 | 34->36 | 55 | 55 | 0.7 | 128.2 | 2.4 | 777 | 27.4 |
| 11-09T23:43 | 11-10T00:14 | 36->38 | 60 | 60 | 0.9 | 137.0 | 2.2 | 753 | 29.9 |
| 11-10T00:14 | 11-10T00:46 | 38->40 | 46 | 46 | 0.6 | 99.1 | 1.9 | 572 | 22.8 |
| 11-10T00:46 | 11-10T01:17 | 40->42 | 54 | 54 | 0.7 | 124.5 | 2.0 | 723 | 27.1 |
| 11-10T01:17 | 11-10T01:49 | 42->44 | 42 | 42 | 0.6 | 108.5 | 1.7 | 516 | 21.1 |
| 11-10T01:49 | 11-10T02:50 | 44->45 | 27 | 27 | 0.3 | 74.2 | 1.4 | 303 | 27.2 |
| 11-10T02:50 | 11-10T09:56 | 45->46 | 25 | 25 | 0.2 | 45.5 | 2.3 | 245 | 25.2 |
| 11-10T09:56 | 11-10T10:29 | 46->48 | 47 | 47 | 0.5 | 105.9 | 2.3 | 539 | 23.6 |
| 11-10T10:29 | 11-10T11:03 | 48->50 | 42 | 42 | 0.6 | 92.5 | 1.9 | 469 | 21.1 |
| 11-10T11:03 | 11-10T11:36 | 50->51 | 35 | 35 | 0.5 | 83.8 | 1.1 | 327 | 35.3 |

## top transcripts
| # | source | ticket | role | label | calls | turns | ctx med/max k | cr M | out k | cw M | effort | compact | reads/distinct | $ |
| 1 | CTO session | (CTO) |  |  | 630 | 130 | 451/964 | 310.4 | 522 | 4.65 | high:630 | 1 | 22/21 | 109.69 |
| 2 | CTO helpers | D-10 | orchestrator | D-10 red-fix list, open items | 612 | 1 | 439/772 | 262.0 | 407 | 1.68 | high:612 | 0 | 5/5 | 68.92 |
| 3 | CTO helpers | D-5 | general-purpose | D-5: the templates | 491 | 1 | 381/664 | 182.2 | 348 | 2.81 | high:491 | 0 | 3/3 | 57.44 |
| 4 | CTO helpers | W2-121 | general-purpose | Item 8: tickets, tests first | 396 | 1 | 364/613 | 137.0 | 289 | 2.19 | high:396 | 0 | 1/1 | 44.10 |
| 5 | CTO helpers | ACT-OPERATOR-1 | general-purpose | Prepare ACT-OPERATOR-1 | 164 | 1 | 375/530 | 54.7 | 216 | 1.92 | high:164 | 0 | 9/9 | 24.86 |
| 6 | CTO helpers | D-6 | general-purpose | D-6 part 2 and its rows | 299 | 1 | 253/406 | 72.8 | 190 | 0.91 | high:299 | 0 | 0/0 | 22.92 |
| 7 | CTO helpers | W2-146 | general-purpose | Operator agent: ticket and tests | 172 | 1 | 187/334 | 31.5 | 125 | 2.73 | high:172 | 0 | 15/12 | 22.44 |
| 8 | CTO helpers | W2-149 | orchestrator | Set-up A wiring in W2-149 | 208 | 1 | 321/460 | 62.7 | 194 | 1.15 | high:208 | 0 | 20/17 | 22.14 |
| 9 | CTO helpers | W2-149 | orchestrator | W2-149 F11, install ACT, OPERATOR-2 | 242 | 1 | 348/495 | 76.7 | 210 | 0.49 | high:242 | 0 | 8/8 | 21.99 |
| 10 | CTO helpers | W2-149 | general-purpose | Prepare the sets globs ACT | 169 | 1 | 293/440 | 47.0 | 204 | 0.42 | high:169 | 0 | 9/5 | 15.61 |
| 11 | launched workers | W2-20 | engineer/other | W2-20-engineer-r2-2 | 131 | 2 | 333/443 | 40.9 | 164 | 0.45 | high:131 | 0 | 47/39 | 15.04 |
| 12 | launched workers | W2-148 | engineer/other | W2-148-engineer | 104 | 1 | 328/460 | 31.2 | 264 | 0.43 | high:104 | 0 | 22/22 | 14.95 |
| 13 | launched workers | W2-20 | engineer/other | W2-20-engineer | 147 | 8 | 277/388 | 38.0 | 177 | 0.36 | high:147 | 0 | 42/32 | 14.01 |
| 14 | launched workers | W2-56 | test designer | W2-56-designer-r2 | 135 | 1 | 303/385 | 37.9 | 161 | 0.35 | high:135 | 0 | 36/29 | 13.64 |
| 15 | CTO helpers | ACT-SELECT-FIXES-1 | general-purpose | Prepare ACT-SELECT-FIXES-1 and hook | 161 | 1 | 261/380 | 39.7 | 173 | 0.36 | high:161 | 0 | 4/4 | 13.22 |
| 16 | launched workers | W2-149 | test designer | W2-149-designer-sgx-2 | 83 | 1 | 290/413 | 23.0 | 206 | 0.40 | xhigh:83 | 0 | 30/28 | 11.91 |
| 17 | launched workers | W2-145 | test designer | W2-145-designer | 97 | 2 | 272/387 | 24.9 | 161 | 0.39 | high:97 | 0 | 32/30 | 11.32 |
| 18 | CTO helpers | W2-146 | general-purpose | Launch script, tests first | 128 | 1 | 181/275 | 22.4 | 83 | 0.89 | high:128 | 0 | 23/21 | 10.59 |
| 19 | launched workers | W2-20 | test designer | W2-20-designer | 99 | 3 | 233/348 | 22.5 | 167 | 0.32 | high:99 | 0 | 28/23 | 10.41 |
| 20 | launched workers | W2-149 | test designer | W2-149-designer | 64 | 1 | 299/378 | 16.5 | 200 | 0.35 | high:64 | 0 | 24/20 | 10.10 |
| 21 | launched workers | W2-56 | engineer/other | W2-56-engineer | 108 | 1 | 245/309 | 23.9 | 140 | 0.28 | high:108 | 0 | 22/20 | 9.83 |
| 22 | launched workers | W2-150 | engineer/other | W2-150-engineer | 120 | 1 | 219/305 | 24.2 | 112 | 0.27 | high:120 | 0 | 39/33 | 9.28 |
| 23 | launched workers | W2-149 | engineer/other | W2-149-engineer | 69 | 1 | 247/328 | 15.6 | 183 | 0.30 | high:69 | 0 | 16/16 | 9.18 |
| 24 | CTO helpers | W2-56 | general-purpose | W2-56: second half and engineer | 171 | 1 | 183/262 | 29.6 | 98 | 0.24 | high:171 | 0 | 6/5 | 9.11 |
| 25 | launched workers | W2-149 | independent-auditor | ACT-W2-149-INSTALL-1-review-v2 | 77 | 1 | 220/363 | 15.8 | 157 | 0.35 | max:77 | 0 | 37/31 | 9.10 |

## check: 188 sessions with own result: total_cost_usd 683.39 vs priced here 683.11 (ratio 1.000)

## tool calls / result chars
Read 3525 28.1 M chars
Bash 10546 15.8 M chars
Grep 2073 3.4 M chars
Edit 1974 0.3 M chars
Write 1007 0.2 M chars
Glob 211 0.1 M chars
WebFetch 9 0.1 M chars
Agent 42 0.1 M chars
Monitor 66 0.0 M chars
SendMessage 62 0.0 M chars
1 CTO session {'Bash': '0.4M', 'Read': '0.1M', 'Agent': '0.0M', 'SendMessage': '0.0M'}
2 CTO helpers {'Bash': '8.5M', 'Read': '4.1M', 'Write': '0.1M', 'WebFetch': '0.1M'}
3 launched workers {'Read': '23.6M', 'Bash': '6.9M', 'Grep': '3.4M', 'Edit': '0.3M'}
5 sentinel {'Bash': '0.0M', 'Read': '0.0M', 'PushNotification': '0.0M'}
6 dead-man pushes {'PushNotification': '0.0M', 'ToolSearch': '0.0M'}
8 operator folder session {'Read': '0.2M', 'Bash': '0.0M'}
9 live tests (pytest) {'Bash': '0.0M', 'Write': '0.0M', 'Read': '0.0M'}
