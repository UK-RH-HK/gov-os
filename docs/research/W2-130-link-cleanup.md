# W2-130: the link clean-up, its record (DEC-1073 (5)(a))

Ticket DAEO-q8cl (W2-130), profile STANDARD. Written by the ticket lead (orchestrator), 2026-11-14, at the end of
run 3. This record holds what the ticket's eight success lines and four failure lines ask to be kept: the commits,
the marks and their independent check, the tickets' `sources:`, the trailer residuals, the status reconciliation,
the lessons, the counts before and after, and what is left for D-5, D-6 and D-9. The fenced blocks named
`w2-130:<name>` are read by `tests/acceptance/W2-130/`; the prose is for a reader.

The register holds the owner's decisions. A mark changes no decision's meaning: every register change here is a
status line kept whole with marks appended (DEC-866), or a status the owner decided (DEC-1098 (3)). No commit was
rewritten.

## 1. When it started, and on whose word (F4)

- The clean-up's first commit is `e12f8a30ca7d` (e12f8a30c), whose parent `232efc47dd70`
  is the starting head.
- W2-129's landing (DAEO-q7lk, merge `34eed411ac8c`) and the adoption of W2-92's stated links
  (DAEO-n0wb, merge `3679ca0bad0b`) are both ancestors of e12f8a30c.
- The owner allowed the start in **DEC-1097 (9)**.
- The owner's ruling on the status list is **DEC-1098 (3)**, committed in `9546edd61565`. That
  commit is an ancestor of every clean-up commit that changes a status (c4420040f, and the R-12 follow-up), and not
  of e12f8a30c.

## 2. The commits

| commit | what | lists |
|---|---|---|
| `e12f8a30ca7d` | batches a1, a2 (the marks: the 87 first, then the rest), a0 (the archive's line 34, one decision per line), b1 (50 open and in-progress tickets' `sources:`) | marks, sources |
| `c4420040f9b3` | after the owner's sitting (DEC-1098 (3)): the decided status words, the a3 marks, this ticket's KPI 4 line and its `sources:` DEC-1098 and DEC-1088 | marks, status |
| `8d245901b239` | follow-up (2): DECISIONS-IN-FORCE's R-12 line reworded (P-W2-130-3 (a)) | status, r12 |
| `8f8d707f0bd0` | follow-up (3): each lesson's `sources:` key (DEC-1073 (5)(c)) | lessons |
| `bce798c3a911` | follow-up (4): the two marks the auditor passed, DEC-1115<-DEC-1122 and DEC-026<-DEC-086 | marks |
| `57cbacfbfc86` | follow-up (1): the open and in-progress tickets' `sources:` from `gov links --propose-sources`, less DEC-1123 (2)'s forms (P-W2-130-4 (a)) | sources |

The follow-ups are numbered as the plan numbered them; (1) was made last, after the CTO's answer to P-W2-130-4. Each
changes one kind of file and nothing else. This record and LINK-RECONCILIATION.md are committed after them and are
not clean-up commits.

```yaml w2-130:commits
starting_head: 232efc47dd707dd76038cf8211842d9b4472473c
first_commit: e12f8a30ca7dbbf470396f9e2ac9edd68a2aa968
w2_129_landing: 34eed411ac8c1d58dc8279c6d55700a0dcbc2c21
w2_92_adoption: 3679ca0bad0b44fd772bcf76380dc9081165e3e0
start_decision: DEC-1097 (9)
status_decision: DEC-1098 (3)
status_decision_commit: 9546edd61565603981cb2d3148bc4dfb88b26b13
sitting_commit: 2f9c80b1f80747f26507093551fd4da5e5eccc0f
cleanup:
- e12f8a30ca7dbbf470396f9e2ac9edd68a2aa968
- c4420040f9b31403d05c8a035d385edd1d6fcc76
- 8d245901b239f447e78c4b5dd3f32cd9dba94bbb
- 8f8d707f0bd0024a981833ccc43caf5e88b0655e
- bce798c3a9113544daca5effee9d602080b64741
- 57cbacfbfc861eb982cf08b6aebb3c699171a1de
marks:
- e12f8a30ca7dbbf470396f9e2ac9edd68a2aa968
- c4420040f9b31403d05c8a035d385edd1d6fcc76
- bce798c3a9113544daca5effee9d602080b64741
sources:
- e12f8a30ca7dbbf470396f9e2ac9edd68a2aa968
- 57cbacfbfc861eb982cf08b6aebb3c699171a1de
status:
- c4420040f9b31403d05c8a035d385edd1d6fcc76
- 8d245901b239f447e78c4b5dd3f32cd9dba94bbb
r12: 8d245901b239f447e78c4b5dd3f32cd9dba94bbb
lessons: 8f8d707f0bd0024a981833ccc43caf5e88b0655e
```

## 3. The marks (S1, S2)

**The 87 first.** The census's script (`docs/research/D4B-link-census.py` at 3d1c459e, run on 24f06026) finds 215
decisions current though stated changed; 87 of them have no hint of a changer in their own entry. e12f8a30c marks
them from `gov links --propose-marks` (patches a1 and a2 as the drafts' builder printed them for the commit, after
the auditor's drops and rewrites: section 4). Every register hunk of e12f8a30c is a status-line append.

```yaml w2-130:ids-87
- DEC-030
- DEC-039
- DEC-066
- DEC-070
- DEC-082
- DEC-083
- DEC-090
- DEC-093
- DEC-107
- DEC-121
- DEC-153
- DEC-156
- DEC-157
- DEC-176
- DEC-180
- DEC-220
- DEC-235
- DEC-241
- DEC-250
- DEC-258
- DEC-269
- DEC-285
- DEC-290
- DEC-293
- DEC-304
- DEC-318
- DEC-362
- DEC-365
- DEC-367
- DEC-371
- DEC-376
- DEC-378
- DEC-384
- DEC-385
- DEC-386
- DEC-390
- DEC-391
- DEC-394
- DEC-398
- DEC-403
- DEC-407
- DEC-409
- DEC-417
- DEC-421
- DEC-508
- DEC-511
- DEC-513
- DEC-605
- DEC-709
- DEC-721
- DEC-761
- DEC-787
- DEC-832
- DEC-839
- DEC-851
- DEC-853
- DEC-861
- DEC-897
- DEC-914
- DEC-916
- DEC-925
- DEC-943
- DEC-949
- DEC-958
- DEC-961
- DEC-966
- DEC-967
- DEC-968
- DEC-971
- DEC-973
- DEC-974
- DEC-976
- DEC-982
- DEC-989
- DEC-991
- DEC-994
- DEC-1003
- DEC-1012
- DEC-1028
- DEC-1037
- DEC-1038
- DEC-1039
- DEC-1047
- DEC-1048
- DEC-1050
- DEC-1052
- DEC-1066
```

**The census's 215 and the changers it states.**

```yaml w2-130:census
DEC-030:
- DEC-080
DEC-039:
- DEC-075
DEC-053:
- DEC-165
DEC-066:
- DEC-094
DEC-070:
- DEC-096
DEC-072:
- DEC-064
DEC-082:
- DEC-096
DEC-083:
- DEC-163
DEC-090:
- DEC-741
DEC-093:
- DEC-220
DEC-096:
- DEC-953
- DEC-1010
DEC-107:
- DEC-117
DEC-120:
- DEC-172
- DEC-173
- DEC-825
DEC-121:
- DEC-127
DEC-140:
- DEC-842
DEC-150:
- DEC-156
DEC-151:
- DEC-172
- DEC-825
DEC-153:
- DEC-209
DEC-156:
- DEC-165
- DEC-176
- DEC-434
DEC-157:
- DEC-209
DEC-162:
- DEC-156
DEC-176:
- DEC-365
- DEC-402
DEC-180:
- DEC-311
DEC-183:
- DEC-205
- DEC-235
- DEC-371
DEC-192:
- DEC-202
- DEC-825
DEC-208:
- DEC-237
- DEC-250
- DEC-838
DEC-220:
- DEC-416
- DEC-974
DEC-235:
- DEC-363
DEC-237:
- DEC-250
- DEC-838
DEC-241:
- DEC-316
DEC-248:
- DEC-838
DEC-250:
- DEC-420
DEC-253:
- DEC-912
DEC-258:
- DEC-264
DEC-261:
- DEC-798
- DEC-1033
DEC-269:
- DEC-394
DEC-281:
- DEC-208
- DEC-237
- DEC-838
- DEC-901
DEC-285:
- DEC-1045
DEC-290:
- DEC-1045
DEC-293:
- DEC-300
DEC-304:
- DEC-310
DEC-318:
- DEC-359
DEC-362:
- DEC-389
DEC-365:
- DEC-402
- DEC-407
- DEC-409
DEC-367:
- DEC-409
DEC-371:
- DEC-386
DEC-376:
- DEC-395
DEC-378:
- DEC-402
DEC-384:
- DEC-397
DEC-385:
- DEC-399
DEC-386:
- DEC-392
DEC-390:
- DEC-394
DEC-391:
- DEC-393
- DEC-396
DEC-394:
- DEC-398
- DEC-403
DEC-398:
- DEC-403
DEC-403:
- DEC-410
DEC-407:
- DEC-409
DEC-409:
- DEC-428
DEC-410:
- DEC-421
- DEC-918
DEC-413:
- DEC-880
- DEC-909
- DEC-912
- DEC-916
DEC-417:
- DEC-421
DEC-421:
- DEC-572
DEC-448:
- DEC-456
- DEC-477
DEC-451:
- DEC-838
DEC-454:
- DEC-868
- DEC-899
- DEC-904
- DEC-908
DEC-455:
- DEC-868
- DEC-899
- DEC-904
- DEC-908
DEC-460:
- DEC-839
- DEC-840
DEC-466:
- DEC-953
DEC-480:
- DEC-868
- DEC-899
- DEC-904
- DEC-908
DEC-490:
- DEC-868
- DEC-899
- DEC-904
- DEC-908
DEC-492:
- DEC-866
- DEC-868
- DEC-899
- DEC-904
- DEC-908
DEC-493:
- DEC-896
- DEC-903
- DEC-904
DEC-501:
- DEC-502
- DEC-512
- DEC-825
DEC-502:
- DEC-512
- DEC-825
DEC-508:
- DEC-820
DEC-511:
- DEC-522
- DEC-1057
DEC-513:
- DEC-518
- DEC-536
DEC-518:
- DEC-533
- DEC-536
- DEC-825
DEC-526:
- DEC-541
- DEC-825
DEC-594:
- DEC-593
DEC-605:
- DEC-822
DEC-608:
- DEC-880
- DEC-913
- DEC-917
DEC-624:
- DEC-626
- DEC-825
DEC-665:
- DEC-838
DEC-709:
- DEC-719
DEC-718:
- DEC-900
- DEC-953
DEC-721:
- DEC-953
DEC-723:
- DEC-820
- DEC-953
DEC-724:
- DEC-860
- DEC-861
DEC-726:
- DEC-843
- DEC-852
- DEC-880
DEC-728:
- DEC-723
- DEC-953
DEC-737:
- DEC-847
DEC-742:
- DEC-942
DEC-757:
- DEC-899
- DEC-900
- DEC-953
DEC-761:
- DEC-772
DEC-762:
- DEC-953
DEC-766:
- DEC-953
DEC-769:
- DEC-953
DEC-776:
- DEC-847
DEC-780:
- DEC-775
- DEC-953
DEC-786:
- DEC-847
DEC-787:
- DEC-948
DEC-788:
- DEC-861
DEC-792:
- DEC-837
DEC-804:
- DEC-807
DEC-805:
- DEC-971
DEC-806:
- DEC-953
DEC-813:
- DEC-889
- DEC-899
DEC-819:
- DEC-856
- DEC-887
DEC-820:
- DEC-953
DEC-821:
- DEC-873
DEC-822:
- DEC-953
DEC-823:
- DEC-869
DEC-826:
- DEC-953
DEC-829:
- DEC-831
DEC-830:
- DEC-848
DEC-831:
- DEC-941
DEC-832:
- DEC-957
DEC-839:
- DEC-957
DEC-841:
- DEC-880
DEC-843:
- DEC-852
- DEC-880
DEC-847:
- DEC-880
- DEC-941
- DEC-942
- DEC-953
DEC-849:
- DEC-857
- DEC-953
DEC-850:
- DEC-855
DEC-851:
- DEC-1052
- DEC-1057
DEC-852:
- DEC-880
- DEC-889
DEC-853:
- DEC-884
DEC-855:
- DEC-858
- DEC-936
- DEC-938
- DEC-972
DEC-856:
- DEC-887
DEC-861:
- DEC-1057
DEC-862:
- DEC-906
- DEC-953
DEC-868:
- DEC-892
- DEC-953
DEC-873:
- DEC-953
DEC-879:
- DEC-883
- DEC-884
DEC-880:
- DEC-843
- DEC-882
- DEC-884
- DEC-889
- DEC-904
- DEC-952
DEC-883:
- DEC-889
- DEC-890
DEC-884:
- DEC-889
- DEC-896
- DEC-899
- DEC-918
- DEC-921
- DEC-953
DEC-889:
- DEC-892
- DEC-896
- DEC-899
- DEC-904
DEC-890:
- DEC-896
- DEC-899
DEC-891:
- DEC-906
- DEC-924
- DEC-953
DEC-892:
- DEC-896
- DEC-899
DEC-893:
- DEC-953
- DEC-1045
DEC-895:
- DEC-922
- DEC-953
DEC-896:
- DEC-891
- DEC-923
- DEC-953
- DEC-1057
DEC-897:
- DEC-909
DEC-898:
- DEC-899
- DEC-902
- DEC-904
DEC-899:
- DEC-902
- DEC-912
- DEC-915
- DEC-918
- DEC-924
- DEC-925
- DEC-953
DEC-900:
- DEC-906
DEC-904:
- DEC-905
- DEC-922
DEC-905:
- DEC-906
- DEC-962
DEC-906:
- DEC-953
- DEC-962
DEC-910:
- DEC-911
DEC-911:
- DEC-923
- DEC-953
DEC-914:
- DEC-916
DEC-915:
- DEC-953
DEC-916:
- DEC-987
- DEC-1010
DEC-923:
- DEC-925
- DEC-953
DEC-924:
- DEC-925
- DEC-953
DEC-925:
- DEC-1057
DEC-926:
- DEC-953
DEC-927:
- DEC-928
- DEC-953
- DEC-1057
DEC-928:
- DEC-953
DEC-929:
- DEC-953
DEC-930:
- DEC-949
DEC-933:
- DEC-953
- DEC-961
- DEC-973
- DEC-1049
DEC-934:
- DEC-936
- DEC-973
- DEC-1049
DEC-936:
- DEC-938
- DEC-941
- DEC-946
- DEC-953
- DEC-974
DEC-938:
- DEC-941
- DEC-949
- DEC-951
- DEC-953
- DEC-973
DEC-939:
- DEC-945
- DEC-953
- DEC-961
- DEC-1001
DEC-941:
- DEC-942
- DEC-944
- DEC-946
- DEC-953
- DEC-954
DEC-942:
- DEC-946
- DEC-947
- DEC-953
- DEC-961
DEC-943:
- DEC-1052
DEC-946:
- DEC-953
DEC-947:
- DEC-953
- DEC-960
- DEC-961
DEC-949:
- DEC-973
- DEC-1057
DEC-951:
- DEC-953
- DEC-973
DEC-952:
- DEC-953
DEC-953:
- DEC-954
- DEC-959
- DEC-968
- DEC-1045
DEC-954:
- DEC-957
- DEC-962
- DEC-1037
DEC-957:
- DEC-959
- DEC-1052
DEC-958:
- DEC-1050
DEC-959:
- DEC-968
DEC-961:
- DEC-984
DEC-962:
- DEC-963
- DEC-1001
DEC-963:
- DEC-966
DEC-964:
- DEC-970
DEC-966:
- DEC-1045
DEC-967:
- DEC-975
DEC-968:
- DEC-1049
DEC-971:
- DEC-1001
DEC-972:
- DEC-973
- DEC-1021
DEC-973:
- DEC-1049
DEC-974:
- DEC-979
DEC-975:
- DEC-1032
DEC-976:
- DEC-979
DEC-982:
- DEC-1003
DEC-988:
- DEC-989
DEC-989:
- DEC-1045
DEC-991:
- DEC-1050
- DEC-1057
DEC-994:
- DEC-998
DEC-1003:
- DEC-1052
- DEC-1057
DEC-1009:
- DEC-1069
DEC-1012:
- DEC-1057
DEC-1028:
- DEC-1057
DEC-1032:
- DEC-1033
DEC-1037:
- DEC-1039
DEC-1038:
- DEC-1057
DEC-1039:
- DEC-1047
- DEC-1049
- DEC-1052
DEC-1047:
- DEC-1049
- DEC-1051
DEC-1048:
- DEC-1051
DEC-1049:
- DEC-1050
DEC-1050:
- DEC-1057
DEC-1052:
- DEC-1055
DEC-1053:
- DEC-880
DEC-1066:
- DEC-1067
```

**The 13 pairs stated only in ARCHIVE-SUPERSEDED §A** (W2-92's drift script, `--from-head`, on the starting head's
register and archive; `drafts/w2-130/work-drift-head.json`). Three are marked (DEC-454<-DEC-868, DEC-454<-DEC-899,
DEC-455<-DEC-899); the other ten were judged wrong (below). Patch a0 rewrote the archive's collective line so that
each decision names only the changers its own entry supports (the auditor's F4 and the sitting's H2).

```yaml w2-130:archive-13
- changed: DEC-454
  changer: DEC-868
- changed: DEC-454
  changer: DEC-899
- changed: DEC-454
  changer: DEC-904
- changed: DEC-455
  changer: DEC-899
- changed: DEC-455
  changer: DEC-904
- changed: DEC-480
  changer: DEC-899
- changed: DEC-480
  changer: DEC-904
- changed: DEC-490
  changer: DEC-868
- changed: DEC-490
  changer: DEC-899
- changed: DEC-490
  changer: DEC-908
- changed: DEC-492
  changer: DEC-904
- changed: DEC-492
  changer: DEC-908
- changed: DEC-501
  changer: DEC-512
```

**Left unmarked because an independent auditor judged the pair wrong.** `gov links --all` reports exactly 8
UNMARKED_CHANGE at the last clean-up commit, the 8 pairs below with `in_gov_links: true`. The other 11 are census
pairs no status line names; `gov links` no longer reports them because patch a0 removed the archive's cross
product. This run's auditor (aud-marks-1, 2026-11-13, at 09542040f) judged all 19 wrong, each against both entries;
the earlier auditor's finding is named where it judged the same pair.

| pair | reported by gov links | finding |
|---|---|---|
| DEC-853<-DEC-884 | yes | B (aud-marks-1, 2026-11-13); earlier F14 (reviews/w2-130-marks.md part 2) |
| DEC-1050<-DEC-1057 | yes | B (aud-marks-1, 2026-11-13); earlier F1 (reviews/w2-130-marks.md part 1) |
| DEC-120<-DEC-173 | yes | B (aud-marks-1, 2026-11-13); earlier F2 (reviews/w2-130-marks.md part 1) |
| DEC-724<-DEC-860 | yes | B (aud-marks-1, 2026-11-13); earlier F3 (reviews/w2-130-marks.md part 1) |
| DEC-056<-DEC-017 | yes | B (aud-marks-1, 2026-11-13) |
| DEC-072<-DEC-064 | yes | B (aud-marks-1, 2026-11-13) |
| DEC-162<-DEC-156 | yes | B (aud-marks-1, 2026-11-13) |
| DEC-1053<-DEC-880 | yes | B (aud-marks-1, 2026-11-13) |
| DEC-454<-DEC-904 | no | C (aud-marks-1, 2026-11-13); earlier F4 (reviews/w2-130-marks.md part 1) |
| DEC-455<-DEC-904 | no | C (aud-marks-1, 2026-11-13); earlier F4 (reviews/w2-130-marks.md part 1) |
| DEC-480<-DEC-899 | no | C (aud-marks-1, 2026-11-13); earlier F4 (reviews/w2-130-marks.md part 1) |
| DEC-480<-DEC-904 | no | C (aud-marks-1, 2026-11-13); earlier F4 (reviews/w2-130-marks.md part 1) |
| DEC-490<-DEC-868 | no | C (aud-marks-1, 2026-11-13); earlier F4 (reviews/w2-130-marks.md part 1) |
| DEC-490<-DEC-899 | no | C (aud-marks-1, 2026-11-13); earlier F4 (reviews/w2-130-marks.md part 1) |
| DEC-490<-DEC-908 | no | C (aud-marks-1, 2026-11-13); earlier F4 (reviews/w2-130-marks.md part 1) |
| DEC-492<-DEC-904 | no | C (aud-marks-1, 2026-11-13); earlier F4 (reviews/w2-130-marks.md part 1) |
| DEC-492<-DEC-908 | no | C (aud-marks-1, 2026-11-13); earlier F4 (reviews/w2-130-marks.md part 1) |
| DEC-780<-DEC-775 | no | C (aud-marks-1, 2026-11-13) |
| DEC-501<-DEC-512 | no | C (aud-marks-1, 2026-11-13) |

```yaml w2-130:judged-wrong
- changed: DEC-853
  changer: DEC-884
  verdict: 'wrong: stays unmarked (DEC-884 confirms it)'
  finding: B (aud-marks-1, 2026-11-13); earlier F14 (reviews/w2-130-marks.md part 2)
  in_gov_links: true
- changed: DEC-1050
  changer: DEC-1057
  verdict: 'wrong: stays unmarked (the subject is DEC-991; DEC-1050 is cited as the one that corrects it)'
  finding: B (aud-marks-1, 2026-11-13); earlier F1 (reviews/w2-130-marks.md part 1)
  in_gov_links: true
- changed: DEC-120
  changer: DEC-173
  verdict: 'wrong: stays unmarked (the row''s subject is DEC-172, already marked)'
  finding: B (aud-marks-1, 2026-11-13); earlier F2 (reviews/w2-130-marks.md part 1)
  in_gov_links: true
- changed: DEC-724
  changer: DEC-860
  verdict: 'wrong: stays unmarked (the rule is DEC-861''s)'
  finding: B (aud-marks-1, 2026-11-13); earlier F3 (reviews/w2-130-marks.md part 1)
  in_gov_links: true
- changed: DEC-056
  changer: DEC-017
  verdict: 'wrong: stays unmarked (the subject is the code adapter)'
  finding: B (aud-marks-1, 2026-11-13)
  in_gov_links: true
- changed: DEC-072
  changer: DEC-064
  verdict: 'wrong: stays unmarked (the subject is S0a''s Q4; the changer is older)'
  finding: B (aud-marks-1, 2026-11-13)
  in_gov_links: true
- changed: DEC-162
  changer: DEC-156
  verdict: 'wrong: stays unmarked (the subject is DEC-150; the changer is older)'
  finding: B (aud-marks-1, 2026-11-13)
  in_gov_links: true
- changed: DEC-1053
  changer: DEC-880
  verdict: 'wrong: stays unmarked (the subject is W2-48''s cache; the changer is older)'
  finding: B (aud-marks-1, 2026-11-13)
  in_gov_links: true
- changed: DEC-454
  changer: DEC-904
  verdict: 'wrong: stays unmarked'
  finding: C (aud-marks-1, 2026-11-13); earlier F4 (reviews/w2-130-marks.md part 1)
  in_gov_links: false
- changed: DEC-455
  changer: DEC-904
  verdict: 'wrong: stays unmarked'
  finding: C (aud-marks-1, 2026-11-13); earlier F4 (reviews/w2-130-marks.md part 1)
  in_gov_links: false
- changed: DEC-480
  changer: DEC-899
  verdict: 'wrong: stays unmarked'
  finding: C (aud-marks-1, 2026-11-13); earlier F4 (reviews/w2-130-marks.md part 1)
  in_gov_links: false
- changed: DEC-480
  changer: DEC-904
  verdict: 'wrong: stays unmarked'
  finding: C (aud-marks-1, 2026-11-13); earlier F4 (reviews/w2-130-marks.md part 1)
  in_gov_links: false
- changed: DEC-490
  changer: DEC-868
  verdict: 'wrong: stays unmarked'
  finding: C (aud-marks-1, 2026-11-13); earlier F4 (reviews/w2-130-marks.md part 1)
  in_gov_links: false
- changed: DEC-490
  changer: DEC-899
  verdict: 'wrong: stays unmarked'
  finding: C (aud-marks-1, 2026-11-13); earlier F4 (reviews/w2-130-marks.md part 1)
  in_gov_links: false
- changed: DEC-490
  changer: DEC-908
  verdict: 'wrong: stays unmarked'
  finding: C (aud-marks-1, 2026-11-13); earlier F4 (reviews/w2-130-marks.md part 1)
  in_gov_links: false
- changed: DEC-492
  changer: DEC-904
  verdict: 'wrong: stays unmarked'
  finding: C (aud-marks-1, 2026-11-13); earlier F4 (reviews/w2-130-marks.md part 1)
  in_gov_links: false
- changed: DEC-492
  changer: DEC-908
  verdict: 'wrong: stays unmarked'
  finding: C (aud-marks-1, 2026-11-13); earlier F4 (reviews/w2-130-marks.md part 1)
  in_gov_links: false
- changed: DEC-780
  changer: DEC-775
  verdict: 'wrong: stays unmarked'
  finding: C (aud-marks-1, 2026-11-13)
  in_gov_links: false
- changed: DEC-501
  changer: DEC-512
  verdict: 'wrong: stays unmarked'
  finding: C (aud-marks-1, 2026-11-13)
  in_gov_links: false
```

**The two follow-up marks.** DEC-1115<-DEC-1122 and DEC-026<-DEC-086 were the two UNMARKED_CHANGE left besides the
8 after c4420040f. `gov links --propose-marks` proposed `**Changed by:** DEC-1122 (4)` and `**Changed by:** DEC-086`
(patch-marks-3, at bce798c3a's parent). The auditor judged both right and corrected their parts (F1: "(4)" is
DEC-1115's item, so the mark names DEC-1122 (2) with item (4) in words; F2: DEC-086 settles DEC-026 "for Wave 1").
bce798c3a commits them in the corrected texts, after the check (2026-11-13T22:46:14Z, at 09542040f, an ancestor).

**The drift count (S2).** `docs/research/W2-92-proto-drift.py`'s definitions, applied to the entries' own text
(no store): 6 pairs at the last clean-up commit, every one of them a pair the auditor judged wrong,
so the count after setting them aside is 0. None of the sitting's group C, D or E ids is current, so none is counted.

```python w2-130:drift
"""W2-130 S2: the drift count by docs/research/W2-92-proto-drift.py's definitions, read from the entries' own text.

Run from the repository's root as `python3 -` (this script on stdin); no store is read and nothing is written.
The definitions are W2-92-proto-drift.py's (the census's, D4B-link-census.py at 3d1c459e): a statement is a register
label, its free text or the change log (loader.register_statements) or an ARCHIVE-SUPERSEDED §A line read with the
same patterns; a decision is current when its status is ACCEPTED and no SUPERSEDES edge targets it (the records and
edges read from HEAD by the loader's own rule, as the script's --from-head does); a decision ARCHIVE-SUPERSEDED §B
calls spent is left out (DEC-1073 (2)); a decision not ACCEPTED is never current. A drift pair is (changed, changer):
the changed decision current and stated changed (supersede or amend) by the changer, and its own status line (the
first line under its heading, the loader's `first`) not naming the changer's id (the rule `gov links` marks by,
src/gov/links/check.py; the census's "status line marks" read per changer).
Prints one JSON object {"drift": [{"changed", "changer"}...], "count": n}.
"""
import collections
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "src"))
from gov.store import loader  # noqa: E402

DEC = re.compile(r"\bDEC-(\d{3,})\b")
ARCHIVE = "governance/project/orchestration/ARCHIVE-SUPERSEDED.md"

rows, edge_rows, _, _, _, _ = loader._read_records(ROOT)
rec = {rid: {"type": kind, "status": status} for _, rid, kind, status in rows}
superseded_edges = {d for t, s, d in edge_rows if t == "SUPERSEDES"}

reg_rel = yaml.safe_load((ROOT / loader.PATH_MAP_REL).read_text())[loader.REGISTER_KEY]
reg_text = (ROOT / reg_rel).read_text()
entries, _ = loader.register_entries(reg_text)
entry = {e["id"]: e for e in entries}
said = loader.register_statements(reg_text, entries)
BY, vclass = loader._BY, loader._verb_class

arch_stmt, arch_spent = [], set()
if (ROOT / ARCHIVE).is_file():
    text = (ROOT / ARCHIVE).read_text()
    for line in text.split("## B.", 1)[-1].split("\n"):
        if line.startswith("- DEC-") and re.search(r"\bSpent\b|\bspent\b", line):
            arch_spent |= {"DEC-" + x for x in DEC.findall(line[2:].split(":")[0])}
    for line in text.split("## B.")[0].split("\n"):
        if not line.startswith("- DEC-"):
            continue
        head_, _, tail = line[2:].partition(":")
        for b in BY.finditer(tail):
            for t in DEC.findall(head_):
                for y in DEC.findall(b.group(2)):
                    arch_stmt.append({"source": "DEC-" + y, "target": "DEC-" + t, "cls": vclass(b.group(1))})


def current(t):
    r = rec.get(t)
    return bool(r) and r["status"] == "ACCEPTED" and t not in superseded_edges


changers = collections.defaultdict(set)
for s in said + arch_stmt:
    if s["cls"] in ("supersede", "amend") and s["target"] in entry and current(s["target"]):
        changers[s["target"]].add(s["source"])
for t in [t for t in changers if t in arch_spent]:
    del changers[t]


def status_line(t):
    lines = entry[t]["span"].split("\n") if "span" in entry[t] else []
    first = entry[t].get("first") or next((ln for ln in lines if ln.startswith("- **Status:**")), "")
    return first.split("\n")[0]


def names(line, changer):
    return re.search(rf"\b{changer}(?![0-9])", line) is not None


key = lambda x: int(x[4:])  # noqa: E731
drift = [{"changed": t, "changer": c} for t in sorted(changers, key=key) for c in sorted(changers[t], key=key)
         if not names(status_line(t), c)]
print(json.dumps({"drift": drift, "count": len(drift)}))
```

```yaml w2-130:drift-run
head: 57cbacfbfc861eb982cf08b6aebb3c699171a1de
command: python3 - < (the w2-130:drift block), cwd a clone of the repository at head
output:
  drift:
  - changed: DEC-072
    changer: DEC-064
  - changed: DEC-120
    changer: DEC-173
  - changed: DEC-162
    changer: DEC-156
  - changed: DEC-724
    changer: DEC-860
  - changed: DEC-1050
    changer: DEC-1057
  - changed: DEC-1053
    changer: DEC-880
  count: 6
set_aside:
- changed: DEC-072
  changer: DEC-064
- changed: DEC-120
  changer: DEC-173
- changed: DEC-162
  changer: DEC-156
- changed: DEC-724
  changer: DEC-860
- changed: DEC-1050
  changer: DEC-1057
- changed: DEC-1053
  changer: DEC-880
count_after_set_aside: 0
```

## 4. The independent check of the marks (S3, F3)

Each marks commit was checked by an independent auditor before it was made, at a head that is its ancestor:

- **e12f8a30c** (a1, a2): the auditor's review part 1 (`reviews/w2-130-marks.md`), at 2f9c80b1f, verdict written
  2026-11-08T01:35:59Z; the commit is 2026-11-08T01:39:21Z. Every free-text mark (19: 8 committed, 11 dropped as
  wrong) was read by hand against both entries; every labelled mark (132) was checked by script against the
  changer's own label. 12 marks were dropped (F1 to F4) and four parts rewritten (F4, F5) before the commit.
- **c4420040f** (f1's ruled marks, f5): the review's part 2, at ce7f10eb8a2a, verdict written 2026-11-09T00:41:51Z;
  the commit is 2026-11-09T00:42:54Z. f5's 17 marks were each checked against the changer's text (one dropped,
  F14: DEC-853<-DEC-884); the 13 group B ruling marks were checked against the rulings; DEC-786<-DEC-942 and
  DEC-927<-DEC-1057 as appends.
- **bce798c3a** (the two follow-up marks): this run's auditor (aud-marks-1), at 09542040f, 2026-11-13T22:46:14Z;
  the commit is 2026-11-13T23:29:46Z.

In `audits`, `free_text` is every mark `gov links` (this tree's tool) flags as derived from free text on the
commit's register with its marks taken off, and every free-text mark the auditor dropped. `labelled` is 20 marks
drawn by the stated seed from the labelled marks the auditor judged (the draw is stated in `draw`), or every
labelled mark where the commit adds 20 or fewer. `also_judged` holds the auditor's other rulings that the draw did
not reach. A wrong mark's fate is `dropped`; a right mark whose part the auditor rewrote is `committed` with the
committed text.

```yaml w2-130:audits
- commit: e12f8a30ca7dbbf470396f9e2ac9edd68a2aa968
  audit_head: 2f9c80b1f80747f26507093551fd4da5e5eccc0f
  audit_date: '2026-11-08T01:35:59+00:00'
  audit_source: the independent auditor's review, part 1 (.gov-runtime/scratch/orchestrator/reviews/w2-130-marks.md; session ad44f5fe, subagent agent-abeeaeb52fe9d7a0a, verdict first written 2026-11-08T01:35:59Z), which checked every free-text mark by hand and every labelled mark by script against the changer's own label
  seed: 1302
  draw: 'random.Random(1302).sample(sorted(pool), 20); pool: the 132 labelled marks the auditor checked for a1 and a2, as ''DEC-a<-DEC-b'' strings (e12f8a30c''s 131 committed labelled marks and DEC-1050<-DEC-1057, dropped by F1); also_judged: the auditor''s other rulings on labelled marks (F1, F5) not drawn'
  free_text:
  - changed: DEC-090
    changer: DEC-741
    mark: '**Changed by:** DEC-741'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-741'
  - changed: DEC-1066
    changer: DEC-1067
    mark: '**Changed by:** DEC-1067 (2)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-1067 (2)'
  - changed: DEC-261
    changer: DEC-1033
    mark: '**Changed by:** DEC-1033'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-1033'
  - changed: DEC-421
    changer: DEC-572
    mark: '**Changed by:** DEC-572'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-572'
  - changed: DEC-454
    changer: DEC-868
    mark: '**Changed by:** DEC-868'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-868 (items 1 (b) and 3), DEC-899 (P-IS-4 (a))'
  - changed: DEC-454
    changer: DEC-899
    mark: '**Changed by:** DEC-899'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-868 (items 1 (b) and 3), DEC-899 (P-IS-4 (a))'
  - changed: DEC-455
    changer: DEC-899
    mark: '**Changed by:** DEC-899'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-899 (P-IS-4 (a))'
  - changed: DEC-709
    changer: DEC-719
    mark: '**Changed by:** DEC-719'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-719'
  - changed: DEC-120
    changer: DEC-173
    mark: '**Changed by:** DEC-173'
    verdict: wrong
    fate: dropped
    finding: F2
  - changed: DEC-724
    changer: DEC-860
    mark: '**Changed by:** DEC-860'
    verdict: wrong
    fate: dropped
    finding: F3
  - changed: DEC-454
    changer: DEC-904
    mark: '**Changed by:** DEC-904'
    verdict: wrong
    fate: dropped
    finding: F4
  - changed: DEC-455
    changer: DEC-904
    mark: '**Changed by:** DEC-904'
    verdict: wrong
    fate: dropped
    finding: F4
  - changed: DEC-480
    changer: DEC-899
    mark: '**Changed by:** DEC-899'
    verdict: wrong
    fate: dropped
    finding: F4
  - changed: DEC-480
    changer: DEC-904
    mark: '**Changed by:** DEC-904'
    verdict: wrong
    fate: dropped
    finding: F4
  - changed: DEC-490
    changer: DEC-868
    mark: '**Changed by:** DEC-868'
    verdict: wrong
    fate: dropped
    finding: F4
  - changed: DEC-490
    changer: DEC-899
    mark: '**Changed by:** DEC-899'
    verdict: wrong
    fate: dropped
    finding: F4
  - changed: DEC-490
    changer: DEC-908
    mark: '**Changed by:** DEC-908'
    verdict: wrong
    fate: dropped
    finding: F4
  - changed: DEC-492
    changer: DEC-904
    mark: '**Changed by:** DEC-904'
    verdict: wrong
    fate: dropped
    finding: F4
  - changed: DEC-492
    changer: DEC-908
    mark: '**Changed by:** DEC-908'
    verdict: wrong
    fate: dropped
    finding: F4
  labelled:
  - changed: DEC-973
    changer: DEC-1049
    mark: '**Changed by:** DEC-1049 (the nightly at 04:00, its 08:00 check)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-1049 (the nightly at 04:00, its 08:00 check)'
  - changed: DEC-121
    changer: DEC-127
    mark: '**Changed by:** DEC-127 (its fallback)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-127 (its fallback)'
  - changed: DEC-991
    changer: DEC-1057
    mark: '**Changed by:** DEC-1057'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-1050, DEC-1057'
  - changed: DEC-957
    changer: DEC-1052
    mark: '**Changed by:** DEC-1052'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-1052'
  - changed: DEC-966
    changer: DEC-1045
    mark: '**Changed by:** DEC-1045 (item 4)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-1045 (item 4)'
  - changed: DEC-365
    changer: DEC-407
    mark: '**Changed by:** DEC-407 ("unset `GOV_ROLE` is the owner")'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-402, DEC-407 ("unset `GOV_ROLE` is the owner"), DEC-409'
  - changed: DEC-1070
    changer: DEC-1071
    mark: '**Changed by:** DEC-1071'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-1071'
  - changed: DEC-968
    changer: DEC-1049
    mark: '**Changed by:** DEC-1049 (1)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-1049 (1)'
  - changed: DEC-1069
    changer: DEC-1070
    mark: '**Changed by:** DEC-1070'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-1070'
  - changed: DEC-304
    changer: DEC-310
    mark: '**Changed by:** DEC-310'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-310'
  - changed: DEC-723
    changer: DEC-820
    mark: '**Changed by:** DEC-820'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-820'
  - changed: DEC-949
    changer: DEC-1057
    mark: '**Changed by:** DEC-1057'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-1057, DEC-973'
  - changed: DEC-1049
    changer: DEC-1050
    mark: '**Changed by:** DEC-1050 (widened)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-1050 (widened)'
  - changed: DEC-933
    changer: DEC-1049
    mark: '**Changed by:** DEC-1049 (item 2)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-1049 (item 2)'
  - changed: DEC-157
    changer: DEC-209
    mark: '**Changed by:** DEC-209'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-209'
  - changed: DEC-093
    changer: DEC-220
    mark: '**Changed by:** DEC-220 (which packages reach the owner)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-220 (which packages reach the owner)'
  - changed: DEC-971
    changer: DEC-1001
    mark: '**Changed by:** DEC-1001 (item 5)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-1001 (item 5)'
  - changed: DEC-107
    changer: DEC-117
    mark: '**Changed by:** DEC-117'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-117'
  - changed: DEC-511
    changer: DEC-522
    mark: '**Changed by:** DEC-522 (its expiry)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-1057 (lifted: no committed `gov checkpoint` record per round, R-6), DEC-522 (its expiry)'
  - changed: DEC-376
    changer: DEC-395
    mark: '**Changed by:** DEC-395'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-395'
  also_judged:
  - changed: DEC-1050
    changer: DEC-1057
    mark: '**Changed by:** DEC-1057 (8)'
    verdict: wrong
    fate: dropped
    finding: F1
  - changed: DEC-1084
    changer: DEC-1087
    mark: '**Changed by:** DEC-1087 (W2-33''s layer lines moved to Wave 3, W3-P23: reversed by (13)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-1087 (13) (W2-33''s layer lines back in Wave 2)'
    finding: F5 (part rewritten)
  - changed: DEC-941
    changer: DEC-946
    mark: '**Changed by:** DEC-946 (item 6))'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-946 (blocks A to E: their order)'
    finding: F5 (part rewritten)
  - changed: DEC-988
    changer: DEC-989
    mark: '**Changed by:** DEC-989 (items)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-989 (item 3''s baseline)'
    finding: F5 (part rewritten, should)
  - changed: DEC-1032
    changer: DEC-1033
    mark: '**Changed by:** DEC-1033 (items)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-1033 (items 2 and 3)'
    finding: F5 (part rewritten, should)
  labelled_all_checked: every one of the 132 labelled marks checked by script for the changer's own label naming the marked entry (part 1, 'What I checked'); F1 dropped one, F5 rewrote three parts
- commit: c4420040f9b31403d05c8a035d385edd1d6fcc76
  audit_head: ce7f10eb8a2aead2f345c72879fc072d458ecaaf
  audit_date: '2026-11-09T00:41:51+00:00'
  audit_source: the independent auditor's review, part 2 'Final patches' (.gov-runtime/scratch/orchestrator/reviews/w2-130-marks.md; same session and subagent, verdict first written 2026-11-09T00:41:51Z)
  seed: 1302
  draw: 'random.Random(1302).sample(sorted(pool), 20); pool: every labelled mark the auditor judged for c4420040f, as ''DEC-a<-DEC-b'' strings (30: f5''s 16 labelled, the 13 group B ruling marks less DEC-024<-DEC-074, DEC-786<-DEC-942, DEC-927<-DEC-1057); the other 10 are in also_judged'
  free_text:
  - changed: DEC-024
    changer: DEC-074
    mark: '**Changed by:** DEC-074'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-074 (Q5)'
    basis: a group B ruling's mark (DEC-1098 (3)), applied as the ruling names it
  - changed: DEC-761
    changer: DEC-772
    mark: '**Changed by:** DEC-772 (item 1)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-772 (item 1)'
    basis: 'the free-text f5 mark: "This replaces DEC-761 item 1''s line"'
  labelled:
  - changed: DEC-899
    changer: DEC-924
    mark: '**Changed by:** DEC-924'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-902 (item 10: the proposal decided), DEC-912 (item 2), DEC-918 (item 4), DEC-924, DEC-925 (item 4)'
  - changed: DEC-721
    changer: DEC-953
    mark: '**Changed by:** DEC-953'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-953'
  - changed: DEC-017
    changer: DEC-074
    mark: '**Changed by:** DEC-074 (R1)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-074 (R1)'
  - changed: DEC-884
    changer: DEC-918
    mark: '**Changed by:** DEC-918'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-918, DEC-921 (item 3)'
  - changed: DEC-786
    changer: DEC-942
    mark: '**Changed by:** DEC-942'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-942'
  - changed: DEC-044
    changer: DEC-096
    mark: '**Changed by:** DEC-096'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-096'
  - changed: DEC-899
    changer: DEC-912
    mark: '**Changed by:** DEC-912 (item 2)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-902 (item 10: the proposal decided), DEC-912 (item 2), DEC-918 (item 4), DEC-924, DEC-925 (item 4)'
  - changed: DEC-899
    changer: DEC-918
    mark: '**Changed by:** DEC-918 (item 4)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-902 (item 10: the proposal decided), DEC-912 (item 2), DEC-918 (item 4), DEC-924, DEC-925 (item 4)'
  - changed: DEC-853
    changer: DEC-884
    mark: '**Changed by:** DEC-884 (item 4)'
    verdict: wrong
    fate: dropped
    finding: F14
  - changed: DEC-034
    changer: DEC-080
    mark: '**Changed by:** DEC-080 · **Changed by:** DEC-396'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-080 · **Changed by:** DEC-396'
  - changed: DEC-899
    changer: DEC-925
    mark: '**Changed by:** DEC-925 (item 4)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-902 (item 10: the proposal decided), DEC-912 (item 2), DEC-918 (item 4), DEC-924, DEC-925 (item 4)'
  - changed: DEC-927
    changer: DEC-1057
    mark: '**Changed by:** DEC-1057 (item 2)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-1057 (item 2)'
  - changed: DEC-914
    changer: DEC-916
    mark: '**Changed by:** DEC-916 (item 4)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-916 (item 4)'
  - changed: DEC-884
    changer: DEC-921
    mark: '**Changed by:** DEC-921 (item 3)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-918, DEC-921 (item 3)'
  - changed: DEC-033
    changer: DEC-080
    mark: '**Changed by:** DEC-080'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-080'
  - changed: DEC-037
    changer: DEC-080
    mark: '**Changed by:** DEC-080'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-080'
  - changed: DEC-032
    changer: DEC-080
    mark: '**Changed by:** DEC-080'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-080'
  - changed: DEC-896
    changer: DEC-1057
    mark: '**Changed by:** DEC-1057 (item 2)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-1057 (item 2)'
  - changed: DEC-007
    changer: DEC-075
    mark: '**Changed by:** DEC-075'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-075'
  - changed: DEC-040
    changer: DEC-083
    mark: '**Changed by:** DEC-083 (installs: owner approval per tool)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-083 (installs: owner approval per tool)'
  also_judged:
  - changed: DEC-005
    changer: DEC-085
    mark: '**Changed by:** DEC-085 (readiness reduction)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-085 (readiness reduction)'
  - changed: DEC-016
    changer: DEC-074
    mark: '**Changed by:** DEC-074 (R1)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-074 (R1)'
  - changed: DEC-031
    changer: DEC-080
    mark: '**Changed by:** DEC-080'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-080'
  - changed: DEC-034
    changer: DEC-396
    mark: '**Changed by:** DEC-396'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-080 · **Changed by:** DEC-396'
  - changed: DEC-035
    changer: DEC-080
    mark: '**Changed by:** DEC-080 (numbers stay placeholders)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-080 (numbers stay placeholders)'
  - changed: DEC-036
    changer: DEC-080
    mark: '**Changed by:** DEC-080'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-080'
  - changed: DEC-042
    changer: DEC-083
    mark: '**Changed by:** DEC-083 (MR-3 for every task)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-083 (MR-3 for every task)'
  - changed: DEC-891
    changer: DEC-924
    mark: '**Changed by:** DEC-924'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-924'
  - changed: DEC-897
    changer: DEC-909
    mark: '**Changed by:** DEC-909 (item 1)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-909 (item 1)'
  - changed: DEC-899
    changer: DEC-902
    mark: '**Changed by:** DEC-902 (items)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-902 (item 10: the proposal decided), DEC-912 (item 2), DEC-918 (item 4), DEC-924, DEC-925 (item 4)'
- commit: bce798c3a9113544daca5effee9d602080b64741
  audit_head: 09542040f7c66260cba26e5e62a251cf602da9be
  audit_date: '2026-11-13T22:46:14+00:00'
  audit_source: this run's independent auditor (session d51ff894-0d36-4511-87bf-05ca51f1a74a, aud-marks-1, verdict block dated 2026-11-13T22:46:14+00:00 at 09542040f)
  seed: null
  free_text: []
  labelled:
  - changed: DEC-026
    changer: DEC-086
    mark: '**Changed by:** DEC-086'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-086 (for Wave 1)'
    finding: F2 (part named)
  - changed: DEC-1115
    changer: DEC-1122
    mark: '**Changed by:** DEC-1122 (4)'
    verdict: right
    fate: committed
    committed_mark: '**Changed by:** DEC-1122 (2) (item (4): its 80 % trigger brought forward to now, until the weekly reset)'
    finding: F1 (part corrected)
```

**The comparison** of each marks commit's diff with the check: 0 committed free-text marks unchecked, 0 committed
marks judged wrong.

```yaml w2-130:comparison
e12f8a30ca7dbbf470396f9e2ac9edd68a2aa968:
  unchecked: 0
  wrong: 0
  committed_marks: 139
  free_text_committed: 8
c4420040f9b31403d05c8a035d385edd1d6fcc76:
  unchecked: 0
  wrong: 0
  committed_marks: 31
  free_text_committed: 2
bce798c3a9113544daca5effee9d602080b64741:
  unchecked: 0
  wrong: 0
  committed_marks: 2
  free_text_committed: 0
```

**The patches** e12f8a30c applied, as the drafts' builder printed them for the commit (`drafts/w2-130/`): a0
changes the archive only; a1 (99 marks on 81 entries) and a2 (40 on 35) are the register's marks after the
auditor's drops and rewrites (the builder took them as inputs; the patches it printed before the audit, 100 and 51
marks, were not kept); b1 is the 50 tickets' `sources:`. Their marks equal e12f8a30c's marks exactly.

```diff w2-130:patch-a0
diff --git a/governance/project/orchestration/ARCHIVE-SUPERSEDED.md b/governance/project/orchestration/ARCHIVE-SUPERSEDED.md
--- a/governance/project/orchestration/ARCHIVE-SUPERSEDED.md
+++ b/governance/project/orchestration/ARCHIVE-SUPERSEDED.md
@@ -31,7 +31,11 @@
 - DEC-365, DEC-407: their ancestry rule replaced by DEC-409.
 - DEC-410: changed by DEC-918.
 - DEC-448: its one-off limit superseded by DEC-477.
-- DEC-454, DEC-455, DEC-480, DEC-490, DEC-492: changed by DEC-868, DEC-899, DEC-904 and DEC-908. Their close parts are now lifted (LIFTED §A).
+- DEC-454: changed by DEC-868, DEC-899 and DEC-908. Its close parts are now lifted (LIFTED §A).
+- DEC-455: changed by DEC-868, DEC-899 and DEC-908. Its close parts are now lifted (LIFTED §A).
+- DEC-480: changed by DEC-868 and DEC-908. Its close parts are now lifted (LIFTED §A).
+- DEC-490: changed by DEC-904. Its close parts are now lifted (LIFTED §A).
+- DEC-492: changed by DEC-868 and DEC-899. Its close parts are now lifted (LIFTED §A).
 - DEC-460: its cause corrected by DEC-840, and its model replaced by DEC-839.
 - DEC-466: every close through `gov close` and `gov check` as a blocking gate. SUPERSEDED by DEC-953 item 1 (LIFTED §A).
 - DEC-493: changed by DEC-896 item 2 and DEC-903 (the overlay holds the test map).
```

```diff w2-130:patch-a1
diff --git a/docs/DECISION_REGISTER.md b/docs/DECISION_REGISTER.md
--- a/docs/DECISION_REGISTER.md
+++ b/docs/DECISION_REGISTER.md
@@ -233,7 +233,7 @@
 ## 4. Retrieval decisions
 
 ### DEC-030 — Retrieval completeness principle
-- **Status:** ACCEPTED · **Basis:** OWNER
+- **Status:** ACCEPTED · **Basis:** OWNER · **Changed by:** DEC-080
 - **Decision:** A top-k or per-query token allowance (e.g. 8k) is a batch size, not an evidence-completeness limit. Retrieval supports multiple batches, pagination/continuation, facets, adaptive follow-up, multi-hop, provenance-preserving merge, deduplication, authority/current/superseded filtering, and an explicit stopping reason. Parallel facet retrieval → merge/filter → unresolved dependencies → sequential follow-up → repeat → bounded context compilation. Evidence larger than one packet uses hierarchical synthesis whose notes are derived, cited, lineage-preserving, disclose unresolved evidence, and are rebuildable.
 - **Gates extended:** D2, D3, C9, W4, W10
 
@@ -299,7 +299,7 @@
 - **Revisit trigger:** the assembled Gov OS needs a component the Rust code already provides (e.g. SRR release signing at R2, a `gov` binary behind API-0002).
 
 ### DEC-039 — Threat model: the Gov OS guards against mistakes and drift, not a same-privilege adversary
-- **Status:** ACCEPTED (owner, 2026-09-29); to be written as ADR-0001 · **Basis:** ESTABLISHED (owner's own Phase-2 finding) + SUGGESTION
+- **Status:** ACCEPTED (owner, 2026-09-29); to be written as ADR-0001 · **Basis:** ESTABLISHED (owner's own Phase-2 finding) + SUGGESTION · **Changed by:** DEC-075
 - **Decision:** The Gov OS's purpose is to keep agents accurate, bounded and traceable. It does **not** attempt to be a security boundary against a process running with the owner's OS privileges. The hard boundary is: git history, CI on a protected branch, and owner-signed approvals (signed commits/tags or PR approval by the owner's account). This is ADR-0001 of the new repository.
 - **Rationale:** Phase 2's eight-round loop was an attempt to make a same-privilege process secure against itself; the repository's own records identify this as the confused-deputy / ambient-authority problem and concede the seal is not proof-grade.
 - **Consequence:** No in-process trust classes beyond the simple rule inherited from D-0007 (DEC-046).
@@ -450,7 +450,7 @@
 - These rules go verbatim into Charter v5 and apply to the Gov OS's own development from S1.
 
 ### DEC-066 — Organisation layer and the five distinct functions
-- **Status:** ACCEPTED (owner, 2026-09-29) · **Basis:** OWNER + SUGGESTION (mechanism)
+- **Status:** ACCEPTED (owner, 2026-09-29) · **Basis:** OWNER + SUGGESTION (mechanism) · **Changed by:** DEC-094 (Wave 2 roster)
 - **Decision:** Roles are subagent definitions generated by rulesync from kernel role files plus a project roster; each carries purpose, allowed-path pattern, tools, model tier, authority level and handoff format. Wave 1: orchestrator, product/specification, independent test designer, engineer, independent auditor. Wave 2: architecture, frontend, backend, database/data, integration/API, DevOps/SRE, security, performance, UX, typed handoffs. Wave 3: research, AI/ML, data author, change controller, memory/knowledge, tooling, release, claims/concurrency. `gov doctor` (installation health), discovery skill + `gov readiness`, `gov impact` (CIT-P), OpenSpec apply/archive + `gov close` (CIT-E), and the audit skill with an Independent Auditor role are separate.
 
 ### DEC-067 — Two layers of testing; Gate V returns as qualification
@@ -466,7 +466,7 @@
 - **Decision:** Acceptance tests live under `tests/acceptance/` and are written only by the Independent Test Designer role from the task's KPIs and the specification. The implementer role's allowed paths never include them (default-deny guard, DEC-041). An implementation task becomes READY only when its acceptance tests exist. `gov close` runs them.
 
 ### DEC-070 — Independent fidelity audit of the successor documents, and audit at every wave exit
-- **Status:** ACCEPTED (owner, 2026-09-29) · **Basis:** OWNER, implementing MR-4
+- **Status:** ACCEPTED (owner, 2026-09-29) · **Basis:** OWNER, implementing MR-4 · **Changed by:** DEC-096
 - **Decision:** After S1 drafts Charter v5, Contract v4, ADR-0001 and ADR-0002, a fresh read-only Independent Auditor (S1-A) builds a traceability matrix: every clause of the originals and owner records maps to the carrying clause, or to its recorded disposition and the decision behind it. Rows are classed OK / MISSING / WEAKENED / CONTRADICTS / UNJUSTIFIED_DROP / SCOPE_CREEP. It checks that MR-1…MR-6 appear verbatim, that all 26 readiness dimensions are carried, and that nothing reintroduces same-privilege-adversary machinery. The yardstick is the originals **plus** the accepted decisions, so a recorded drop is not a defect. At most two audit→repair rounds; contested findings go to the owner as decision packages. `docs/source/` is archived only after S1-A closes. The same role audits each wave's output against Contract v4 at the wave's exit. Recorded in architecture v0.3 (MR-4, §2.5, §6.1, §7).
 
 ### DEC-071 — S0b1 complete (record of facts, 2026-09-29)
@@ -525,7 +525,7 @@
 - **Decision:** S1 is one session and one author (subagents only for mechanical extraction, counting and validation), running from `~/gov-os-workbench/s1/` with the Gov OS repository as an additional directory. It applies MR-1 and MR-6 to the Gov OS itself: it builds the Gov OS's own 26-dimension readiness table, asks the owner only what the sources don't answer, as ranked decision packages, and records the answers. It then writes Charter v5, Contract v4 (all 60 capabilities, with waves, acceptance checks, providers, sources and scenario ids), ADR-0001, ADR-0002, and the Wave 1 WBS as tickets with KPIs, roles and allowed paths. Everything goes on branch `s1/spec` of the Gov OS repository, and the register is committed as `docs/DECISION_REGISTER.md`. S1 does not push, merge, implement, or write acceptance tests (those are the Independent Test Designer's, MR-3).
 
 ### DEC-082 — How S1-A runs, and what closes S1
-- **Status:** ACCEPTED (owner, by running it) · **Basis:** SUGGESTION, implementing DEC-070
+- **Status:** ACCEPTED (owner, by running it) · **Basis:** SUGGESTION, implementing DEC-070 · **Changed by:** DEC-096
 - **Decision:** S1-A is a fresh, read-only session in `~/gov-os-workbench/s1a/`. It builds its own traceability matrix from the originals **before** looking at S1's source map. Its yardstick is the originals plus decisions whose status is ACCEPTED or DONE; PROPOSED entries justify nothing. Verdict: ACCEPT, ACCEPT_WITH_FINDINGS or REJECT, at most two rounds. After closure, the owner merges `s1/spec` into `main`; then `docs/source/` is archived (removed from the working tree, reachable through the tag); then Wave 1 starts.
 
 ## 5. Proposed Contract v3 amendments
@@ -742,7 +742,7 @@
 decision packages (round 1, asked 2026-09-30). They are the only changes to this file in S1.
 
 ### DEC-083 — PROPOSED decisions ratified for Charter v5 and Contract v4; DEC-040 amended (tool installs)
-- **Status:** ACCEPTED (owner, 2026-09-30) · **Basis:** OWNER, on S1 package P1-A option (a) with one amendment
+- **Status:** ACCEPTED (owner, 2026-09-30) · **Basis:** OWNER, on S1 package P1-A option (a) with one amendment · **Changed by:** DEC-163 (for the research role only)
 - **Accepted as written:** DEC-003, DEC-004, DEC-005 (readiness part as settled by DEC-085), DEC-006, DEC-010, DEC-011,
   DEC-012, DEC-014, DEC-015 (native LSP; Serena not adopted), DEC-022, DEC-023, DEC-025, DEC-026 (as settled by DEC-086),
   DEC-027, DEC-041, DEC-044, DEC-046, DEC-050, DEC-062.
@@ -825,7 +825,7 @@
   the generation with `gov readiness --generate`.
 
 ### DEC-090 — The adoption transaction A0–A11 in Contract v4
-- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on S1-A DP-3 option (b) · **Refines:** DEC-006
+- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on S1-A DP-3 option (b) · **Refines:** DEC-006 · **Changed by:** DEC-741
 - **Decision:** CAP-44 states A0–A11 with one evidence record per stage and the three final verdicts
   (ADOPTED_HEALTHY, ADOPTED_WITH_ACCEPTED_EXCEPTIONS, NOT_ADOPTED_HEALTHY). Wave 1 (`gov adopt --lite`) delivers A0–A4,
   A6 and A8 with a safety baseline and a rollback point per batch, **and A5**: an independent review of the path map
@@ -844,7 +844,7 @@
   dropped by the compression.
 
 ### DEC-093 — Decision packages: at most five at a time; P1 may bypass the cap
-- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on S1-A DP-6 option (a) with an addition
+- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on S1-A DP-6 option (a) with an addition · **Changed by:** DEC-220 (which packages reach the owner)
 - **Decision:** Decision packages are ranked P1–P3 and asked at most five at a time. A P1 package may bypass the cap.
 
 ### DEC-094 — Test execution and integration are distinct roles, added in Wave 2
@@ -981,7 +981,7 @@
 ticket's KPI text is unchanged. The acceptance tests at `43fdf41` cover KD-1…KD-5 and take no side on KD-6…KD-8.
 
 ### DEC-107 — W1-02 KD-1: how a session declares its role and ticket; the stricter of session and subagent applies
-- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-02 KPI dispute KD-1 · **Implements:** CAP-58.a, CAP-58.c
+- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-02 KPI dispute KD-1 · **Implements:** CAP-58.a, CAP-58.c · **Changed by:** DEC-117
 - **Decision:** A session declares its role and its active ticket through the environment variables `GOV_ROLE` and
   `GOV_TICKET`, set at session start. Inside a subagent, the hook input's `agent_type` identifies the subagent's role,
   and the guard applies the stricter of the session's role and the subagent's. A missing or unknown role means
@@ -1107,7 +1107,7 @@
 - **Verification:** the Auto-mode KPI is verified by driving the hook, and by one live headless attempt.
 
 ### DEC-121 — W1-04 KD-2: the tool-registry schema
-- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-04 KPI dispute KD-2
+- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-04 KPI dispute KD-2 · **Changed by:** DEC-127 (its fallback)
 - **Decision:** The test designer's recommended registry schema is accepted. If the test designer proposed none: one
   file, `governance/project/tool-registry.yaml`, listing entries with `id`, `version`, `source`, `sha256`,
   `install_command`, `uninstall_command`, `installed_at` and `decision` (the approving DEC), validated by a JSON Schema
@@ -1405,7 +1405,7 @@
 - DEC-161 limits which sessions are sandboxed; the closures hold for those sessions.
 
 ### DEC-153 — New Wave 1 tickets from EXP-001
-- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, S2 brief, on EVIDENCE §5.5 · **Under:** DEC-152
+- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, S2 brief, on EVIDENCE §5.5 · **Under:** DEC-152 · **Changed by:** DEC-209
 - **Decision:** Wave 1 gains three tickets:
   1. **The launcher** (`gov launch`, or equivalent). It builds per-role `--settings` (sandbox block plus role `Edit`
      deny rules), sets `GOV_ROLE` and `GOV_TICKET`, and refuses to start unless the sandbox is on, strict and
@@ -1427,14 +1427,14 @@
   repository root.
 
 ### DEC-156 — DP-7 corrected: the orchestrator may write anywhere except `tests/acceptance/**`
-- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, answer to S2 · **Amends:** DEC-150 (replaces its standing paths and commit rule)
+- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, answer to S2 · **Amends:** DEC-150 (replaces its standing paths and commit rule) · **Changed by:** DEC-165 (one path outside the repository), DEC-176, DEC-434 (as far as a ticket lead is concerned)
 - **Decision:** The orchestrator role may write anywhere in the repository except `tests/acceptance/**` (MR-3). The
   guard enforces only that exclusion for the orchestrator. Containment still records its changes. Its checkpoint goes
   to `.gov-runtime/scratch/orchestrator/` until W1-25. The orchestrator's interactive session (VS Code or terminal)
   is not sandboxed.
 
 ### DEC-157 — P-1: installs stay as DEC-083 decided
-- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on S2 package P-1, option (d), the owner's own · **Confirms:** DEC-083
+- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on S2 package P-1, option (d), the owner's own · **Confirms:** DEC-083 · **Changed by:** DEC-209
 - **Decision:** The orchestrator installs tools under DEC-083 as decided: the guard asks, and the owner approves in
   chat. Worker roles never install system-wide.
 
@@ -1637,7 +1637,7 @@
     change is its own commit, with the trailer `Task: DAEO-6cc2`.
 
 ### DEC-176 — DP-2: `.gov-runtime/` other than `scratch/**` stays denied to the orchestrator
-- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on W1-45 package DP-2 option (a) · **Amends:** DEC-156
+- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on W1-45 package DP-2 option (a) · **Amends:** DEC-156 · **Changed by:** DEC-365, DEC-402
 - **Decision:**
   - Everything under `.gov-runtime/` other than `scratch/**` stays denied to the orchestrator: the freeze flag, the
     snapshots, the findings and the records.
@@ -1674,7 +1674,7 @@
   - In general, a finding that makes the guard fail open is a defect, not a residual.
 
 ### DEC-180 — `.gov-runtime/` is protected in worker sessions by an `Edit` deny rule the launcher sets
-- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, at W1-45's close · **Extends:** DEC-176 · **Under:** DEC-152, DEC-161, EXP-001
+- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, at W1-45's close · **Extends:** DEC-176 · **Under:** DEC-152, DEC-161, EXP-001 · **Changed by:** DEC-311
 - **Decision:**
   - The settings the launcher builds for every worker role carry an `Edit` deny rule for `.gov-runtime/**` except
     `.gov-runtime/scratch/**`.
@@ -2056,7 +2056,7 @@
 points on W1-47 (`DAEO-o4fg`) and W1-08 (`DAEO-uudf`).
 
 ### DEC-220 — Delegated decisions
-- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER (orchestrator prompt v3, section 6) · **Under:** MR-6 · **Amends:** DEC-093 (which packages reach the owner)
+- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER (orchestrator prompt v3, section 6) · **Under:** MR-6 · **Amends:** DEC-093 (which packages reach the owner) · **Changed by:** DEC-416, DEC-974
 - **Decision:**
   - The orchestrator decides a package itself when all of these hold: it is P2 or P3; it is reversible; the
     orchestrator's recommendation and the proposer's (test designer, engineer, reviewer or product-spec worker)
@@ -2239,7 +2239,7 @@
 to DEC-242 answer the five open packages on W1-08 (`DAEO-uudf`) and W1-46 (`DAEO-jdqr`). DEC-243 accepts the digest.
 
 ### DEC-235 — Parallel tickets in Wave 1 (a light form of CAP-23)
-- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER (orchestrator prompt v4, section 3) · **Under:** CAP-23, DEC-076 · **Amends:** the Wave 3 placing of parallel work, for this light form only; DEC-183 (a worker starts in its ticket's worktree, not the repository root)
+- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER (orchestrator prompt v4, section 3) · **Under:** CAP-23, DEC-076 · **Amends:** the Wave 3 placing of parallel work, for this light form only; DEC-183 (a worker starts in its ticket's worktree, not the repository root) · **Changed by:** DEC-363
 - **Decision:**
   - Up to 6 tickets are in flight at once, each in its own short-lived worktree
     (`~/gov-os-worktrees/<W1-id>`, branch `w1/<W1-id>`, cut from `w1/integrate`). A ticket starts only when its
@@ -2301,7 +2301,7 @@
     behaviour (DEC-136).
 
 ### DEC-241 — W1-46 DP-5: the research allowlist file and its starting hosts
-- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-46 package DP-5 option (a) · **Under:** DEC-158, DEC-163, CAP-61.c
+- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-46 package DP-5 option (a) · **Under:** DEC-158, DEC-163, CAP-61.c · **Changed by:** DEC-316
 - **Decision:**
   - `governance/project/research-allowlist.yaml` extends the kernel default. The owner extends the list. That path
     is added to W1-46's `allowed_paths`, in its own commit with the trailer `Task: DAEO-jdqr`.
@@ -2409,7 +2409,7 @@
   - Findings follow the delegation rule (DEC-220); owner-level ones come to the owner.
 
 ### DEC-250 — Stops after W1-49 closes
-- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER · **Amends:** DEC-237, DEC-208 (the main orchestrator's `CONTEXT_CHECKPOINT` stop)
+- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER · **Amends:** DEC-237, DEC-208 (the main orchestrator's `CONTEXT_CHECKPOINT` stop) · **Changed by:** DEC-420 (one more stop)
 - **Decision:**
   - Until W1-49 closes, the `CONTEXT_CHECKPOINT` stop stays.
   - After W1-49 closes, the orchestrator stops only for owner-level decision packages (P1, and everything the
@@ -2528,7 +2528,7 @@
 checkpoint's path and its RESUME HERE section only), and the owner's answer may add one assertion.
 
 ### DEC-258 — W1-49 DP-1: what "ensures the checkpoint is current" means for a PreCompact hook
-- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-49 package DP-1 option (a) with measure (i); confidence medium-high on the option, medium on the 30 minutes · **Under:** DEC-248, CAP-37.g
+- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-49 package DP-1 option (a) with measure (i); confidence medium-high on the option, medium on the 30 minutes · **Under:** DEC-248, CAP-37.g · **Changed by:** DEC-264
 - **Decision:**
   - A hook can check and block; it cannot write the checkpoint's content. The checkpoint is current when its file
     is at most 30 minutes old.
@@ -2651,7 +2651,7 @@
   finding. A ticket is found by its `id` or its `wbs_id`, as the guard does.
 
 ### DEC-269 — W1-50 DP-6: a path the merge commit itself changes is judged by the merge commit's trailers
-- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-50 package DP-6 option (a); confidence medium-high · **Under:** DEC-255, DEC-156, DEC-253
+- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-50 package DP-6 option (a); confidence medium-high · **Under:** DEC-255, DEC-156, DEC-253 · **Changed by:** DEC-394 (refines "content a parent holds")
 - **Decision:** A path a merge commit changes beyond what its parents hold (a conflict resolution, a hand edit) is
   judged by the merge commit's own trailers, or against the caller when it has none. An orchestrator's conflict
   resolution under `tests/acceptance/**` is therefore a finding, and elsewhere it is not.
@@ -2835,7 +2835,7 @@
 the guard or containment. The suite on the branch already follows them.
 
 ### DEC-285 — W1-15 DP-1: the filter's interface, and how a check command is run
-- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-15 package DP-1 option (a); confidence medium-high on the function, medium on the check convention · **Under:** CAP-03.a, CAP-03.e, CAP-38.b
+- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-15 package DP-1 option (a); confidence medium-high on the function, medium on the check convention · **Under:** CAP-03.a, CAP-03.e, CAP-38.b · **Changed by:** DEC-1045
 - **Decision:**
   - The filter is the function `gov.secrets.indexable(root, paths)`: it takes the project root and a list of
     project-relative paths and returns, in order, the sub-list an indexer may read. It drops a file that holds a
@@ -2871,7 +2871,7 @@
   policy (W1-17 or W1-24). `bootstrap.md` is corrected at W1-15's close.
 
 ### DEC-290 — W1-15 DP-6: allowlists, and secrets inside a store
-- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-15 package DP-6, the lead's three recommendations; confidence medium · **Under:** CAP-03.a, CAP-38.b
+- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-15 package DP-6, the lead's three recommendations; confidence medium · **Under:** CAP-03.a, CAP-38.b · **Changed by:** DEC-1045
 - **Decision:**
   - The root `.gitleaks.toml` allowlists, by path, the tracked documents that only name the canary identifier (the
     ticket file, plan documents, this suite's README), after the engineer runs gitleaks over the tree and reports
@@ -2912,7 +2912,7 @@
     holder.
 
 ### DEC-293 — W1-09 DP-3: which acceptance tests folder makes a ticket READY
-- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 package DP-3 option (a); confidence high for the folder, medium for the classes · **Under:** DEC-069, CAP-31.c
+- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-09 package DP-3 option (a); confidence high for the folder, medium for the classes · **Under:** DEC-069, CAP-31.c · **Changed by:** DEC-300
 - **Decision:** The folder is the ticket's `acceptance_tests.path`, else `tests/acceptance/<wbs_id>/`, else
   `tests/acceptance/<ticket id>/`. It must be a directory. The rule applies to tickets of every class.
 
@@ -3024,7 +3024,7 @@
   without `--schema` being passed. One test covers it.
 
 ### DEC-304 — W1-12 DP-3: the kernel `templates/openspec/` folder stays unused for now
-- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-12 package DP-3 option (1), the lead's fallback; confidence medium · **Under:** DEC-198, DEC-222
+- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-04) · **Basis:** W1-12 package DP-3 option (1), the lead's fallback; confidence medium · **Under:** DEC-198, DEC-222 · **Changed by:** DEC-310
 - **Decision:** OpenSpec reads templates only from the schema's own `templates/` folder, so the templates the KPI
   validates live there, and `template/governance/kernel/templates/openspec/**` holds nothing. That is recorded as a
   residual. The text of G-07 and G-09 is in the S0b2 output in the workbench, not in the archived sources; whether
@@ -3132,7 +3132,7 @@
   tickets no longer need `main.py`. W1-25's engineer starts once this change is merged.
 
 ### DEC-318 — W1-50 DP-4: a commit that names a closed ticket, or one never started
-- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-50 package DP-4 · **Under:** DEC-255, CAP-58.h
+- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on W1-50 package DP-4 · **Under:** DEC-255, CAP-58.h · **Changed by:** DEC-359
 - **Decision:** A commit whose trailers name a closed ticket is judged by that ticket's role and `allowed_paths`
   only if it is an ancestor of the ticket's close commit; otherwise it is a finding. A commit that names a ticket
   that was never started is a finding.
@@ -3695,7 +3695,7 @@
   - Then W1-16 is merged and closed.
 
 ### DEC-362 — W1-16: the wrapper turns the tool's loopback UI off
-- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on the question W1-16 package DP-4 left open · **Under:** DEC-338, DEC-346
+- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on the question W1-16 package DP-4 left open · **Under:** DEC-338, DEC-346 · **Changed by:** DEC-389 (the mechanism only)
 - **Decision:** The codebase-memory wrapper sets `--ui=false`. The change of the tool's configuration is recorded in
   the notes of its entry in `governance/project/tool-registry.yaml`.
 
@@ -3711,7 +3711,7 @@
   suite. W1-28 makes the state readable.
 
 ### DEC-365 — W1-28 DP-2 and DP-3: the orchestrator may set the freeze, only the owner lifts it, and the caller is `GOV_ROLE`
-- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-28 packages DP-2 option (b) and DP-3 · **Amends:** DEC-176 · **Under:** CAP-05.a, CAP-05.d, DEC-179
+- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-28 packages DP-2 option (b) and DP-3 · **Amends:** DEC-176 · **Under:** CAP-05.a, CAP-05.d, DEC-179 · **Changed by:** DEC-402, DEC-407 ("unset `GOV_ROLE` is the owner"), DEC-409
 - **Decision:**
   - The orchestrator may set the freeze. Only the owner lifts it.
   - The caller is `GOV_ROLE` when it is set: `orchestrator` is allowed, and every worker role is refused. When
@@ -3731,7 +3731,7 @@
   - A repeat reverts nothing and succeeds.
 
 ### DEC-367 — W1-28 DP-6: the record of a rollback or a cancel is a commit to the ticket file
-- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-28 package DP-6 · **Under:** CAP-05.d, DEC-366
+- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-28 package DP-6 · **Under:** CAP-05.d, DEC-366 · **Changed by:** DEC-409
 - **Decision:**
   - The record for `--rollback` and `--cancel-agents` is a commit to the ticket file, made after the reverts, with
     the trailers `Task: <ticket>` and `Reverts-Task: <ticket>`.
@@ -3753,7 +3753,7 @@
   file path only, and never anything under `s0b2/probe/`.
 
 ### DEC-371 — Leads start their workers with `gov launch`
-- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER; orchestrator prompt v4.2, section 4 · **Supersedes:** DEC-183 for the roles the launcher starts · **Under:** DEC-231, DEC-311
+- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER; orchestrator prompt v4.2, section 4 · **Supersedes:** DEC-183 for the roles the launcher starts · **Under:** DEC-231, DEC-311 · **Changed by:** DEC-386
 - **Decision:**
   - W1-46 is closed, so from now on a ticket lead starts its workers with `gov launch <role> <ticket>`, sandboxed.
   - The W1-46 residuals stand as `governance/project/bootstrap.md` records them at its close.
@@ -3814,7 +3814,7 @@
 W1-28 DP-10, W1-19's packages and installs, and the launcher. DEC-372 stays as recorded.
 
 ### DEC-376 — The held-out copies are removed, and no worker bulk-copies the tree
-- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on the incident the W1-28 ticket lead reported · **Under:** DEC-213, DEC-218, MR-3
+- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on the incident the W1-28 ticket lead reported · **Under:** DEC-213, DEC-218, MR-3 · **Changed by:** DEC-395
 - **Decision:**
   - The owner removed `/tmp/gov-launch-independent-test-designer-5e58yicw` (3.4 GB, no process using it) through
     the operator.
@@ -3836,7 +3836,7 @@
   - The `--ui=false` wrapper change (DEC-362) and its registry note go in the same round; then W1-16 closes.
 
 ### DEC-378 — W1-28 DP-10: a rollback sets the freeze flag first, and it stays
-- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-28 package DP-10 option (a) · **Under:** DEC-365, DEC-368, CAP-05.c
+- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, on W1-28 package DP-10 option (a) · **Under:** DEC-365, DEC-368, CAP-05.c · **Changed by:** DEC-402
 - **Decision:**
   - `gov pause --rollback` sets the freeze flag first, once the caller is allowed, and the flag stays whatever the
     rollback's result (a conflict, an unknown ticket, a dirty tree). Only the owner lifts it.
@@ -3886,7 +3886,7 @@
   Nobody lists folders there, and nobody touches `s0b2/probe/`.
 
 ### DEC-384 — W1-19's installs: complete packages from the S0b2 registry, verifying what is on disk
-- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER · **Under:** DEC-083, DEC-195, DEC-198
+- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER · **Under:** DEC-083, DEC-195, DEC-198 · **Changed by:** DEC-397
 - **Decision:**
   - The orchestrator fills the four install packages from `~/gov-os-workbench/s0b2/out/TOOL_REGISTRY.yaml`.
   - Verifying the artefacts already on disk (the Ollama executable, the embedding model, the reranker snapshot)
@@ -3895,7 +3895,7 @@
   - The complete packages come to the owner. Meanwhile the model-free part of W1-19 is built.
 
 ### DEC-385 — No test fixture copies the held-out file
-- **Status:** ACCEPTED (owner, 2026-10-05; stricter-only, the ticket is the orchestrator's choice) · **Basis:** OWNER · **Under:** DEC-213, DEC-376
+- **Status:** ACCEPTED (owner, 2026-10-05; stricter-only, the ticket is the orchestrator's choice) · **Basis:** OWNER · **Under:** DEC-213, DEC-376 · **Changed by:** DEC-399
 - **Decision:**
   - Every test fixture that copies the repository leaves `governance/project/held-out.yaml` out, so it is never
     copied into a temporary project.
@@ -3904,7 +3904,7 @@
     own commit.
 
 ### DEC-386 — The launcher removes its temp folder and starts product-spec workers sandboxed
-- **Status:** ACCEPTED (owner, 2026-10-05; stricter-only, the ticket is the orchestrator's choice) · **Basis:** OWNER · **Amends:** DEC-371 · **Under:** DEC-159, DEC-311, CAP-58
+- **Status:** ACCEPTED (owner, 2026-10-05; stricter-only, the ticket is the orchestrator's choice) · **Basis:** OWNER · **Amends:** DEC-371 · **Under:** DEC-159, DEC-311, CAP-58 · **Changed by:** DEC-392
 - **Decision:**
   - `gov launch` removes its per-session temp folder when the session ends.
   - The launcher gets a `product-spec` role with an empty network allowlist, so product-spec workers are sandboxed
@@ -3990,7 +3990,7 @@
 stricter reading, and were told to the owner, who may choose otherwise.
 
 ### DEC-390 — W1-50 DP-11 to DP-16: the stricter reading in each case
-- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-05) · **Basis:** W1-50 packages DP-11 (a), DP-12 (a), DP-13 (a), DP-14 (c), DP-15 (a), DP-16 (a finding); confidence medium-low to medium-high · **Under:** CAP-58, DEC-254, DEC-269, DEC-358, DEC-359, DEC-360
+- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-05) · **Basis:** W1-50 packages DP-11 (a), DP-12 (a), DP-13 (a), DP-14 (c), DP-15 (a), DP-16 (a finding); confidence medium-low to medium-high · **Under:** CAP-58, DEC-254, DEC-269, DEC-358, DEC-359, DEC-360 · **Changed by:** DEC-394 (replaces its DP-15 rule)
 - **Decision:**
   - DP-15: when a merge commit has a parent that is not among the commits new in the move, every path it changes
     against its first parent is judged by the merge commit's own trailers, or against the caller without them. An
@@ -4018,7 +4018,7 @@
 of stopping reasons of ADR-0002 §4 and goes to the owner.
 
 ### DEC-391 — W1-20 DP-1 to DP-7: the interface, the ids, the depth, the code facet and the gaps of `gov closure`
-- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-20 packages DP-1 (a), DP-2 (a), DP-3 (a), DP-4 (a), DP-5 (gap reasons), DP-6 (a), DP-7 (b); confidence medium to high · **Under:** CAP-57.a, CAP-09, DEC-033, DEC-034, DEC-035, DEC-080, DEC-317, DEC-322, DEC-344
+- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-20 packages DP-1 (a), DP-2 (a), DP-3 (a), DP-4 (a), DP-5 (gap reasons), DP-6 (a), DP-7 (b); confidence medium to high · **Under:** CAP-57.a, CAP-09, DEC-033, DEC-034, DEC-035, DEC-080, DEC-317, DEC-322, DEC-344 · **Changed by:** DEC-393, DEC-396
 - **Decision:**
   - DP-1: both `gov closure (--depth N | --radius R) <id>...` and `gov.closure.closure(root, ids, depth=N)`, which
     returns the envelope's `result`. Its keys: `start`, `depth`, `stopping_reason`, `closure` (`id`, `kind`), `gaps`
@@ -4099,7 +4099,7 @@
 medium-high confidence. The owner was told on 2026-10-05.
 
 ### DEC-394 — W1-50 DP-18 and DP-17: a merge commit's own change by the three-way rule; a ticket-file commit in a worker's call
-- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-05) · **Basis:** W1-50 packages DP-18 option (a) and DP-17 option (a), confidence medium-high; the third reviewer's findings F1 and F2 · **Amends:** DEC-390 (replaces its DP-15 rule), DEC-269 (refines "content a parent holds") · **Under:** CAP-58, DEC-254, DEC-359
+- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-05) · **Basis:** W1-50 packages DP-18 option (a) and DP-17 option (a), confidence medium-high; the third reviewer's findings F1 and F2 · **Amends:** DEC-390 (replaces its DP-15 rule), DEC-269 (refines "content a parent holds") · **Under:** CAP-58, DEC-254, DEC-359 · **Changed by:** DEC-398, DEC-403
 - **Decision:**
   - DP-18: a path a merge commit changes against its first parent is brought by another parent only when that
     parent's content of the path differs from the merge base of the parents; with several merge bases, it must differ
@@ -4154,7 +4154,7 @@
   - The orchestrator runs the installs; the guard's ask is the owner's approval. W1-19 is then finished.
 
 ### DEC-398 — W1-11 DP-6: the approval rule reads merges by the merge base, with one helper shared with containment
-- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, W1-11 package DP-6 option (b) · **Amends:** DEC-394 · **Under:** DEC-360, DEC-387, CAP-51.a
+- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER, W1-11 package DP-6 option (b) · **Amends:** DEC-394 · **Under:** DEC-360, DEC-387, CAP-51.a · **Changed by:** DEC-403 ("against its first parent")
 - **Decision:**
   - The approval rule judges a merge against the merge base. It shares one helper with W1-50's three-way rule
     (DEC-394), so the approval check and containment read merges the same way.
@@ -4218,7 +4218,7 @@
 agree at medium confidence or higher. The owner was told on 2026-10-05.
 
 ### DEC-403 — W1-50 DP-20 and DP-19: the merge helper reads every parent; an octopus with a crossing parent fails closed
-- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-05) · **Basis:** W1-50 packages DP-20 option (a), confidence medium-high, and DP-19 option (a), confidence medium; the fourth reviewer's finding F1 (seven merge shapes that undo acceptance tests silently) · **Amends:** DEC-394, DEC-398 ("against its first parent") · **Under:** CAP-58, DEC-269, DEC-401
+- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-05) · **Basis:** W1-50 packages DP-20 option (a), confidence medium-high, and DP-19 option (a), confidence medium; the fourth reviewer's finding F1 (seven merge shapes that undo acceptance tests silently) · **Amends:** DEC-394, DEC-398 ("against its first parent") · **Under:** CAP-58, DEC-269, DEC-401 · **Changed by:** DEC-410 (the octopus sentence; what `brought` holds)
 - **Decision:**
   - DP-20: the one helper that reads a merge (`gov.guard.containment_merge.read_merge`) reads every parent the way
     it reads the first. A path where the merge commit's content differs from any parent's is the merge commit's own
@@ -4295,7 +4295,7 @@
   - Tuning on the dev set alone (option (c), a larger top-k) is not accepted as the fix.
 
 ### DEC-407 — W1-50 DP-F2: accepted for the merge; before W1-50 closes, the flag is compared around every Bash call and owner identity follows process ancestry
-- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** W1-50 freeze branch package DP-F2 option (a) now, option (b) and a new rule before the close · **Amends:** DEC-365 ("unset `GOV_ROLE` is the owner") · **Under:** DEC-402, DEC-404, DEC-311
+- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** W1-50 freeze branch package DP-F2 option (a) now, option (b) and a new rule before the close · **Amends:** DEC-365 ("unset `GOV_ROLE` is the owner") · **Under:** DEC-402, DEC-404, DEC-311 · **Changed by:** DEC-409 (its ancestry rule is replaced)
 - **Decision:**
   - Now, so the freeze branch can merge: W1-46's one live assertion is revised as a rewrite after implementation,
     reason "owner decision: freeze marker".
@@ -4327,7 +4327,7 @@
 changed here; the orchestrator told the owner so.
 
 ### DEC-409 — Lifting a freeze requires the owner in person: no Claude Code ancestor, an interactive terminal with a typed one-time code, and a guard rule on the lift form
-- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER · **Amends:** DEC-365, DEC-407 (its ancestry rule is replaced), DEC-367 as the owner named it · **Under:** DEC-402, DEC-404, CAP-05.a
+- **Status:** ACCEPTED (owner, 2026-10-05) · **Basis:** OWNER · **Amends:** DEC-365, DEC-407 (its ancestry rule is replaced), DEC-367 as the owner named it · **Under:** DEC-402, DEC-404, CAP-05.a · **Changed by:** DEC-428 (the one manual check before W1-50 closes)
 - **Decision:**
   1. `gov pause --off` refuses if any ancestor process is a Claude Code session, wherever that session was
      started. The operator console cannot lift either; only a plain terminal can.
@@ -4460,7 +4460,7 @@
 passed, `tests/unit` 760 passed, every other suite passed). The owner was told on 2026-10-06.
 
 ### DEC-417 — W1-50 DP-29, DP-30 and the bound on a move: as built
-- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-06) · **Basis:** W1-50 packages DP-29 and DP-30, the stricter option of each, as the lead built them; the sixth reviewer's finding F3 · **Under:** DEC-410, DEC-413, DEC-401
+- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-06) · **Basis:** W1-50 packages DP-29 and DP-30, the stricter option of each, as the lead built them; the sixth reviewer's finding F3 · **Under:** DEC-410, DEC-413, DEC-401 · **Changed by:** DEC-421 (its residual)
 - **Decision:**
   - DP-29: under `tests/acceptance/**`, a path two parents both changed against their one merge base in the same
     way is the merge commit's own change too, although it differs from no parent.
@@ -4542,7 +4542,7 @@
     others, each from its branch's last commit.
 
 ### DEC-421 — W1-50: the both-sides rule is extended to ticket files
-- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** OWNER, on the residual of W1-50's seventh round (the sixth reviewer's finding F1) · **Amends:** DEC-410 (DP-24), DEC-417 (its residual) · **Under:** DEC-413
+- **Status:** ACCEPTED (owner, 2026-10-06) · **Basis:** OWNER, on the residual of W1-50's seventh round (the sixth reviewer's finding F1) · **Amends:** DEC-410 (DP-24), DEC-417 (its residual) · **Under:** DEC-413 · **Changed by:** DEC-572
 - **Decision:**
   - Under `.tickets/**` too, a path that more than one parent changed against the merge base is the merge commit's
     own, whichever side's content it holds. Stricter-only.
@@ -5567,7 +5567,7 @@
 - **Decision:** Per session: the session role's file under `.claude/agents/`, plus `CLAUDE.md` and `AGENTS.md` where they exist. MCP counts 0, because the Governance OS defines no MCP server.
 
 ### DEC-508 — The held-out file: the brief rule is confirmed, and the guard refuses any agent tool call whose targets include it
-- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER, on the incident in W1-31's second run (a test designer's search with a glob over the folder that holds the held-out file) · **Under:** DEC-108
+- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** OWNER, on the incident in W1-31's second run (a test designer's search with a glob over the folder that holds the held-out file) · **Under:** DEC-108 · **Changed by:** DEC-820
 - **Decision:**
   - The orchestrator's brief rule is confirmed: no worker runs a glob, a search or a listing over `governance/project/`; files there are named one by one.
   - Delegated to the orchestrator, stricter-only: the guard refuses any agent tool call whose expanded file targets (globs included, DEC-108) include the project's held-out file under `governance/project/` (the owner's answer names its path). The orchestrator chooses the ticket.
@@ -5587,7 +5587,7 @@
 ## 137. Owner answer: what else counts as an adoption gap at a close, when every such exception ends, and real checkpoints (register v0.137, appended by the W1 orchestrator on branch `w1/integrate`)
 
 ### DEC-511 — Four more adoption gaps until W1-41; every adoption-gap exception ends when W1-41 is merged; W1-42 shows one clean `gov close`; leads write real checkpoints
-- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER, on package P-15 option (a) with three guards. `gov close DAEO-2lwj`, run once with the fixed tool, reported 55 findings in seven classes (`log/close-W1-30b.json`); four things among them are not on DEC-492's list. · **Refines:** DEC-476, DEC-492, DEC-505
+- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER, on package P-15 option (a) with three guards. `gov close DAEO-2lwj`, run once with the fixed tool, reported 55 findings in seven classes (`log/close-W1-30b.json`); four things among them are not on DEC-492's list. · **Refines:** DEC-476, DEC-492, DEC-505 · **Changed by:** DEC-1057 (lifted: no committed `gov checkpoint` record per round, R-6), DEC-522 (its expiry)
 - **Decision:**
   - **Until W1-41, these also count as adoption gaps:**
     - a missing checkpoint record;
@@ -5629,7 +5629,7 @@
 ## 139. Owner decisions on test run time: no double runs, a measuring agent, and the bar for parallel runs (register v0.139, appended by the W1 orchestrator on branch `w1/integrate`)
 
 ### DEC-513 — No double runs: a `gov close` that directly follows its ticket's merge counts as the post-merge regression
-- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER · **Refines:** the orchestrator's practice of a full regression after every merge
+- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER · **Refines:** the orchestrator's practice of a full regression after every merge · **Changed by:** DEC-518, DEC-536
 - **Decision:**
   - When a merge is followed directly by its ticket's `gov close` on the same merge commit, the `gov close` run counts as the post-merge regression; no separate regression is run for it.
   - A separate full regression is needed only after a merge that is not followed directly by a close.
@@ -6470,7 +6470,7 @@
   - **New brief rule, from now on:** briefs and logs refer to a canary or planted secret by its id, never by its value.
 
 ### DEC-605 — P-40: `gov` is installed for this user, by the owner
-- **Status:** ACCEPTED (owner, 2026-10-10) · **Basis:** OWNER, on package P-40 option (a), approved and done · **Under:** DEC-083
+- **Status:** ACCEPTED (owner, 2026-10-10) · **Basis:** OWNER, on package P-40 option (a), approved and done · **Under:** DEC-083 · **Changed by:** DEC-822
 - **Decision:** The owner installed `gov` through the operator: `python3 -m pip install --user --break-system-packages -e /home/usain/Dynamic-Agentic-Engineering-OS`. Result: gov 0.1.0, its script at `/home/usain/.local/bin/gov`, `import gov` resolving to this repository's `src/gov/__init__.py`, PyYAML already present. The install created the git-ignored metadata folder `src/gov.egg-info/`, which stays. No tracked file changed. It is recorded in the tool registry with this approval, and in the exit package as a runner tool.
 
 ### DEC-606 — DEC-600, DEC-601 and DEC-602 are accepted
@@ -7454,7 +7454,7 @@
 - **Decision:** the repair ticket `ade-ke2y`, written in the a-dev clone by the refused second `gov close ORION-im01` (TRAILER_MISSING on `540004a`, before a-dev's trailers base `bb1852e`), stays closed with `tk close` (`127227c`, a note naming DEC-704). The refusal it repairs is settled by DEC-704, and history is not rewritten. Named for the exit auditor alongside ORION-im01's close (`5fb754d`).
 
 ### DEC-709 — Commits rebuild the index after staging, so the pre-commit hook's checks pass honestly; fast pre-commit checks and the commit-time re-index go on the Wave 2 list, ranked high
-- **Status:** ACCEPTED (owner, 2026-10-15) · **Under:** DEC-075, DEC-342, DEC-706 · **Basis:** the first commit after B3 (this register entry, v0.215) was refused by the pre-commit hook: `gov ci checks G1 G2` gave `CHECK_FAILED: hard-block checks failed: index-freshness, recovery-rebuild` (exit 3, 290 s; staged-secrets 0 secrets). The G1 index-freshness check compares the lexical index with every tracked file as it stands; three were newer than the last rebuild (`.tickets/DAEO-cdoi.md`, `governance/project/bootstrap.md`, the staged register), and recovery-rebuild failed on the same stale index. Both were green at `de9389fc` right after a rebuild.
+- **Status:** ACCEPTED (owner, 2026-10-15) · **Under:** DEC-075, DEC-342, DEC-706 · **Basis:** the first commit after B3 (this register entry, v0.215) was refused by the pre-commit hook: `gov ci checks G1 G2` gave `CHECK_FAILED: hard-block checks failed: index-freshness, recovery-rebuild` (exit 3, 290 s; staged-secrets 0 secrets). The G1 index-freshness check compares the lexical index with every tracked file as it stands; three were newer than the last rebuild (`.tickets/DAEO-cdoi.md`, `governance/project/bootstrap.md`, the staged register), and recovery-rebuild failed on the same stale index. Both were green at `de9389fc` right after a rebuild. · **Changed by:** DEC-719
 - **Decision:** option (a).
   - From now on, after staging and before each commit, `gov rebuild --no-embeddings` runs, then the commit, so the pre-commit hook's checks pass honestly with nothing bypassed. This is not working round the hook: it makes index freshness true.
   - W1-42's brief carries the same instruction, and a lead reports any hook refusal rather than working round it (DEC-706).
@@ -8625,7 +8625,7 @@
   2. **W2-52 starts now, stacked on W2-49.**
 
 ### DEC-787 — Every report ends with one OWNER_ACTION line
-- **Status:** ACCEPTED (owner, 2026-10-18; the owner commits this entry with `Role: owner`, in the next batch) · **Under:** DEC-486, DEC-220 · **Basis:** so the owner can be notified automatically.
+- **Status:** ACCEPTED (owner, 2026-10-18; the owner commits this entry with `Role: owner`, in the next batch) · **Under:** DEC-486, DEC-220 · **Basis:** so the owner can be notified automatically. · **Changed by:** DEC-948
 - **Decision:** every report of the orchestrator ends with exactly one final line, naming every open owner item:
   `OWNER_ACTION: <P1|P2|COMMIT|none> <ids> - <one-line summary>`
   For example: `OWNER_ACTION: P1 P-W2-35 - W2-53's close refused; options (a) to (c)`, `OWNER_ACTION: COMMIT DEC-782 to DEC-786 staged`, or `OWNER_ACTION: none`.
@@ -9089,7 +9089,7 @@
   4. The new ticket W2-62 (DEC-837) is added; W2-33 stays in Wave 2, cut down (DEC-832). Wave 2 then holds 55 tickets plus W2-00.
 
 ### DEC-832 — The Charter's eight unplanned roles: four as skill packs the engineer loads, four to Wave 3 (plan §11 item 6; item 1a)
-- **Status:** ACCEPTED (owner, 2026-10-19; the owner commits this entry with `Role: owner`, in the next batch) · **Under:** Charter v5 §6, DEC-105 (defer, for four), DEC-829 items 4 (iii) and (iv), CAP-24.b, CAP-33 · **Basis:** OWNER, 2026-10-19: the plan's alternative, as skill packs rather than new governance roles · **Replaces:** the plan's recommendation to defer all eight.
+- **Status:** ACCEPTED (owner, 2026-10-19; the owner commits this entry with `Role: owner`, in the next batch) · **Under:** Charter v5 §6, DEC-105 (defer, for four), DEC-829 items 4 (iii) and (iv), CAP-24.b, CAP-33 · **Basis:** OWNER, 2026-10-19: the plan's alternative, as skill packs rather than new governance roles · **Replaces:** the plan's recommendation to defer all eight. · **Changed by:** DEC-957 (the skill packs come in Wave 2)
 - **Decision:**
   1. **Backend, database and data, integration and API, and security become skill packs,** not governance roles: method text that the engineer role loads at launch, through W2-60. They add no role, no guard entry, no permission and no path; a skill grants nothing on its own authority (CAP-24.b).
   2. **W2-33 stays in Wave 2, cut down to these four packs:** about 1.5 days of product-spec work, no new machinery. It is a kernel skill change, so it goes through CIT-P (CAP-33). It starts after W2-60 (which loads them) and W2-11 (one versioned source per skill), and it is admitted by this decision under DEC-829 (iii).
@@ -9143,7 +9143,7 @@
   4. The checkpoint at every handover (DEC-837 item 3) stays, whatever the window.
 
 ### DEC-839 — Lens F's other values: model, effort and subagents per launch; agent teams off; prompt v3 (plan §11 item 5; item 3)
-- **Status:** ACCEPTED (owner, 2026-10-19; the owner commits this entry with `Role: owner`, with prompt v3 and the common lead brief, in the next batch) · **Under:** DEC-826 Q6, DEC-460, DEC-715, DEC-724 · **Basis:** OWNER, 2026-10-19; lens F (`docs/assessment/2026-10/F-models-context.md`) Table 3, R7, R9.
+- **Status:** ACCEPTED (owner, 2026-10-19; the owner commits this entry with `Role: owner`, with prompt v3 and the common lead brief, in the next batch) · **Under:** DEC-826 Q6, DEC-460, DEC-715, DEC-724 · **Basis:** OWNER, 2026-10-19; lens F (`docs/assessment/2026-10/F-models-context.md`) Table 3, R7, R9. · **Changed by:** DEC-957 (effort)
 - **Decision:**
   1. **Model:** `claude-opus-5-5` for every role.
   2. **Effort, set on every launch** (`--effort`, CLI 2.1.292):
@@ -9242,7 +9242,7 @@
   4. The OWNER_ACTION line stays at the end of every report (DEC-787).
 
 ### DEC-851 — Every standing owner rule is written where sessions read it (standing)
-- **Status:** ACCEPTED (owner, 2026-10-19; the owner commits this entry with `Role: owner`, in the next batch; standing) · **Under:** DEC-819, DEC-824, DEC-825 item 1 · **Basis:** OWNER, 2026-10-19: a rule that reaches none of these places does not exist for the next session.
+- **Status:** ACCEPTED (owner, 2026-10-19; the owner commits this entry with `Role: owner`, in the next batch; standing) · **Under:** DEC-819, DEC-824, DEC-825 item 1 · **Basis:** OWNER, 2026-10-19: a rule that reaches none of these places does not exist for the next session. · **Changed by:** DEC-1052 (item 1), DEC-1057
 - **Decision:**
   1. **Every standing owner rule,** from now on and for every rule already given on 2026-10-19, is written into each place a session actually reads it:
      - the decision register, as a DEC entry;
@@ -9370,7 +9370,7 @@
 The owner committed DEC-859 and DEC-860 (`f0680605`) and set a standing rule that replaces DEC-724's "the owner commits owner entries" and the owner's earlier patch-file idea. From this section on, the orchestrator commits the records of the owner's decisions itself, signed as below.
 
 ### DEC-861 — The orchestrator commits the records of the owner's decisions; the owner's push is the acceptance (standing)
-- **Status:** ACCEPTED (owner, 2026-10-20, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-20)`; standing) · **Under:** DEC-724, DEC-788, DEC-851, ADR-0001 · **Basis:** OWNER, 2026-10-20: "Nothing is ever left staged in the main tree, so no merge, close or lead ever waits on me." · **Changes:** DEC-724 (owner entries were committed by the owner with `Role: owner`) and DEC-788 (the daily owner batch).
+- **Status:** ACCEPTED (owner, 2026-10-20, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-20)`; standing) · **Under:** DEC-724, DEC-788, DEC-851, ADR-0001 · **Basis:** OWNER, 2026-10-20: "Nothing is ever left staged in the main tree, so no merge, close or lead ever waits on me." · **Changes:** DEC-724 (owner entries were committed by the owner with `Role: owner`) and DEC-788 (the daily owner batch). · **Changed by:** DEC-1057
 - **Decision:**
   1. **What the orchestrator commits:** the records of the owner's decisions (the register, the plan files, the prompt, the briefs, the path map and the ratchet lists), as soon as they are written. Nothing is left staged in the main tree.
   2. **How it signs:** never as the owner. Its commits carry `Role: orchestrator`, never `Role: owner`, plus `Task: decision-record` and `Decided-by: owner (chat, <date>)` naming whose decision it records. The owner's own commits keep `Role: owner`.
@@ -10807,7 +10807,7 @@
 - Next free id: DEC-916.
 
 ### DEC-916 — A ticket run in rounds gets up to two reviews per round declared in its plan (standing, under the rule about rules)
-- **Status:** ACCEPTED (owner, 2026-10-24, in the chat; standing; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-24)`) · **Under:** DEC-413, DEC-851, DEC-904 item 5, DEC-909, DEC-912 · **Basis:** package P-W2-67-R23 (`governance/project/orchestration/packages/P-W2-67-R23.md`): W2-67 runs in three rounds declared in its ticket's plan; round 1 used both of DEC-413's reviews.
+- **Status:** ACCEPTED (owner, 2026-10-24, in the chat; standing; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-24)`) · **Under:** DEC-413, DEC-851, DEC-904 item 5, DEC-909, DEC-912 · **Basis:** package P-W2-67-R23 (`governance/project/orchestration/packages/P-W2-67-R23.md`): W2-67 runs in three rounds declared in its ticket's plan; round 1 used both of DEC-413's reviews. · **Changed by:** DEC-1010, DEC-987
 - **Decision:**
   1. **A ticket run in rounds gets up to two reviews per round,** only for rounds declared in its ticket's plan before the round starts.
   2. **A third review in any round is the owner's exception,** as before (DEC-909, DEC-912).
@@ -11048,7 +11048,7 @@
 | 0.310 | 2026-10-26 | Owner (recorded by the orchestrator, DEC-861): DEC-924 (P-W2-07-DR2: Q1 (a), `611955fa` accepted as history by the owner's own Role: owner commit, validated first; standing: assessment and audit reports in commits of their own; Q2 (a), W2-07's round 2 beside W2-57 with the files split, the second to merge merges back, re-verifies and gets a fresh probe if stale). Next free id: DEC-925. |
 
 ### DEC-925 — P-REPIN-R1 (a): W2-74 for the regeneration's test revisions, the registry line, the warning's interim, the queue restarted; settings changes run in full on a clone first and ACT commands in a file (standing); P-W2-57-B: B1 (a), B2 (b), the rest delegated
-- **Status:** ACCEPTED (owner, 2026-10-27, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-27)`; item 2 standing) · **Under:** DEC-922, DEC-923, DEC-924, DEC-911, DEC-917, DEC-899, DEC-906, DEC-866, DEC-851, DEC-861 · **Basis:** packages P-REPIN-R1 and P-W2-57-B (`governance/project/orchestration/packages/P-REPIN-R1.md`). On 2026-10-26, W2-70's close (DAEO-uzme) ran 68 minutes on the full suite and was refused (exit 3, count 1; repair ticket DAEO-2upp). Its eight remaining reds came from the first re-pin's settings regeneration, not from W2-70. The owner committed the accepted-history entry for `611955fa` (`048f5758`, DEC-924) and pushed both branches.
+- **Status:** ACCEPTED (owner, 2026-10-27, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-27)`; item 2 standing) · **Under:** DEC-922, DEC-923, DEC-924, DEC-911, DEC-917, DEC-899, DEC-906, DEC-866, DEC-851, DEC-861 · **Basis:** packages P-REPIN-R1 and P-W2-57-B (`governance/project/orchestration/packages/P-REPIN-R1.md`). On 2026-10-26, W2-70's close (DAEO-uzme) ran 68 minutes on the full suite and was refused (exit 3, count 1; repair ticket DAEO-2upp). Its eight remaining reds came from the first re-pin's settings regeneration, not from W2-70. The owner committed the accepted-history entry for `611955fa` (`048f5758`, DEC-924) and pushed both branches. · **Changed by:** DEC-1057 (item 2)
 - **Decision:**
   1. **P-REPIN-R1 (a).**
      - **W2-74** (LITE, test designer; ticket `DAEO-2azm`). Each change carries a `Rewrite-Reason:`. It:
@@ -11605,7 +11605,7 @@
 
 
 ### DEC-943 — Brief gaps in every lead's return, fixed the same week; the orchestrator's own drift measured (standing)
-- **Status:** ACCEPTED (owner, 2026-10-29, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-29)`; standing) · **Under:** DEC-824, DEC-793, DEC-836, DEC-930, DEC-938, DEC-941, CAP-33
+- **Status:** ACCEPTED (owner, 2026-10-29, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-29)`; standing) · **Under:** DEC-824, DEC-793, DEC-836, DEC-930, DEC-938, DEC-941, CAP-33 · **Changed by:** DEC-1052 (item 1)
 - **Decision:**
   1. **Brief gaps.** Every lead's return gains a "brief gaps" section: what it had to discover, look up or ask that its brief, ticket or skills did not tell it, with the time it cost.
      - The orchestrator collects them and fixes the common brief, the brief builder or the kernel skills the same week.
@@ -11764,7 +11764,7 @@
 
 
 ### DEC-949 — The morning package carries only the night; daytime decisions reach the owner as they arise; scope growth in the weekly numbers (standing)
-- **Status:** ACCEPTED (owner, 2026-10-29, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-29)`; standing) · **Under:** DEC-938, DEC-936, DEC-930, DEC-941, DEC-946 · **Changes:** DEC-938 (refined: the morning package's scope) and DEC-930 item 2 (the weekly numbers)
+- **Status:** ACCEPTED (owner, 2026-10-29, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-29)`; standing) · **Under:** DEC-938, DEC-936, DEC-930, DEC-941, DEC-946 · **Changes:** DEC-938 (refined: the morning package's scope) and DEC-930 item 2 (the weekly numbers) · **Changed by:** DEC-1057, DEC-973
 - **Decision:**
   1. **The 07:30 morning package is only for what happens overnight:** the nightly's findings, night-time alerts, and anything that arose between the end of the owner's day and 07:30.
   2. **Decisions that arise during the day** (from leads, closes, reviews, merges, the orchestrator's own findings) come to the owner as they arise:
@@ -11989,7 +11989,7 @@
 | 0.340 | 2026-10-30 | Owner (recorded by the orchestrator, DEC-861): DEC-957 (the batch stopped before ACT 1; STORE_MISSING fixed by a rebuild; installs ask only in the CTO's session; ACT 1 (a) with W2-90 for the 235 tests; ROLES-SPEC-1 approved with the domain skill packs in Wave 2, a software company's work order, a roles research session, a fresh session daily for every orchestrator, the CTO's skills on demand, effort high for the CTO and Senior Engineers, and the P3/P2/P1/emergency rubric; memory's target 95 % with 85 % the floor, and all seven gaps closed before memory is ready). Next free id: DEC-958. |
 
 ### DEC-958 — The five-rule guard's false refusals: each recorded, counted in the daily document, and a package to fix the hook if they keep happening (standing)
-- **Status:** ACCEPTED (owner, 2026-10-30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-30)`; standing) · **Under:** DEC-953 item 2, DEC-954, DEC-957, DEC-849, ADR-0001 · **Basis:** the first false refusal after ACT 1 (2026-10-30 21:45 GMT: the hook's rule 1 refused the orchestrator's lead-brief build because the acceptance folder appeared as text in an argument; the write went to the briefs folder)
+- **Status:** ACCEPTED (owner, 2026-10-30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-30)`; standing) · **Under:** DEC-953 item 2, DEC-954, DEC-957, DEC-849, ADR-0001 · **Basis:** the first false refusal after ACT 1 (2026-10-30 21:45 GMT: the hook's rule 1 refused the orchestrator's lead-brief build because the acceptance folder appeared as text in an argument; the write went to the briefs folder) · **Changed by:** DEC-1050 (the harvest)
 - **Decision:**
   1. **Watch:** every refusal by the five-rule hook (`.claude/hooks/pretooluse.py`, reasons ending "DEC-953 item 2"), in every session, is collected and judged: a true refusal, or a false positive (the hook refused something none of its five rules is meant to stop).
   2. **Record each false positive:** the time, the command's form (one line, at most 200 characters, never a secret or file contents), the rule that refused it, and what it cost (minutes and the workaround). The record is `.gov-runtime/scratch/orchestrator/log/guard-refusals.jsonl`, harvested from the session transcripts by `tools/guard_refusals.py` (checked by a background watcher) and backed by the leads' returns (`guard_refusals:` lines, their workers' included).
@@ -12034,7 +12034,7 @@
 | 0.343 | 2026-10-30 | Owner (recorded by the orchestrator, DEC-861): DEC-960 (the memory gate counts a running verification once). Next free id: DEC-961. |
 
 ### DEC-961 — The machine is shared by capacity alone: no memory set aside for full runs, no close or night holds, the nightly holds nothing; the remaining holds listed for the owner (standing)
-- **Status:** ACCEPTED (owner, 2026-10-30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-30)`; standing) · **Under:** DEC-953, DEC-954, DEC-947 item 5, DEC-898 · **Supersedes:** DEC-960 · **Changes:** DEC-947, DEC-942 items 4 and 5, DEC-939 item 6, DEC-933 item 2 · **Basis:** the owner's message of 2026-10-30; `packages/HOLDS-REVIEW-1.md`
+- **Status:** ACCEPTED (owner, 2026-10-30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-30)`; standing) · **Under:** DEC-953, DEC-954, DEC-947 item 5, DEC-898 · **Supersedes:** DEC-960 · **Changes:** DEC-947, DEC-942 items 4 and 5, DEC-939 item 6, DEC-933 item 2 · **Basis:** the owner's message of 2026-10-30; `packages/HOLDS-REVIEW-1.md` · **Changed by:** DEC-984 ("the nightly takes no lock and holds nothing")
 - **Decision:**
   1. **No memory is set aside for a full test run** (the 7.4 GiB verification peak). The gate counts the floor, each running lead at what it uses (at least its working size) and the newcomer. A full run (a close's, the nightly's, a lead's) gets its place like anything else: it checks the gate before it starts (`gate_check.py --full-run`, room for its own measured peak) and waits until there is room. The floor and the out-of-memory trip-wire stay as they are.
   2. **No hold for a waiting close** (CLOSE-PENDING) **and no 00:30 to 05:30 window** for launches. Closes, scoped test runs and new leads run side by side whenever the gate's capacity allows and their paths don't conflict.
@@ -12115,7 +12115,7 @@
 | 0.349 | 2026-10-31 | Owner (recorded by the orchestrator, DEC-861): DEC-966 (P-W2-90-1 (a) and (a); the designers' store twice a day; rebuild speed a priority, P-SPEED-1). Next free id: DEC-967. |
 
 ### DEC-967 — P-SPEED-1 (a): W2-107 starts now, at the front of the queue with W2-106 (standing)
-- **Status:** ACCEPTED (owner, 2026-10-31, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-31)`; standing) · **Under:** DEC-966 item 4 · **Basis:** `packages/P-SPEED-1.md`
+- **Status:** ACCEPTED (owner, 2026-10-31, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-31)`; standing) · **Under:** DEC-966 item 4 · **Basis:** `packages/P-SPEED-1.md` · **Changed by:** DEC-975
 - **Decision:** option (a): gitleaks results remembered by content hash, in a ticket of its own (W2-107, `DAEO-kiar`, FULL), started now at the front of the queue with W2-106, since every rebuild, close and nightly waits on it. The nightly's full-scan setting (`GOV_SECRETS_FULL_SCAN=1` in `nightly.sh`) is the orchestrator's at W2-107's merge, with `test_nightly.sh` and a review.
 - **Where it goes (DEC-851):** this register; W2-107's ticket and brief; the chain; RESUME HERE.
 
@@ -12124,7 +12124,7 @@
 | 0.350 | 2026-10-31 | Owner (recorded by the orchestrator, DEC-861): DEC-967 (P-SPEED-1 (a): W2-107 now, at the front with W2-106). Next free id: DEC-968. |
 
 ### DEC-968 — The full suite once a day, in the nightly, and nowhere else; a close refused only by a failure its own change caused; every other failure dealt with at once (standing)
-- **Status:** ACCEPTED (owner, 2026-10-31, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-31)`; standing) · **Under:** DEC-953, DEC-959, DEC-961, DEC-962 · **Changes:** DEC-953 item 4 and §0's close rule, DEC-959 item 1 · **Basis:** `packages/P-CLOSE-ATTR-1.md`; the batch of five's run of 2026-10-30 22:45 to 2026-10-31 01:31
+- **Status:** ACCEPTED (owner, 2026-10-31, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-31)`; standing) · **Under:** DEC-953, DEC-959, DEC-961, DEC-962 · **Changes:** DEC-953 item 4 and §0's close rule, DEC-959 item 1 · **Basis:** `packages/P-CLOSE-ATTR-1.md`; the batch of five's run of 2026-10-30 22:45 to 2026-10-31 01:31 · **Changed by:** DEC-1049 (1)
 - **Decision (the owner's three rules, with tonight's cases):**
   1. **The full suite runs once a day, in the nightly, and nowhere else.** No lead, close or merge runs it, core tickets included (for example W2-107 and W2-106, which change the core): they run the scoped set, their own acceptance tests plus every suite the selection says the change can reach. A break the selection missed is found by the nightly the next morning, traced to that day's merges and handled as decided.
   2. **A close is refused only by a failure its own change caused (P-CLOSE-ATTR-1 (a)).** Each case that fails alone is re-run without the batch's merges (the same head, the merges reverted). If it still fails there, it is not the change's: the close goes on and its record names it. If it passes there, the close is refused. A merge that cannot be reverted refuses (untraced). Tonight's batch of five would have been refused by seven failures, none from its five tickets: three from the orchestrator's record commits, the rest W2-54's known load failures.
@@ -12168,7 +12168,7 @@
 | 0.353 | 2026-10-31 | Delegated (orchestrator): DEC-970 (the night's P2s and P3s; four fixes on the spot; P-GATE-WAIT-1 withdrawn; three slips). Next free id: DEC-971. |
 
 ### DEC-971 — The owner's answers to P1-MORNING-2026-10-31: six items as recommended, with the exception of item 3 bounded (standing)
-- **Status:** ACCEPTED (owner, 2026-10-31, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-31)`; standing) · **Under:** DEC-968, DEC-970, DEC-805, DEC-962 item 2, DEC-934 · **Basis:** `packages/P1-MORNING-2026-10-31.md`. **DEC-970's delegated decisions stand.**
+- **Status:** ACCEPTED (owner, 2026-10-31, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-31)`; standing) · **Under:** DEC-968, DEC-970, DEC-805, DEC-962 item 2, DEC-934 · **Basis:** `packages/P1-MORNING-2026-10-31.md`. **DEC-970's delegated decisions stand.** · **Changed by:** DEC-1001 (item 5)
 - **Decision:**
   1. **W2-52 P-8 (a):** the CTO makes the one write of the regenerated `.claude/skills/adopt/SKILL.md` in W2-52's worktree, in its own session, and the owner approves the prompt it raises.
   2. **W2-49 P-A (b) and P-B:** W2-49 closes on Contract v4.2; DEC-841's nine items go to a small v4.3 Contract ticket, with CAP-53.b split. `contract.yaml` is the Contract's authority; the three missing providers are added to `CONTRACT_v4.md`, the 276 one-line records fixed, and a check that the two forms agree is added (`validate_w2.py`), riding with the v4.3 ticket.
@@ -12197,7 +12197,7 @@
 | 0.355 | 2026-10-31 | Owner (recorded by the orchestrator, DEC-861): DEC-972 (the non-blocking ping, none at night, the blocking one only as a daytime fallback). Next free id: DEC-973. |
 
 ### DEC-973 — The quiet hours 02:00 to 07:30; the nightly at 04:00; its check at 08:00; the morning package at 09:00 (standing)
-- **Status:** ACCEPTED (owner, 2026-10-31, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-31)`; standing) · **Under:** DEC-972, DEC-933, DEC-934, DEC-938, DEC-949, DEC-951, DEC-952 item 6 · **Changes:** DEC-972 item 2 (the quiet hours), and the nightly's and the morning's times in DEC-933, DEC-934, DEC-938, DEC-949 and DEC-951 B
+- **Status:** ACCEPTED (owner, 2026-10-31, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-31)`; standing) · **Under:** DEC-972, DEC-933, DEC-934, DEC-938, DEC-949, DEC-951, DEC-952 item 6 · **Changes:** DEC-972 item 2 (the quiet hours), and the nightly's and the morning's times in DEC-933, DEC-934, DEC-938, DEC-949 and DEC-951 B · **Changed by:** DEC-1049 (the nightly at 04:00, its 08:00 check)
 - **Decision:**
   1. **P-PING-1 (a) plus (d), with the quiet hours from 02:00 to 07:30:** no pings then (emergencies excepted); work keeps going at night, and decisions accumulate for the owner in the morning package. From 07:30 to 02:00, pings by `ping_log.sh` and `PushNotification` (DEC-972).
   2. **The nightly full run moves to 04:00** and runs from 04:00 to about 07:00; its window ends at 08:00.
@@ -12215,7 +12215,7 @@
 | 0.356 | 2026-10-31 | Owner (recorded by the orchestrator, DEC-861): DEC-973 (quiet hours 02:00-07:30; the nightly at 04:00, its check at 08:00, the morning package at 09:00, the handover after it; ACT-NIGHTLY-0400). Next free id: DEC-974. |
 
 ### DEC-974 — The memory-chain line back in every status block; a new ticket in the WBS is a P1; a lighter lane for the CTO's own tools, to be proposed (standing)
-- **Status:** ACCEPTED (owner, 2026-10-31, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-31)`; items 1 and 2 standing; item 3 a proposal to come) · **Under:** DEC-952 item 4, DEC-948, DEC-949, DEC-818, DEC-954 · **Changes:** the CTO's filing of tickets under delegation (DEC-220, DEC-936 item 2.5: no longer a P2 or P3 for a WBS ticket)
+- **Status:** ACCEPTED (owner, 2026-10-31, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-31)`; items 1 and 2 standing; item 3 a proposal to come) · **Under:** DEC-952 item 4, DEC-948, DEC-949, DEC-818, DEC-954 · **Changes:** the CTO's filing of tickets under delegation (DEC-220, DEC-936 item 2.5: no longer a P2 or P3 for a WBS ticket) · **Changed by:** DEC-979 (item 3)
 - **Decision:**
   1. **The memory-chain line (DEC-952 item 4, reaffirmed):** every status block carries it again. It had dropped out of the CTO's blocks on 2026-10-31 (the CTO's slip). The 20:00 CAPACITY-1 brief gives memory's state: what has merged, what is running, what has not started, and when the next measure is due.
   2. **A new ticket in the WBS is a P1 (standing):** adding a ticket changes the WBS and the plan, so it goes to the owner as a P1 package (six parts, DEC-818) with the CTO's recommendation, before it is filed. This covers follow-ups, splits (an "a/b" ticket) and tickets for a red found by a close or the nightly; a red fixed on the spot inside an existing ticket's scope needs no new ticket. A lead never files one: it names the need in its return. The 20:00 brief lists every ticket added since the plan's approval (DEC-954), each with the decision that added it and who decided it (the owner, or the CTO under delegation).
@@ -12241,7 +12241,7 @@
 | 0.358 | 2026-10-31 | Owner (recorded by the orchestrator, DEC-861): DEC-975 (W2-107 first, no new lead until it closes; the machine re-measured after it for CAPACITY-1's sizing; the CPU query embedder kept, re-tested against the GPU on the combined memory as a W2-15b KPI). Next free id: DEC-976. |
 
 ### DEC-976 — W2-96's run 2: P-W2-96-GATE (a), resume when the queue allows; its P3 logged (delegated)
-- **Status:** ACCEPTED (orchestrator, delegated under DEC-936 item 2.5: a P2, reversible, the lead's recommendation at high confidence and the orchestrator's agree, nothing in the Charter, the master rules or the Contract's scope, the guard not weakened; for the owner to overturn) · **Under:** DEC-970, DEC-961, DEC-975 · **Basis:** W2-96's return `log/W2-96-A5-resume-dec970.json` (17:26, PACKAGES, head `162f8f4ed51e`)
+- **Status:** ACCEPTED (orchestrator, delegated under DEC-936 item 2.5: a P2, reversible, the lead's recommendation at high confidence and the orchestrator's agree, nothing in the Charter, the master rules or the Contract's scope, the guard not weakened; for the owner to overturn) · **Under:** DEC-970, DEC-961, DEC-975 · **Basis:** W2-96's return `log/W2-96-A5-resume-dec970.json` (17:26, PACKAGES, head `162f8f4ed51e`) · **Changed by:** DEC-979
 - **Decision:**
   1. **P-W2-96-GATE (a):** W2-96 resumes when the lead queue lets it start (DEC-975: after W2-107's close), with no exemption from the load gate; option (b), exempting single-process runs, is a capacity rule and goes to the owner inside CAPACITY-1, not here. Left: the lead's red check of review 3's cases, the engineer's `gov accept` on all 106 cases, review 4 (the round's last, DEC-916), the scoped run and the probe record. Brief `briefs/W2-96-A5-resume-dec976.md`; queued after W2-105.
   2. **P-W2-96-R9-PREMISE (a)** (the lead's P3, `c348af6b`): listed, stands.
@@ -12324,7 +12324,7 @@
 | 0.364 | 2026-10-31 | Delegated (orchestrator): DEC-981 (W2-11 r1 versions every skill copy, adopt's after W2-52). Next free id: DEC-982. |
 
 ### DEC-982 — Three tickets filed (W2-112, W2-113, W2-114); the smart way of working to become part of the Gov OS (standing)
-- **Status:** ACCEPTED (owner, 2026-10-31, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-31)`; item 2 standing) · **Under:** DEC-974, DEC-979, DEC-906, DEC-953 · **Basis:** `packages/P-RERANKER-1.md`, `packages/P1-NEW-TICKETS-2026-10-31.md`
+- **Status:** ACCEPTED (owner, 2026-10-31, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-31)`; item 2 standing) · **Under:** DEC-974, DEC-979, DEC-906, DEC-953 · **Basis:** `packages/P-RERANKER-1.md`, `packages/P1-NEW-TICKETS-2026-10-31.md` · **Changed by:** DEC-1003 (the smart way of working is the product's)
 - **Decision:**
   1. **Filed as recommended:** W2-112 (`DAEO-clon`), one shared reranker for every session (P-RERANKER-1 (a)), after W2-32 and before ACT 2; W2-113 (`DAEO-g29a`), an adopted product's CTO named at adoption, after W2-110 and W2-52, before EXAMIN's copy; W2-114 (`DAEO-4eux`), W1-28's copy check reads code, not message text. **W2-114's revision of W1-28's acceptance test is the owner's named decision under DEC-906.**
   2. **The smart way of working becomes part of the Gov OS, not the CTO's own tools (standing):** the practices established in Wave 2, which replace bulk work with smart work: the secrets scan on new or changed content only (by content hash; a full scan in the nightly; the cache cleared on any rule or version change); scoped tests at every level, records and governance files never widening a run; the full suite once a day, in the nightly; a close refused only by failures its own change caused, proven with and without the change; every failure the change did not cause fixed at once or escalated, never left on a list; batch closes that take out a failing ticket and close the rest on the same run; test before merge (the merge queue), skipping a run when the merged code is identical; heavy jobs take a slot, everything else runs freely; failures re-run alone to filter out load, and timing tests time only their own work; checks done once per run, not before every search; shared services (one embedding service, one reranker) instead of a copy per session; the test designer and the engineer in parallel, the engineer seeing pass or fail only, QA batched per stream with core tickets individually; the designers' store kept separate, double-buffered, refreshed twice a day; and the audit's 10 practices for closing a ticket, which `gov close` itself must embody. The CTO maps each to the product (a feature that has it, a ticket that will give it and whether its spec and KPIs say so, or none), proposes the changes to existing tickets' specs and KPIs, and proposes new tickets as P1s (before or after EXAMIN's copy), naming what stays this repository's own and why: `packages/SMART-WORK-1.md`.
@@ -12403,7 +12403,7 @@
 | 0.371 | 2026-11-01 | Owner (recorded by the orchestrator, DEC-861): DEC-988 (P1-MORNING-2026-11-01's answers; the batch re-attributed on its results; root causes A (merge queue, one merge per ticket, the last green nightly as the baseline) and B (the freeze, a dead-man's switch ACT)). Next free id: DEC-989. |
 
 ### DEC-989 — The attribution baseline until a green nightly after ACT 1; a ticket's merge and close are one step (standing)
-- **Status:** ACCEPTED (owner, 2026-11-01, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-01)`; standing) · **Under:** DEC-988 items 3, DEC-968, DEC-959 item 1 · **Changes:** DEC-988 item 3's baseline until a fully green nightly exists after ACT 1
+- **Status:** ACCEPTED (owner, 2026-11-01, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-01)`; standing) · **Under:** DEC-988 items 3, DEC-968, DEC-959 item 1 · **Changes:** DEC-988 item 3's baseline until a fully green nightly exists after ACT 1 · **Changed by:** DEC-1045
 - **Decision:**
   1. **The baseline:** until a fully green nightly exists after ACT 1, a failure is attributed against **the last nightly that ran to a verdict**, its reds recorded as known (a red is cleared only if that nightly had it red, the same failure); never against code made by undoing merges. Once a green nightly exists after ACT 1, the last green nightly's head (DEC-988 item 3).
   2. **No ticket sits merged but not closed:** once W2-97's merge queue lands, a ticket's merge and its close are one step. When the queue's run on the candidate merge is green, the ticket merges and closes on that run, with its close record.
@@ -12424,7 +12424,7 @@
 | 0.373 | 2026-11-01 | Orchestrator (delegated): DEC-990 (P-W2-97-PM-1 (a), the tools folder in the project overlay). Next free id: DEC-991. |
 
 ### DEC-991 — The CTO's approvals: know the allow list; by day ping, then run; in the quiet hours never run, queue for 09:00 (standing)
-- **Status:** ACCEPTED (owner, 2026-11-01, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-01)`; standing) · **Under:** DEC-988 item 4 (the freeze), DEC-972, DEC-973, DEC-949 · **Changes:** the freeze fix proposed in the handover of 2026-11-01 (its items 1 and 2 are replaced by this rule; items 3 and 4 stand)
+- **Status:** ACCEPTED (owner, 2026-11-01, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-01)`; standing) · **Under:** DEC-988 item 4 (the freeze), DEC-972, DEC-973, DEC-949 · **Changes:** the freeze fix proposed in the handover of 2026-11-01 (its items 1 and 2 are replaced by this rule; items 3 and 4 stand) · **Changed by:** DEC-1050, DEC-1057
 - **Context:** the CTO's session froze from 01:46 to 10:37 on 2026-11-01 on one Bash call that needed a one-time approval (`rm -rf` of a `/tmp` folder, chained to a commit), and from 04:01 for 7 h 45 min on 2026-10-31 on an `owner-ping`. The old session's transcript holds 26 one-time approvals: 14 caused by `rm` in any form (the user settings' ask rules), 9 by `owner-ping` (ask rules), 3 by Claude Code's built-in safety check on `.claude/` paths (a `cp` reading from or writing to `.claude/`, even with `Bash(*)` allowed). Nothing else prompted.
 - **Decision (the owner's words, in order):**
   1. **Know your own allow list,** and before running a command, check whether it could need the owner's approval.
@@ -12463,7 +12463,7 @@
 | 0.375 | 2026-11-01 | Orchestrator (delegated): DEC-992 (W2-11's P-W2-11-1 to 8), DEC-993 (W2-81's round 2 for F1). Next free id: DEC-994. |
 
 ### DEC-994 — The owner's answers to ACT-DEADMAN-1, ACT-QUIET-DENY-1 and P1-ORCH-APPROVALS-1 (standing)
-- **Status:** ACCEPTED (owner, 2026-11-01, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-01)`; standing) · **Under:** DEC-991, DEC-988 item 4, DEC-974, DEC-982
+- **Status:** ACCEPTED (owner, 2026-11-01, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-01)`; standing) · **Under:** DEC-991, DEC-988 item 4, DEC-974, DEC-982 · **Changed by:** DEC-998 (item 1)
 - **Decision:**
   1. **ACT-DEADMAN-1: channel (b) only,** the push to the owner's phone through Remote Control (`--channel push`). Tested well before the crontab line goes in: (1) a forced test alert while the owner is away from the PC (the owner locks it for 20 minutes and says when); (2) a simulated stall, replaying a transcript, through the whole path to the push (in cron's bare environment), not just the alert call. The owner confirms on the phone whether each arrived; then the CTO brings the crontab line with `--channel push`. If (b) fails: why, and the options.
   2. **ACT-QUIET-DENY-1: yes, with `onFailure: block`;** the owner's operator added it (checked 12:57: the block is in `.claude/settings.local.json`; a session started in the main tree with the clock forced to 03:00 had a prompting `rm` refused at once and queued).
@@ -12568,7 +12568,7 @@
 
 
 ### DEC-1003 — Every practice the CTO adopts in its own tools is mapped into the product's tickets the same day (standing)
-- **Status:** ACCEPTED (owner, 2026-11-01, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-01)`; standing) · **Under:** DEC-982 (the smart way of working is the product's), DEC-983 (SMART-WORK-1), DEC-979 item 2 (the tools lane) · **Changes:** DEC-982's "a practice built only in your tools is a gap to name" becomes a same-day mapping
+- **Status:** ACCEPTED (owner, 2026-11-01, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-01)`; standing) · **Under:** DEC-982 (the smart way of working is the product's), DEC-983 (SMART-WORK-1), DEC-979 item 2 (the tools lane) · **Changes:** DEC-982's "a practice built only in your tools is a gap to name" becomes a same-day mapping · **Changed by:** DEC-1052, DEC-1057 (scoped, O-11)
 - **Decision:** (1) Today's four queue changes (DEC-1001 (a) to (d)) reach the Gov OS: each mapped, as SMART-WORK-1 did, to the product ticket that should carry it (W2-115, W2-117, W2-20 or W2-76 as fits), with its KPI change, as proposals for the owner (`packages/SMART-WORK-2.md`). (2) **Standing:** every new practice the CTO adopts in its own tools is mapped into the product's tickets the same day, as a KPI change proposal, so the smart way of working never lives only in the CTO's tools; the daily document lists each with its proposal.
 - **Where it goes (DEC-851):** this register; the prompt §0; the decisions-in-force list; RESUME HERE; the lighter lane's rule (DEC-979 item 2).
 
@@ -12663,7 +12663,7 @@
 | 0.393 | 2026-11-01 | Owner (recorded by the orchestrator, DEC-861): DEC-1011. Next free id: DEC-1012. |
 
 ### DEC-1012 — A rule broken twice becomes a mechanism (standing); RESEARCH-AGENT-FAILURES-1's other practices and KPI lines listed for the owner
-- **Status:** ACCEPTED (owner, 2026-11-01, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-01)`; standing) · **Under:** RESEARCH-AGENT-FAILURES-1 (row 9), DEC-1003, DEC-1007, DEC-979 item 2
+- **Status:** ACCEPTED (owner, 2026-11-01, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-01)`; standing) · **Under:** RESEARCH-AGENT-FAILURES-1 (row 9), DEC-1003, DEC-1007, DEC-979 item 2 · **Changed by:** DEC-1057
 - **Decision:** (1) **Any rule broken twice becomes a mechanism** (a check, a hook line in the CTO's tools lane, or a dispatcher duty), within a day, mapped into the product the same day (DEC-1003). Applied at once to the two rules broken twice today: hand-run lead chains (started with a trailing `&` twice, DEC-731) — `tools/lead_chain2.sh` and `lead_chain.sh` now refuse (leads start only through the dispatcher's ready list); the return watcher not re-armed (twice) — `lead_return_watch.sh` refuses (returns arrive in the dispatcher's inbox). (2) The package's other practices and its KPI lines are listed for the owner before approval. (3) Before tonight's handover, RESUME HERE fits in one read: older material moves to an archive file RESUME HERE points to. (4) Tonight: the handover before 02:00, the sentinel started, the fresh session's test push.
 
 | Version | Date | Change |
@@ -12794,7 +12794,7 @@
 | 0.409 | 2026-11-02 | Owner (recorded by the orchestrator, DEC-861): DEC-1027. Next free id: DEC-1028. |
 
 ### DEC-1028 — The push test passed; W2-55's table kept current by a mechanism; ACT-STOP-WAITER-1; W2-42a; a load-balancing plan before A; no CTO commits while an owner ACT is applied (item 6 standing)
-- **Status:** ACCEPTED (owner, 2026-11-02, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-02)`; item 6 standing) · **Under:** DEC-1022 item 1, DEC-1027, DEC-974, DEC-958, DEC-1012
+- **Status:** ACCEPTED (owner, 2026-11-02, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-02)`; item 6 standing) · **Under:** DEC-1022 item 1, DEC-1027, DEC-974, DEC-958, DEC-1012 · **Changed by:** DEC-1057 (6)
 - **Decision:** (1) ACT-PUSH-INPUT-1 passed: the 10:37 approval came from Claude Code's own push on the owner's phone. (2) W2-55, option (i): its backfill case reads the register as of the proposal file's own commit, not the moving base; and new rows are a mechanism, not a promise: the tool that records a decision adds that decision's row (W2-55's proposer gains an append mode that adds rows only for entries the file lacks, never rewriting a row, and the CTO's decision-recording tool runs it in the same commit). (3) ACT-STOP-WAITER-1: yes, applied by the owner's operator (`.claude/settings.local.json` holds `PermissionRequest` and `Stop`); its live check in the next fresh session. (4) P1-GUARD-PARSER-W2 (a): W2-42a filed (FULL), the eight parser lines of ACT-GUARD-FIX-3 in the product's guard, before EXAMIN's copy. (5) Decision A waits for one comprehensive load-balancing plan for this machine (20 threads, 24 GB for WSL, one GPU), as a package: (a) every rebuild and embedding request in a ticket's life and a landing batch's, by server, counted; (b) less work (seeding every copy from the warm integration store, the baseline read from the nightly's results, warm clones, one integration refresh per landing; next, one shared read-only index with per-worktree changes); (c) faster embedding (batching, separate traffic, the GPU's share, CPUs per server, real parallel runners, with figures); (d) how many agents at once, set by measured peaks, and how the dispatcher keeps it there; (e) one working hour measured (each server's and the rerankers' CPU and memory, requests by client); (f) one recommendation in order of impact, with targets (rebuilds per ticket, no timed-out embedding request, the busy-core band) and how each is checked. (6) Standing: while an ACT of the owner's is being applied, the CTO makes no main-tree commit (its tools included) until the owner says it is done (on 2026-11-02 the CTO committed twice in the main tree while ACT-GUARD-FIX-3 was applied). Mechanism: the CTO writes `log/act-in-progress.txt` when an ACT is handed over and ends it only on the owner's word.
 
 | Version | Date | Change |
@@ -12872,7 +12872,7 @@
 | 0.418 | 2026-11-02 | Orchestrator (delegated): DEC-1036. Next free id: DEC-1037. |
 
 ### DEC-1037 — The emergency re-pin in two windows; the full run on the re-pinned head; a clean restart before the freeze lifts; limits derived from the machine; a stop parks the queue's approvals
-- **Status:** ACCEPTED (owner, 2026-11-02 ~15:50; recorded by the orchestrator, DEC-861) · **Under:** DEC-1033, DEC-1032, DEC-105, DEC-1003 · **Changes:** DEC-954 Q8 (b) ("ACT 2, one re-pin"; P-W2-110-4 item 6): apply now
+- **Status:** ACCEPTED (owner, 2026-11-02 ~15:50; recorded by the orchestrator, DEC-861) · **Under:** DEC-1033, DEC-1032, DEC-105, DEC-1003 · **Changes:** DEC-954 Q8 (b) ("ACT 2, one re-pin"; P-W2-110-4 item 6): apply now · **Changed by:** DEC-1039 (3)
 - **Decision:** (1) P1-REPIN-EMERGENCY (`governance/project/orchestration/packages/P1-REPIN-EMERGENCY.md`) option (a): an emergency re-pin of the gov every session runs (`~/.local/bin/gov`, today `pin-5c401220` of 28 October) from `w2/integrate`, in two windows: window 1 after W2-122 and W2-123 land, then ACT-QUERY-GPU-2 in the same window once no process of the old pin runs; window 2 after W2-112 lands (with W2-126 if landed). Every check before the switch as the P1 lists, the guard's included (W2-84's reads); the old pin kept for an instant rollback (one rename); any failed check, or a broken search after the switch, means switching straight back to the old pin and telling the owner.
 (2) The full suite runs on the re-pinned head as soon as window 1 is done, not at night, while the freeze keeps the machine free; the CTO gives its expected time.
 (3) A clean restart before the freeze lifts, inside the emergency and within its rules (acceptance tests by test designers only, MR-3): every red of that full run listed with the ticket that fixes it (W2-90b and W2-105 among the six stopped; W2-90c, W2-66b, W2-55, W1-01b; any other), those landed and run first at top priority, and the full run repeated until it is green or every remaining red has its fix landing. Then the owner lifts the freeze and leads launch normally.
@@ -12889,7 +12889,7 @@
 | 0.419 | 2026-11-02 | Owner (recorded by the orchestrator, DEC-861): DEC-1037. Next free id: DEC-1038. |
 
 ### DEC-1038 — Machine changes outside the repository by ACT only; the CTO's checkpoint straight to scratch; the overload's standing targets, its incidents, and every heavy job through the gate
-- **Status:** ACCEPTED (owner, 2026-11-02 ~16:20; recorded by the orchestrator, DEC-861) · **Under:** DEC-1033, DEC-1032, DEC-1037, DEC-979, DEC-1011
+- **Status:** ACCEPTED (owner, 2026-11-02 ~16:20; recorded by the orchestrator, DEC-861) · **Under:** DEC-1033, DEC-1032, DEC-1037, DEC-979, DEC-1011 · **Changed by:** DEC-1057 (1)
 - **Decision:** (1) From now on, anything outside the repository that changes how the machine runs (files under `~/.local/bin`, `~/.config`, `~/.ollama`, the crontab, `.wslconfig`, services, environment files) comes to the owner as an ACT; the CTO and its agents do not place it themselves (the `~/.local/bin/ollama` wrapper of 15:50 was placed without one: accepted in DEC-1037 as an interim).
 (2) The CTO's checkpoint is written straight to scratch (`.gov-runtime/scratch/checkpoints/<ticket>/`), never under `docs/checkpoints/` and never moved by hand: `tools/cto_checkpoint.sh "<next action>" [inputs]` calls the checkpoint writer with its automatic destination (the Stop hook's) and fails if anything under `docs/checkpoints/` changed; the CTO no longer runs `gov checkpoint` in the main tree (two slips on 2026-11-02 came from moving that file by hand).
 (3) The WSL configuration: the owner's question answered by the CTO (below, "Recorded with it" (a)); no change before the RAM upgrade's planned restart.
@@ -12901,7 +12901,7 @@
 | 0.420 | 2026-11-02 | Owner (recorded by the orchestrator, DEC-861): DEC-1038. Next free id: DEC-1039. |
 
 ### DEC-1039 — The emergency plan: every infrastructure fix now as an emergency patch, re-pinned as often as needed; the tests and code inventoried and refactored; the full suite until green; the Wave 2 plan refactored; then the lift and the formal closes
-- **Status:** ACCEPTED (owner, 2026-11-02 ~18:20; recorded by the orchestrator, DEC-861) · **Under:** DEC-1033, DEC-1032, DEC-1037, DEC-1038, DEC-105, DEC-1003, MR-3 · **Changes:** DEC-1037 (3) (the clean restart through tickets) and the ticket path for the infrastructure fixes, for the emergency's length
+- **Status:** ACCEPTED (owner, 2026-11-02 ~18:20; recorded by the orchestrator, DEC-861) · **Under:** DEC-1033, DEC-1032, DEC-1037, DEC-1038, DEC-105, DEC-1003, MR-3 · **Changes:** DEC-1037 (3) (the clean restart through tickets) and the ticket path for the infrastructure fixes, for the emergency's length · **Changed by:** DEC-1047, DEC-1049 (item 3), DEC-1052
 - **Decision (the owner's plan, in order, all in emergency mode):**
 (1) No infrastructure fix waits for the normal ticket path. Every one is done now as an emergency patch, out of the ordinary, with the same rules as the reds (an acceptance test that must change is revised by a test designer; a review where needed): the shared reranker on the GPU (W2-112); W2-122's seeding and W2-123's bounded retry; the vector cache (W2-126); the real gitleaks fix (each gate slot confined to its share of the CPUs with taskset, the secret scan's pool sized to the CPUs it may use, nightly.sh's runs included); the machine-derived limits and the standing targets (`BRIEF-MACHINE-TARGETS.md`). Re-pin as many times as needed, each with its checks and rollback, as window 1, so every bottleneck and non-smart way of working is gone.
 (1b) **Added by the owner, 2026-11-02 ~18:40, part of the emergency fixes:** with the infrastructure fixes, a Gov Load Balancer, for this repository now and for the Gov OS: leads, closes, landings and rebuilds planned together by their phases and each phase's measured peak on every resource (CPU, RAM, the GPU and its memory), pairing GPU-heavy work (leads searching, rebuilds embedding) with CPU-heavy work (test runs) so neither peaks twice at once, keeping the embedders and rerankers on the GPU within its budget, even if that limits leads to two or three. The rule documented: the GPU's dedicated memory never spills into shared memory, and never runs out into a CUDA crash; the load balancer and the dispatcher tested on it, and on the phase balancing. In the CTO's tools first; for the Gov OS, the CTO proposes whether it is its own ticket or KPI lines in W2-20 and W2-121 (DEC-1003).
@@ -12976,7 +12976,7 @@
 | 0.429 | 2026-11-02 | Orchestrator (delegated): DEC-1046. Next free id: DEC-1047. |
 
 ### DEC-1047 — The emergency raised one level: everything stopped but the memory infrastructure; a harsh investigation of what to lift, measured against the Gov OS's aim; DEC-1010 stays
-- **Status:** ACCEPTED (owner, 2026-11-02 ~21:40, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-02)`; standing until the owner lifts it) · **Under:** DEC-1039, DEC-1045, DEC-1033, DEC-1010, DEC-953 · **Changes:** DEC-1039's order (the investigation and the owner's decisions on it come before steps 2's refactor, 3 and 3b)
+- **Status:** ACCEPTED (owner, 2026-11-02 ~21:40, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-02)`; standing until the owner lifts it) · **Under:** DEC-1039, DEC-1045, DEC-1033, DEC-1010, DEC-953 · **Changes:** DEC-1039's order (the investigation and the owner's decisions on it come before steps 2's refactor, 3 and 3b) · **Changed by:** DEC-1049, DEC-1051 (item 1)
 - **Why (the owner's words, in short):** for two weeks the machine was fought instead of the product built; process meant to protect became the work. Gitleaks guarding a private repository ran on every rebuild, landing, close and test run (W2-69's tests alone started about 120 gitleaks from one slot; load 54 to 76 on 20 CPUs); per-session rerankers crashed the GPU; cold rebuilds; checks and ceremonies everywhere, every time.
 - **The aim (the yardstick):** the Gov OS stops drift and makes the owner's agents work, and record their work, as a good software company does; not a security battle, not a rule battle. It needs: a good tool extending the agents' memory (RAG and combined memory); help developing the spec and the KPIs (research and discovery agents) and their execution by other agents; roles whose permissions keep apart work whose interests conflict (the builder never writes or reads its own acceptance tests; the reviewer never fixes what it reviews); governance of the WBS and of tickets' launching and closing with well-structured dependencies ("governing the traffic, not governing a city"). What matters is tests and code that match the KPIs and the spec and pass green; everything else must justify itself.
 - **Decision:** (1) **Stop** every ticket and lead now, at safe points, except the memory infrastructure: W2-112 finishes its last review round (done; P-W2-112-F9 with the owner), W2-126 finishes, the W2-122 + W2-123 landing completes. W2-42a stopped at a safe point (both agents). The Load Balancer stays on. DEC-1045 applies as decided (the orchestrator's reading: its product switch, an application of DEC-1045, continues). Nothing else starts. (2) **The investigation**, harsh, read-only, in chunks across parallel agents within the Load Balancer, one agent combining the findings into one list without duplicates: (a) ten named practices to start with (the full `gov check` in every lead's verification; real-model tests W1-19, W1-21 in tickets' runs; the guard's ~9,000 tests in tickets' runs; `gov context` loading the whole register for every cited decision, 1.6 million tokens against 6,000; the 56,000-character lead briefs; the guard-refusal harvest re-scanning every transcript every minute; attribution re-running each red three times with and without the batch; tests starting their own code-graph daemons; review effort not matched to risk; the ceremony around small decisions), and every other problem of the kind; (b) the Gov OS itself (its rules, gates, checks, records and ceremonies, the guard's rules included, and the code and tests that exist only to build or enforce them); (c) the CTO's own tools and practices; (d) the WBS and the tickets (which tickets and KPI lines exist only to build, extend or polish what is to be lifted; which are still needed for the aim; which can be merged or retired; feeding DEC-1039 step 3b). For each: its cost (machine time, tokens, the owner's time), what it protects, and the recommendation (lift, scope to the change, move to the nightly, keep). The benchmark is DEC-1010's test: a rule, check or ceremony earns its place only where what it guards against is within the aim, reachable in ordinary work, and would otherwise fail open or lose work; anything else that blocks or slows work is bureaucracy, recommended lifted. And one question answered with reasons and costs: copy what works into a fresh repository and start over with less bureaucracy, or keep this repository and lift and refactor here. **The list comes to the owner first; nothing is lifted before the owner decides.** (3) **What stays, whatever the investigation finds:** DEC-1010 (a moderator triages every finding against the ticket's own scope and KPIs; a finding blocks only if in scope, reachable in ordinary work, and failing open or losing work; at most two review rounds, then the owner once; READY computed by code, `verdict.py`, from each reviewer's structured verdict, never declared by an agent).
@@ -12986,7 +12986,7 @@
 | 0.430 | 2026-11-02 | Owner (recorded by the orchestrator, DEC-861): DEC-1047. Next free id: DEC-1048. |
 
 ### DEC-1048 — P-W2-112-F9 (c): the interim GPU-slot module stays as the machine-wide guard and W2-112's code lands; a cleanup approved; P-LB-PRODUCT-1 after the investigation; the DEC-1045 product switch continues
-- **Status:** ACCEPTED (owner, 2026-11-02 ~21:50, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-02)`; item 5 delegated, for the owner to overturn) · **Under:** DEC-1010, DEC-105, DEC-1047, DEC-1046, DEC-1043, DEC-1036
+- **Status:** ACCEPTED (owner, 2026-11-02 ~21:50, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-02)`; item 5 delegated, for the owner to overturn) · **Under:** DEC-1010, DEC-105, DEC-1047, DEC-1046, DEC-1043, DEC-1036 · **Changed by:** DEC-1051 (item 1)
 - **Decision:** (1) **P-W2-112-F9 (c), as recommended:** keep the interim module (`gov-reranker-gpu-slot.pth`, ACT-RERANK-GPU-SLOTS-1) as the machine-wide guard (it caps every reranker, whatever its tree's commit); W2-112's KPI success-7 re-baselined: §5 of the research document records that the module is not to be retired by an ACT now, and is retired only when old code fails closed by construction ((b), a later ticket); a test designer revises `test_w2_112_retirement_act.py` to it (`Rewrite-Reason: DEC-1048`); its engineer rewrites §5; then W2-112's code lands through the queue. No third review round (DEC-1010): the change after round 2 is the re-baselined text and its test, checked by the lead's acceptance run. W2-112 is memory infrastructure and finishes under DEC-1047. (2) The owner approved removing `/tmp/gov-launch-engineer-y6het9bm` (done, 21:51). (3) P-LB-PRODUCT-1 waits for the investigation's list (DEC-1047). (4) The DEC-1045 product switch continues. (5) (delegated) DEC-1046 item 1 (P-W2-112-SLOTS (i), no private reranker beside the service in the product) moves after W2-112's landing, as a follow-up (the owner: "land W2-112's code"); `tools/rerank_service_slot_hold.py` stays the interim guard meanwhile.
 
 | Version | Date | Change |
@@ -13019,7 +13019,7 @@
 | 0.434 | 2026-11-02 | Owner (recorded by the orchestrator, DEC-861): DEC-1051. Next free id: DEC-1052. |
 
 ### DEC-1052 — P1-LIFT-1 and P1-PLAN decided: the basis, the rows, the templates with READY and DONE by code, the test suite cut to about 5,000, the homes, the updated plan, tonight's restart
-- **Status:** ACCEPTED (owner, 2026-11-02 ~23:58, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-02)`; standing) · **Under:** DEC-1047, DEC-1050, DEC-1051, DEC-1010, DEC-1039 · **Changes:** DEC-1003 (a practice enters the product only after it has proven itself in use), DEC-851 item 1 and DEC-943 item 1 (the templates' four recommendations), DEC-957's review effort kept, DEC-1039 steps 2, 3, 3b and the order of the plan
+- **Status:** ACCEPTED (owner, 2026-11-02 ~23:58, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-02)`; standing) · **Under:** DEC-1047, DEC-1050, DEC-1051, DEC-1010, DEC-1039 · **Changes:** DEC-1003 (a practice enters the product only after it has proven itself in use), DEC-851 item 1 and DEC-943 item 1 (the templates' four recommendations), DEC-957's review effort kept, DEC-1039 steps 2, 3, 3b and the order of the plan · **Changed by:** DEC-1055
 - **The basis (standing):** everything is judged on one question: does it help deliver tests and code that match the KPIs and the spec, with less drift? In order: (1) does it serve memory, spec-and-KPI development, role separation, or the traffic of tickets; (2) without it, would ordinary work fail open or lose work (DEC-1010); (3) does it run only where the risk is (the change, or the full suite), not everywhere every time; (4) does it make agents deliver more with less drift, or only add records, approvals and pings; (5) a practice enters the product only after it has proven itself in use, never the same day.
 - **The rows** (`packages/INVESTIGATION-1-COMBINED.md`): **approved:** T-2, T-3 (first), T-6 to T-11, T-13; Q-2 to Q-14; G-4 to G-9, G-13; M-2, M-3, M-5, M-6; R-6, R-7, R-9, R-10, R-12, R-13; O-5, O-8, O-9, O-11, O-12, O-13; K-1 to K-4; W-1 to W-10. **R-1 to R-5, O-1, O-2, O-4:** no cuts; the templates replace them. **O-3 refused:** a fresh CTO session every day; orchestrators keep long contexts. **O-6:** ACTs are for machine changes (installs, services, crontab) and only where they help; restarts of the repository's own servers from committed configs are approved by class; no ACTs for records. **G-12 refused:** review effort stays as it is. **G-3:** the hidden half of the memory measure moves outside every worktree, so no guard rule is needed for it. **G-14:** role separation is enforced deterministically from the path map: each role's reads and writes are its paths; the engineer never reads the acceptance tests; the test designer never reads the engineer's new code (it may read the integrated code, DEC-963); simple path checks, no shell guessing; repeated QA findings mean the spec is missing something and go back to product-spec. **M-1:** W2-04 accepted as built; no more runs on it. **M-4:** memory embeds the WBS, the specs and KPIs, the tickets, the code and the decisions; tests and the close, checkpoint and probe records are not embedded (they stay in keyword search, and tickets link to their tests); W2-61's measure before and after. **E1 and R1-21:** yes, inside the refactoring, E1 before the guard ACT. **Option A:** the product switches are re-scoped tickets after the resume.
 - **The templates:** the four recommendations approved (TPL-1 to TPL-8 as one package, the three scripts first; lines waiting on decisions become switches in the facts file; DEC-851 and DEC-943 narrowed for templates: a line only where it changes what is done, one owner, product-spec writes and the CTO approves, gaps closed by a tool or a measured line; the six measures report only). **READY and DONE are computed by code from the filled templates** (the required fields: non-goals, how each KPI line is verified, the definition of done), as `verdict.py` computes READY from a review; not warnings.
@@ -13153,7 +13153,7 @@
 | 0.449 | 2026-11-03 | Owner (recorded by the orchestrator, DEC-861): DEC-1065. Next free id: DEC-1066. |
 
 ### DEC-1066 — D4B-GAPS decided: G1, G3, G2 as W2-32's rounds; W2-32's KPIs cover the fusion; G4 in D-7; Q09 re-labelled; a research and discovery agent on retrieval now; a measure 4 if room remains
-- **Status:** ACCEPTED (owner, 2026-11-03 ~23:15, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-03)`) · **Under:** DEC-1055, DEC-1065 (3), DEC-1060, DEC-957 (95 %), W2-15a's KPI (the gaps chosen with the owner) · **Source:** `governance/project/orchestration/packages/LIFT-1/D4B-GAPS.md` (`dcb6da73`); W2-15a's evidence record (`docs/research/EXP-003/w2-15a-baseline.md`, merged `ff691ec2`)
+- **Status:** ACCEPTED (owner, 2026-11-03 ~23:15, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-03)`) · **Under:** DEC-1055, DEC-1065 (3), DEC-1060, DEC-957 (95 %), W2-15a's KPI (the gaps chosen with the owner) · **Source:** `governance/project/orchestration/packages/LIFT-1/D4B-GAPS.md` (`dcb6da73`); W2-15a's evidence record (`docs/research/EXP-003/w2-15a-baseline.md`, merged `ff691ec2`) · **Changed by:** DEC-1067 (2)
 - **Decision:** (1) W2-32's three rounds, in this order: **G1** (the embedder and the reranker read the whole chunk; parent expansion keeps its expanded parents across continuations), **G3** (the fusion keeps each route's top hits), **G2** (keyword ranking tuned for code questions). (2) **W2-32's KPIs change to cover G3:** its gap lines name the fusion keeping each route's top hits (DEC-1065 (3)). (3) **G4 now, inside D-7:** the evaluation set's own documents (lens B's report, `docs/assessment/2026-10/B-memory-retrieval.md`, and the evaluation fixtures, `fixtures/evaluation/**`) are kept out of **both** indexes (the vectors and the keyword index). (4) **Q09 re-labelled blind** by a session independent of the retrieval work, the old label kept on record, as q03 was (DEC-1060). (5) **A research and discovery agent now, in parallel** (not after S9; the owner's target 95 %, higher believed reachable), read-only, no install: how the best open-source retrieval systems fuse and combine routes and what they measure (fusion methods: rank fusion and variants, weighted fusion, score normalisation, keeping each route's top hits, routing by question type; reranker types: cross-encoders of several sizes, late-interaction models, multi-chunk rerankers, LLM rerankers, with their gains; stronger embedders, chunking strategies, query rewriting; for each the published metrics, the GPU and time cost on this machine beside what already runs, and what it needs from the owner); every method that needs no install (a fusion rule, a cut, a weight) tried on measure 1's own route rankings, hit@5 and full evidence on the 48 questions with the hidden half separately; a package to the owner with the CTO's view on what changes before measure 3. (6) If room for improvement remains after W2-32's rounds, **a measure 4** is added.
 - **Basis:** question 1 (memory, the Gov OS's first aim) and question 2 (a measure contaminated by its own documents fails open on memory's acceptance); question 5 (a method enters the product after it is shown on the measure).
 
@@ -13525,7 +13525,7 @@
   code, not warned).
 
 ### DEC-1084 — D9-FATES §5 decided and the fates applied; exit criterion 5 re-worded; the spill floor 2,048 MiB; the measure re-anchors in memory (a W2-61h line); ACT-GUARD-SETS-1 decided; L5 and an 80-candidate cell measured; the bundle's figures asked
-- **Status:** ACCEPTED (owner, 2026-11-06, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-06)`) · **Under:** DEC-1083, DEC-1082 (3), DEC-1081 (3), DEC-1079 · **Source:** `governance/project/orchestration/packages/LIFT-1/D9-FATES.md` (v2.1), `packages/ACT-GUARD-SETS-1.md`, `packages/LIFT-1/D4B-SCORE-ONCE.md` · **Changes:** DEC-1083 (7) (W2-66b and W2-90c)
+- **Status:** ACCEPTED (owner, 2026-11-06, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-06)`) · **Under:** DEC-1083, DEC-1082 (3), DEC-1081 (3), DEC-1079 · **Source:** `governance/project/orchestration/packages/LIFT-1/D9-FATES.md` (v2.1), `packages/ACT-GUARD-SETS-1.md`, `packages/LIFT-1/D4B-SCORE-ONCE.md` · **Changes:** DEC-1083 (7) (W2-66b and W2-90c) · **Changed by:** DEC-1087 (13) (W2-33's layer lines back in Wave 2)
 - **Decision:**
   - **D9-FATES §5:**
     - (1) W2-111 stays open as a LITE test revision outside K9.
```

```diff w2-130:patch-a2
diff --git a/docs/DECISION_REGISTER.md b/docs/DECISION_REGISTER.md
--- a/docs/DECISION_REGISTER.md
+++ b/docs/DECISION_REGISTER.md
@@ -862,7 +862,7 @@
 | 0.14 | 2026-10-01 | S1-A round 1: DEC-088 (audit triggers), DEC-089 (gap tickets in W1), DEC-090 (A0–A11), DEC-091 (parent-child retrieval W1), DEC-092 (covers lists), DEC-093 (five-package cap, P1 bypass), DEC-094 (test execution, integration roles W2), DEC-095 (DEC-040: ACCEPTED as amended by DEC-083). |
 
 ### DEC-096 — Loop policy: iterate to convergence; escalate after three consecutive non-converging iterations
-- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER · **Amends:** DEC-044, DEC-070, DEC-082 · **Changed by:** DEC-953 (item 1)
+- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER · **Amends:** DEC-044, DEC-070, DEC-082 · **Changed by:** DEC-953 (item 1) · **Changed by:** DEC-1010
 - **Decision:** Any iterative loop that runs until convergence (review→repair, audit→repair, test→fix, verification)
   continues until it converges, or until three consecutive iterations fail to converge. The third consecutive failure
   produces an escalation package for the owner: each iteration's outcome, why it is not converging, and the options
@@ -1707,7 +1707,7 @@
 KPI disputes (KD-1…KD-3), the orchestrator's DP-5, and two items the orchestrator reported.
 
 ### DEC-183 — Worker identity and headless flags until the launcher exists
-- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on the W1 orchestrator's report · **Under:** DEC-161, DEC-107 · **Changed by:** superseded by DEC-371 for the roles the launcher starts (shown by DEC-825, 2026-10-19)
+- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, on the W1 orchestrator's report · **Under:** DEC-161, DEC-107 · **Changed by:** superseded by DEC-371 for the roles the launcher starts (shown by DEC-825, 2026-10-19) · **Changed by:** DEC-205 (the command's first word), DEC-235
 - **Decision:**
   - Until W1-46 closes, every headless worker session is started with
     `--settings '{"env":{"GOV_ROLE":"<role>","GOV_TICKET":"<id>"}}'`, which overrides the `env` block in
@@ -1922,7 +1922,7 @@
   prefix `PATH=~/.nvm/versions/node/v22.23.3/bin:$PATH`.
 
 ### DEC-208 — The orchestrator's context limit: about 300k tokens, automatic from W1-29
-- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER · **Under:** DEC-025, CAP-37 · **Changed by:** its 300k context limit and auto-compact threshold superseded by DEC-838 (the model's full window, no threshold); marked by DEC-866, 2026-10-20
+- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER · **Under:** DEC-025, CAP-37 · **Changed by:** its 300k context limit and auto-compact threshold superseded by DEC-838 (the model's full window, no threshold); marked by DEC-866, 2026-10-20 · **Changed by:** DEC-237, DEC-250 (the main orchestrator's `CONTEXT_CHECKPOINT` stop)
 - **Decision:**
   - The orchestrator checkpoints and stops with `CONTEXT_CHECKPOINT` at about 300k tokens used, of a 1M window. Its
     prompt says so since commit `66e09aa1`.
@@ -2268,7 +2268,7 @@
   - Tickets, claims, the register and `bootstrap.md` are edited only by the main orchestrator, in the main tree.
 
 ### DEC-237 — Context limits for the main orchestrator and the ticket leads
-- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER (orchestrator prompt v4, section 7 and brief A5) · **Amends:** DEC-208 · **Changed by:** its 300k stops for the orchestrator and the leads superseded by DEC-838 (no early stop; a checkpoint at every handover, DEC-837); marked by DEC-866, 2026-10-20
+- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER (orchestrator prompt v4, section 7 and brief A5) · **Amends:** DEC-208 · **Changed by:** its 300k stops for the orchestrator and the leads superseded by DEC-838 (no early stop; a checkpoint at every handover, DEC-837); marked by DEC-866, 2026-10-20 · **Changed by:** DEC-250
 - **Decision:**
   - The main orchestrator stops with `CONTEXT_CHECKPOINT` at about 300k tokens, after a merge or a close. Leads
     keep running in their worktrees.
@@ -2567,7 +2567,7 @@
     `Task: DAEO-1ve2`.
 
 ### DEC-261 — W1-18 DP-2: `gov` starts the daemon and never stops it
-- **Status:** ACCEPTED (owner, 2026-10-04); amended by DEC-798 (2026-10-19: a second, CPU-only daemon for query embeddings) · **Basis:** OWNER, on W1-18 package DP-2 option (a) · **Under:** DEC-074 Q4, ADR-0002 §3
+- **Status:** ACCEPTED (owner, 2026-10-04); amended by DEC-798 (2026-10-19: a second, CPU-only daemon for query embeddings) · **Basis:** OWNER, on W1-18 package DP-2 option (a) · **Under:** DEC-074 Q4, ADR-0002 §3 · **Changed by:** DEC-1033
 - **Decision:**
   - `gov` starts `ollama serve` on demand and never stops it. Ollama's 5-minute idle unload frees the model's GPU
     memory, which was the owner's intent.
@@ -4360,7 +4360,7 @@
 The owner was told on 2026-10-05.
 
 ### DEC-410 — W1-50 DP-21 to DP-28: a merge commit's own change to a ticket file or an acceptance test is a finding whatever its trailers; a path both sides changed is the merge commit's own; 24 parents at most
-- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-05) · **Basis:** W1-50 packages DP-21 (b), DP-22 (the complement), DP-23 (a), DP-24 (b), DP-25 (a), DP-26 (a), DP-27 (b), DP-28 (a); the fifth reviewer's findings F1 to F9 · **Amends:** DEC-403 (the octopus sentence; what `brought` holds) · **Under:** CAP-58, DEC-269, DEC-255, DEC-359, DEC-401 · **Changed by:** DEC-918: under `tests/acceptance/`, a path both parents changed is not the merge commit's own change when the merge holds exactly git's own merge of that file
+- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, stricter-only, 2026-10-05) · **Basis:** W1-50 packages DP-21 (b), DP-22 (the complement), DP-23 (a), DP-24 (b), DP-25 (a), DP-26 (a), DP-27 (b), DP-28 (a); the fifth reviewer's findings F1 to F9 · **Amends:** DEC-403 (the octopus sentence; what `brought` holds) · **Under:** CAP-58, DEC-269, DEC-255, DEC-359, DEC-401 · **Changed by:** DEC-918: under `tests/acceptance/`, a path both parents changed is not the merge commit's own change when the merge holds exactly git's own merge of that file · **Changed by:** DEC-421 (DP-24)
 - **Decision:**
   - DP-21: a change to a file under `.tickets/**` that a merge commit itself makes (its own change, by the helper)
     is a finding whatever the merge commit's trailers, also with orchestrator trailers or none.
@@ -4898,7 +4898,7 @@
     other check gains this answer, and the answer is never green.
 
 ### DEC-448 — `gov doctor`: registered tool locations, historical records, one rebuild, and the Claude Code drift
-- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** `gov doctor` on this repository: Node 18 found against 22 pinned, `openspec` and `ccusage` not found, 180 references to moved paths, a stale index, Claude Code drift · **Under:** DEC-202, DEC-210, DEC-440 · **Changed by:** its one-off limit superseded by DEC-477 (its other parts stand) (shown by DEC-825, 2026-10-19)
+- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** `gov doctor` on this repository: Node 18 found against 22 pinned, `openspec` and `ccusage` not found, 180 references to moved paths, a stale index, Claude Code drift · **Under:** DEC-202, DEC-210, DEC-440 · **Changed by:** its one-off limit superseded by DEC-477 (its other parts stand) (shown by DEC-825, 2026-10-19) · **Changed by:** DEC-456 (the set of historical records)
 - **Decision:**
   - Each tool is checked at its registered location (the PATH prefix of DEC-202 and the registry's paths),
     not only on PATH, so Node 22, `openspec` and `ccusage` are found where they are installed. The machine's
@@ -4962,7 +4962,7 @@
     No second rule set is written anywhere.
 
 ### DEC-454 — What `gov close` measures where its KPI lines left the mechanism open
-- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; the owner may overturn any point) · **Basis:** W1-30's second return (six packages for the owner) and the orchestrator's reading of the code against each KPI clause (DEC-449): the disposition of every finding was a constant, a context that could not be built was replaced by a hash of the ticket file, "the regression tests" were two folders of unit tests, the reviewer's "wrote nothing" was the record's own word, a fourth iteration had no owner's decision to wait for, and the stale-evidence rule measured nothing · **Under:** DEC-096, DEC-136, DEC-137, DEC-413, DEC-425 · **Changed by:** DEC-908 (for one part): an identical refusal reuses and names its repair ticket (W2-07's KPI 10, W2-M252).
+- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; the owner may overturn any point) · **Basis:** W1-30's second return (six packages for the owner) and the orchestrator's reading of the code against each KPI clause (DEC-449): the disposition of every finding was a constant, a context that could not be built was replaced by a hash of the ticket file, "the regression tests" were two folders of unit tests, the reviewer's "wrote nothing" was the record's own word, a fourth iteration had no owner's decision to wait for, and the stale-evidence rule measured nothing · **Under:** DEC-096, DEC-136, DEC-137, DEC-413, DEC-425 · **Changed by:** DEC-908 (for one part): an identical refusal reuses and names its repair ticket (W2-07's KPI 10, W2-M252). · **Changed by:** DEC-868 (items 1 (b) and 3), DEC-899 (P-IS-4 (a))
 - **Decision:**
   - **The regression tests** of a close are every test under the project's `tests/` outside the ticket's own
     acceptance folder. All run to their end. A failure, a collection error or a time limit reached refuses the
@@ -4989,7 +4989,7 @@
 ## 113. One delegated decision: where the owner's choice after an escalation is recorded (register v0.113, appended by the W1 orchestrator on branch `w1/integrate`)
 
 ### DEC-455 — The owner's choice after an escalation is the register entry; `gov close` records its id, and every refusal for a finding counts
-- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; the owner may overturn it) · **Basis:** W1-30's test designer (round 4): DEC-096 and CAP-59.a name six options for the owner (fix differently, narrow, split, defer, delete, continue) but no field that records which was chosen; and the orchestrator's reading of `gov close` (DEC-449) after its lead's third start ended unfinished: only failing tests were counted as an iteration · **Under:** DEC-096, DEC-454, CAP-59.a · **Changed by:** DEC-868 item 3 and DEC-908 (for one part): a broken context is refused at once by the pre-close `gov check`, uncounted, not a counted iteration.
+- **Status:** ACCEPTED (orchestrator, delegated under DEC-416, 2026-10-07; the owner may overturn it) · **Basis:** W1-30's test designer (round 4): DEC-096 and CAP-59.a name six options for the owner (fix differently, narrow, split, defer, delete, continue) but no field that records which was chosen; and the orchestrator's reading of `gov close` (DEC-449) after its lead's third start ended unfinished: only failing tests were counted as an iteration · **Under:** DEC-096, DEC-454, CAP-59.a · **Changed by:** DEC-868 item 3 and DEC-908 (for one part): a broken context is refused at once by the pre-close `gov check`, uncounted, not a counted iteration. · **Changed by:** DEC-899 (P-IS-4 (a))
 - **Decision:**
   - The owner's choice is recorded where the owner records decisions: in the register entry itself, in its text.
     `gov close` takes that entry's id as an argument, accepts it only when the ticket is escalated and W1-11's
@@ -5407,7 +5407,7 @@
 - **Orchestrator's reading, recorded as such:** DEC-476 keeps `gov close` without a baseline inside it, so "do not count toward escalation" is applied outside the tool: where the tool's own counter is raised by such a refusal, the orchestrator does not treat it as an iteration, and a block reached only by such refusals is brought to the owner as that, not as a looping ticket.
 
 ### DEC-493 — W1-39's allowed paths gain the doctor call site, the overlay's path map, Copier's standard answers file and an ignore file
-- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** package P-7, from the W1-39 lead's packages P-1, P-2 and P-5 and two residuals of earlier tickets. · **Changed by:** DEC-896 item 2 and DEC-903 (for one part): the overlay holds the path map and the test map.
+- **Status:** ACCEPTED (owner, 2026-10-07) · **Basis:** package P-7, from the W1-39 lead's packages P-1, P-2 and P-5 and two residuals of earlier tickets. · **Changed by:** DEC-896 item 2 and DEC-903 (for one part): the overlay holds the path map and the test map. · **Changed by:** DEC-904 (the overlay)
 - **Decision:** W1-39's `allowed_paths` gain, each in its own commit with `Task: DAEO-5ylr`:
   - `src/gov/doctor/command.py` and `tests/unit/doctor/**`, for the lock-comparison call only;
   - `template/governance/project/**`, shipping a minimal path map that an update never overwrites;
@@ -5695,7 +5695,7 @@
 ## 142. Owner answers: the regression after every merge again, W1-40 and W1-31 close, W1-41's paths and follow-up, when the close exceptions end, the guard against two files (register v0.142, appended by the W1 orchestrator on branch `w1/integrate`)
 
 ### DEC-518 — DEC-513 amended: a full regression runs after every merge into `w1/integrate`
-- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER. DEC-513's premise was wrong: `gov close` runs only the ticket's own acceptance suite. · **Amends:** DEC-513 · **Changed by:** corrected by DEC-533 (shown by DEC-825, 2026-10-19)
+- **Status:** ACCEPTED (owner, 2026-10-08) · **Basis:** OWNER. DEC-513's premise was wrong: `gov close` runs only the ticket's own acceptance suite. · **Amends:** DEC-513 · **Changed by:** corrected by DEC-533 (shown by DEC-825, 2026-10-19) · **Changed by:** DEC-536
 - **Decision:**
   - A full regression runs after every merge into `w1/integrate`, as before DEC-513. One is run now at the current head, since W1-31 was merged without one.
   - If the parallel trial passes (DEC-515), the W1-30 follow-up makes `gov close`'s regression step run every suite, in parallel; then the separate regression is dropped.
@@ -7562,7 +7562,7 @@
 ## 220. The owner's exit decision of 2026-10-16: Wave 1 passes with accepted exceptions (register v0.220, prepared by the W1 orchestrator on branch `w1/integrate`, committed by the owner)
 
 ### DEC-718 — Wave 1 passes with accepted exceptions: every finding of the exit audit and every exception of DEC-714 is named with what closes it and its Wave 2 owner; the adoption-readiness block passes before any pilot adoption
-- **Status:** ACCEPTED (owner, 2026-10-16; committed by the owner with `Role: owner`) · **Under:** DEC-412, DEC-465, DEC-565, DEC-584, DEC-626, DEC-704, DEC-712, DEC-714, DEC-715, DEC-716, DEC-717 · **Basis:** the W1-43 exit audit, `docs/audit/wave-1/W1-43-wave-1-exit-audit.md` with its context pack beside it. The owner committed both in a plain terminal as `82459573`, after the auto-mode classifier had refused the auditor's commit and then the operator's, and after the owner had the lefthook hooks uninstalled again (F-M13). The verdict is FAIL as the record stands at `60ea6924`, with no BLOCKER. It has 13 MAJOR findings (F-M1 to F-M13) and 10 MINOR (F-m1 to F-m10). The auditor's option (a): one owner decision, committed with `Role: owner`, accepts the findings as named exceptions, each with what closes it and a Wave 2 owner on one consolidated Wave 2 list. That turns the verdict into PASS WITH ACCEPTED EXCEPTIONS without further audit work. Since the audit the owner has switched auto mode off (`permissions.disableAutoMode`) and made accept-edits the default mode, with an owner-curated allow list; agents may not `git push`. · **Changed by:** DEC-900: item 11's first exception (RETR-X-02) is closed by the owner's AR-9 ruling, the stated gap; W1-42's two accepted reds are retired with their entries.
+- **Status:** ACCEPTED (owner, 2026-10-16; committed by the owner with `Role: owner`) · **Under:** DEC-412, DEC-465, DEC-565, DEC-584, DEC-626, DEC-704, DEC-712, DEC-714, DEC-715, DEC-716, DEC-717 · **Basis:** the W1-43 exit audit, `docs/audit/wave-1/W1-43-wave-1-exit-audit.md` with its context pack beside it. The owner committed both in a plain terminal as `82459573`, after the auto-mode classifier had refused the auditor's commit and then the operator's, and after the owner had the lefthook hooks uninstalled again (F-M13). The verdict is FAIL as the record stands at `60ea6924`, with no BLOCKER. It has 13 MAJOR findings (F-M1 to F-M13) and 10 MINOR (F-m1 to F-m10). The auditor's option (a): one owner decision, committed with `Role: owner`, accepts the findings as named exceptions, each with what closes it and a Wave 2 owner on one consolidated Wave 2 list. That turns the verdict into PASS WITH ACCEPTED EXCEPTIONS without further audit work. Since the audit the owner has switched auto mode off (`permissions.disableAutoMode`) and made accept-edits the default mode, with an owner-curated allow list; agents may not `git push`. · **Changed by:** DEC-900: item 11's first exception (RETR-X-02) is closed by the owner's AR-9 ruling, the stated gap; W1-42's two accepted reds are retired with their entries. · **Changed by:** DEC-953
 - **Decision:**
   1. **Wave 1 passes with accepted exceptions** (the auditor's option (a)). The exit verdict is PASS WITH ACCEPTED EXCEPTIONS. Every finding below is an accepted exception, named with what closes it and its Wave 2 owner.
      - "Wave 2 owner" names the role that does the work. The orchestrator coordinates every item; *owner* marks the owner's own acts.
@@ -7692,7 +7692,7 @@
   4. The queued package for an owner signing key (Q-5) is dropped.
 
 ### DEC-723 — The EXAMIN profile runs early and read-only on a copy the owner makes; agents never write, list, glob or search in `~/gov-os-workbench` (P-W2-4 (a))
-- **Status:** ACCEPTED (owner, 2026-10-16; the owner commits this entry with `Role: owner`) · **Under:** DEC-718, DEC-525 · **Basis:** EXAMIN's size, languages and test runner decide whether Track B waits for the language-agnostic test commands and the check runner's scale work; measuring them early sizes that work before it is built. In the planning session, a listing of the workbench folder printed a protected folder's name (nothing in it was read). · **Changed by:** DEC-953 (item 2)
+- **Status:** ACCEPTED (owner, 2026-10-16; the owner commits this entry with `Role: owner`) · **Under:** DEC-718, DEC-525 · **Basis:** EXAMIN's size, languages and test runner decide whether Track B waits for the language-agnostic test commands and the check runner's scale work; measuring them early sizes that work before it is built. In the planning session, a listing of the workbench folder printed a protected folder's name (nothing in it was read). · **Changed by:** DEC-953 (item 2) · **Changed by:** DEC-820
 - **Decision:**
   1. W2-26 (the EXAMIN profile, EXP-003's EXAMIN leg) runs early, beside Track A, read-only.
   2. **The owner makes the copy** at `~/gov-os-workbench/examin/` in a plain terminal and gives the orchestrator its exact path.
@@ -9185,7 +9185,7 @@
   3. Both entries' status lines gain a "Changed by" note (DEC-825).
 
 ### DEC-843 — W2-48: the key restated as behaviour; pytest-testmon and coverage as one DEC-083 package when it starts (plan §11 item 8)
-- **Status:** ACCEPTED (owner, 2026-10-19; the owner commits this entry with `Role: owner`, in the next batch; the install itself comes as its own package under DEC-083) · **Under:** DEC-726, DEC-083, DEC-823 item 4 · **Basis:** OWNER, 2026-10-19; lens G R6, F6 · **Changes:** DEC-726 item 1 ("keyed on exact input hashes"). · **Changed by:** items 1 and 2 (the behaviour key; the glue to pytest-testmon and coverage) superseded by DEC-880: W2-48's cache is withdrawn; item 3 (the two tools' install package) stands while they are installed (DEC-882 corrects DEC-880's wider mark)
+- **Status:** ACCEPTED (owner, 2026-10-19; the owner commits this entry with `Role: owner`, in the next batch; the install itself comes as its own package under DEC-083) · **Under:** DEC-726, DEC-083, DEC-823 item 4 · **Basis:** OWNER, 2026-10-19; lens G R6, F6 · **Changes:** DEC-726 item 1 ("keyed on exact input hashes"). · **Changed by:** items 1 and 2 (the behaviour key; the glue to pytest-testmon and coverage) superseded by DEC-880: W2-48's cache is withdrawn; item 3 (the two tools' install package) stands while they are installed (DEC-882 corrects DEC-880's wider mark) · **Changed by:** DEC-852 (adds three conditions to W2-48's KPIs)
 - **Decision:**
   1. W2-48's key KPI is restated as behaviour: each planted change re-runs every dependent test; a change outside every input reuses; every reuse is recorded, with the run it came from; a failed result is never reused.
   2. It is glued to pytest-testmon and coverage: `--testmon-env` set to a hash of the declared data globs and the test command; `.testmondata` written only by main-tree closes; `--testmon-noselect` for W2-24's and W2-46's full runs.
@@ -9658,7 +9658,7 @@
 ## 268. The owner's answers of 2026-10-21 on P-W2-58-4, P-W2-48-8, P-W2-59-8 and P-W2-58-3 (register v0.268, recorded by the W2 orchestrator on branch `w2/integrate`)
 
 ### DEC-880 — W2-58's one narrow extra round; W2-48's cache withdrawn and a lite W2-38 brought back as path-scoped regression (W2-66); W2-65; credentials out of the working trees
-- **Status:** ACCEPTED (owner, 2026-10-21, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-21)`) · **Under:** DEC-413, DEC-857, DEC-873, DEC-852, DEC-869, DEC-876, DEC-841, DEC-105, DEC-866, DEC-820, DEC-861 · **Basis:** the packages P-W2-58-4, P-W2-48-8, P-W2-59-8 and P-W2-58-3 (`governance/project/orchestration/packages/`), from W2-58's run 2, W2-48's run 2 and W2-59's run 3. · **Changed by:** DEC-882: DEC-843 is superseded in its items 1 and 2 only; its item 3, the install approval, stands while the tools are installed; DEC-884: the settings regeneration follows the combined re-pin (item 3); DEC-889: W2-48's lesson is the measured causes (folder listings 7,076, undeclared reads 3,750, dot-files 125, child processes about 500), and item 2 (b)'s leads' verification keeps its scope in the close's form
+- **Status:** ACCEPTED (owner, 2026-10-21, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-21)`) · **Under:** DEC-413, DEC-857, DEC-873, DEC-852, DEC-869, DEC-876, DEC-841, DEC-105, DEC-866, DEC-820, DEC-861 · **Basis:** the packages P-W2-58-4, P-W2-48-8, P-W2-59-8 and P-W2-58-3 (`governance/project/orchestration/packages/`), from W2-58's run 2, W2-48's run 2 and W2-59's run 3. · **Changed by:** DEC-882: DEC-843 is superseded in its items 1 and 2 only; its item 3, the install approval, stands while the tools are installed; DEC-884: the settings regeneration follows the combined re-pin (item 3); DEC-889: W2-48's lesson is the measured causes (folder listings 7,076, undeclared reads 3,750, dot-files 125, child processes about 500), and item 2 (b)'s leads' verification keeps its scope in the close's form · **Changed by:** DEC-904 (item 2), DEC-952 (item 2)
 - **Decision:**
   1. **P-W2-58-4 (a): one narrow extra round for W2-58, an exception to DEC-413 for this ticket only.**
      - The guard expands `~` in every path it judges (Read, Grep, Glob, Edit, Write and Bash), with tests for each tool.
@@ -10116,7 +10116,7 @@
 ## 280. The owner's rule of 2026-10-22 on placeholders (register v0.280, recorded by the W2 orchestrator on branch `w2/integrate`)
 
 ### DEC-893 — No placeholder reaches the owner or a commit: a scan in the record checks
-- **Status:** ACCEPTED (owner, standing, 2026-10-22, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-22)`) · **Under:** DEC-868, DEC-862 (a), DEC-861, DEC-851 · **Basis:** the owner's `Role: owner` commit of DEC-892's W1-38 entry (`49c24ac9`, 2026-10-22). The entry's reason carries an unfilled placeholder, "2026-10-22 00:2x", which the orchestrator had prepared. <!-- placeholder-examples --> · **Changed by:** DEC-953 (item 1)
+- **Status:** ACCEPTED (owner, standing, 2026-10-22, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-22)`) · **Under:** DEC-868, DEC-862 (a), DEC-861, DEC-851 · **Basis:** the owner's `Role: owner` commit of DEC-892's W1-38 entry (`49c24ac9`, 2026-10-22). The entry's reason carries an unfilled placeholder, "2026-10-22 00:2x", which the orchestrator had prepared. <!-- placeholder-examples --> · **Changed by:** DEC-953 (item 1) · **Changed by:** DEC-1045
 - **Decision:**
   1. **The committed entry is not corrected now.** The real time goes into the owner's next ratchet commit, or into W2-57's removal of the entry. The alone run fell between 00:12 and 00:16 on 2026-10-22: after W2-63's refused close ended at 00:11, and before the DEC-891 commit at 00:16.
   2. **The rule (standing):** the orchestrator's record checks include a scan that refuses placeholders in any prepared entry, patch or record before it reaches the owner or a commit:
@@ -11252,7 +11252,7 @@
 | 0.316 | 2026-10-28 | Owner (recorded by the orchestrator, DEC-861): DEC-932 (DEC-931's reading accepted; a narrow scoped close passes under the pin, no fix, row W2-L449; package P-REPIN-2 proposes a re-pin per judge improvement). Next free id: DEC-933. |
 
 ### DEC-933 — P-REPIN-2 (a): each judge improvement re-pinned as it lands; the nightly in a 02:00 to 05:00 window, booked by a measured estimate, every night, for the Gov OS and every adopted product (standing)
-- **Status:** ACCEPTED (owner, 2026-10-28, in the chat; it supersedes the owner's earlier message of the same night on P-REPIN-2 and the nightly, recorded in its place; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-28)`; standing; item 2's application revised by DEC-934: committed scripts, logs, the morning check, the Windows wake task; item 1's re-pin 2 done, DEC-935) · **Under:** DEC-932 item 3, DEC-852 item 3, DEC-880, DEC-889 items 4 and 12, DEC-915 item 4, DEC-922, DEC-928 item 3, DEC-851, DEC-861 · **Basis:** package P-REPIN-2 (`governance/project/orchestration/packages/P-REPIN-2.md`). · **Changed by:** DEC-953 (items 1, 3) · **Changed by:** DEC-961 (item 2: the nightly starts at 02:00 on its window and holds nothing else; it takes no lock at night) · **Changed by:** DEC-973 (the nightly at 04:00, its check at 08:00, the morning package at 09:00)
+- **Status:** ACCEPTED (owner, 2026-10-28, in the chat; it supersedes the owner's earlier message of the same night on P-REPIN-2 and the nightly, recorded in its place; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-28)`; standing; item 2's application revised by DEC-934: committed scripts, logs, the morning check, the Windows wake task; item 1's re-pin 2 done, DEC-935) · **Under:** DEC-932 item 3, DEC-852 item 3, DEC-880, DEC-889 items 4 and 12, DEC-915 item 4, DEC-922, DEC-928 item 3, DEC-851, DEC-861 · **Basis:** package P-REPIN-2 (`governance/project/orchestration/packages/P-REPIN-2.md`). · **Changed by:** DEC-953 (items 1, 3) · **Changed by:** DEC-961 (item 2: the nightly starts at 02:00 on its window and holds nothing else; it takes no lock at night) · **Changed by:** DEC-973 (the nightly at 04:00, its check at 08:00, the morning package at 09:00) · **Changed by:** DEC-1049 (item 2)
 - **Decision:**
   1. **P-REPIN-2 (a); the cadence is standing.** Each judge improvement is re-pinned as soon as it merges and passes its checks, not bundled. Re-pin 2 carries W2-57 and W2-07 round 2 as soon as W2-07 merges; re-pin 3 carries W2-68 and W2-71 when they land.
   2. **The nightly (a condition of (a), and a standing rule for the Gov OS and every adopted product; the rule about rules):**
@@ -11285,7 +11285,7 @@
 
 
 ### DEC-934 — ACT-NIGHTLY-1 revised: cron runs committed, reviewed code; logs kept under a budget; a missed night is a P1; cron checked in this WSL, with a Windows task for restarts and sleep (standing)
-- **Status:** ACCEPTED (item 2 changed by DEC-936 item 1: a night's P1s wait until 07:30 unless the owner is active; owner, 2026-10-28, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-28)`; items 1 and 2 standing) · **Under:** DEC-933 item 2, DEC-852 item 3, DEC-898, DEC-928 item 3, DEC-851, DEC-861 · **Basis:** ACT-NIGHTLY-1 as first sent (`70c7924d`), not installed. The same message confirmed ACT-W2-57-LS-1, committed as `6367e965` (`Role: owner`); after it gate (b) is green (`gov check` exit 0: 15 GREEN, 2 known YELLOW) and the record checks pass. · **Changed by:** DEC-973 (the nightly at 04:00, its check at 08:00, the morning package at 09:00)
+- **Status:** ACCEPTED (item 2 changed by DEC-936 item 1: a night's P1s wait until 07:30 unless the owner is active; owner, 2026-10-28, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-28)`; items 1 and 2 standing) · **Under:** DEC-933 item 2, DEC-852 item 3, DEC-898, DEC-928 item 3, DEC-851, DEC-861 · **Basis:** ACT-NIGHTLY-1 as first sent (`70c7924d`), not installed. The same message confirmed ACT-W2-57-LS-1, committed as `6367e965` (`Role: owner`); after it gate (b) is green (`gov check` exit 0: 15 GREEN, 2 known YELLOW) and the record checks pass. · **Changed by:** DEC-973 (the nightly at 04:00, its check at 08:00, the morning package at 09:00) · **Changed by:** DEC-1049
 - **Decision (the owner's four points):**
   1. **The cron line runs committed, reviewed code,** not a script in scratch: the nightly is committed with its tests and reviewed by the orchestrator, and cron calls the committed path (or checks a committed sha256).
   2. **Log, don't discard:** the run's output goes to a dated log file, rotated under a budget, and the morning digest reports whether the nightly ran. A missed or failed-to-start nightly is a P1 in the digest, so a silent miss can't happen.
@@ -11345,7 +11345,7 @@
 
 
 ### DEC-936 — ACT-NIGHTLY-1 installed; a night's P1s wait until 07:30 unless the owner is active; carry on without waiting, as many leads as the machine allows; P2s delegated; six additions for the re-plan package (standing)
-- **Status:** ACCEPTED (item 2's priority line replaced by DEC-946; item 2.5's digest folded into the morning package (DEC-941 item 4c); item 1's night-time pings replaced by DEC-938's morning package; owner, 2026-10-28, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-28)`; items 2 to 4 standing) · **Under:** DEC-930, DEC-933, DEC-934, DEC-935, DEC-855, DEC-847, DEC-898, DEC-851, DEC-861 · **Changes:** DEC-855 (pings: only P1s and ACTs; P2s decided as delegated, listed in the digest for the owner to overturn), DEC-934 item 2 (the morning check's P1 pings wait until 07:30 unless the owner is active). · **Changed by:** DEC-953 (item 1) · **Changed by:** DEC-1088 (item 3.4)
+- **Status:** ACCEPTED (item 2's priority line replaced by DEC-946; item 2.5's digest folded into the morning package (DEC-941 item 4c); item 1's night-time pings replaced by DEC-938's morning package; owner, 2026-10-28, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-28)`; items 2 to 4 standing) · **Under:** DEC-930, DEC-933, DEC-934, DEC-935, DEC-855, DEC-847, DEC-898, DEC-851, DEC-861 · **Changes:** DEC-855 (pings: only P1s and ACTs; P2s decided as delegated, listed in the digest for the owner to overturn), DEC-934 item 2 (the morning check's P1 pings wait until 07:30 unless the owner is active). · **Changed by:** DEC-953 (item 1) · **Changed by:** DEC-1088 (item 3.4) · **Changed by:** DEC-974 (item 2.5)
 - **Status reported by the owner, checked by the orchestrator (2026-10-28):**
   - **ACT-NIGHTLY-1 Part A:** the three crontab lines, cron active (the backup was empty). Checked: `crontab -l` shows them; `systemctl is-active cron` gives `active`.
   - **Part B:** the task "GovOS nightly wake" is Ready (next run 2026-10-29 01:50, `WakeToRun` true, start when available, a 4-hour limit, not on battery). Wake timers are allowed. Windows Update's active hours are 12:00 to 06:00, which cover 01:30 to 05:30.
@@ -11458,7 +11458,7 @@
 
 
 ### DEC-939 — The owner's answers to P1-MORNING-2026-10-29: long commands in the background with a 07:45 watchdog; a rebuild time limit and a rebuild lock (W2-76); W2-58 re-closed; W2-71's partial-clone fix; W2-68 merged and re-pinned, the batch on after W2-M406's fix (W2-77); the nightly's lock-wait and a 01:00 cut-off for full runs; Pushover for emergencies (standing)
-- **Status:** ACCEPTED (item 7 (Pushover) reversed by DEC-945; owner, 2026-10-29, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-29)`; items 1, 2, 6 and 7 standing) · **Under:** DEC-938, DEC-937, DEC-936, DEC-934, DEC-933, DEC-915 item 4, DEC-898, DEC-851, DEC-861 · **Basis:** `governance/project/orchestration/packages/P1-MORNING-2026-10-29.md` (`d8882b3f`). The delegated P2s listed there (DEC-937, W2-75's merge, W2-71's run 2, the nightly's lock-wait) are accepted. · **Changed by:** DEC-953 (item 1) · **Changed by:** DEC-961 (item 6, the 01:00 cut-off, ended; item 2's rebuild lock listed for the owner's review, HOLDS-REVIEW-1)
+- **Status:** ACCEPTED (item 7 (Pushover) reversed by DEC-945; owner, 2026-10-29, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-29)`; items 1, 2, 6 and 7 standing) · **Under:** DEC-938, DEC-937, DEC-936, DEC-934, DEC-933, DEC-915 item 4, DEC-898, DEC-851, DEC-861 · **Basis:** `governance/project/orchestration/packages/P1-MORNING-2026-10-29.md` (`d8882b3f`). The delegated P2s listed there (DEC-937, W2-75's merge, W2-71's run 2, the nightly's lock-wait) are accepted. · **Changed by:** DEC-953 (item 1) · **Changed by:** DEC-961 (item 6, the 01:00 cut-off, ended; item 2's rebuild lock listed for the owner's review, HOLDS-REVIEW-1) · **Changed by:** DEC-1001 (item 2)
 - **Decision:**
   1. **(a), standing:** every command that can take more than a few minutes runs in the background; the 07:45 watchdog pings "package late, with the reason" if the package has not gone. Prompt §7.
   2. **The diagnosis plan, and two safeguards (standing):**
@@ -11508,7 +11508,7 @@
 - **Where it goes (DEC-851):** this register; `packages/` (the final files); RESUME HERE.
 
 ### DEC-941 — The re-plan of Wave 2 accepted with amendments: memory, K3 and K6 start today in parallel; the nine held tickets merged back and closed in priority order; release path an entry criterion for EXAMIN's real repository; Wave 2-grade evidence for everything EXAMIN's copy relies on (standing)
-- **Status:** ACCEPTED (K9's entry criteria gain a Definition of Ready and stream playbooks (DEC-944); item 1d's ceiling of 4 leads removed (DEC-942); owner, 2026-10-29, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-29)`; items 1d, 4, 6 and 7 standing) · **Under:** DEC-940, DEC-930, DEC-936, DEC-939, DEC-929, DEC-933, DEC-851, DEC-861 · **Changes:** DEC-831's slot order (replaced by item 1 and the re-plan's blocks), DEC-847's ceiling (item 1d), DEC-936 item 2.5 and DEC-938 item 2 (item 4c: one daily document) · **Basis:** `REPLAN-W2.md`, `STATE-OF-GOV-OS` (drafts, DEC-940), `P-SCOPE-RECORDS-1`, `P-TOOLS-REVIEW-1`. · **Changed by:** DEC-953 (items 1, 2, 6, 10) · **Changed by:** DEC-954 (Q1: EXAMIN's copy gated by K9's criteria, not a date) · **Changed by:** DEC-1089 (item 3)
+- **Status:** ACCEPTED (K9's entry criteria gain a Definition of Ready and stream playbooks (DEC-944); item 1d's ceiling of 4 leads removed (DEC-942); owner, 2026-10-29, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-29)`; items 1d, 4, 6 and 7 standing) · **Under:** DEC-940, DEC-930, DEC-936, DEC-939, DEC-929, DEC-933, DEC-851, DEC-861 · **Changes:** DEC-831's slot order (replaced by item 1 and the re-plan's blocks), DEC-847's ceiling (item 1d), DEC-936 item 2.5 and DEC-938 item 2 (item 4c: one daily document) · **Basis:** `REPLAN-W2.md`, `STATE-OF-GOV-OS` (drafts, DEC-940), `P-SCOPE-RECORDS-1`, `P-TOOLS-REVIEW-1`. · **Changed by:** DEC-953 (items 1, 2, 6, 10) · **Changed by:** DEC-954 (Q1: EXAMIN's copy gated by K9's criteria, not a date) · **Changed by:** DEC-1089 (item 3) · **Changed by:** DEC-946 (blocks A to E: their order)
 - **Decision (the owner's eight amendments to an accepted re-plan):**
   1. **Start today, in parallel; do not wait for block A.**
      1. File W2-55, W2-56, W2-60, W2-61, W2-64 and the proving-ground ticket today.
@@ -11805,7 +11805,7 @@
 
 
 ### DEC-951 — The owner's answers to P1-MORNING-2026-10-30 and P-W2-60a-ROUND3; a red nightly the orchestrator has explained and repaired needs no owner; the morning ping on time (items A and B standing)
-- **Status:** ACCEPTED (owner, 2026-10-30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-30)`; items A and B standing) · **Under:** DEC-938, DEC-949, DEC-413, DEC-757, DEC-915, DEC-941, DEC-946 · **Changes:** DEC-938's hold on closes after a red nightly (item A); DEC-938's schedule (item B) · **Basis:** `packages/P1-MORNING-2026-10-30.md`, `packages/P-W2-60a-ROUND3.md` · **Changed by:** DEC-953 (item 3)
+- **Status:** ACCEPTED (owner, 2026-10-30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-30)`; items A and B standing) · **Under:** DEC-938, DEC-949, DEC-413, DEC-757, DEC-915, DEC-941, DEC-946 · **Changes:** DEC-938's hold on closes after a red nightly (item A); DEC-938's schedule (item B) · **Basis:** `packages/P1-MORNING-2026-10-30.md`, `packages/P-W2-60a-ROUND3.md` · **Changed by:** DEC-953 (item 3) · **Changed by:** DEC-973
 - **Decision:**
   1. **Release the closes now:** W2-71, W2-77, W2-57, W2-03, W2-26 and the rest that are ready.
   2. **P-B1-1: yes.** A short test-designer revision of W1-02's deadline support, then W2-05 resumes.
@@ -11856,7 +11856,7 @@
 | 0.335 | 2026-10-30 | Owner (recorded by the orchestrator, DEC-861): DEC-952 (memory's quick wins W2-86 and W2-87 first, each re-measured; scoped verification for leads; standing: interim results at once, the memory-chain line, the rules-in-force digest, a fresh session each morning; its close batch, re-pin 3 and lock items superseded by DEC-953). Next free id: DEC-953. |
 
 ### DEC-953 — The owner's decision on AUDIT-GOV-FEATURES-1: the Gov OS is built and tested first, then dog-fooded; every Gov OS feature lifted as a gate on this repository's own development; tickets close on the audit's 10 practices; the guard keeps four rules (standing)
-- **Status:** ACCEPTED (owner, 2026-10-30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-30)`; standing) · **Under:** DEC-105 (option (a), amended), MR-3, MR-6, ADR-0001 · **Changes:** Wave 2's exit criterion 1 (WBS §0 rule 1; AR-8 and F-M3 as applied, DEC-718, DEC-721): the proof of `gov close` moves to the proving ground (W2-81) and EXAMIN's copy; the standing rules listed in `governance/project/orchestration/LIFTED-BY-DEC953.md` · **Basis:** `governance/project/orchestration/packages/AUDIT-GOV-FEATURES-1.md` (`a4939b45`); the owner's text, verbatim, in `.gov-runtime/scratch/orchestrator/drafts/DEC-953-owner-text.md` · **Changed by:** DEC-954 (item 2: a fifth rule, the hidden half from every worktree; items 6 and 10: the order and the plan approved) · **Changed by:** DEC-959 item 1 (how often tests run: the lead's scoped run once, the merge queue's run once per batch on the merged result, the close cites it; the full suite only in the nightly and for core changes) · **Changed by:** DEC-968 (item 4: never full outside the nightly; §0's "a red that fails alone refuses the close": only a red the change caused)
+- **Status:** ACCEPTED (owner, 2026-10-30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-30)`; standing) · **Under:** DEC-105 (option (a), amended), MR-3, MR-6, ADR-0001 · **Changes:** Wave 2's exit criterion 1 (WBS §0 rule 1; AR-8 and F-M3 as applied, DEC-718, DEC-721): the proof of `gov close` moves to the proving ground (W2-81) and EXAMIN's copy; the standing rules listed in `governance/project/orchestration/LIFTED-BY-DEC953.md` · **Basis:** `governance/project/orchestration/packages/AUDIT-GOV-FEATURES-1.md` (`a4939b45`); the owner's text, verbatim, in `.gov-runtime/scratch/orchestrator/drafts/DEC-953-owner-text.md` · **Changed by:** DEC-954 (item 2: a fifth rule, the hidden half from every worktree; items 6 and 10: the order and the plan approved) · **Changed by:** DEC-959 item 1 (how often tests run: the lead's scoped run once, the merge queue's run once per batch on the merged result, the close cites it; the full suite only in the nightly and for core changes) · **Changed by:** DEC-968 (item 4: never full outside the nightly; §0's "a red that fails alone refuses the close": only a red the change caused) · **Changed by:** DEC-1045 (the lifted gates)
 - **Decision:**
   1. **Option (a), amended:** every Gov OS feature is lifted as a gate on this repository's own development. Tickets close on the audit's 10 practices (§5), nothing more: independent tests first; the change's tests on the merged commit in a clean clone, one run at a time; an independent review for FULL tickets; the nightly full run; the guard's four rules; gitleaks; git discipline; the disk floor and scratch budgets; a close record; a quick check of changed record files. Nothing is deleted from the product: the lifted features stay built and tested.
   2. **The guard keeps four rules:** an implementer never writes acceptance tests; no reads of the hidden half of an evaluation set or the held-out material; no reads of secrets; no installs without the owner. Everything else in the guard is lifted, the command forms included. The orchestrator brings the fastest safe way to switch the rest off (an ACT where it needs the owner).
@@ -11886,7 +11886,7 @@
 | 0.336 | 2026-10-30 | Owner (recorded by the orchestrator, DEC-861): DEC-953 (AUDIT-GOV-FEATURES-1, option (a) amended: every Gov OS feature lifted as a gate on this repository's own development; closes on the audit's 10 practices; the guard at four rules; the nightly a plain full run, reds investigated at once and holding nothing; one test-selection tool at every level, governance files left out; the five closes now; memory and K3 first, then EXAMIN's minimum; gov close proved on W2-81 and EXAMIN's copy; decisions compacted; three-layer orchestration planned; working with the owner unchanged; the updated plan first). Next free id: DEC-954. |
 
 ### DEC-954 — The owner's approval of PLAN-W2-DEC953, with answers and amendments: EXAMIN gated by milestones, not a date; ACT 1 the five-rule guard; the roles spec first; memory for any repository; ACT 2 one re-pin; the three layers as the CTO and Senior Engineers (standing)
-- **Status:** ACCEPTED (owner, 2026-10-30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-30)`; standing) · **Under:** DEC-953, DEC-105, DEC-906, MR-3, MR-6 · **Changes:** DEC-953 item 2 (a fifth rule; the hidden half from every worktree), DEC-953 item 6 (the order), DEC-953 item 10 (the plan approved); DEC-941 (the date target) · **Basis:** `governance/project/orchestration/packages/PLAN-W2-DEC953.md` (`fb63fe81`), `P-W2-78-PARK.md`, `P-W2-64-1.md`; the owner's text, verbatim, in `.gov-runtime/scratch/orchestrator/drafts/DEC-954-owner-text.md` · **Changed by:** DEC-962 (full runs no longer share one lock; closes no longer go first)
+- **Status:** ACCEPTED (owner, 2026-10-30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-30)`; standing) · **Under:** DEC-953, DEC-105, DEC-906, MR-3, MR-6 · **Changes:** DEC-953 item 2 (a fifth rule; the hidden half from every worktree), DEC-953 item 6 (the order), DEC-953 item 10 (the plan approved); DEC-941 (the date target) · **Basis:** `governance/project/orchestration/packages/PLAN-W2-DEC953.md` (`fb63fe81`), `P-W2-78-PARK.md`, `P-W2-64-1.md`; the owner's text, verbatim, in `.gov-runtime/scratch/orchestrator/drafts/DEC-954-owner-text.md` · **Changed by:** DEC-962 (full runs no longer share one lock; closes no longer go first) · **Changed by:** DEC-1037 (Q8), DEC-957 (Q9)
 - **Decision:**
   - **Q1, EXAMIN gated by milestones:** EXAMIN's copy starts only when K9's entry criteria are met (memory proven; the roles, skills and briefs landed; the proving ground passed; the rest of the minimum closed). The plan's dates are estimates, re-estimated weekly. No adoption on a weak Gov OS because a date arrived.
   - **Q2:** the 10 built tickets are finished after ACT 1, under the five-rule guard, each closed on the 10 practices.
@@ -11933,7 +11933,7 @@
 | 0.339 | 2026-10-30 | Delegated (orchestrator, DEC-936 item 2.5): DEC-956 (W2-76: the watchdog case's setup revised by a test designer; a per-run rebuild-lock override set by the test harness; run 2 after ACT 1). Next free id: DEC-957. |
 
 ### DEC-957 — The owner's decisions on ACT 1, ROLES-SPEC-1 and MEMORY-SPEC-MAP: the batch stopped, installs only through the CTO, the 235 tests revised in W2-90, the roles approved with a software company's work order and an escalation rubric, memory's target 95 % (standing)
-- **Status:** ACCEPTED (owner, 2026-10-30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-30)`; standing) · **Under:** DEC-953, DEC-954, DEC-955, DEC-906, MR-3, MR-4, MR-6 · **Changes:** DEC-954 Q9 (memory's target and readiness); ROLES-SPEC-1's Q5, Q8, Q12; DEC-839 (effort) for the CTO and Senior Engineers; DEC-832 (the skill packs come in Wave 2) · **Basis:** `packages/ACT-1-GUARD.md`, `packages/ROLES-SPEC-1.md`, `packages/MEMORY-SPEC-MAP.md` · **Changed by:** DEC-959 (the work order: the test designer and the engineer work in parallel from the spec; the QA engineer per stream, in batches; integration by the local merge queue)
+- **Status:** ACCEPTED (owner, 2026-10-30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-30)`; standing) · **Under:** DEC-953, DEC-954, DEC-955, DEC-906, MR-3, MR-4, MR-6 · **Changes:** DEC-954 Q9 (memory's target and readiness); ROLES-SPEC-1's Q5, Q8, Q12; DEC-839 (effort) for the CTO and Senior Engineers; DEC-832 (the skill packs come in Wave 2) · **Basis:** `packages/ACT-1-GUARD.md`, `packages/ROLES-SPEC-1.md`, `packages/MEMORY-SPEC-MAP.md` · **Changed by:** DEC-959 (the work order: the test designer and the engineer work in parallel from the spec; the QA engineer per stream, in batches; integration by the local merge queue) · **Changed by:** DEC-1052
 - **Decision:**
   - **Before ACT 1:**
     1. stop the four-ticket close batch (W2-57, W2-77, W2-03, W2-26), which tests the head with the register fault; it re-runs on the corrected head in the fresh session after ACT 1;
@@ -12050,7 +12050,7 @@
 | 0.344 | 2026-10-30 | Owner (recorded by the orchestrator, DEC-861): DEC-961 (capacity alone: no reserved verification peak, full runs check the gate themselves, no close or night holds, the nightly holds nothing; HOLDS-REVIEW-1 for the owner). Next free id: DEC-962. |
 
 ### DEC-962 — The owner's decisions on HOLDS-REVIEW-1: the one-run lock ended, the rebuild lock kept until W2-76 is measured, rules 4 to 17 kept, a proposal for parallel work without two writers in one tree, the nightly's own estimate kept (standing)
-- **Status:** ACCEPTED (owner, 2026-10-30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-30)`; standing) · **Under:** DEC-961, DEC-959, DEC-939 item 2 · **Changes:** DEC-905, DEC-906 item 3, DEC-954 (the one-run lock and "closes first") · **Basis:** `packages/HOLDS-REVIEW-1.md` · **Changed by:** DEC-963 (item 4: P-PARALLEL-1 approved as (b), amended)
+- **Status:** ACCEPTED (owner, 2026-10-30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-30)`; standing) · **Under:** DEC-961, DEC-959, DEC-939 item 2 · **Changes:** DEC-905, DEC-906 item 3, DEC-954 (the one-run lock and "closes first") · **Basis:** `packages/HOLDS-REVIEW-1.md` · **Changed by:** DEC-963 (item 4: P-PARALLEL-1 approved as (b), amended) · **Changed by:** DEC-1001
 - **Decision:**
   1. **Rules 1 and 2 end:** full test runs no longer share one lock and closes no longer go first; each full run asks the gate for room for its own peak (`gate_check.py --full-run`) and runs.
   2. **Rule 3 stays** (one store rebuild at a time) until W2-76's machine-wide lock has been measured; the orchestrator then brings the owner its figures for a decision.
@@ -12102,7 +12102,7 @@
 | 0.348 | 2026-10-31 | Delegated (orchestrator, DEC-936 item 2.5): DEC-965 (W2-90 merged with 7 named reds; P2-C, P2-D, P2-E (a)). Next free id: DEC-966. |
 
 ### DEC-966 — The owner's decisions on P-W2-90-1 and on speed: the template's install block removed, its hook lines pinned; the designers' store refreshed twice a day; rebuild speed a priority (standing)
-- **Status:** ACCEPTED (owner, 2026-10-31, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-31)`; standing) · **Under:** DEC-957, DEC-965, DEC-172, DEC-822, DEC-963, DEC-939 item 2 · **Changes:** DEC-963 (the store's refresh) · **Changed by:** DEC-1087 (3) (item 3: the store refreshed after every merge by W2-116's hook, not twice a day) · **Basis:** `packages/P-W2-90-1.md`; W2-76's measured rebuild stages (`log/W2-76-A5-run1.json`: secrets 274.8 of 307.4 s; run 2: 547.9 of 735.4 s)
+- **Status:** ACCEPTED (owner, 2026-10-31, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-31)`; standing) · **Under:** DEC-957, DEC-965, DEC-172, DEC-822, DEC-963, DEC-939 item 2 · **Changes:** DEC-963 (the store's refresh) · **Changed by:** DEC-1087 (3) (item 3: the store refreshed after every merge by W2-116's hook, not twice a day) · **Basis:** `packages/P-W2-90-1.md`; W2-76's measured rebuild stages (`log/W2-76-A5-run1.json`: secrets 274.8 of 307.4 s; run 2: 547.9 of 735.4 s) · **Changed by:** DEC-1045 (item 4)
 - **Decision:**
   1. **P1-A (a):** the template's install block is removed (`template/.rulesync/permissions.jsonc`'s `npm install*` and `pip install*` deny rules), so an adopted product's CTO session can ask the owner, as this repository does (DEC-172). A small ticket; then W2-90's next round moves its 3 cases.
   2. **P1-B (a):** the template's hook lines get the fixed-interpreter form this repository uses (DEC-822, W2-59): a fail-open must not ship in EXAMIN's copy. A ticket; then W2-90's next round moves its 4 cases.
@@ -12389,7 +12389,7 @@
 | 0.370 | 2026-11-01 | Owner (recorded by the orchestrator, DEC-861): DEC-987 (P-W2-96-R4 (a), a third review for W2-96). Next free id: DEC-988. |
 
 ### DEC-988 — The owner's answers to P1-MORNING-2026-11-01; the batch re-attributed on its own results; two root causes to fix (standing)
-- **Status:** ACCEPTED (owner, 2026-11-01, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-01)`; items 3 to 5 standing) · **Under:** DEC-968, DEC-973, DEC-979, DEC-959 item 1, DEC-949 · **Basis:** `packages/P1-MORNING-2026-11-01.md`, `packages/P-W2-110-4.md`
+- **Status:** ACCEPTED (owner, 2026-11-01, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-01)`; items 3 to 5 standing) · **Under:** DEC-968, DEC-973, DEC-979, DEC-959 item 1, DEC-949 · **Basis:** `packages/P1-MORNING-2026-11-01.md`, `packages/P-W2-110-4.md` · **Changed by:** DEC-989 (item 3's baseline)
 - **Decision:**
   1. **P1-MORNING-2026-11-01:** the missed nightly (b): no run by day; tonight's 04:00 nightly checks everything. **P-W2-110-4 (a):** W2-110 is merged now and closed after ACT 2's re-pin; its three reds are named as waiting for ACT 2. **P-W2-55-HOOK (b), then (a):** the session-start hook loads `gov context --in-force` once the backfill has marked the done entries. **P-W2-55-BACKFILL:** a product-spec pass over the in-force entries' tags first, then the owner's sample review, then the CTO applies it.
   2. **The batch of eight:** its tickets were not the problem; the close tool's baseline was. Its tests (the 05:26 run) are not re-run: their results are re-used and only the attribution of its failing tests is done again against a correct baseline; if none is caused by the batch, all eight close.
@@ -12630,7 +12630,7 @@
 | 0.390 | 2026-11-01 | Owner (recorded by the orchestrator, DEC-861): DEC-1008 (W2-121 filed, before EXAMIN's copy, in K9's entry criteria; peaks; every heavy step in a slot). Next free id: DEC-1009. |
 
 ### DEC-1009 — W2-61h's P-W2-61h-1 (a); the CTO's return watcher retired for the dispatcher's inbox (delegated)
-- **Status:** ACCEPTED (orchestrator, delegated: a P2, older tests revised under an approved decision by the same role, DEC-957; a tools-lane change) · **Under:** DEC-954 Q9a, DEC-995, DEC-1007
+- **Status:** ACCEPTED (orchestrator, delegated: a P2, older tests revised under an approved decision by the same role, DEC-957; a tools-lane change) · **Under:** DEC-954 Q9a, DEC-995, DEC-1007 · **Changed by:** DEC-1069
 - **Amended:** by DEC-1069 (4) (owner, 2026-11-04): the set grows to about 40 per half; the visible half is no longer only lens B's 20 and W2-61h's 4.
 - **Decision:** (1) P-W2-61h-1 (a): W2-61h's paths gain W2-61's visible-half, baseline and scores cases and README; its fresh test designer revises the four cases that assume 20 visible questions (lens B's 20 still required exactly; nothing lowered). (2) `lead_return_watch.sh` is retired: it marked returns seen before the dispatcher could put them in its inbox (W2-61h's return of 20:06 was missed by the inbox that way). The CTO wakes on `tools/inbox_wait.sh`, which only reads the inbox; the 30-minute stale-inbox alert is the net.
 
@@ -12828,7 +12828,7 @@
 | 0.413 | 2026-11-02 | Owner (recorded by the orchestrator, DEC-861): DEC-1031. Next free id: DEC-1032. |
 
 ### DEC-1032 — P1-LOAD-BALANCE-1 decided; a freeze until the machine runs at normal speed; the infrastructure sprint (standing until lifted)
-- **Status:** ACCEPTED (owner, 2026-11-02, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-02)`; the freeze standing until the owner lifts it) · **Under:** DEC-1028 item 5, DEC-1031, DEC-1029, DEC-1030, DEC-798, DEC-975, DEC-974 · **Changes:** DEC-798 and DEC-975 (the query embedder on the CPU)
+- **Status:** ACCEPTED (owner, 2026-11-02, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-02)`; the freeze standing until the owner lifts it) · **Under:** DEC-1028 item 5, DEC-1031, DEC-1029, DEC-1030, DEC-798, DEC-975, DEC-974 · **Changes:** DEC-798 and DEC-975 (the query embedder on the CPU) · **Changed by:** DEC-1033 (items 2 and 3)
 - **Context:** ACT-W1-01-EXEMPT-1 committed by the owner (`2acc8a31`); ACT-RERANK-CPU-1 applied by mistake and undone; ACT-RERANK-GPU-SLOTS-1 applied (at most two rerankers on the GPU; tested with three processes).
 - **Decision:** (1) The plan's five decisions, yes: the query embedding moves to the GPU, with its ACT; DEC-798 and DEC-975 are amended (the query embedder may run on the GPU: the determinism test on the memory measure changed no answer's pass or fail; the vectors are not bit-identical, as the CPU's are not); the vector-cache ticket is filed (each text embedded once on the machine); W2-112 (the shared reranker) before EXAMIN's copy; the GPU budget (the embedder first, about 3.5 GB; the shared reranker second, about 2.5 to 3.5 GB; at least 2 GB headroom; nothing else by default) as W2-20's default share; lever b.6 (the retrieval check's dev tiers pre-built once, not cold on every `gov check`). (2) **A freeze until the machine runs at normal speed:** no new lead starts except the infrastructure work below; W2-122 and W2-123 finish (they are part of the fix); W2-04 finishes its repair round; the landing in flight completes; everything else waits. (3) **The infrastructure sprint, in order, with what the owner must give as one package:** (i) the shared reranker (W2-112), on the GPU, starts now, at the front; (ii) query embedding on the GPU: the ACT now; (iii) the dispatcher balances the whole machine (CPU, RAM, the GPU and its memory, by measured peaks): health judged by progress (no false "hung"), new work admitted only with room on every resource, slots by device, the rerankers' memory and GPU slots counted, an alert when a model loads only partly on the GPU; the CTO's tools, reviewed, today; (iv) rebuilds: no cold rebuild anywhere: every copy (a lead's worktree, the queue's clone, a close, the nightly) seeded from the warm integration index and then embedding only what changed; the merged result's index becomes the new integration index instead of being built again; the head without the batch read from the nightly's results, never rebuilt; the vector-cache ticket starts now; the count and time of rebuilds per ticket and per batch shown before and after; (v) then a short assessment, rethinking and redesign of how leads are launched, verified, landed and closed, judged on what (i) to (iv) achieved (what stays, what changes, how many rebuilds a ticket and a batch truly need and why, the throughput it should reach in closes a day), decided by the owner before the freeze lifts. A report at each step's end; the owner told when the targets are met: no timed-out embedding, no cold rebuild, the GPU stable within its budget, busy cores in their band.
 
@@ -12994,7 +12994,7 @@
 | 0.431 | 2026-11-02 | Owner (recorded by the orchestrator, DEC-861) and delegated item 5: DEC-1048. Next free id: DEC-1049. |
 
 ### DEC-1049 — No nightly full-suite run until the investigation's lifting and refactoring are done (amends DEC-1047)
-- **Status:** ACCEPTED (owner, 2026-11-02 ~21:55, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-02)`; standing until the owner's word) · **Amends:** DEC-1047 · **Changes:** DEC-933 item 2, DEC-934, DEC-968 (1) (the full suite once a day, in the nightly), DEC-973 (the nightly at 04:00, its 08:00 check), DEC-1039 item 3 (the full suite on the re-pinned head), for the length of this decision
+- **Status:** ACCEPTED (owner, 2026-11-02 ~21:55, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-02)`; standing until the owner's word) · **Amends:** DEC-1047 · **Changes:** DEC-933 item 2, DEC-934, DEC-968 (1) (the full suite once a day, in the nightly), DEC-973 (the nightly at 04:00, its 08:00 check), DEC-1039 item 3 (the full suite on the re-pinned head), for the length of this decision · **Changed by:** DEC-1050 (widened)
 - **Decision:** (1) No nightly full-suite run until the investigation's lifting and refactoring are done; the full suite runs again only on the owner's word. (2) An ACT for the owner's operator, now, well before 04:00, stops every scheduled nightly run: the 04:00 nightly and its 08:00 and @reboot checks in the crontab, each line kept, commented out, for an exact undo; the dispatcher's every-minute line stays as it is; the ACT's check shows no nightly scheduled (`packages/ACT-NIGHTLY-STOP-1.md`). (3) The orchestrator, in its own tools: the dispatcher's pre-nightly landing hold (DEC-1018) switched off by configuration while this holds; no "nightly MISSED" P1 (the morning package says the nightly is stopped by DEC-1049); scoped tests and acceptance tests still run with each change (DEC-968).
 
 | Version | Date | Change |
@@ -13158,7 +13158,7 @@
 - **Basis:** question 1 (memory, the Gov OS's first aim) and question 2 (a measure contaminated by its own documents fails open on memory's acceptance); question 5 (a method enters the product after it is shown on the measure).
 
 ### DEC-1067 — D4B-RESEARCH decided: G3 as routing by question type; the hidden half never chooses; blind label checks of the six never-hit questions; the reranker request capped at 16; G4 extended; tonight's order to measure 3 and beyond
-- **Status:** ACCEPTED (owner, 2026-11-04 ~01:30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-04)`) · **Under:** DEC-1066, DEC-1055, DEC-1065, DEC-1060, DEC-957 (95 %) · **Source:** `governance/project/orchestration/packages/LIFT-1/D4B-RESEARCH.md` (`c5c014b2`); the survey `docs/research/EXP-003/retrieval-survey/REPORT.md` (`w2/research-retrieval`, `d49aae04`) · **Changed by:** DEC-1090 (item (f), by W2-137 once measured)
+- **Status:** ACCEPTED (owner, 2026-11-04 ~01:30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-04)`) · **Under:** DEC-1066, DEC-1055, DEC-1065, DEC-1060, DEC-957 (95 %) · **Source:** `governance/project/orchestration/packages/LIFT-1/D4B-RESEARCH.md` (`c5c014b2`); the survey `docs/research/EXP-003/retrieval-survey/REPORT.md` (`w2/research-retrieval`, `d49aae04`) · **Changed by:** DEC-1090 (item (f), by W2-137 once measured) · **Changed by:** DEC-1071 (b)
 - **Decision:** (a) **G3 for W2-32's S8 is routing by question type** (D4B-RESEARCH item 2: a question naming a symbol puts the code route's first 2 hits ahead after the rerank; a question naming a record puts that record's 2 best chunks ahead), each half kept only if it holds at its measure; this replaces DEC-1066 (2)'s wording "the fusion keeps each route's top hits". (b) **The hidden half never chooses:** only levers that also win on the visible half alone are adopted; the hidden half is reported separately and never used to choose; the research branch's `raw/` stays off `w2/integrate` and out of the index; only its `REPORT.md` and `harness/` merge. (c) **Blind label checks now** on Q16, Q19 (by a session independent of the retrieval work) and h02, h07, h11, h24 (by W2-61h's role); a label changes only where it is wrong, never to fit the results, the old label kept on record (DEC-1060's form). (d), (e) **The stronger reranker and embedder: decided by the owner in the morning**, on tonight's results; **no install tonight**. (f) **Reranker requests capped at 16 texts; G4 extended** to W2-15a's raw measure output (`docs/research/EXP-003/w2-15a/raw/**`, merged in D-7, `27a80411`). **Tonight's order:** (1) measure 2 finishes (D-7's effect); (2) the index-time fixes in one rebuild: G1 (the embedder and the reranker read the whole chunk; parent expansion sends no span twice), merged with its full re-embed; (3) on the fixed stores, the research agent tests each query-time change on its own in its harness (G3's routing; every method using all the routes together: each route's top hits guaranteed a place in the reranker's pool; the reranker shown each chunk's path, title and section; repository-specific instructions for the embedder and the reranker; questions expanded with the record ids and symbols the graphs find; several phrasings searched and fused; route agreement and authority combined with the reranker's score; any other method it finds); (4) measure 3: G1 with every query-time change that won on its own, together; if the total falls short of the separate gains, find the interfering pair; (5) index-time methods worth trying (chunks carrying their file and section headings when embedded; file-level and chunk-level indexes together; others) grouped into the next rebuild, then measure 4, and 5 or more if needed; (6) every change judged on the 48 questions, hit@5 and full evidence, the halves separately, kept only if it wins on the visible half alone, the speed per search recorded each time; the last measure before re-pin window 3 is the verdict against the floor (85 % on the 48, at least 21 of 24 on the hidden half). **GPU safety as on 2026-11-04 00:20:** only today's models, nothing new loaded; experiments check memory before each batch, send smaller batches near the limit and wait at or above 15.5 GB or on any spill; the CTO's automatic backstop pauses a run past 15.5 GB, on a spill or on an embedder losing layers; a measure or a store rebuild never runs beside an experiment, and between them the GPU returns inside its budget (the shared reranker restarted under class 3 if it keeps memory). **Quiet hours:** no ping unless an emergency; one package by 09:00 (the figures after each measure, which methods worked and by how much, the speed, the CTO's recommendation on the stronger reranker and embedder with the evidence, anything else for the owner).
 - **Basis:** question 1 (memory) and question 2 (a measure chosen on its own held-out half fails open on memory's acceptance); question 5 (a method enters the product only after it wins on the measure).
 
@@ -13168,14 +13168,14 @@
 - **Basis:** question 1 (memory: the sessions should run the product that scores 38, not the pin's 25) and question 2 (a measure whose questions are wrong or keyword-only misjudges memory; GPU work in turns fails safe).
 
 ### DEC-1069 — D4B-AUDIT decided: every recommended label fix; the set grows to about 40 per half (DEC-1009 amended); R5's thresholds and two new rubric rules; the merges; the reranker trial approved, all three candidates run in turn; a standing model bench
-- **Status:** ACCEPTED (owner, 2026-11-04 ~13:00, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-04)`) · **Under:** DEC-1068, DEC-1067, DEC-1060, DEC-1009 (amended here), W2-61h's KPIs (amended here) · **Source:** `governance/project/orchestration/packages/LIFT-1/D4B-AUDIT.md` (`b598288b`), `governance/project/orchestration/packages/ACT-RERANK-TRIAL-1.md` · **Changed by:** DEC-1076 (4)
+- **Status:** ACCEPTED (owner, 2026-11-04 ~13:00, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-04)`) · **Under:** DEC-1068, DEC-1067, DEC-1060, DEC-1009 (amended here), W2-61h's KPIs (amended here) · **Source:** `governance/project/orchestration/packages/LIFT-1/D4B-AUDIT.md` (`b598288b`), `governance/project/orchestration/packages/ACT-RERANK-TRIAL-1.md` · **Changed by:** DEC-1076 (4) · **Changed by:** DEC-1070
 - **Decision:** **The labels.** (1) Every recommended label fix is applied: the visible ones (Q14, Q07, Q04 re-labelled; Q13, Q17 re-anchored; the five minor re-words of Q02, Q10, Q11, Q12, Q23) by a session independent of the retrieval work, as for Q16 and Q19; the hidden h03 and h08 by the owner's operator, as for h02 and h24 (a brief like ACT-HLABEL-1). (2) Q04: kept beside Q09 after its re-label (option (a)). (3) Q03's split into two entries confirmed. **The bigger set.** (4) The set grows to **about 40 per half**: **DEC-1009 is amended** (the visible half is no longer lens B's 20 + W2-61h's 4 only), recorded as the owner's. (5) **R5:** each governing domain at least 10 % of each half, no subsystem above 25 %; **W2-61h's category quotas are amended to fit**. (6) **A rubric rule before the new questions are written:** no question whose answer changes with ordinary work (counts of dependents, lists that grow) unless its gold is computed from the repository at the measured head; and **the measure script writes a reason line for every automatic re-anchor**. (7) **The hidden auditor's P2:** test-harness code is never the governing source for a code fact, except for a question about the test harness itself. (8) **The writers:** the visible 16 by a session independent of the retrieval work; the hidden 16 by the owner's operator from the rubric (a brief like ACT-HLABEL-1); then the cross-check as proposed. (9) **Then m6:** the live product with today's 0.6B reranker on the 80, three runs, every search's ranked output kept: the new baseline for the methods and the trial. **The merges.** (10) The retired-README fix and the five methods (each off by default) merge now; the methods' measures follow m6, by DAY.md's rule re-based on m6. **The reranker trial (ACT-RERANK-TRIAL-1).** (11) Approved: the operator's steps 0 to 3 now (the downloads and the trial venv), so the models are ready by m6; the CTO stops the live reranker for the trial's quiet window when no agent's work depends on ranked search, and says when; the choice rule as written, with the 3.0 s median limit. (12) After m6, **all three candidates run in turn, whatever the scores** (the 0.6B with m6's own figures, mxbai-rerank-large-v2, then Qwen3-Reranker-4B in 8-bit); no early stop at 95 % or more: the full comparison is wanted; for each: hit@5 and full evidence on the visible half (it chooses) and the hidden half (reported, never used to choose), the GPU peak, the load time, the time per search alone and with 10 and 20 searches at once, and any failure; adoption follows the choice rule (running a model is not adopting it); the result to the owner. (13) **A standing model bench:** the harness and its commands kept, so any future reranker or embedder is measured the same way; the embedder trial (Qwen3-Embedding-4B) follows the reranker's decision, recorded the same way. **All GPU work takes turns, one at a time, under the GPU safety rules.** The operator's three briefs (h03 and h08; the hidden 16; the trial's steps 0 to 3) go to the owner in one message, in the order they should run.
 - **Accepted later (owner, 2026-11-04 ~15:20, in the chat):** the hidden 40's category table ends one short in each of the decision, callers and code-paraphrase categories (16 slots could not meet quotas needing 17); every governing domain reaches at least 4 of 40.
 - **Amended:** by DEC-1070 (owner, 2026-11-04 ~18:40): (12) stops after the 0.6B (T2); mxbai-rerank-large-v2 and Qwen3-Reranker-4B wait for the recall work and the 0.6B's new record; (13)'s embedder trial waits likewise.
 - **Basis:** question 1 (memory: a finer, wider and correct measure decides the methods and the models) and question 2 (a label never changes to fit a result; GPU work in turns fails safe).
 
 ### DEC-1070 — The holistic report decided: the trial stopped after T2; three question sets with three jobs; the recall work in one fix before any new method; hit@5 then MRR as the written choice rule; Q07 and Q14 re-worded; labels audited on a schedule only
-- **Status:** ACCEPTED (owner, 2026-11-04 ~18:40, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-04)`) · **Under:** DEC-1069 (amended here), DEC-1068, DEC-1067, DEC-1009, DEC-1060 · **Source:** the CTO's holistic report in the chat (2026-11-04 ~18:20), recorded in `.gov-runtime/scratch/orchestrator/drafts/d4b/DAY.md` · **Changed by:** DEC-1074 (1)
+- **Status:** ACCEPTED (owner, 2026-11-04 ~18:40, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-04)`) · **Under:** DEC-1069 (amended here), DEC-1068, DEC-1067, DEC-1009, DEC-1060 · **Source:** the CTO's holistic report in the chat (2026-11-04 ~18:20), recorded in `.gov-runtime/scratch/orchestrator/drafts/d4b/DAY.md` · **Changed by:** DEC-1074 (1) · **Changed by:** DEC-1071
 - **Decision:** **First, now.** (1) The reranker trial stops after T2: no mxbai-rerank-large-v2 and no Qwen3-Reranker-4B until the recall work is done and the 0.6B has its new record; the live reranker restored at once (T6) and ranked searches confirmed; the trial's venv and downloads kept as they are for later. **The question sets: three jobs from now on.** (2) **The visible 40 are the tuning set:** methods are tried and chosen on it. (3) **The hidden 40 are the check on the tuning:** reported in counts only, never used to choose; a method that helps the visible half but not the hidden half is suspect. (4) **A new measurement set:** written fresh, blind, by the rubric, by a new writer, outside every tree; never used to choose or tune; measured only at decision points (before a re-pin); its figure is the verdict on memory. The CTO proposes its size (at least 40) and the brief for the writer: a new session the owner opens, outside the CTO's system, used only for this. (5) **Memory is reported at every decision point as three figures:** the tuning set, the hidden check, and the measurement set once it exists. The honest reading of memory today is nearer the hidden 72 % than the visible 90 %. **The recall work, in one fix.** (6) **A recall diagnosis** of every never-retrieved question and of the misses beyond the 20 that reach the reranker (ranks 22 and 40 among them); the hidden half by W2-61h's role, in kinds only. It includes the closure route's unranked set: whether it crowds the fusion or cuts gold chunks out of the 20. (7) **Then generic fixes** that help any question (candidate depth, how the routes and the closure enter the fusion, coverage), never fixes aimed at named misses; each is chosen on the visible half and checked on the hidden half. No new method is chosen on the visible half alone until the diagnosis is in. (8) **Then the 0.6B re-measured with the fixes**, on the tuning sets and the new measurement set: its new record. **How choices are made.** (9) **The finer choice measure:** hit@5, then the mean reciprocal rank of the first gold source, from the kept ranks; recorded as the written rule before any further choice, for the methods and for the rerankers when they return. (10) **The rerankers come back only after the 0.6B's new record:** chosen on the tuning sets with that measure, confirmed on the measurement set. (11) **The index-time methods (M1 to M5):** judged as written (DAY.md's rule on m6, with (9)'s tie-break), and each also confirmed on the measurement set before window 4, so a gain on the tuning set alone cannot carry it. **The questions themselves.** (12) **A blind phrasing audit** on both halves, counts only. (13) **Q07 and Q14 re-worded to stable facts** (R11), by an independent session. (14) **A standing rule:** labels are audited on a schedule, all questions at once, never because a question missed.
 - **Accepted later (owner, 2026-11-04 ~19:10, in the chat):** (4) the measurement set is **60 questions**, as the CTO proposed in ACT-MSET-1; its "about 75 %" is only the assumption behind the precision figure, not an expectation: **the target is unchanged, 95 % hit@5, with 85 % the floor, and it is to be achieved** (stated in ACT-MSET-1 before the writer reads it). The path-map line declaring `memory-verdict` (its hidden glob; every role but the orchestrator refused) is approved. **The order stands:** the recall diagnosis and its generic fixes; then the 0.6B re-measured on the tuning sets and the measurement set; then the rerankers (mxbai-rerank-large-v2, then Qwen3-Reranker-4B in 8-bit) trialled the same way; then the results to the owner, who decides.
 - **Basis:** question 1 (memory: a verdict from a set never used to choose, and recall fixed before ranking is tuned) and question 2 (selection pressure from named misses fits the tuning set; the hidden half and a fresh set keep the figure honest).
@@ -13269,7 +13269,7 @@
 - **Basis:** question 1 (memory: a link recorded when a record is written, and checked cheaply, keeps every agent on the current rule) and question 2 (a measurement used once must measure the final structure).
 
 ### DEC-1074 — The night's result decided: 67.8 % the 0.6B's honest figure; every used set now tuning or diagnostic; the 60's misses classified before the next lever; a new verdict set of 80; consistency within 5 points; v456 and the stated links approved for window 4; W2-54's premise rewritten; LINK-INTEGRITY adopted; the open items
-- **Status:** ACCEPTED (owner, 2026-11-05 morning, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-05)`) · **Under:** DEC-1071, DEC-1072, DEC-1073 · **Changes:** DEC-1071 (3) (the consistency bound, item 4), DEC-1070 (2)-(4) (the sets' jobs, item 1) · **Source:** `governance/project/orchestration/packages/LIFT-1/D4B-MORNING-2026-11-05.md` (`7f5a80b7`), `LINK-INTEGRITY.md` (`23610a2e`) · **Changed by:** DEC-1076 (1)
+- **Status:** ACCEPTED (owner, 2026-11-05 morning, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-05)`) · **Under:** DEC-1071, DEC-1072, DEC-1073 · **Changes:** DEC-1071 (3) (the consistency bound, item 4), DEC-1070 (2)-(4) (the sets' jobs, item 1) · **Source:** `governance/project/orchestration/packages/LIFT-1/D4B-MORNING-2026-11-05.md` (`7f5a80b7`), `LINK-INTEGRITY.md` (`23610a2e`) · **Changed by:** DEC-1076 (1) · **Changed by:** DEC-1087 (7)
 - **Decision:**
   - **(1) 67.8 % is recorded as the 0.6B's honest figure on this structure:** v456 + the stated links, 40/59 on
     `memory-verdict`.
```

```diff w2-130:patch-b1
diff --git a/.tickets/DAEO-057v.md b/.tickets/DAEO-057v.md
--- a/.tickets/DAEO-057v.md
+++ b/.tickets/DAEO-057v.md
@@ -35,6 +35,14 @@
 profile: STANDARD
 sources:
 - CAP-43
+- W2-H021
+- W2-H032
+- W2-L172
+- W2-L173
+- W2-L174
+- W2-L230
+- W2-M123
+- W2-M279
 est_loc: 140
 acceptance_tests:
   path: tests/acceptance/W2-18/
diff --git a/.tickets/DAEO-0pyc.md b/.tickets/DAEO-0pyc.md
--- a/.tickets/DAEO-0pyc.md
+++ b/.tickets/DAEO-0pyc.md
@@ -49,6 +49,23 @@
 - DEC-725
 - DEC-954
 - DEC-957
+- DEC-1031
+- DEC-1055
+- DEC-1064
+- DEC-1065
+- DEC-1066
+- DEC-1067
+- DEC-1068
+- DEC-1069
+- DEC-1071
+- DEC-1074
+- DEC-1083
+- DEC-1086
+- W2-L065
+- W2-M073
+- W2-M103
+- W2-M104
+- W2-M191
 est_loc: 320
 acceptance_tests:
   path: tests/acceptance/W2-32/
diff --git a/.tickets/DAEO-0z8c.md b/.tickets/DAEO-0z8c.md
--- a/.tickets/DAEO-0z8c.md
+++ b/.tickets/DAEO-0z8c.md
@@ -36,6 +36,23 @@
 sources:
 - DEC-710
 - DEC-971
+- DEC-580
+- DEC-712
+- DEC-777
+- DEC-783
+- DEC-802
+- DEC-804
+- DEC-805
+- DEC-807
+- DEC-906
+- DEC-951
+- DEC-953
+- DEC-970
+- DEC-980
+- W2-L160
+- W2-M105
+- W2-M113
+- W2-M161
 est_loc: 140
 acceptance_tests:
   path: tests/acceptance/W2-05/
diff --git a/.tickets/DAEO-2bdu.md b/.tickets/DAEO-2bdu.md
--- a/.tickets/DAEO-2bdu.md
+++ b/.tickets/DAEO-2bdu.md
@@ -84,6 +84,14 @@
 - CAP-10
 - CAP-19
 - DEC-957
+- CAP-44.b
+- CAP-44.f
+- CAP-44.g
+- DEC-016
+- DEC-1083
+- DEC-1084
+- W2-124
+- W2-26
 est_loc: 500
 acceptance_tests:
   path: tests/acceptance/W2-88/
diff --git a/.tickets/DAEO-4k3l.md b/.tickets/DAEO-4k3l.md
--- a/.tickets/DAEO-4k3l.md
+++ b/.tickets/DAEO-4k3l.md
@@ -59,6 +59,12 @@
 - CAP-31.d
 - CAP-33.a
 - DEC-983
+- CAP-44.a
+- DEC-1052
+- DEC-1083
+- DEC-968
+- DEC-982
+- W2-128
 est_loc: 200
 acceptance_tests:
   path: tests/acceptance/W2-82/
diff --git a/.tickets/DAEO-6n5k.md b/.tickets/DAEO-6n5k.md
--- a/.tickets/DAEO-6n5k.md
+++ b/.tickets/DAEO-6n5k.md
@@ -34,6 +34,9 @@
 - CAP-33.b
 - CAP-33.g
 - DEC-167
+- DEC-1083
+- W2-L319
+- W2-M285
 est_loc: 280
 acceptance_tests:
   path: tests/acceptance/W2-37/
diff --git a/.tickets/DAEO-6ox0.md b/.tickets/DAEO-6ox0.md
--- a/.tickets/DAEO-6ox0.md
+++ b/.tickets/DAEO-6ox0.md
@@ -31,6 +31,18 @@
 sources:
 - CAP-61.f
 - DEC-160
+- DEC-1083
+- W2-H052
+- W2-L316
+- W2-L328
+- W2-M334
+- W2-M335
+- W2-M336
+- W2-M337
+- W2-M338
+- W2-M344
+- W2-M347
+- W2-M350
 est_loc: 60
 acceptance_tests:
   judged_by: 'its class (WBS §0 rule 1, W2-07): its evidence record'
diff --git a/.tickets/DAEO-6y0x.md b/.tickets/DAEO-6y0x.md
--- a/.tickets/DAEO-6y0x.md
+++ b/.tickets/DAEO-6y0x.md
@@ -36,6 +36,7 @@
 - DEC-820
 - DEC-845
 - DEC-873
+- DEC-1010
 est_loc: 0
 acceptance_tests:
   path: tests/acceptance/W2-93/
diff --git a/.tickets/DAEO-a3u2.md b/.tickets/DAEO-a3u2.md
--- a/.tickets/DAEO-a3u2.md
+++ b/.tickets/DAEO-a3u2.md
@@ -45,6 +45,11 @@
 - DEC-833
 - DEC-860
 - CAP-10.a
+- DEC-1013
+- DEC-1055
+- DEC-1084
+- DEC-968
+- DEC-996
 est_loc: 30
 acceptance_tests:
   path: tests/acceptance/W2-91/
diff --git a/.tickets/DAEO-arrl.md b/.tickets/DAEO-arrl.md
--- a/.tickets/DAEO-arrl.md
+++ b/.tickets/DAEO-arrl.md
@@ -47,6 +47,11 @@
 - DEC-833
 - DEC-941
 - DEC-983
+- DEC-1028
+- DEC-1083
+- DEC-1084
+- DEC-953
+- DEC-982
 est_loc: 150
 acceptance_tests:
   path: tests/acceptance/W2-55/
diff --git a/.tickets/DAEO-blwa.md b/.tickets/DAEO-blwa.md
--- a/.tickets/DAEO-blwa.md
+++ b/.tickets/DAEO-blwa.md
@@ -33,6 +33,10 @@
 - DEC-1014
 - DEC-1011
 - DEC-1001
+- DEC-1015
+- DEC-1027
+- DEC-982
+- DEC-996
 est_loc: 150
 acceptance_tests:
   path: tests/acceptance/W2-122/
diff --git a/.tickets/DAEO-cb2b.md b/.tickets/DAEO-cb2b.md
--- a/.tickets/DAEO-cb2b.md
+++ b/.tickets/DAEO-cb2b.md
@@ -55,6 +55,26 @@
 - DEC-1003
 - DEC-979
 - DEC-998
+- DEC-1009
+- DEC-1010
+- DEC-1014
+- DEC-1015
+- DEC-1018
+- DEC-1030
+- DEC-1031
+- DEC-1083
+- DEC-1084
+- DEC-1088
+- DEC-715
+- DEC-944
+- DEC-952
+- DEC-982
+- DEC-983
+- DEC-989
+- DEC-995
+- W2-118
+- W2-21
+- W2-H046
 est_loc: 500
 acceptance_tests:
   path: tests/acceptance/W2-121/
diff --git a/.tickets/DAEO-clon.md b/.tickets/DAEO-clon.md
--- a/.tickets/DAEO-clon.md
+++ b/.tickets/DAEO-clon.md
@@ -51,6 +51,7 @@
 - DEC-1048
 - DEC-1068
 - ADR-0002
+- DEC-1034
 est_loc: 200
 acceptance_tests:
   path: tests/acceptance/W2-112/
diff --git a/.tickets/DAEO-cv58.md b/.tickets/DAEO-cv58.md
--- a/.tickets/DAEO-cv58.md
+++ b/.tickets/DAEO-cv58.md
@@ -51,6 +51,10 @@
 - DEC-801
 - DEC-786
 - DEC-941
+- CAP-35.c
+- CAP-36.a
+- DEC-1014
+- DEC-1015
 est_loc: 250
 acceptance_tests:
   path: tests/acceptance/W2-60a/
diff --git a/.tickets/DAEO-ecac.md b/.tickets/DAEO-ecac.md
--- a/.tickets/DAEO-ecac.md
+++ b/.tickets/DAEO-ecac.md
@@ -54,6 +54,12 @@
 - DEC-957
 - DEC-959
 - DEC-983
+- CAP-36.a
+- DEC-847
+- DEC-953
+- DEC-963
+- DEC-982
+- W3-P09
 est_loc: 160
 acceptance_tests:
   path: tests/acceptance/W2-60b/
diff --git a/.tickets/DAEO-emq1.md b/.tickets/DAEO-emq1.md
--- a/.tickets/DAEO-emq1.md
+++ b/.tickets/DAEO-emq1.md
@@ -65,6 +65,18 @@
 - DEC-968
 - DEC-966
 - DEC-953
+- DEC-1001
+- DEC-1002
+- DEC-1003
+- DEC-1010
+- DEC-1014
+- DEC-1015
+- DEC-1050
+- DEC-1083
+- DEC-959
+- DEC-988
+- DEC-989
+- W2-117
 est_loc: 400
 acceptance_tests:
   path: tests/acceptance/W2-115/
diff --git a/.tickets/DAEO-f58b.md b/.tickets/DAEO-f58b.md
--- a/.tickets/DAEO-f58b.md
+++ b/.tickets/DAEO-f58b.md
@@ -43,6 +43,13 @@
 - DEC-982
 - DEC-963
 - DEC-966
+- DEC-1014
+- DEC-1015
+- DEC-1083
+- DEC-1087
+- DEC-719
+- W2-06
+- W2-M088
 est_loc: 150
 acceptance_tests:
   path: tests/acceptance/W2-116/
diff --git a/.tickets/DAEO-fau3.md b/.tickets/DAEO-fau3.md
--- a/.tickets/DAEO-fau3.md
+++ b/.tickets/DAEO-fau3.md
@@ -36,6 +36,20 @@
 profile: FULL
 sources:
 - DEC-729
+- W2-H006
+- W2-H007
+- W2-H009
+- W2-H010
+- W2-H011
+- W2-H013
+- W2-H031
+- W2-L216
+- W2-M019
+- W2-M031
+- W2-M047
+- W2-M061
+- W2-M067
+- W2-M173
 est_loc: 180
 acceptance_tests:
   path: tests/acceptance/W2-42/
diff --git a/.tickets/DAEO-fu3n.md b/.tickets/DAEO-fu3n.md
--- a/.tickets/DAEO-fu3n.md
+++ b/.tickets/DAEO-fu3n.md
@@ -43,6 +43,12 @@
 - DEC-965
 - DEC-966
 - DEC-953
+- DEC-1016
+- DEC-1022
+- DEC-822
+- DEC-906
+- DEC-970
+- MR-3
 est_loc: 60
 acceptance_tests:
   path: tests/acceptance/W2-90c/
diff --git a/.tickets/DAEO-g29a.md b/.tickets/DAEO-g29a.md
--- a/.tickets/DAEO-g29a.md
+++ b/.tickets/DAEO-g29a.md
@@ -41,6 +41,9 @@
 - DEC-957
 - DEC-982
 - DEC-974
+- DEC-1083
+- DEC-991
+- DEC-994
 est_loc: 60
 acceptance_tests:
   path: tests/acceptance/W2-113/
diff --git a/.tickets/DAEO-h2k3.md b/.tickets/DAEO-h2k3.md
--- a/.tickets/DAEO-h2k3.md
+++ b/.tickets/DAEO-h2k3.md
@@ -51,6 +51,17 @@
 - DEC-954
 - DEC-957
 - DEC-950
+- DEC-1052
+- DEC-1055
+- DEC-1068
+- DEC-1069
+- DEC-1070
+- DEC-1074
+- DEC-1078
+- DEC-1079
+- DEC-1083
+- DEC-1084
+- DEC-866
 est_loc: 0
 acceptance_tests:
   path: tests/acceptance/W2-61h/
diff --git a/.tickets/DAEO-i89t.md b/.tickets/DAEO-i89t.md
--- a/.tickets/DAEO-i89t.md
+++ b/.tickets/DAEO-i89t.md
@@ -33,6 +33,8 @@
 - DEC-992
 - CAP-24.b
 - DEC-718
+- DEC-1083
+- W2-L097
 est_loc: 80
 acceptance_tests:
   path: tests/acceptance/W2-120/
diff --git a/.tickets/DAEO-jip3.md b/.tickets/DAEO-jip3.md
--- a/.tickets/DAEO-jip3.md
+++ b/.tickets/DAEO-jip3.md
@@ -33,6 +33,8 @@
 - CAP-59.b
 - CAP-56
 - DEC-096
+- DEC-1083
+- W2-25
 est_loc: 0
 acceptance_tests:
   path: tests/acceptance/W2-47/
diff --git a/.tickets/DAEO-jpr0.md b/.tickets/DAEO-jpr0.md
--- a/.tickets/DAEO-jpr0.md
+++ b/.tickets/DAEO-jpr0.md
@@ -48,6 +48,13 @@
 - DEC-1031
 - DEC-1015
 - DEC-374
+- DEC-1026
+- DEC-1033
+- DEC-1039
+- DEC-1042
+- DEC-1046
+- DEC-1052
+- W2-123
 est_loc: 150
 acceptance_tests:
   path: tests/acceptance/W2-126/
diff --git a/.tickets/DAEO-jzvg.md b/.tickets/DAEO-jzvg.md
--- a/.tickets/DAEO-jzvg.md
+++ b/.tickets/DAEO-jzvg.md
@@ -46,6 +46,15 @@
 - DEC-736
 - DEC-757
 - DEC-762
+- DEC-1083
+- DEC-890
+- W2-H026
+- W2-H042
+- W2-L119
+- W2-M159
+- W2-M160
+- W2-M162
+- W2-M253
 est_loc: 300
 acceptance_tests:
   path: tests/acceptance/W2-19/
diff --git a/.tickets/DAEO-k7hz.md b/.tickets/DAEO-k7hz.md
--- a/.tickets/DAEO-k7hz.md
+++ b/.tickets/DAEO-k7hz.md
@@ -85,6 +85,21 @@
 - DEC-957
 - DEC-959
 - DEC-983
+- DEC-1083
+- DEC-951
+- DEC-952
+- DEC-953
+- DEC-974
+- DEC-979
+- DEC-982
+- DEC-991
+- DEC-994
+- DEC-995
+- DEC-996
+- W2-L256
+- W2-L257
+- W2-L258
+- W2-L268
 est_loc: 120
 acceptance_tests:
   path: tests/acceptance/W2-11/
diff --git a/.tickets/DAEO-kmcr.md b/.tickets/DAEO-kmcr.md
--- a/.tickets/DAEO-kmcr.md
+++ b/.tickets/DAEO-kmcr.md
@@ -42,6 +42,20 @@
 sources:
 - DEC-729
 - DEC-954
+- W2-H035
+- W2-H036
+- W2-H050
+- W2-M216
+- W2-M217
+- W2-M218
+- W2-M219
+- W2-M220
+- W2-M224
+- W2-M225
+- W2-M229
+- W2-M232
+- W2-M307
+- W2-M312
 est_loc: 220
 acceptance_tests:
   path: tests/acceptance/W2-23/
diff --git a/.tickets/DAEO-l78m.md b/.tickets/DAEO-l78m.md
--- a/.tickets/DAEO-l78m.md
+++ b/.tickets/DAEO-l78m.md
@@ -52,6 +52,15 @@
 - DEC-953
 - DEC-954
 - DEC-957
+- CAP-03.a
+- CAP-03.d
+- CAP-44.b
+- CAP-44.e
+- CAP-44.g
+- CAP-44.h
+- CAP-44.j
+- DEC-898
+- DEC-906
 est_loc: 1200
 acceptance_tests:
   path: tests/acceptance/W2-81/
diff --git a/.tickets/DAEO-lrre.md b/.tickets/DAEO-lrre.md
--- a/.tickets/DAEO-lrre.md
+++ b/.tickets/DAEO-lrre.md
@@ -46,6 +46,15 @@
 - DEC-957
 - DEC-959
 - DEC-983
+- DEC-1010
+- DEC-1083
+- DEC-236
+- DEC-839
+- DEC-847
+- DEC-963
+- DEC-982
+- DEC-991
+- DEC-994
 est_loc: 260
 acceptance_tests:
   path: tests/acceptance/W2-33/
diff --git a/.tickets/DAEO-m4rq.md b/.tickets/DAEO-m4rq.md
--- a/.tickets/DAEO-m4rq.md
+++ b/.tickets/DAEO-m4rq.md
@@ -39,6 +39,10 @@
 - DEC-1084
 - DEC-1083
 - DEC-820
+- DEC-1052
+- DEC-1078
+- DEC-1079
+- W2-61h
 est_loc: 60
 acceptance_tests:
   path: tests/acceptance/W2-134/
diff --git a/.tickets/DAEO-mb2t.md b/.tickets/DAEO-mb2t.md
--- a/.tickets/DAEO-mb2t.md
+++ b/.tickets/DAEO-mb2t.md
@@ -37,6 +37,11 @@
 - DEC-1027
 - DEC-1015
 - DEC-1014
+- DEC-1083
+- DEC-530
+- DEC-954
+- W2-26
+- W2-88
 est_loc: 80
 acceptance_tests:
   path: tests/acceptance/W2-124/
diff --git a/.tickets/DAEO-n0wb.md b/.tickets/DAEO-n0wb.md
--- a/.tickets/DAEO-n0wb.md
+++ b/.tickets/DAEO-n0wb.md
@@ -57,6 +57,9 @@
 - DEC-1072
 - DEC-1073
 - DEC-1074
+- DEC-1055
+- DEC-1065
+- DEC-423
 est_loc: 200
 acceptance_tests:
   path: tests/acceptance/W2-92/
diff --git a/.tickets/DAEO-neam.md b/.tickets/DAEO-neam.md
--- a/.tickets/DAEO-neam.md
+++ b/.tickets/DAEO-neam.md
@@ -32,6 +32,14 @@
 profile: STANDARD
 sources:
 - DEC-729
+- W2-H018
+- W2-M129
+- W2-M130
+- W2-M151
+- W2-M211
+- W2-M212
+- W2-M259
+- W2-M265
 est_loc: 160
 acceptance_tests:
   path: tests/acceptance/W2-45/
diff --git a/.tickets/DAEO-nn1s.md b/.tickets/DAEO-nn1s.md
--- a/.tickets/DAEO-nn1s.md
+++ b/.tickets/DAEO-nn1s.md
@@ -108,6 +108,9 @@
 - DEC-729
 - DEC-953
 - DEC-954
+- DEC-1083
+- DEC-1084
+- W2-24
 est_loc: 0
 acceptance_tests:
   judged_by: 'its class (WBS §0 rule 1, W2-07): its named evidence files'
diff --git a/.tickets/DAEO-nqa2.md b/.tickets/DAEO-nqa2.md
--- a/.tickets/DAEO-nqa2.md
+++ b/.tickets/DAEO-nqa2.md
@@ -51,6 +51,10 @@
 - DEC-966
 - DEC-953
 - DEC-906
+- DEC-1016
+- DEC-999
+- MR-3
+- W2-106
 est_loc: 300
 acceptance_tests:
   path: tests/acceptance/W2-90b/
diff --git a/.tickets/DAEO-ouet.md b/.tickets/DAEO-ouet.md
--- a/.tickets/DAEO-ouet.md
+++ b/.tickets/DAEO-ouet.md
@@ -39,6 +39,9 @@
 - DEC-820
 - DEC-317
 - MR-3
+- DEC-911
+- DEC-970
+- DEC-987
 est_loc: 250
 acceptance_tests:
   path: tests/acceptance/W2-96/
diff --git a/.tickets/DAEO-q7lk.md b/.tickets/DAEO-q7lk.md
--- a/.tickets/DAEO-q7lk.md
+++ b/.tickets/DAEO-q7lk.md
@@ -56,6 +56,7 @@
 - DEC-861
 - DEC-182
 - CAP-27
+- DEC-1088
 est_loc: 400
 acceptance_tests:
   path: tests/acceptance/W2-129/
diff --git a/.tickets/DAEO-qzrq.md b/.tickets/DAEO-qzrq.md
--- a/.tickets/DAEO-qzrq.md
+++ b/.tickets/DAEO-qzrq.md
@@ -37,6 +37,13 @@
 - DEC-1014
 - DEC-1011
 - DEC-1010
+- DEC-1015
+- DEC-1017
+- DEC-1026
+- DEC-1032
+- DEC-1033
+- DEC-982
+- DEC-996
 est_loc: 80
 acceptance_tests:
   path: tests/acceptance/W2-123/
diff --git a/.tickets/DAEO-r30l.md b/.tickets/DAEO-r30l.md
--- a/.tickets/DAEO-r30l.md
+++ b/.tickets/DAEO-r30l.md
@@ -66,6 +66,22 @@
 - DEC-950
 - DEC-954
 - DEC-983
+- DEC-1001
+- DEC-1003
+- DEC-1010
+- DEC-1017
+- DEC-1030
+- DEC-1031
+- DEC-1038
+- DEC-1039
+- DEC-1088
+- DEC-899
+- DEC-961
+- DEC-979
+- DEC-982
+- W2-M188
+- W2-M244
+- W2-M262
 est_loc: 320
 acceptance_tests:
   path: tests/acceptance/W2-20/
diff --git a/.tickets/DAEO-rd0g.md b/.tickets/DAEO-rd0g.md
--- a/.tickets/DAEO-rd0g.md
+++ b/.tickets/DAEO-rd0g.md
@@ -43,6 +43,16 @@
 - DEC-078
 - DEC-954
 - DEC-957
+- DEC-1055
+- DEC-1072
+- DEC-1083
+- W2-15b
+- W2-L102
+- W2-L321
+- W2-L322
+- W2-L329
+- W2-M340
+- W2-M342
 est_loc: 100
 acceptance_tests:
   judged_by: 'its class (WBS §0 rule 1, W2-07): its evidence record'
diff --git a/.tickets/DAEO-sdhj.md b/.tickets/DAEO-sdhj.md
--- a/.tickets/DAEO-sdhj.md
+++ b/.tickets/DAEO-sdhj.md
@@ -33,6 +33,7 @@
 profile: FULL
 sources:
 - CAP-45.a
+- W2-M176
 est_loc: 260
 acceptance_tests:
   path: tests/acceptance/W2-17/
diff --git a/.tickets/DAEO-sdxk.md b/.tickets/DAEO-sdxk.md
--- a/.tickets/DAEO-sdxk.md
+++ b/.tickets/DAEO-sdxk.md
@@ -33,6 +33,24 @@
 profile: LITE
 sources:
 - DEC-729
+- DEC-1032
+- DEC-1033
+- DEC-1037
+- DEC-1038
+- DEC-1039
+- DEC-1040
+- DEC-1045
+- DEC-1050
+- DEC-1052
+- DEC-1055
+- DEC-1061
+- DEC-1063
+- DEC-1066
+- DEC-1067
+- DEC-1069
+- DEC-1073
+- DEC-953
+- DEC-968
 est_loc: 0
 acceptance_tests:
   judged_by: 'its class (WBS §0 rule 1, W2-07): its named evidence files (the exit report)'
diff --git a/.tickets/DAEO-swdu.md b/.tickets/DAEO-swdu.md
--- a/.tickets/DAEO-swdu.md
+++ b/.tickets/DAEO-swdu.md
@@ -54,6 +54,20 @@
 - DEC-860
 - DEC-954
 - DEC-957
+- DEC-1083
+- DEC-798
+- W2-15a
+- W2-61
+- W2-L102
+- W2-L317
+- W2-L320
+- W2-L321
+- W2-L322
+- W2-M017
+- W2-M089
+- W2-M340
+- W2-M342
+- W2-M351
 est_loc: 60
 acceptance_tests:
   judged_by: 'its class (WBS §0 rule 1, W2-07): its evidence record'
diff --git a/.tickets/DAEO-t8mp.md b/.tickets/DAEO-t8mp.md
--- a/.tickets/DAEO-t8mp.md
+++ b/.tickets/DAEO-t8mp.md
@@ -80,6 +80,14 @@
 - DEC-793
 - DEC-943
 - CAP-33
+- DEC-1014
+- DEC-1084
+- DEC-1085
+- DEC-1087
+- DEC-1088
+- DEC-1092
+- DEC-1094
+- W2-11b
 est_loc: 400
 acceptance_tests:
   path: tests/acceptance/W2-128/
diff --git a/.tickets/DAEO-u4oz.md b/.tickets/DAEO-u4oz.md
--- a/.tickets/DAEO-u4oz.md
+++ b/.tickets/DAEO-u4oz.md
@@ -38,6 +38,15 @@
 sources:
 - CAP-15.d
 - DEC-860
+- CAP-15.b
+- DEC-1025
+- DEC-1052
+- W2-H034
+- W2-M126
+- W2-M215
+- W2-M239
+- W2-M294
+- W2-M330
 est_loc: 220
 acceptance_tests:
   path: tests/acceptance/W2-04/
diff --git a/.tickets/DAEO-w19l.md b/.tickets/DAEO-w19l.md
--- a/.tickets/DAEO-w19l.md
+++ b/.tickets/DAEO-w19l.md
@@ -29,6 +29,7 @@
 sources:
 - CAP-32.d
 - DEC-166
+- W2-M284
 est_loc: 160
 acceptance_tests:
   path: tests/acceptance/W2-36/
diff --git a/.tickets/DAEO-wi46.md b/.tickets/DAEO-wi46.md
--- a/.tickets/DAEO-wi46.md
+++ b/.tickets/DAEO-wi46.md
@@ -43,6 +43,8 @@
 - DEC-957
 - DEC-616
 - DEC-645
+- DEC-1083
+- DEC-1084
 est_loc: 150
 acceptance_tests:
   path: tests/acceptance/W2-98/
diff --git a/.tickets/DAEO-wnnz.md b/.tickets/DAEO-wnnz.md
--- a/.tickets/DAEO-wnnz.md
+++ b/.tickets/DAEO-wnnz.md
@@ -63,6 +63,25 @@
 - DEC-784
 - DEC-877
 - DEC-941
+- DEC-1010
+- DEC-1035
+- DEC-1052
+- DEC-1083
+- DEC-715
+- DEC-902
+- W2-112
+- W2-127
+- W2-21
+- W2-I012
+- W2-L105
+- W2-M094
+- W2-M095
+- W2-M097
+- W2-M181
+- W2-M187
+- W2-M275
+- W2-M393
+- W2-M405
 est_loc: 250
 acceptance_tests:
   path: tests/acceptance/W2-56/
diff --git a/.tickets/DAEO-yadm.md b/.tickets/DAEO-yadm.md
--- a/.tickets/DAEO-yadm.md
+++ b/.tickets/DAEO-yadm.md
@@ -35,6 +35,11 @@
 sources:
 - CAP-30.c
 - MR-2
+- W2-H015
+- W2-H051
+- W2-M082
+- W2-M274
+- W2-M283
 est_loc: 180
 acceptance_tests:
   path: tests/acceptance/W2-34/
diff --git a/.tickets/DAEO-zqvn.md b/.tickets/DAEO-zqvn.md
--- a/.tickets/DAEO-zqvn.md
+++ b/.tickets/DAEO-zqvn.md
@@ -51,6 +51,22 @@
 sources:
 - DEC-725
 - DEC-900
+- DEC-1052
+- DEC-1055
+- DEC-1056
+- DEC-1063
+- DEC-1065
+- DEC-1066
+- DEC-419
+- DEC-802
+- DEC-860
+- W2-L233
+- W2-M071
+- W2-M072
+- W2-M100
+- W2-M102
+- W2-M292
+- W2-M296
 est_loc: 300
 acceptance_tests:
   path: tests/acceptance/W2-13/
```

**patch-marks-3:** `gov links --propose-marks --all` at bce798c3a's parent (8f8d707f0). Two of its hunks were
applied, in the auditor's corrected texts; the 8 judged-wrong pairs were not.

```diff w2-130:patch-marks-3
diff --git a/docs/DECISION_REGISTER.md b/docs/DECISION_REGISTER.md
--- a/docs/DECISION_REGISTER.md
+++ b/docs/DECISION_REGISTER.md
@@ -219,7 +219,7 @@
 - **Gates:** A3, E1, N2, N3, O5 (G0–G3 local, G4–G5 CI)
 
 ### DEC-026 — Telemetry
-- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** ESTABLISHED
+- **Status:** ACCEPTED (owner, 2026-09-30, DEC-083; recorded by DEC-1098 (3)); it was PROPOSED · **Basis:** ESTABLISHED · **Changed by:** DEC-086
 - **Decision:** Start with Claude Code OpenTelemetry → local collector → Prometheus → Grafana (no cloud, light). [E-OTEL] Add Langfuse (plugin, self-host or cloud) when per-turn traces are needed. [E-LANGFUSE]
 - **Primary metric:** governance tokens per completed task (DEC-004).
 - **Gates:** P1, P2 (partial), U
@@ -393,7 +393,7 @@
 - **Decision:** Neutralise the hook script (renamed, reversible), remove its wiring from the repo's untracked `.claude/settings.local.json` (backup kept), install gitleaks to `~/.local/bin` with checksum verification, and take a `git bundle --all` backup before any ref surgery. Old per-project Claude Code auto-memory for this repository path, if present, is moved aside only with explicit owner approval.
 
 ### DEC-056 — Restructure executed (record of facts, 2026-09-29)
-- **Status:** DONE · **Basis:** session report
+- **Status:** DONE · **Basis:** session report · **Changed by:** DEC-017
 - Base `1ab6782fa4e8f490c8b97ac6959cdd77a29350f9`; annotated tag `archive/gov-os-v4-final` (tag object `6e4ae20`).
 - Bundle `~/gov-os-inventory/restructure/pre-restructure.bundle`, verified, sha256 `efafe460af693d4159ba4549067309c20c5a2def2aabc0284527aacfc0532434`.
 - 168 branches moved to `refs/archive/heads/*` with matching shas; `main` is the only branch; tags, `refs/safe-hold/*` and `refs/codex/*` unchanged. 72 linked worktrees removed; the read-only `br-frozen-3c880d8` was moved to `~/gov-os-inventory/restructure/`.
@@ -478,7 +478,7 @@
 - The matrix still shows S0a's CORE/LATER labels; Contract v4 relabels them by wave (DEC-064).
 
 ### DEC-072 — S0b2 scope and guardrails
-- **Status:** ACCEPTED (owner, by running it) · **Basis:** SUGGESTION
+- **Status:** ACCEPTED (owner, by running it) · **Basis:** SUGGESTION · **Changed by:** DEC-064
 - **Decision:** S0b2 installs the stack user-level (owner approves each install; versions pinned; uninstall commands recorded), runs twelve integration checks (I-01…I-12) on sandbox clones of the dev tiers, decides the four open choices by BAKEOFF_PLAN's fixed rules (retrieval tie-break now "shared store", since Node ≥ 20.19 is needed for OpenSpec anyway), compiles the dev tiers' Rust and TypeScript for the first time, and measures resources. The scale probe indexes an owner-generated qual tier of Programme B in `s0b2/probe/`; the session may not read its contents or the oracle. beads_rust excluded (Q2). Running S0b2 accepts S0a Q2, Q6 (probe on the qual tier) and Q7 (user-level, approved installs); Q1, Q3, Q5, Q8, Q9 settle in S1; Q4 is superseded by DEC-064.
 
 ### DEC-073 — Operating model until the Gov OS lands
@@ -1097,7 +1097,7 @@
 The KPI text of the three tickets is unchanged. W1-04's `allowed_paths` change under DEC-120 only.
 
 ### DEC-120 — W1-04 KD-1: the install rule reaches the harness through the PreToolUse guard
-- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-04 KPI dispute KD-1 · **Implements:** DEC-083 · **Changed by:** its settings "second line" withdrawn by DEC-172 (shown by DEC-825, 2026-10-19)
+- **Status:** ACCEPTED (owner, 2026-10-01) · **Basis:** OWNER, on W1-04 KPI dispute KD-1 · **Implements:** DEC-083 · **Changed by:** its settings "second line" withdrawn by DEC-172 (shown by DEC-825, 2026-10-19) · **Changed by:** DEC-173
 - **Decision:** The install rule reaches the harness through the PreToolUse guard. For a Bash call it classifies as an
   install, the guard returns the permission decision `ask` when the acting role is orchestrator, and `deny` for every
   other role, and for no role. The classifier only ever escalates: a match never allows something the harness would
@@ -1472,7 +1472,7 @@
   - that its `GOV_ROLE` and `GOV_TICKET` reach the guard.
 
 ### DEC-162 — The qualification oracle is hidden from every session started in the repository root
-- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, answer to the S2 open point on DEC-161 · **Refines:** DEC-152 (oracle hiding), DEC-161
+- **Status:** ACCEPTED (owner, 2026-10-03) · **Basis:** OWNER, answer to the S2 open point on DEC-161 · **Refines:** DEC-152 (oracle hiding), DEC-161 · **Changed by:** DEC-156
 - **Decision:** The qualification oracle is hidden from every session started in the repository root, the unsandboxed
   orchestrator included, by two layers:
   - a `Read` deny rule with the oracle's absolute path in the repository's committed `.claude/settings.json`;
@@ -7700,7 +7700,7 @@
   4. **Agents never list, glob or search `~/gov-os-workbench`.** They name a file there explicitly, or ask the owner.
 
 ### DEC-724 — Owner acceptances are owner git facts: `Role: owner`, batched, and a `gov approve` command (P-W2-5 (a), refined)
-- **Status:** ACCEPTED (owner, 2026-10-16; the owner commits this entry with `Role: owner`) · **Changed by:** its owner commits replaced by DEC-861: the orchestrator commits the records with `Decided-by: owner`, the owner pushes (2026-10-20) · **Under:** DEC-409, DEC-718 (AR-7, F-M6) · **Basis:** F-M6 found register entries set ACCEPTED in commits the orchestrator made, with no git fact of the owner's approval.
+- **Status:** ACCEPTED (owner, 2026-10-16; the owner commits this entry with `Role: owner`) · **Changed by:** its owner commits replaced by DEC-861: the orchestrator commits the records with `Decided-by: owner`, the owner pushes (2026-10-20) · **Under:** DEC-409, DEC-718 (AR-7, F-M6) · **Basis:** F-M6 found register entries set ACCEPTED in commits the orchestrator made, with no git fact of the owner's approval. · **Changed by:** DEC-860
 - **Decision:**
   1. From now on, the owner commits every owner register entry with `Role: owner`. The orchestrator drafts and stages; it never commits an owner entry.
   2. **Owner decisions are staged in batches:** at most one owner commit per session break.
@@ -9274,7 +9274,7 @@
 The owner committed DEC-831 to DEC-852 (`a5789de1`) and answered the two packages of that report, the notification test and the rebuild's cost. Every entry below is the owner's; the owner commits them with `Role: owner`, with the files they govern, in one batch.
 
 ### DEC-853 — P-W2-49 (a): the secrets scan's time limit and pool are fixed in W2-50's resume; a store unchanged since its last clean scan is not re-scanned
-- **Status:** DONE (owner, 2026-11-09, DEC-1098 (3)); it was ACCEPTED (owner, 2026-10-19; the owner commits this entry with `Role: owner`, in the next batch; the change to a hard-block check's mechanics is approved here, CAP-33) · **Under:** DEC-802, DEC-780, CAP-38.b · **Basis:** P-W2-49 (`governance/project/orchestration/packages/P-W2-49.md`): `secrets-indexing` timed out (60 s per gitleaks run, about 24 at a time) on `store.db` (250 MB) and `code.db` (210 MB), so every close would be refused.
+- **Status:** DONE (owner, 2026-11-09, DEC-1098 (3)); it was ACCEPTED (owner, 2026-10-19; the owner commits this entry with `Role: owner`, in the next batch; the change to a hard-block check's mechanics is approved here, CAP-33) · **Under:** DEC-802, DEC-780, CAP-38.b · **Basis:** P-W2-49 (`governance/project/orchestration/packages/P-W2-49.md`): `secrets-indexing` timed out (60 s per gitleaks run, about 24 at a time) on `store.db` (250 MB) and `code.db` (210 MB), so every close would be refused. · **Changed by:** DEC-884 (item 4)
 - **Decision:**
   1. **(a):** the fix rides in W2-50's resume, which already rewrites `stores_with_secrets` in `src/gov/secrets/__init__.py`: the time limit grows with the content's size (or a large store is scanned in bounded chunks, each within the limit), and the pool is bounded so that large files are not starved. Every file is still scanned with every rule set, and a scan that cannot finish still fails closed.
   2. **Added by the owner:** a store whose hash has not changed since its last clean scan is not re-scanned; the clean result is reused, keyed on the store's hash. A changed store is always scanned in full. **A finding is never reused.**
@@ -13005,7 +13005,7 @@
 | 0.432 | 2026-11-02 | Owner (recorded by the orchestrator, DEC-861): DEC-1049. Next free id: DEC-1050. |
 
 ### DEC-1050 — P1-LIFT-1's twelve decide-first rows decided; the refactoring's parallel work: brief templates, the plan, the remaining 63 rows
-- **Status:** ACCEPTED (owner, 2026-11-02 ~22:46, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-02)`; standing) · **Under:** DEC-1047, DEC-1049, DEC-1010, DEC-953 item 2 · **Changes:** DEC-958 (the harvest), DEC-991's `rm` ask, DEC-1049 (widened) · **Superseded by:** DEC-1158 (1) (item (5))
+- **Status:** ACCEPTED (owner, 2026-11-02 ~22:46, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-02)`; standing) · **Under:** DEC-1047, DEC-1049, DEC-1010, DEC-953 item 2 · **Changes:** DEC-958 (the harvest), DEC-991's `rm` ask, DEC-1049 (widened) · **Superseded by:** DEC-1158 (1) (item (5)) · **Changed by:** DEC-1057 (8)
 - **Decision (the owner's words, in short):** the emergency is at its highest. (1)-(4) **T-5, T-4, T-1, Q-1 approved**; further: if the merge queue and the close already run what `gov check` protects, the full `gov check` leaves leads' verification altogether (the CTO checks and reports). (5) **T-12, O-10 approved, and wider: nothing scheduled runs until the refactoring is finished**; the full suite runs next only on the refactored repository, on the owner's word; the old regime's acceptance of reds and the checks built around it do not carry over. (6) **The guard harvest stops** (done: `guard_harvest_s` 10^9 in the dispatcher's config, backup `.pre-dec1050`); the five guard rules stay, but during the refactoring they are fixed into good, smart practice: they must not refuse honest work again and again. (7) **R-1 to R-5 refused as written:** cutting the brief is not the fix; find out why leads read only about 3 % of it (who wrote it, how it is built, what they skip and why); a lead in a repository of 170,000 lines needs better guidance, not less: the right paths, commands and how to report; the fix is better brief templates that agents actually read and follow. (8) **O-7 approved, and wider:** agents may delete freely (`rm`) without asking; protect only against the catastrophic: deleting the repository, its `.git`, the main tree's tracked files, or anything outside the project and its scratch. (9) **R-8, R-11 approved:** pings only when work waits on the owner, two digests a day; not a priority. (10) **O-1, O-2, O-4 refused:** no cut to the CTO's prompt without evidence that it improves delivery; the measure is productivity, delivered work and less drift, not tokens or cost. (11) **G-12 refused:** review effort stays as it is. (12) **G-1, G-2 approved now:** rules 1 and 5 stop guessing at shell commands, the landing check on who wrote any acceptance test going in first; the root fix is agents briefed so well (commands, paths, how to report) that they do not trip the guard, with the templates. **Keep this repository: approved.** **Templates (new, in parallel):** investigate how good software companies brief and record work (ticket and task templates, specs and acceptance criteria, definitions of ready and done, design notes, pull-request and review templates, hand-overs); design templates for every role (research and discovery, product-spec, test designer, engineer, QA and reviewer, lead, CTO) and for tickets and briefs, so every session uses the same ones and agents read and follow them, alongside the roles and skills; bring them as spec and KPIs for tasks in the refactoring. **The 63 remaining rows and the plan:** the owner reviews the remaining rows now; in parallel the CTO drafts the refactoring plan (every row's change, the ticket fates, the approved test refactor P1-INVENTORY-1, the code tidy-up, the templates, the WBS refactor DEC-1039 step 3b; for each step who does it, the order, how it is verified, the time, and the new estimate for EXAMIN's copy), updated after the owner's decisions on the rows. Nothing else is lifted before the owner decides.
 
 | Version | Date | Change |
@@ -13039,7 +13039,7 @@
 | 0.436 | 2026-11-03 | Owner (recorded by the orchestrator, DEC-861): DEC-1052 gains the basis as a standing practice. Next free id: DEC-1053. |
 
 ### DEC-1053 — D-0's clean-up list decided: what is merged, what is deleted, what waits for D-9
-- **Status:** ACCEPTED (owner, 2026-11-03 ~11:55, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-03)`) · **Under:** DEC-1052 (D-0, O-8, O-13) · **Source:** `governance/project/orchestration/packages/LIFT-1/D0-CLEANUP-LIST.md` (`ad3d1529`) · **Changed by:** DEC-1164 (12) (item (6): the CTO disposes of the branches now)
+- **Status:** ACCEPTED (owner, 2026-11-03 ~11:55, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-03)`) · **Under:** DEC-1052 (D-0, O-8, O-13) · **Source:** `governance/project/orchestration/packages/LIFT-1/D0-CLEANUP-LIST.md` (`ad3d1529`) · **Changed by:** DEC-1164 (12) (item (6): the CTO disposes of the branches now) · **Changed by:** DEC-880
 - **Decision:** every ASK line as recommended. (1) `emg/w1-19-helper` (`a0d1d3a0`, the W1-19 test helper, DEC-1046 item 3) is merged into `w2/integrate` in D-1, then its branch and worktree deleted. (2) `w2/W2-48` (the cache withdrawn by DEC-880) is deleted. (3) W2-67's stray planted file `tests/acceptance/W1-27/w2_67_td4_plant.py` (untracked, in the W2-67 worktree) is deleted. (4) The 42 worktrees and branches with nothing unmerged are removed, after each worktree's ignored `.gov-runtime/scratch/` is archived to `.gov-runtime/scratch/orchestrator/archive/worktree-scratch/<name>/`. (5) The run folders as listed: the 56 near-empty folders; the base and head clones of W2-55, W2-86, W2-87 and W2-61's `repo/`, keeping `measure/`, `records/`, `register/` and `logs/` (the measures' evidence); in `W2-00/`, `close/`, `precheck-w254-20261030-2146/`, `w103-before-w272/` and `tooltrials/`. (6) `w2/W2-78` and the in-flight tickets' branches with unmerged work wait for D-9's fates.
 - **Basis:** question 4 (less to search and keep; nothing that holds work is lost) and question 2 (no work lost: unmerged work listed first).
 
@@ -14178,7 +14178,7 @@
 
 
 ### DEC-1115 — Yes to ACT-SETS-GLOBS-1 (by hand) and ACT-CLAUDE-COPIES-1 (by the operator agent, its first live run); TPL-6's Appendix A applied now; before the lift, past 80 % of the week's usage only the lift's critical path runs
-- **Status:** ACCEPTED (owner, 2026-11-09, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-09)`); item (4) standing until the lift · **Under:** DEC-1104 (4), DEC-1112 (3), DEC-1050, DEC-1052, DEC-1089 (3), DEC-1091 · **Source:** the owner's message (chat, 2026-11-09), on ACT-SETS-GLOBS-1, ACT-CLAUDE-COPIES-1, TPL6-APPENDIX-A and FORECAST-W2-2 §5 · **Changed:** item (4) changed by DEC-1149 (3) (usage never stops a lead; report only); item (4) spent at the lift, DEC-1164 (7)
+- **Status:** ACCEPTED (owner, 2026-11-09, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-09)`); item (4) standing until the lift · **Under:** DEC-1104 (4), DEC-1112 (3), DEC-1050, DEC-1052, DEC-1089 (3), DEC-1091 · **Source:** the owner's message (chat, 2026-11-09), on ACT-SETS-GLOBS-1, ACT-CLAUDE-COPIES-1, TPL6-APPENDIX-A and FORECAST-W2-2 §5 · **Changed:** item (4) changed by DEC-1149 (3) (usage never stops a lead; report only); item (4) spent at the lift, DEC-1164 (7) · **Changed by:** DEC-1122 (4)
 - **Decision:**
   - (1) **ACT-SETS-GLOBS-1: yes** (`yes ACT-SETS-GLOBS-1 1f93d6ef`, class (b)); the owner's operator applies it by
     hand now (the package's §5).
```

## 5. The tickets' `sources:` (S4)

- **e12f8a30c (b1):** 394 ids added to 50 open and in-progress tickets, from `gov links --propose-sources`; no
  closed ticket touched (DEC-1098 (3), H1 (b)).
- **Follow-up (1), 57cbacfbfc86:** `gov links --propose-sources --all` at its parent (11c4d7a5a),
  the open and in-progress tickets' sections (patch-sources-2), less the 65 ids DEC-1123 (2)'s forms already
  link (P-W2-130-4 (a)): 53 backlog rows in their ticket's `list_rows`, 11
  WBS ids whose ticket's id is in `sources:`, 1 DEC-798 through its live DEC-1033. It adds
  32 ids to 12 tickets and changes only `sources:` lines. (W3-P09 on DAEO-ecac, a plan row in that
  ticket's `list_rows`, is one of the forms; a first version of the commit added it and was amended before the
  commit left this branch.)
- **W2-H046** on DAEO-6w5n is the one backlog row not in its ticket's `list_rows`. It is added to `sources:` as
  `--propose-sources` gives it: putting it in `list_rows` would change a field other than `sources:` (F1).
- **After:** `gov links --all` reports UNLINKED_ID on an open or in-progress ticket only for the 65 ids
  below, each linked by one of DEC-1123 (2)'s forms. A D-6 row asks `gov links` to read `list_rows` and a WBS id's
  ticket id as linked, so these stop being reported.

```yaml w2-130:dec-1123-linked
DAEO-057v:
- form: list_rows
  id: W2-H021
  via: W2-H021
- form: list_rows
  id: W2-H032
  via: W2-H032
- form: list_rows
  id: W2-L172
  via: W2-L172
- form: list_rows
  id: W2-L173
  via: W2-L173
- form: list_rows
  id: W2-L174
  via: W2-L174
- form: list_rows
  id: W2-L230
  via: W2-L230
- form: list_rows
  id: W2-M123
  via: W2-M123
- form: list_rows
  id: W2-M279
  via: W2-M279
DAEO-4k3l:
- form: wbs
  id: W2-128
  via: DAEO-t8mp
DAEO-6w5n:
- form: wbs
  id: W2-118
  via: DAEO-ts4y
- form: wbs
  id: W2-21
  via: DAEO-1ahb
DAEO-ar89:
- form: wbs
  id: W1-19
  via: DAEO-t6hf
DAEO-ecac:
- form: list_rows
  id: W3-P09
  via: W3-P09
DAEO-fau3:
- form: list_rows
  id: W2-H006
  via: W2-H006
- form: list_rows
  id: W2-H007
  via: W2-H007
- form: list_rows
  id: W2-H009
  via: W2-H009
- form: list_rows
  id: W2-H010
  via: W2-H010
- form: list_rows
  id: W2-H011
  via: W2-H011
- form: list_rows
  id: W2-H013
  via: W2-H013
- form: list_rows
  id: W2-H031
  via: W2-H031
- form: list_rows
  id: W2-L216
  via: W2-L216
- form: list_rows
  id: W2-M019
  via: W2-M019
- form: list_rows
  id: W2-M031
  via: W2-M031
- form: list_rows
  id: W2-M047
  via: W2-M047
- form: list_rows
  id: W2-M061
  via: W2-M061
- form: list_rows
  id: W2-M067
  via: W2-M067
- form: list_rows
  id: W2-M173
  via: W2-M173
DAEO-j9z6:
- form: wbs
  id: W2-117
  via: DAEO-zkr9
DAEO-jip3:
- form: wbs
  id: W2-25
  via: DAEO-btt7
DAEO-jzvg:
- form: list_rows
  id: W2-H026
  via: W2-H026
- form: list_rows
  id: W2-H042
  via: W2-H042
- form: list_rows
  id: W2-L119
  via: W2-L119
- form: list_rows
  id: W2-M159
  via: W2-M159
- form: list_rows
  id: W2-M160
  via: W2-M160
- form: list_rows
  id: W2-M162
  via: W2-M162
- form: list_rows
  id: W2-M253
  via: W2-M253
DAEO-m4rq:
- form: wbs
  id: W2-61h
  via: DAEO-h2k3
DAEO-nn1s:
- form: wbs
  id: W2-24
  via: DAEO-0mab
DAEO-rd0g:
- form: wbs
  id: W2-15b
  via: DAEO-swdu
- form: list_rows
  id: W2-L102
  via: W2-L102
- form: list_rows
  id: W2-L321
  via: W2-L321
- form: list_rows
  id: W2-L322
  via: W2-L322
- form: list_rows
  id: W2-L329
  via: W2-L329
- form: list_rows
  id: W2-M340
  via: W2-M340
- form: list_rows
  id: W2-M342
  via: W2-M342
DAEO-sdhj:
- form: list_rows
  id: W2-M176
  via: W2-M176
DAEO-swdu:
- form: dec-798
  id: DEC-798
  via: DEC-1033
- form: wbs
  id: W2-15a
  via: DAEO-rd0g
- form: wbs
  id: W2-61
  via: DAEO-iw1f
- form: list_rows
  id: W2-L102
  via: W2-L102
- form: list_rows
  id: W2-L317
  via: W2-L317
- form: list_rows
  id: W2-L320
  via: W2-L320
- form: list_rows
  id: W2-L321
  via: W2-L321
- form: list_rows
  id: W2-L322
  via: W2-L322
- form: list_rows
  id: W2-M017
  via: W2-M017
- form: list_rows
  id: W2-M089
  via: W2-M089
- form: list_rows
  id: W2-M340
  via: W2-M340
- form: list_rows
  id: W2-M342
  via: W2-M342
- form: list_rows
  id: W2-M351
  via: W2-M351
DAEO-w19l:
- form: list_rows
  id: W2-M284
  via: W2-M284
DAEO-yadm:
- form: list_rows
  id: W2-H015
  via: W2-H015
- form: list_rows
  id: W2-H051
  via: W2-H051
- form: list_rows
  id: W2-M082
  via: W2-M082
- form: list_rows
  id: W2-M274
  via: W2-M274
- form: list_rows
  id: W2-M283
  via: W2-M283
```

```diff w2-130:patch-sources-2
diff --git a/.tickets/DAEO-057v.md b/.tickets/DAEO-057v.md
--- a/.tickets/DAEO-057v.md
+++ b/.tickets/DAEO-057v.md
@@ -35,6 +35,14 @@
 profile: STANDARD
 sources:
 - CAP-43
+- W2-H021
+- W2-H032
+- W2-L172
+- W2-L173
+- W2-L174
+- W2-L230
+- W2-M123
+- W2-M279
 est_loc: 140
 acceptance_tests:
   path: tests/acceptance/W2-18/
diff --git a/.tickets/DAEO-4k3l.md b/.tickets/DAEO-4k3l.md
--- a/.tickets/DAEO-4k3l.md
+++ b/.tickets/DAEO-4k3l.md
@@ -67,6 +67,7 @@
 - DEC-982
 - DAEO-t8mp
 - DEC-1099
+- W2-128
 est_loc: 200
 acceptance_tests:
   path: tests/acceptance/W2-82/
diff --git a/.tickets/DAEO-6f0s.md b/.tickets/DAEO-6f0s.md
--- a/.tickets/DAEO-6f0s.md
+++ b/.tickets/DAEO-6f0s.md
@@ -41,7 +41,7 @@
 - 'not W2-60a''s reviewed core (role text, skills, the record''s base fields, no compaction, the refused arguments): W2-60a lands it first'
 - 'not a gate for W2-27 (EXAMIN''s copy): launches during the copy use each role''s `Launch default` line (P1-W2-60a-P5 (B), DEC-1167)'
 done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
-sources: [DEC-1167, DEC-1126, DEC-1120, DEC-1119, DEC-839, DEC-1010]
+sources: [DEC-1167, DEC-1126, DEC-1120, DEC-1119, DEC-839, DEC-1010, CAP-35.c, DEC-1014, DEC-1015, W2-60a]
 acceptance_tests: {path: tests/acceptance/W2-184/}
 ---
 
diff --git a/.tickets/DAEO-6w5n.md b/.tickets/DAEO-6w5n.md
--- a/.tickets/DAEO-6w5n.md
+++ b/.tickets/DAEO-6w5n.md
@@ -33,7 +33,7 @@
 non_goals:
 - the dispatcher core (W2-121, part a) and the other parts
 done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
-sources: [DEC-1007, DEC-1008, DEC-1003, DEC-979, DEC-998, DEC-1009, DEC-1010, DEC-1014, DEC-1015, DEC-1018, DEC-1030, DEC-1031, DEC-1083, DEC-1084, DEC-1088, DEC-715, DEC-944, DEC-952, DEC-982, DEC-983, DEC-989, DEC-995, DAEO-ts4y, DAEO-1ahb]
+sources: [DEC-1007, DEC-1008, DEC-1003, DEC-979, DEC-998, DEC-1009, DEC-1010, DEC-1014, DEC-1015, DEC-1018, DEC-1030, DEC-1031, DEC-1083, DEC-1084, DEC-1088, DEC-715, DEC-944, DEC-952, DEC-982, DEC-983, DEC-989, DEC-995, DAEO-ts4y, DAEO-1ahb, W2-118, W2-21, W2-H046]
 acceptance_tests:
   path: tests/acceptance/W2-121d/
   author: independent-test-designer (MR-3); written before implementation
diff --git a/.tickets/DAEO-aks1.md b/.tickets/DAEO-aks1.md
--- a/.tickets/DAEO-aks1.md
+++ b/.tickets/DAEO-aks1.md
@@ -42,7 +42,7 @@
 non_goals:
 - the code (W2-88), the skill text (W2-88a), the synthetic repositories (W2-88's proof (a)), EXAMIN's copy (W2-27, proof (d))
 done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
-sources: [DEC-1150, DEC-996, DEC-954, DEC-1099, DEC-078, DEC-718, DEC-723]
+sources: [DEC-1150, DEC-996, DEC-954, DEC-1099, DEC-078, DEC-718, DEC-723, CAP-10, CAP-19, DEC-1097, DEC-1098, DEC-833, DEC-860]
 track: A
 ---
 # W2-88b W2-88's proofs on real repositories (a child of W2-88)
diff --git a/.tickets/DAEO-ar89.md b/.tickets/DAEO-ar89.md
--- a/.tickets/DAEO-ar89.md
+++ b/.tickets/DAEO-ar89.md
@@ -35,6 +35,7 @@
 - DEC-1123
 - DEC-105
 - DAEO-t6hf
+- W1-19
 est_loc: 60
 acceptance_tests:
   path: tests/acceptance/W1-19/
diff --git a/.tickets/DAEO-ecac.md b/.tickets/DAEO-ecac.md
--- a/.tickets/DAEO-ecac.md
+++ b/.tickets/DAEO-ecac.md
@@ -62,6 +62,8 @@
 - DEC-963
 - DEC-982
 - DEC-1120
+- DEC-1156
+- W3-P09
 est_loc: 160
 acceptance_tests:
   path: tests/acceptance/W2-60b/
diff --git a/.tickets/DAEO-fau3.md b/.tickets/DAEO-fau3.md
--- a/.tickets/DAEO-fau3.md
+++ b/.tickets/DAEO-fau3.md
@@ -36,6 +36,20 @@
 profile: FULL
 sources:
 - DEC-729
+- W2-H006
+- W2-H007
+- W2-H009
+- W2-H010
+- W2-H011
+- W2-H013
+- W2-H031
+- W2-L216
+- W2-M019
+- W2-M031
+- W2-M047
+- W2-M061
+- W2-M067
+- W2-M173
 est_loc: 180
 acceptance_tests:
   path: tests/acceptance/W2-42/
diff --git a/.tickets/DAEO-h2k3.md b/.tickets/DAEO-h2k3.md
--- a/.tickets/DAEO-h2k3.md
+++ b/.tickets/DAEO-h2k3.md
@@ -62,6 +62,11 @@
 - DEC-1083
 - DEC-1084
 - DEC-866
+- DEC-1097
+- DEC-1122
+- DEC-1123
+- DEC-1124
+- DEC-1171
 est_loc: 0
 acceptance_tests:
   path: tests/acceptance/W2-61h/
diff --git a/.tickets/DAEO-h4rh.md b/.tickets/DAEO-h4rh.md
--- a/.tickets/DAEO-h4rh.md
+++ b/.tickets/DAEO-h4rh.md
@@ -109,6 +109,12 @@
 - DEC-1089
 - DEC-1090
 - DEC-1112
+- DEC-1045
+- DEC-1134
+- DEC-1148
+- DEC-1150
+- DEC-1151
+- DEC-757
 est_loc: 0
 acceptance_tests:
   judged_by: 'its class (WBS §0 rule 1, W2-07): its named evidence files'
diff --git a/.tickets/DAEO-j9z6.md b/.tickets/DAEO-j9z6.md
--- a/.tickets/DAEO-j9z6.md
+++ b/.tickets/DAEO-j9z6.md
@@ -35,7 +35,7 @@
 non_goals:
 - the close itself (W2-115); the trailers switch (W2-115's S17)
 done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
-sources: [DEC-983, DEC-982, DEC-979, DEC-968, DEC-966, DEC-953, DEC-1001, DEC-1002, DEC-1003, DEC-1010, DEC-1014, DEC-1015, DEC-1050, DEC-1083, DEC-959, DEC-988, DEC-989, DEC-1123, DEC-1125, DEC-1052, DEC-1079, CAP-33, DAEO-zkr9]
+sources: [DEC-983, DEC-982, DEC-979, DEC-968, DEC-966, DEC-953, DEC-1001, DEC-1002, DEC-1003, DEC-1010, DEC-1014, DEC-1015, DEC-1050, DEC-1083, DEC-959, DEC-988, DEC-989, DEC-1123, DEC-1125, DEC-1052, DEC-1079, CAP-33, DAEO-zkr9, W2-117]
 acceptance_tests:
   path: tests/acceptance/W2-115b/
   author: independent-test-designer (MR-3); written before implementation
diff --git a/.tickets/DAEO-jip3.md b/.tickets/DAEO-jip3.md
--- a/.tickets/DAEO-jip3.md
+++ b/.tickets/DAEO-jip3.md
@@ -35,6 +35,7 @@
 - DEC-096
 - DEC-1083
 - DAEO-btt7
+- W2-25
 est_loc: 0
 acceptance_tests:
   path: tests/acceptance/W2-47/
diff --git a/.tickets/DAEO-jzvg.md b/.tickets/DAEO-jzvg.md
--- a/.tickets/DAEO-jzvg.md
+++ b/.tickets/DAEO-jzvg.md
@@ -48,6 +48,13 @@
 - DEC-762
 - DEC-1083
 - DEC-890
+- W2-H026
+- W2-H042
+- W2-L119
+- W2-M159
+- W2-M160
+- W2-M162
+- W2-M253
 est_loc: 300
 acceptance_tests:
   path: tests/acceptance/W2-19/
diff --git a/.tickets/DAEO-m4rq.md b/.tickets/DAEO-m4rq.md
--- a/.tickets/DAEO-m4rq.md
+++ b/.tickets/DAEO-m4rq.md
@@ -44,6 +44,7 @@
 - DEC-1078
 - DEC-1079
 - DAEO-h2k3
+- W2-61h
 est_loc: 60
 acceptance_tests:
   path: tests/acceptance/W2-134/
diff --git a/.tickets/DAEO-nn1s.md b/.tickets/DAEO-nn1s.md
--- a/.tickets/DAEO-nn1s.md
+++ b/.tickets/DAEO-nn1s.md
@@ -111,6 +111,7 @@
 - DEC-1083
 - DEC-1084
 - DAEO-0mab
+- W2-24
 est_loc: 0
 acceptance_tests:
   judged_by: 'its class (WBS §0 rule 1, W2-07): its named evidence files'
diff --git a/.tickets/DAEO-q8cl.md b/.tickets/DAEO-q8cl.md
--- a/.tickets/DAEO-q8cl.md
+++ b/.tickets/DAEO-q8cl.md
@@ -51,6 +51,7 @@
 - DEC-1010
 - DEC-1098
 - DEC-1088
+- DEC-1123
 est_loc: 0
 acceptance_tests:
   path: tests/acceptance/W2-130/
diff --git a/.tickets/DAEO-rd0g.md b/.tickets/DAEO-rd0g.md
--- a/.tickets/DAEO-rd0g.md
+++ b/.tickets/DAEO-rd0g.md
@@ -46,6 +46,14 @@
 - DEC-1072
 - DEC-1083
 - DAEO-swdu
+- DEC-1171
+- W2-15b
+- W2-L102
+- W2-L321
+- W2-L322
+- W2-L329
+- W2-M340
+- W2-M342
 est_loc: 100
 acceptance_tests:
   judged_by: 'its class (WBS §0 rule 1, W2-07): its evidence record'
diff --git a/.tickets/DAEO-rmhj.md b/.tickets/DAEO-rmhj.md
--- a/.tickets/DAEO-rmhj.md
+++ b/.tickets/DAEO-rmhj.md
@@ -44,6 +44,7 @@
 - DEC-1090
 - DEC-1087
 - DEC-1072
+- DEC-1122
 est_loc: 150
 acceptance_tests:
   path: tests/acceptance/W2-138/
diff --git a/.tickets/DAEO-sdhj.md b/.tickets/DAEO-sdhj.md
--- a/.tickets/DAEO-sdhj.md
+++ b/.tickets/DAEO-sdhj.md
@@ -33,6 +33,7 @@
 profile: FULL
 sources:
 - CAP-45.a
+- W2-M176
 est_loc: 260
 acceptance_tests:
   path: tests/acceptance/W2-17/
diff --git a/.tickets/DAEO-sdxk.md b/.tickets/DAEO-sdxk.md
--- a/.tickets/DAEO-sdxk.md
+++ b/.tickets/DAEO-sdxk.md
@@ -51,6 +51,9 @@
 - DEC-1073
 - DEC-953
 - DEC-968
+- DEC-1121
+- DEC-1123
+- DEC-1130
 est_loc: 0
 acceptance_tests:
   judged_by: 'its class (WBS §0 rule 1, W2-07): its named evidence files (the exit report)'
diff --git a/.tickets/DAEO-sq3a.md b/.tickets/DAEO-sq3a.md
--- a/.tickets/DAEO-sq3a.md
+++ b/.tickets/DAEO-sq3a.md
@@ -40,7 +40,7 @@
 - 'not semantic search inside the sandbox (a proxy-aware Ollama client and its port: parked, DEC-1168 (1))'
 - 'not a gate for EXAMIN''s copy: built after W2-27 starts (DEC-1168 (1))'
 done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
-sources: [DEC-1168, DEC-1167, DEC-158, DEC-1114, DEC-1128]
+sources: [DEC-1168, DEC-1167, DEC-158, DEC-1114, DEC-1128, W2-56]
 acceptance_tests: {path: tests/acceptance/W2-186/}
 ---
 
diff --git a/.tickets/DAEO-swdu.md b/.tickets/DAEO-swdu.md
--- a/.tickets/DAEO-swdu.md
+++ b/.tickets/DAEO-swdu.md
@@ -57,6 +57,19 @@
 - DEC-1083
 - DAEO-rd0g
 - DAEO-iw1f
+- DEC-798
+- W2-15a
+- W2-61
+- W2-L102
+- W2-L317
+- W2-L320
+- W2-L321
+- W2-L322
+- W2-M017
+- W2-M089
+- W2-M340
+- W2-M342
+- W2-M351
 est_loc: 60
 acceptance_tests:
   judged_by: 'its class (WBS §0 rule 1, W2-07): its evidence record'
diff --git a/.tickets/DAEO-w19l.md b/.tickets/DAEO-w19l.md
--- a/.tickets/DAEO-w19l.md
+++ b/.tickets/DAEO-w19l.md
@@ -29,6 +29,7 @@
 sources:
 - CAP-32.d
 - DEC-166
+- W2-M284
 est_loc: 160
 acceptance_tests:
   path: tests/acceptance/W2-36/
diff --git a/.tickets/DAEO-yadm.md b/.tickets/DAEO-yadm.md
--- a/.tickets/DAEO-yadm.md
+++ b/.tickets/DAEO-yadm.md
@@ -35,6 +35,11 @@
 sources:
 - CAP-30.c
 - MR-2
+- W2-H015
+- W2-H051
+- W2-M082
+- W2-M274
+- W2-M283
 est_loc: 180
 acceptance_tests:
   path: tests/acceptance/W2-34/
diff --git a/.tickets/DAEO-zmo4.md b/.tickets/DAEO-zmo4.md
--- a/.tickets/DAEO-zmo4.md
+++ b/.tickets/DAEO-zmo4.md
@@ -60,7 +60,7 @@
 - no change to the ticket template or schema; the marker is one extra front-matter line the schema already allows
 - no change to W2-88's refactoring-plan text (the CTO's one-line note, below)
 done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
-sources: [DEC-1130, DEC-1083, DEC-1052, DEC-1050, DEC-1088, DEC-1121, DEC-1122, DEC-1112, DAEO-o5x1, DAEO-t8mp, DAEO-2bdu, DAEO-kmcr, DAEO-h4rh]
+sources: [DEC-1130, DEC-1083, DEC-1052, DEC-1050, DEC-1088, DEC-1121, DEC-1122, DEC-1112, DAEO-o5x1, DAEO-t8mp, DAEO-2bdu, DAEO-kmcr, DAEO-h4rh, DEC-1147, DEC-1148]
 acceptance_tests: {path: tests/acceptance/W2-174/}
 ---
 
```

**Closed tickets** are not edited (DEC-1088 (6), H1 (b)). Their missing ids, per ticket, from `gov links --all`'s
UNLINKED_ID at the last clean-up commit (142 tickets):

```yaml w2-130:closed-missing
DAEO-03dg:
- DEC-780
- DEC-862
- DEC-889
- DEC-906
- DEC-922
DAEO-03pw:
- CAP-59.a
- CAP-59.b
DAEO-0i6h:
- CAP-24.a
- CAP-24.b
- CAP-24.c
- CAP-28.a
- CAP-30.b
- CAP-30.f
- CAP-32.c
- CAP-33.a
- CAP-33.d
- CAP-33.e
- CAP-33.f
- CAP-34.c
- CAP-38.b
- CAP-38.e
- CAP-47.d
DAEO-0pyc:
- DEC-105
- DEC-1126
- DEC-1169
- W2-L065
- W2-M073
- W2-M103
- W2-M104
- W2-M191
DAEO-0qs5:
- CAP-25.d
- CAP-61.e
DAEO-0rfi:
- DEC-1033
- DEC-1042
- DEC-773
- DEC-866
- W2-30
- W2-32
- W2-34
- W2-40
DAEO-0uhh:
- DEC-954
DAEO-0z8c:
- DEC-1074
- DEC-1109
- DEC-1125
- W2-L160
- W2-M105
- W2-M113
- W2-M161
DAEO-1ahb:
- W2-H001
- W2-H012
- W2-H046
- W2-L105
- W2-M094
- W2-M095
- W2-M097
- W2-M152
- W2-M181
- W2-M187
- W2-M245
- W2-M247
- W2-M275
- W2-M291
- W2-M405
DAEO-1vka:
- DEC-1010
- W2-112
DAEO-2bdu:
- DEC-1132
- W2-124
- W2-26
DAEO-2ds6:
- W2-I041
DAEO-2gc7:
- DEC-906
DAEO-2lwj:
- CAP-07.a
- CAP-13.a
- CAP-20.a
- CAP-24.a
- CAP-31.b
- CAP-38.a
- CAP-38.b
- CAP-38.c
- CAP-38.d
- CAP-38.f
- CAP-46.a
- CAP-50.c
- CAP-59.a
- CAP-59.b
- CAP-59.c
DAEO-32n6:
- CAP-37.g
DAEO-3ef2:
- CAP-38.b
- CAP-52.a
- CAP-52.b
DAEO-49o5:
- DEC-767
- DEC-772
- W2-H029
- W2-L002
- W2-L014
- W2-L227
- W2-M174
- W2-M175
DAEO-4eux:
- DEC-986
DAEO-4yyl:
- CAP-08.a
- CAP-09.a
- CAP-09.b
- CAP-13.a
DAEO-57hm:
- DEC-970
- W2-H064
DAEO-5j8b:
- DEC-826
DAEO-5x4l:
- CAP-04.c
- CAP-14.a
- CAP-16.a
- CAP-16.b
- CAP-16.c
- CAP-18.a
- CAP-18.b
- CAP-38.b
- CAP-51.b
- CAP-55.a
DAEO-5ylr:
- CAP-02.a
- CAP-43.a
- CAP-44.a
DAEO-6cc2:
- CAP-58.e
DAEO-6mk8:
- CAP-04.b
- CAP-40.a
- CAP-40.c
- CAP-40.d
- CAP-53.c
DAEO-6n5k:
- DEC-1157
- DEC-1163
- W2-L319
- W2-M285
DAEO-6ox0:
- W2-H052
- W2-L316
- W2-L328
- W2-M334
- W2-M335
- W2-M336
- W2-M337
- W2-M338
- W2-M344
- W2-M347
- W2-M350
DAEO-6y0x:
- DEC-1143
- DEC-1144
DAEO-78bn:
- CAP-25.a
- CAP-25.b
DAEO-7nne:
- CAP-03.a
- CAP-03.b
- CAP-03.e
- CAP-38.b
- CAP-52.a
DAEO-7r5e:
- DEC-1014
- DEC-803
- W2-H020
- W2-L017
- W2-L106
- W2-L335
- W2-M013
- W2-M142
DAEO-7rr2:
- W2-H047
- W2-M202
DAEO-7y6v:
- W2-H053
- W2-L018
- W2-L324
- W2-L341
DAEO-8goq:
- CAP-27.a
- CAP-28.a
DAEO-8lmb:
- MR-3
DAEO-8nue:
- CAP-17.c
- CAP-55.a
- CAP-57.a
DAEO-8qvp:
- CAP-58.a
DAEO-8s85:
- DEC-1116
- DEC-1122
- DEC-1156
- DEC-315
- DEC-957
DAEO-9279:
- CAP-05.a
- CAP-05.b
- CAP-05.c
- CAP-05.d
- DEC-386
DAEO-9i8e:
- CAP-15.f
DAEO-9nys:
- DEC-914
- DEC-954
- DEC-970
DAEO-a3m2:
- W2-I015
- W2-M016
- W2-M236
DAEO-av72:
- DEC-849
- DEC-899
- DEC-906
DAEO-b6hm:
- DEC-866
- W2-68
- W2-M406
DAEO-be7u:
- CAP-01.b
- CAP-21.a
- CAP-34.d
- CAP-51.a
- DEC-360
- DEC-387
- DEC-418
DAEO-c1uz:
- DEC-868
- DEC-904
DAEO-cb2b:
- W2-118
DAEO-cdoi:
- CAP-06.b
- CAP-06.c
- CAP-06.d
- CAP-15.c
- CAP-42.a
- CAP-42.b
- CAP-42.c
- CAP-44.b
- CAP-44.c
- CAP-44.d
- CAP-44.e
- CAP-44.j
DAEO-clon:
- DEC-1122
DAEO-cuao:
- W2-M049
- W2-M280
DAEO-cv58:
- DEC-105
- DEC-1156
- DEC-1157
- DEC-1167
- DEC-233
- DEC-313
- DEC-951
- DEC-954
- DEC-957
- W2-184
DAEO-cy5o:
- DEC-766
- DEC-886
- DEC-899
- DEC-925
DAEO-drvn:
- CAP-27.a
- CAP-28.b
- DEC-185
- DEC-186
- DEC-187
DAEO-dy7j:
- CAP-24.c
- CAP-50.a
- DEC-239
- DEC-968
- DEC-982
DAEO-e82f:
- W2-59
DAEO-ebmh:
- W2-L429
DAEO-egm9:
- CAP-34.a
- CAP-34.b
- CAP-34.c
- CAP-34.d
DAEO-egsy:
- DEC-729
- DEC-730
DAEO-emkd:
- CAP-38.c
- CAP-39.a
- CAP-58.a
- CAP-58.c
DAEO-f58b:
- DEC-1157
- W2-06
- W2-M088
DAEO-fdkq:
- CAP-39.a
DAEO-fygv:
- CAP-01.c
- CAP-24.c
- CAP-30.b
- CAP-30.e
- CAP-38.b
- CAP-39.d
- CAP-58.a
- DEC-438
- DEC-439
- DEC-441
DAEO-g0ip:
- W2-H047
- W2-L111
- W2-L235
- W2-M147
- W2-M165
- W2-M202
- W2-M209
- W2-M238
- W2-M250
- W2-M251
- W2-M266
DAEO-g23i:
- DEC-968
- DEC-982
- W2-H043
- W2-M163
- W2-M240
- W2-M241
DAEO-g29a:
- DEC-1156
- DEC-995
- DEC-996
- W2-33
DAEO-gdzh:
- DEC-889
DAEO-gjjf:
- CAP-23.c
- CAP-28.b
- CAP-38.b
- CAP-40.c
DAEO-ha8z:
- CAP-45.a
- DEC-614
- DEC-750
DAEO-i89t:
- DEC-1156
- W2-L097
DAEO-ifgf:
- DEC-1149
DAEO-ipqy:
- CAP-25.a
DAEO-iw1f:
- DEC-954
DAEO-j8gn:
- DEC-968
- DEC-982
- W2-H037
- W2-H048
- W2-H049
- W2-L010
- W2-M107
- W2-M108
- W2-M227
- W2-M257
- W2-M258
DAEO-jdqr:
- CAP-22.d
- CAP-25.e
- CAP-27
- CAP-28
- CAP-49.b
- CAP-58.d
- CAP-61.a
- CAP-61.b
- CAP-61.c
- CAP-61.d
DAEO-jfm3:
- W2-04
DAEO-jozo:
- CAP-57.a
DAEO-jpr0:
- W2-123
DAEO-juee:
- W2-M372
- W2-M373
DAEO-k7hz:
- CAP-24
- CAP-37
- CAP-38
- DEC-103
- DEC-371
- DEC-534
- DEC-536
- DEC-537
- DEC-539
- DEC-541
- DEC-729
- DEC-732
- DEC-791
- DEC-801
- DEC-802
- DEC-808
- DEC-832
- DEC-837
- DEC-838
- DEC-862
- DEC-963
- DEC-968
- DEC-981
- DEC-992
- W2-L256
- W2-L268
DAEO-kh9l:
- CAP-33
- DEC-864
- DEC-877
DAEO-kia7:
- W2-H039
- W2-H040
- W2-H041
- W2-M011
- W2-M088
- W2-M143
- W2-M210
- W2-M243
- W2-M282
- W2-M293
- W2-M295
DAEO-kiar:
- DEC-967
- DEC-970
- DEC-975
- DEC-978
DAEO-kl5e:
- W2-M355
DAEO-kmcr:
- W2-H035
- W2-H036
- W2-H050
- W2-M216
- W2-M217
- W2-M218
- W2-M219
- W2-M220
- W2-M224
- W2-M225
- W2-M229
- W2-M232
- W2-M307
- W2-M312
DAEO-ktiw:
- DEC-1065
DAEO-l4gf:
- MR-3
- W2-13
DAEO-l78m:
- CAP-10
- CAP-44.c
- CAP-44.d
- CAP-44.f
- DEC-802
- DEC-860
- DEC-968
- DEC-993
DAEO-lc4q:
- CAP-30.a
- CAP-30.e
DAEO-lkeb:
- CAP-03.e
- CAP-12.a
- CAP-12.b
DAEO-lrre:
- DEC-1087
- DEC-1156
- DEC-971
- W2-113
- W2-153
DAEO-m7u4:
- CAP-22.a
DAEO-mb2t:
- W2-26
- W2-88
DAEO-n0wb:
- DEC-1112
- DEC-1125
DAEO-neam:
- W2-H018
- W2-M129
- W2-M130
- W2-M151
- W2-M211
- W2-M212
- W2-M259
- W2-M265
DAEO-nqa2:
- DEC-1065
- W2-106
DAEO-o4fg:
- CAP-25.f
- CAP-25.g
- CAP-49.c
- CAP-58.f
- CAP-62.a
DAEO-o5x1:
- DEC-1052
DAEO-p3ln:
- DEC-1157
DAEO-pg6i:
- DEC-1071
- DEC-1072
- DEC-1074
- DEC-1083
- DEC-1099
- DEC-1116
DAEO-qty6:
- W2-72
- W2-L441
DAEO-qzca:
- W2-129
DAEO-r30l:
- DEC-1105
- DEC-1122
- W2-M188
- W2-M244
- W2-M262
DAEO-r9ss:
- DEC-663
- DEC-906
- DEC-923
- DEC-924
- W2-H038
- W2-H045
- W2-L209
- W2-L236
- W2-M158
- W2-M166
- W2-M249
- W2-M252
- W2-M286
- W2-M371
DAEO-rmbe:
- W2-L373
- W2-M404
DAEO-rrxp:
- CAP-13.b
- CAP-20.a
- CAP-37.a
- CAP-37.b
- CAP-37.c
- CAP-37.f
- CAP-38.b
DAEO-rxln:
- CAP-03.d
- CAP-11.a
- CAP-17.a
- CAP-18.b
- CAP-38.b
DAEO-s694:
- W2-H022
- W2-H023
- W2-H024
- W2-H025
- W2-H033
- W2-M015
- W2-M115
- W2-M164
- W2-M203
- W2-M204
- W2-M254
- W2-M255
- W2-M256
DAEO-siiz:
- DEC-1033
- DEC-1065
DAEO-skiy:
- CAP-16.b
- CAP-24.b
- CAP-38.b
- CAP-47.b
- CAP-47.d
- CAP-56.a
- DEC-425
- DEC-439
- DEC-441
DAEO-t6hf:
- CAP-10.a
- CAP-18.a
- DEC-1039
- DEC-1046
DAEO-t8mp:
- DEC-1116
- DEC-1121
- W2-11b
DAEO-tgk2:
- DEC-956
- DEC-964
- W2-L451
- W2-M408
DAEO-topz:
- CAP-23.a
- CAP-31.c
- CAP-31.d
- CAP-34.e
DAEO-ts4y:
- DEC-1003
- DEC-1009
- DEC-1014
DAEO-u4oz:
- W2-H034
- W2-M126
- W2-M215
- W2-M239
- W2-M294
- W2-M330
DAEO-u5g6:
- W2-H002
- W2-H008
- W2-H014
- W2-H027
- W2-H028
- W2-M003
- W2-M018
- W2-M271
DAEO-uudf:
- CAP-03.a
- CAP-03.b
- CAP-03.c
- CAP-06.a
- CAP-06.e
- CAP-07.b
- CAP-31.a
- CAP-41.a
- CAP-41.c
- CAP-41.f
- CAP-50.a
- CAP-53.a
- CAP-54.b
DAEO-uzme:
- DEC-750
- DEC-754
- DEC-900
DAEO-v4is:
- DEC-866
DAEO-w616:
- CAP-30.a
- CAP-30.b
- CAP-47.d
- CAP-53.a
DAEO-w9l3:
- CAP-31.a
DAEO-wi46:
- DEC-1156
DAEO-wk2v:
- CAP-01.a
- CAP-01.d
- CAP-15.a
- CAP-15.b
- CAP-15.c
- CAP-15.d
- CAP-15.e
- CAP-15.g
- CAP-38.b
- DEC-425
DAEO-wnnz:
- DEC-1122
- W2-112
- W2-127
- W2-145
- W2-21
- W2-I012
- W2-L105
- W2-M094
- W2-M095
- W2-M097
- W2-M181
- W2-M187
- W2-M275
- W2-M393
- W2-M405
- W3-P28
DAEO-wq2b:
- DEC-962
- DEC-968
- DEC-979
- DEC-982
- DEC-985
DAEO-wqd6:
- CAP-41.b
- CAP-41.d
- CAP-59.c
DAEO-xafn:
- DEC-1107
- DEC-1122
DAEO-xm6l:
- W2-L101
- W2-L206
- W2-L215
- W2-L336
- W2-M139
- W2-M201
- W2-M264
- W2-M287
- W2-M288
- W2-M289
- W2-M290
DAEO-xnbx:
- CAP-58.h
- DEC-378
- DEC-402
- DEC-404
- DEC-407
- DEC-409
- DEC-421
DAEO-xog0:
- CAP-22.a
- CAP-58.b
DAEO-xw3k:
- CAP-02.a
- CAP-06.a
- CAP-06.d
- CAP-07.a
- CAP-20.a
- CAP-25.a
- CAP-38.b
- CAP-46.a
- CAP-54.a
- DEC-416
- DEC-425
DAEO-xwro:
- DEC-1097
DAEO-xxgp:
- W2-H044
- W2-M153
DAEO-ye2a:
- DEC-866
DAEO-ym8a:
- W2-L069
- W2-L221
- W2-M106
- W2-M145
- W2-M267
DAEO-yvzh:
- DEC-244
- DEC-245
- DEC-246
- DEC-247
DAEO-zflj:
- W2-L177
- W2-L243
- W2-M138
- W2-M260
- W2-M301
- W2-M309
- W2-M310
- W2-M316
- W2-M317
DAEO-zkr9:
- DEC-1001
- DEC-1003
- DEC-1010
- DEC-1014
- DEC-1015
- DEC-989
DAEO-zndm:
- W2-H019
- W2-L078
- W2-L135
- W2-M037
- W2-M038
- W2-M156
- W2-M222
DAEO-zoex:
- DEC-385
- DEC-977
DAEO-zqvn:
- DEC-1112
- W2-L233
- W2-M071
- W2-M072
- W2-M100
- W2-M102
- W2-M292
- W2-M296
DAEO-zsvl:
- CAP-15.g
- CAP-37.b
- CAP-37.c
- CAP-37.d
- DEC-413
```

**Ids that name no record**, per ticket, for D-9: none. Every UNKNOWN_ID on a ticket at the last clean-up commit is
an `acceptance_tests.path` that does not exist yet (36, listed by path under `left`, D-9).

```yaml w2-130:no-record
{}
```

## 6. Commit trailers (S5)

History is not rewritten: the starting head 232efc47d is an ancestor of HEAD. Every `Task:` and `Implements:` value
in the history at 232efc47d that names no record is listed once below (`Task: decision-record` is valid under
DEC-861 and not listed), with its commits, its ticket and what it should have named, as DEC-927 listed its 39. The
recount script gives the same set. The `Implements:` values `engineer` and `independent-test-designer` are in commits
the path map's `accepted_history` accepted (read at c5e9d962^); their `should_have_named` is the ids it named.

```yaml w2-130:trailer-residuals
head: 232efc47dd707dd76038cf8211842d9b4472473c
command: python3 - 232efc47d < (the w2-130:recount block), cwd the repository
values:
- trailer: Implements
  value: AR-9
  commits:
  - d5d7fac9cb90cfc80a06085a0e11ea7c502f9f74
  - 340fef31e3adc9e3e4f4cc06d2ae02df109771e1
  - 1eae249cba33d4ca300c56e05cdad0fc70e75d83
  - b252fd7d0e55fa178b3bb9a5f55e95ada60fcb00
  - b2520a0c3b2b2a9183f15f761cbd38676265ddda
  - 9fbaf96958abfc9cd6bc4e0597236926e9074bbe
  tickets:
  - DAEO-2d6f
  - DAEO-2upp
  - DAEO-cv6c
  - DAEO-pr0y
  - DAEO-s1wp
  - DAEO-sg6x
  should_have_named:
  - DEC-900
  - DEC-718
  unresolved:
  - AR-9
- trailer: Implements
  value: CAP-58, CAP-03 (capability level; no covers item names W1-01)
  commits:
  - 57631ec9462aeb69e07f723bbc21802a3eb68c15
  tickets:
  - DAEO-dtv3
  should_have_named:
  - CAP-58
  - CAP-03
  unresolved:
  - (capability
  - level;
  - 'no'
  - covers
  - item
  - names
  - W1-01)
- trailer: Implements
  value: DEC-084, DEC-119 (no covers item names W1-05)
  commits:
  - 442e9c3c10d1aab77fd5c12600d6acc064ef1713
  tickets:
  - DAEO-m7u4
  should_have_named:
  - DEC-084
  - DEC-119
  unresolved:
  - (no
  - covers
  - item
  - names
  - W1-05)
- trailer: Implements
  value: engineer
  commits:
  - d0bfeb6afd9523b4ee6a4e6e2da5333f54b283bf
  - 6be837bbbe4158768ca88ae47972308386e008cf
  - 20d72c1936118e06b86b5eef16c3157e83e6aa94
  - 04878e23252ad3b32c6308ed2ced6db72a062ab6
  - 9e2b97758e2474d8c4b61a3ec54aad724c786965
  - 33401f46ad00189bbab9584138888f44f543c57e
  - 34e1c59f06e6a158bfd0cf0e00c2d83633d69647
  - 5634d4305a7c4f9b677bed6a6cea26ea53c96c94
  - e00fd14a26be19069aeb904418d2dfa7ac868dcb
  - 6f2ec438a6fa9b28b703609ff2c96f7855158c5a
  - 9174e358d77bbb0829a3c6ea9694026018686e9b
  - 2f03393d848672981c0071ecaa18e08cb3a78977
  - 09c327d2172662a166fa10dd593b8c74eabdca74
  - 915a764dd660d1ff2d08944042dd05c6fc02a6a4
  - 80ec31ab61b844888ddc05470aa12ce3d768e908
  - cfea8a26e668c49f60f1fa936b6295d661f47dc5
  - f1c743b3ee92b95b31a5c29cde2e756c9ace969b
  - 614817ec7d6c7a3a9fcf55849c40f414006905b2
  - 8663196dd9445d990f68faaaa34729ec520889e9
  - d2eee219625e620b75b118c109c3778a2aa21a37
  - 60f71c4298bc38cb01bc37a2e6cd0406de8fdaa4
  - 3fd2b5a1e664d7c987a2c9a3ffaafd99f4c60a01
  - 8e9ce18db1c52f1861ce5e579ca4298d0833ea13
  - 527345b7bf43b8f05d9ccb16e39d0c79c0a02563
  - dc05ffe45ee2fccb9f8bf90ec4df6f9e4c033e54
  - 9d22d9807a440c02ee0a20d4dbf249837183bae3
  - 0808dbb6e8ffb9dab21e991689adea990323f8a6
  - 6b1d54fe6cc03ce8899912726799457157a17e01
  - ba38ab8d758b3ab9147c951f30aaafbe9b80eaeb
  - 44062fecf53bdcda83cb3c4bfc668945be5c8709
  - e8ad70b51c91b274dfdbb29e57bd15ccdcd9c08c
  - e4687ef4cf5631d91b8672d6e139a9a244b6e68f
  - 6ebc7cf7f74c1c0bbd03a763a7e1d84f7a88fc21
  - 1475b46c9186bf2201023a4ba658b2ee3f3449a6
  tickets:
  - DAEO-9nys
  - DAEO-c1uz
  - DAEO-cy5o
  - DAEO-e82f
  - DAEO-r9ss
  - DAEO-rmbe
  should_have_named: 'accepted as history, should_implement: DEC-290, DEC-726, DEC-729, DEC-738, DEC-784, DEC-790, DEC-813, DEC-822, DEC-823, DEC-835, DEC-841, DEC-852, DEC-853, DEC-868, DEC-871, DEC-880, DEC-881, DEC-883, DEC-884, DEC-889, DEC-890, DEC-891, DEC-892, DEC-896, DEC-897, DEC-898, DEC-899, DEC-903, DEC-904, DEC-905, DEC-907, DEC-908, DEC-909, DEC-912, DEC-913, DEC-917'
  unresolved:
  - engineer
- trailer: Implements
  value: independent-test-designer
  commits:
  - e052b7b5a8539c1cd9fbd734164e9d28b28d4c1f
  - 39574e4ee5151dedc5742a89dea75a5a37c37c31
  - e04e6ee6effecd971eb7b3021762fd4a8d40769a
  - 5baafb04661140673a70e246b61d4ab2a064e0b7
  - 8b318157db948890ede906618e6b31732e915ea6
  - 78522dea7ce462aca566a7db23565a5c0dc248d9
  - f409ad97575a32f6aab96e6ee6bcb4b7bc008691
  tickets:
  - DAEO-uzme
  should_have_named: 'accepted as history, should_implement: DEC-889, DEC-892, DEC-899, DEC-906, DEC-908, DEC-912'
  unresolved:
  - independent-test-designer
- trailer: Task
  value: W1-01
  commits:
  - 71100b56c030e4cd4b3fe033eb3fad0f5b1dc996
  - b4d7ede4104e8115fa2aa889569a34638bb3a10b
  tickets:
  - DAEO-dtv3
  should_have_named:
  - DAEO-dtv3
  unresolved:
  - W1-01
- trailer: Task
  value: W1-02
  commits:
  - a4e66919e0d6250f436570327c03a44378ac34b0
  - 43fdf41a8dde59c743fc360bc055e2632e9e3d6d
  - 5d65ba79e4c8cfe985cd793424a3d3e9b03b9d75
  tickets:
  - DAEO-emkd
  should_have_named:
  - DAEO-emkd
  unresolved:
  - W1-02
- trailer: Task
  value: W1-03
  commits:
  - 95df6c5032cb8f6c50f5bc13cd45bb1c75d29929
  - e10a3b3cceda184b3823021d024dc62d7bef472c
  - e31e11d4b8ce4ea47328059a9f671ec57ea689aa
  - 5aeb62a82e346ccb58a7325b361a48089cc3c0cb
  - a389ebcf2e7e442da69fa19d3c9043a53c5af9db
  tickets:
  - DAEO-8qvp
  should_have_named:
  - DAEO-8qvp
  unresolved:
  - W1-03
- trailer: Task
  value: W1-04
  commits:
  - 17ef3ae54988515682a497b716b87690882fac49
  - aa649af53606ea1af632f3d2ce114108ea4d5351
  tickets:
  - DAEO-78bn
  should_have_named:
  - DAEO-78bn
  unresolved:
  - W1-04
- trailer: Task
  value: W1-05
  commits:
  - 2b2944ac6079420caf329f19aca9a3ea97c9e141
  - 2cdabc99d9b5f49a43e2a6173f34bdffe8f866a6
  - 7b7d01bf40cd9eccb5965b72b71499694764b561
  tickets:
  - DAEO-m7u4
  should_have_named:
  - DAEO-m7u4
  unresolved:
  - W1-05
- trailer: Task
  value: owner-prompt
  commits:
  - 27ec34826ae5b80a883353677e7812702b69f696
  - 6c4ba2f45d3b7b6bbd2b1d1363d5116421a39994
  - 3ccbf75c869910b8198715b8fa980b9635f5f28e
  - e4dc57ce188a6c856b1bdf93db451cfb3baf1e48
  - 9ea35972573dd6d8e77977a4280dac260459244f
  - d07445dfd1ab836696ae0ba7b28ad7a6eb0a2153
  - 66e09aa1946d15f9e30adad7dc0b5300b79fb9a2
  - d73420b1bc7e0a05913bee14fd0864819c9aaaaa
  - 85e012dbaf6834e12032388962f79ebc6660ecb9
  tickets:
  - null
  should_have_named: decision-record if the commit records an owner decision, else W1-45 (DAEO-6cc2), the Wave 1 coordination ticket
  unresolved:
  - owner-prompt
- trailer: Task
  value: spec-change-S2
  commits:
  - 0186bc4986dad602c9a075806c6c4371ad6702ac
  - 2fcea1ea1432a212faadca8e854593552797e38b
  tickets:
  - null
  should_have_named: W1-45 (DAEO-6cc2), the Wave 1 coordination ticket
  unresolved:
  - spec-change-S2
- trailer: Task
  value: wave-coordination
  commits:
  - 7c6bf8040ff1788555f9c74b5bacec56d2d332b9
  tickets:
  - null
  should_have_named: W1-45 (DAEO-6cc2), the Wave 1 coordination ticket
  unresolved:
  - wave-coordination
```

```python w2-130:recount
"""W2-130 S5: every Task: and Implements: trailer value in `git log <rev>`'s history that names no record.

Run from the repository's root as `python3 - <rev>` (this script on stdin); standard library and git only; reads
git, writes nothing. A value is read from git's own trailer block (`%(trailers:key=Task,key=Implements,unfold)`),
split on commas and white space. `Task:` names no record when a token is neither `decision-record` (valid under
DEC-861) nor a ticket file `.tickets/<token>.md` at <rev>; `Implements:` names no record when a token is none of: a
register entry (`### DEC-n` in docs/DECISION_REGISTER.md at <rev>), a ticket id, a W2 id (a ticket's `wbs_id` or
`external-ref`), or a capability or master-rule id of docs/contract/contract.yaml at <rev>.
Prints one JSON list of {"trailer", "value", "tokens", "commits"} ((trailer, value) once; tokens: the unresolved
elements; commits: every commit carrying it, newest first).
"""
import json
import re
import subprocess
import sys
from pathlib import Path


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", errors="replace",
                          check=False).stdout


rev = git("rev-parse", "--verify", sys.argv[1] + "^{commit}").strip()
log = git("log", "--format=%x1e%H%x1f%(trailers:key=Task,key=Implements,unfold)", rev)
tickets = {Path(name).stem for name in git("ls-tree", "--name-only", rev, ".tickets/").split()}
aliases = set(re.findall(r"(?m)^(?:wbs_id|external-ref): *(\S+)",
                         git("grep", "-h", "-E", "^(wbs_id|external-ref):", rev, "--", ".tickets")))
register = set(re.findall(r"(?m)^### (DEC-\d+)\b", git("show", f"{rev}:docs/DECISION_REGISTER.md")))
contract = git("show", f"{rev}:docs/contract/contract.yaml")
capabilities = set(re.findall(r"\b(?:CAP-\d+(?:\.[a-z])?|MR-\d+)\b", contract))
known = register | tickets | aliases | capabilities
found = {}
for item in log.split("\x1e")[1:]:
    sha, block = item.split("\x1f", 1)
    for line in block.splitlines():
        key, _, value = line.partition(":")
        key, value = key.strip(), value.strip()
        tokens = [t for t in re.split(r"[,\s]+", value) if t]
        if key == "Task":
            bad = [t for t in tokens if t != "decision-record" and t not in tickets]
        elif key == "Implements":
            bad = [t for t in tokens if t not in known]
        else:
            continue
        if bad:
            entry = found.setdefault((key, value), {"trailer": key, "value": value, "tokens": bad, "commits": []})
            if sha not in entry["commits"]:
                entry["commits"].append(sha)
print(json.dumps([found[k] for k in sorted(found)]))
```

## 7. The status reconciliation (S6, F2)

- **The list:** `governance/project/orchestration/packages/W2-130-SITTING.md` (committed in 2f9c80b1f, an ancestor
  of the starting head): the 110 decisions ARCHIVE-SUPERSEDED §B called spent while the register listed them
  current, the 40 PROPOSED entries, and the STATUS_CONFLICT findings (116 at 232efc47d), each with the CTO's
  proposal and its reason.
- **The ruling:** DEC-1098 (3), committed in 9546edd61: groups A to G accepted as proposed; H1 (b); H2 as
  recommended.
- **Applied:** c4420040f writes each decided status (the new word first, the old status text kept); the archive and
  DECISIONS-IN-FORCE agree; the R-12 follow-up (8d245901b) rewords the one line that read as listing the done
  DEC-896 in force.
- **After:** STATUS_CONFLICT 0.
- LINK-RECONCILIATION.md (`governance/project/orchestration/packages/LIFT-1/`) carries the sitting's 150 rows with
  their proposals, reasons and rulings.

## 8. Lessons (S7)

Each lesson's `sources:` names the decision or owner record its own **Source:** line names (8f8d707f0).

| lesson | sources |
|---|---|
| L-0074 | DEC-041, DEC-046 |
| L-0075 | OWNER-DECISION-P2-0008 |
| L-0076 | OWNER-DIRECTION-BR-0004 |
| L-0077 | OWNER-AMENDMENT-P2-0010 |
| L-0078 | DEC-044, DEC-046, OWNER-AMENDMENT-P2-0010 |

```yaml w2-130:lessons
L-0074:
  sources:
  - DEC-041
  - DEC-046
  came_from: 'DEC-041 (DECISION_REGISTER.md) — "L-0074: a universal negative implemented as a positive enumeration fails silently as soon as the product grows a path the author did not list, and tests derived from the same list cannot notice." Carried as a principle by DEC-046.'
  agree: true
L-0075:
  sources:
  - OWNER-DECISION-P2-0008
  came_from: OWNER-DECISION-P2-0008 (OD-P2-08) §9, "Anti-stall rule — active for the remainder of Phase 2."
  agree: true
L-0076:
  sources:
  - OWNER-DIRECTION-BR-0004
  came_from: OWNER-DIRECTION-BR-0004 (OD-BR-04) §2D, "Do not manufacture historical evidence."
  agree: true
L-0077:
  sources:
  - OWNER-AMENDMENT-P2-0010
  came_from: OWNER-AMENDMENT-P2-0010 (OD-P2-10) §7, "Resuming Phase 2 with the bridge — the anti-snowball rule."
  agree: true
L-0078:
  sources:
  - DEC-044
  - DEC-046
  - OWNER-AMENDMENT-P2-0010
  came_from: DEC-044 and DEC-046 (DECISION_REGISTER.md); OWNER-AMENDMENT-P2-0010 (OD-P2-10) §7.
  agree: true
```

## 9. Counts before and after (S8)

`gov links --all --json` (this tree's tool, run on a clone of each commit), by code:

| code | before (232efc47d) | after (the last clean-up commit) |
|---|---|---|
| CLOSED_TICKET_EDITED | 117 | 122 |
| ENFORCES_SUPERSEDED | 43 | 14 |
| NOT_IN_FORCE_AS_RULE | 141 | 19 |
| STATUS_CONFLICT | 116 | 0 |
| TICKET_CHANGE_UNMARKED | 93 | 96 |
| UNKNOWN_ID | 101 | 57 |
| UNLINKED_ID | 1877 | 1417 |
| UNMARKED_CHANGE | 185 | 8 |

The UNLINKED_ID left are on closed tickets (1352, listed above)
and the 65 DEC-1123 (2) form ids on open and in-progress tickets. CLOSED_TICKET_EDITED and
TICKET_CHANGE_UNMARKED rose from commits after the starting head made by other tickets, not by the clean-up.

```yaml w2-130:counts-before
head: 232efc47dd707dd76038cf8211842d9b4472473c
command: 'gov links --all --json --root <a git clone --shared of this repository checked out at 232efc47dd70> (the tool of 57cbacfbfc86, src/gov/links unchanged since 8f8d707f0bd0: PYTHONPATH=<worktree>/src, HOME empty, run as python3 -m gov.cli.main links); at the clean-up''s starting head'
by_code:
  CLOSED_TICKET_EDITED: 117
  ENFORCES_SUPERSEDED: 43
  NOT_IN_FORCE_AS_RULE: 141
  STATUS_CONFLICT: 116
  TICKET_CHANGE_UNMARKED: 93
  UNKNOWN_ID: 101
  UNLINKED_ID: 1877
  UNMARKED_CHANGE: 185
by_code_role:
  CLOSED_TICKET_EDITED:
    orchestrator: 117
  ENFORCES_SUPERSEDED:
    independent-test-designer: 43
  NOT_IN_FORCE_AS_RULE:
    orchestrator: 35
    product-spec: 106
  STATUS_CONFLICT:
    orchestrator: 110
    product-spec: 6
  TICKET_CHANGE_UNMARKED:
    orchestrator: 93
  UNKNOWN_ID:
    independent-test-designer: 44
    orchestrator: 53
    owner: 1
    product-spec: 3
  UNLINKED_ID:
    orchestrator: 1877
  UNMARKED_CHANGE:
    orchestrator: 185
unlinked_by_status:
  closed: 1097
  in_progress: 405
  open: 375
```

```yaml w2-130:counts-after
head: 57cbacfbfc861eb982cf08b6aebb3c699171a1de
command: 'gov links --all --json --root <a git clone --shared of this repository checked out at 57cbacfbfc86> (the tool of 57cbacfbfc86, src/gov/links unchanged since 8f8d707f0bd0: PYTHONPATH=<worktree>/src, HOME empty, run as python3 -m gov.cli.main links); at the last clean-up commit (the sources follow-up)'
by_code:
  CLOSED_TICKET_EDITED: 122
  ENFORCES_SUPERSEDED: 14
  NOT_IN_FORCE_AS_RULE: 19
  TICKET_CHANGE_UNMARKED: 96
  UNKNOWN_ID: 57
  UNLINKED_ID: 1417
  UNMARKED_CHANGE: 8
by_code_role:
  CLOSED_TICKET_EDITED:
    orchestrator: 122
  ENFORCES_SUPERSEDED:
    independent-test-designer: 14
  NOT_IN_FORCE_AS_RULE:
    orchestrator: 19
  TICKET_CHANGE_UNMARKED:
    orchestrator: 96
  UNKNOWN_ID:
    independent-test-designer: 8
    orchestrator: 48
    owner: 1
  UNLINKED_ID:
    orchestrator: 1417
  UNMARKED_CHANGE:
    orchestrator: 8
unlinked_by_status:
  closed: 1352
  in_progress: 2
  open: 63
```

## 10. What is left, by path and role (D-5, D-6, D-9)

- **D-5 (kernel texts, `template/` and `docs/contract/`):** nothing (0 findings).
- **D-6 (code and tests, `src/` and `tests/`):** 22 findings (ENFORCES_SUPERSEDED 14, UNKNOWN_ID 8),
  the test designer's. Also for D-6: `gov links` should read a backlog row in `list_rows`, and a WBS id whose
  ticket id is in `sources:`, as linked (DEC-1123 (2)); and the loader's reading of a verbless `Changed by:` and of
  the archive's group lines (the judged-wrong pairs), so that the 8 stop being reported without an allow-list.
- **D-9 (tickets, `.tickets/`):** 1672 findings (CLOSED_TICKET_EDITED 122, NOT_IN_FORCE_AS_RULE 1, TICKET_CHANGE_UNMARKED 96, UNKNOWN_ID 36, UNLINKED_ID 1417).

```yaml w2-130:left
D-5: {}
D-6:
  tests/acceptance/W2-121/test_s10_plan_ready_list.py:
    independent-test-designer: 3
  tests/acceptance/W2-121b/test_b_s1_landing_batch.py:
    independent-test-designer: 1
  tests/acceptance/W2-121b/test_b_s2_closes.py:
    independent-test-designer: 3
  tests/acceptance/W2-37/README.md:
    independent-test-designer: 4
  tests/acceptance/W2-37/test_w2_37_proposal.py:
    independent-test-designer: 1
  tests/acceptance/W2-37/test_w2_37_resume_findings.py:
    independent-test-designer: 4
  tests/unit/dispatch/test_status.py:
    independent-test-designer: 1
  tests/unit/impact/test_impact.py:
    independent-test-designer: 2
  tests/unit/retrieval/test_semantic_query_vector.py:
    independent-test-designer: 2
  tests/unit/semantic/test_semantic.py:
    independent-test-designer: 1
D-9:
  .tickets/DAEO-03dg.md:
    orchestrator: 7
  .tickets/DAEO-03pw.md:
    orchestrator: 6
  .tickets/DAEO-03ub.md:
    orchestrator: 1
  .tickets/DAEO-057v.md:
    orchestrator: 8
  .tickets/DAEO-0i6h.md:
    orchestrator: 38
  .tickets/DAEO-0pyc.md:
    orchestrator: 9
  .tickets/DAEO-0qs5.md:
    orchestrator: 4
  .tickets/DAEO-0rfi.md:
    orchestrator: 26
  .tickets/DAEO-0uhh.md:
    orchestrator: 7
  .tickets/DAEO-0z8c.md:
    orchestrator: 7
  .tickets/DAEO-168f.md:
    orchestrator: 1
  .tickets/DAEO-1ahb.md:
    orchestrator: 17
  .tickets/DAEO-1k7y.md:
    orchestrator: 1
  .tickets/DAEO-1ve2.md:
    orchestrator: 3
  .tickets/DAEO-1vka.md:
    orchestrator: 3
  .tickets/DAEO-2bdu.md:
    orchestrator: 3
  .tickets/DAEO-2d6f.md:
    orchestrator: 1
  .tickets/DAEO-2ds6.md:
    orchestrator: 1
  .tickets/DAEO-2gc7.md:
    orchestrator: 1
  .tickets/DAEO-2lwj.md:
    orchestrator: 179
  .tickets/DAEO-2upp.md:
    orchestrator: 1
  .tickets/DAEO-32n6.md:
    orchestrator: 6
  .tickets/DAEO-3ef2.md:
    orchestrator: 24
  .tickets/DAEO-49o5.md:
    orchestrator: 11
  .tickets/DAEO-4eux.md:
    orchestrator: 2
  .tickets/DAEO-4k3l.md:
    orchestrator: 1
  .tickets/DAEO-4yyl.md:
    orchestrator: 10
  .tickets/DAEO-57hm.md:
    orchestrator: 2
  .tickets/DAEO-5j8b.md:
    orchestrator: 1
  .tickets/DAEO-5x4l.md:
    orchestrator: 14
  .tickets/DAEO-5ylr.md:
    orchestrator: 29
  .tickets/DAEO-6b2q.md:
    orchestrator: 1
  .tickets/DAEO-6cc2.md:
    orchestrator: 3
  .tickets/DAEO-6f0s.md:
    orchestrator: 1
  .tickets/DAEO-6mk8.md:
    orchestrator: 51
  .tickets/DAEO-6n5k.md:
    orchestrator: 4
  .tickets/DAEO-6ox0.md:
    orchestrator: 11
  .tickets/DAEO-6w5n.md:
    orchestrator: 2
  .tickets/DAEO-6y0x.md:
    orchestrator: 2
  .tickets/DAEO-78bn.md:
    orchestrator: 12
  .tickets/DAEO-7nne.md:
    orchestrator: 27
  .tickets/DAEO-7r5e.md:
    orchestrator: 8
  .tickets/DAEO-7rr2.md:
    orchestrator: 2
  .tickets/DAEO-7y6v.md:
    orchestrator: 4
  .tickets/DAEO-8goq.md:
    orchestrator: 13
  .tickets/DAEO-8lmb.md:
    orchestrator: 2
  .tickets/DAEO-8nue.md:
    orchestrator: 7
  .tickets/DAEO-8qvp.md:
    orchestrator: 8
  .tickets/DAEO-8s85.md:
    orchestrator: 5
  .tickets/DAEO-9279.md:
    orchestrator: 15
  .tickets/DAEO-9bc0.md:
    orchestrator: 2
  .tickets/DAEO-9i8e.md:
    orchestrator: 4
  .tickets/DAEO-9nys.md:
    orchestrator: 20
  .tickets/DAEO-a3m2.md:
    orchestrator: 4
  .tickets/DAEO-ar89.md:
    orchestrator: 1
  .tickets/DAEO-av72.md:
    orchestrator: 4
  .tickets/DAEO-b6hm.md:
    orchestrator: 3
  .tickets/DAEO-be7u.md:
    orchestrator: 27
  .tickets/DAEO-c1uz.md:
    orchestrator: 3
  .tickets/DAEO-cb2b.md:
    orchestrator: 2
  .tickets/DAEO-cdoi.md:
    orchestrator: 55
  .tickets/DAEO-clon.md:
    orchestrator: 1
  .tickets/DAEO-cuao.md:
    orchestrator: 3
  .tickets/DAEO-cv58.md:
    orchestrator: 22
  .tickets/DAEO-cv6c.md:
    orchestrator: 1
  .tickets/DAEO-cy5o.md:
    orchestrator: 10
  .tickets/DAEO-drhj.md:
    orchestrator: 1
  .tickets/DAEO-drvn.md:
    orchestrator: 11
  .tickets/DAEO-dtv3.md:
    orchestrator: 3
  .tickets/DAEO-dy7j.md:
    orchestrator: 7
  .tickets/DAEO-e82f.md:
    orchestrator: 2
  .tickets/DAEO-e8f0.md:
    orchestrator: 1
  .tickets/DAEO-ebmh.md:
    orchestrator: 1
  .tickets/DAEO-ecac.md:
    orchestrator: 1
  .tickets/DAEO-egm9.md:
    orchestrator: 10
  .tickets/DAEO-egsy.md:
    orchestrator: 3
  .tickets/DAEO-emkd.md:
    orchestrator: 40
  .tickets/DAEO-f58b.md:
    orchestrator: 4
  .tickets/DAEO-fau3.md:
    orchestrator: 14
  .tickets/DAEO-fdkq.md:
    orchestrator: 11
  .tickets/DAEO-fu3n.md:
    orchestrator: 1
  .tickets/DAEO-fygv.md:
    orchestrator: 20
  .tickets/DAEO-g0ip.md:
    orchestrator: 11
  .tickets/DAEO-g23i.md:
    orchestrator: 7
  .tickets/DAEO-g29a.md:
    orchestrator: 4
  .tickets/DAEO-g87r.md:
    orchestrator: 1
  .tickets/DAEO-gdzh.md:
    orchestrator: 1
  .tickets/DAEO-gjjf.md:
    orchestrator: 10
  .tickets/DAEO-ha8z.md:
    orchestrator: 6
  .tickets/DAEO-hgv3.md:
    orchestrator: 1
  .tickets/DAEO-i89t.md:
    orchestrator: 2
  .tickets/DAEO-ifgf.md:
    orchestrator: 1
  .tickets/DAEO-ipqy.md:
    orchestrator: 4
  .tickets/DAEO-iw1f.md:
    orchestrator: 1
  .tickets/DAEO-j8gn.md:
    orchestrator: 12
  .tickets/DAEO-j9z6.md:
    orchestrator: 1
  .tickets/DAEO-jdqr.md:
    orchestrator: 33
  .tickets/DAEO-jfm3.md:
    orchestrator: 2
  .tickets/DAEO-jip3.md:
    orchestrator: 1
  .tickets/DAEO-jozo.md:
    orchestrator: 6
  .tickets/DAEO-jpr0.md:
    orchestrator: 1
  .tickets/DAEO-juee.md:
    orchestrator: 2
  .tickets/DAEO-jzvg.md:
    orchestrator: 7
  .tickets/DAEO-k7hz.md:
    orchestrator: 60
  .tickets/DAEO-kh9l.md:
    orchestrator: 7
  .tickets/DAEO-kia7.md:
    orchestrator: 12
  .tickets/DAEO-kiar.md:
    orchestrator: 15
  .tickets/DAEO-kl5e.md:
    orchestrator: 1
  .tickets/DAEO-kmcr.md:
    orchestrator: 15
  .tickets/DAEO-ktiw.md:
    orchestrator: 4
  .tickets/DAEO-l4gf.md:
    orchestrator: 2
  .tickets/DAEO-l78m.md:
    orchestrator: 20
  .tickets/DAEO-lc4q.md:
    orchestrator: 9
  .tickets/DAEO-lkeb.md:
    orchestrator: 17
  .tickets/DAEO-lrre.md:
    orchestrator: 5
  .tickets/DAEO-lxzn.md:
    orchestrator: 1
  .tickets/DAEO-m4rq.md:
    orchestrator: 1
  .tickets/DAEO-m7u4.md:
    orchestrator: 4
  .tickets/DAEO-mb2t.md:
    orchestrator: 2
  .tickets/DAEO-mc6n.md:
    orchestrator: 2
  .tickets/DAEO-n0wb.md:
    orchestrator: 2
  .tickets/DAEO-neam.md:
    orchestrator: 8
  .tickets/DAEO-nn1s.md:
    orchestrator: 1
  .tickets/DAEO-nqa2.md:
    orchestrator: 2
  .tickets/DAEO-o4fg.md:
    orchestrator: 13
  .tickets/DAEO-o5x1.md:
    orchestrator: 3
  .tickets/DAEO-ozyt.md:
    orchestrator: 1
  .tickets/DAEO-p3ln.md:
    orchestrator: 1
  .tickets/DAEO-pg6i.md:
    orchestrator: 6
  .tickets/DAEO-pr0y.md:
    orchestrator: 1
  .tickets/DAEO-qty6.md:
    orchestrator: 2
  .tickets/DAEO-qyt2.md:
    orchestrator: 1
  .tickets/DAEO-qz4p.md:
    orchestrator: 1
  .tickets/DAEO-qzca.md:
    orchestrator: 1
  .tickets/DAEO-r30l.md:
    orchestrator: 7
  .tickets/DAEO-r9ss.md:
    orchestrator: 17
  .tickets/DAEO-rd0g.md:
    orchestrator: 7
  .tickets/DAEO-rmbe.md:
    orchestrator: 3
  .tickets/DAEO-rpfv.md:
    orchestrator: 1
  .tickets/DAEO-rrxp.md:
    orchestrator: 20
  .tickets/DAEO-rxln.md:
    orchestrator: 13
  .tickets/DAEO-s1wp.md:
    orchestrator: 1
  .tickets/DAEO-s694.md:
    orchestrator: 14
  .tickets/DAEO-s9qc.md:
    orchestrator: 1
  .tickets/DAEO-sdhj.md:
    orchestrator: 1
  .tickets/DAEO-sdxk.md:
    orchestrator: 1
  .tickets/DAEO-sg6x.md:
    orchestrator: 1
  .tickets/DAEO-siiz.md:
    orchestrator: 3
  .tickets/DAEO-skiy.md:
    orchestrator: 19
  .tickets/DAEO-swdu.md:
    orchestrator: 14
  .tickets/DAEO-t6hf.md:
    orchestrator: 13
  .tickets/DAEO-t8mp.md:
    orchestrator: 4
  .tickets/DAEO-tgk2.md:
    orchestrator: 6
  .tickets/DAEO-topz.md:
    orchestrator: 7
  .tickets/DAEO-ts4y.md:
    orchestrator: 5
  .tickets/DAEO-u4oz.md:
    orchestrator: 6
  .tickets/DAEO-u5g6.md:
    orchestrator: 9
  .tickets/DAEO-uudf.md:
    orchestrator: 39
  .tickets/DAEO-uzme.md:
    orchestrator: 3
  .tickets/DAEO-v4is.md:
    orchestrator: 2
  .tickets/DAEO-w19l.md:
    orchestrator: 1
  .tickets/DAEO-w616.md:
    orchestrator: 11
  .tickets/DAEO-w9l3.md:
    orchestrator: 4
  .tickets/DAEO-wahn.md:
    orchestrator: 1
  .tickets/DAEO-wbdh.md:
    orchestrator: 1
  .tickets/DAEO-wi46.md:
    orchestrator: 1
  .tickets/DAEO-wk2v.md:
    orchestrator: 16
  .tickets/DAEO-wnnz.md:
    orchestrator: 16
  .tickets/DAEO-wq2b.md:
    orchestrator: 18
  .tickets/DAEO-wqd6.md:
    orchestrator: 8
  .tickets/DAEO-wudw.md:
    orchestrator: 1
  .tickets/DAEO-xafn.md:
    orchestrator: 4
  .tickets/DAEO-xm6l.md:
    orchestrator: 12
  .tickets/DAEO-xnbx.md:
    orchestrator: 25
  .tickets/DAEO-xog0.md:
    orchestrator: 6
  .tickets/DAEO-xw3k.md:
    orchestrator: 32
  .tickets/DAEO-xwro.md:
    orchestrator: 1
  .tickets/DAEO-xxgp.md:
    orchestrator: 4
  .tickets/DAEO-yadm.md:
    orchestrator: 5
  .tickets/DAEO-ye2a.md:
    orchestrator: 1
  .tickets/DAEO-ym8a.md:
    orchestrator: 5
  .tickets/DAEO-yvzh.md:
    orchestrator: 6
  .tickets/DAEO-zflj.md:
    orchestrator: 9
  .tickets/DAEO-zkr9.md:
    orchestrator: 7
  .tickets/DAEO-zmo4.md:
    orchestrator: 1
  .tickets/DAEO-zndm.md:
    orchestrator: 8
  .tickets/DAEO-zoex.md:
    orchestrator: 2
  .tickets/DAEO-zqvn.md:
    orchestrator: 8
  .tickets/DAEO-zsvl.md:
    orchestrator: 13
```
