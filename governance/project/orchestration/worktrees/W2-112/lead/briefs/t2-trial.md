You are a sandboxed engineer worker for ticket DAEO-clon (W2-112), started by the CTO for one measurement only
(P-W2-112-T2: what a sandboxed session's search gets from the shared reranker). Write NO file, change nothing, commit
nothing. Run only the commands below, in order, with the Bash tool, and report their output.

Step 0, the sandbox check (report first):
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-clon','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop and report.

Step 1, three searches (each one command; report each bundle's `result.rerank` and `result.merge.reranked`, and the
wall time):
`cd /home/usain/gov-os-worktrees/W2-00-store && /usr/bin/time -f "%e s" gov retrieve "how does the merge queue attribute a red" --json 2>&1 | python3 -c "import json,sys; t=sys.stdin.read(); i=t.index('{'); d=json.loads(t[i:t.rindex('}')+1])['result']; print(d.get('rerank'), d.get('merge',{}).get('reranked')); print(t[t.rindex('}')+1:].strip())"`
then the same with "what decides a close", then with "where is the guard's rule for acceptance tests".

Step 2: `ls -la ~/.cache/gov-os/rerank.sock; tail -5 ~/.cache/gov-os/rerank.log; echo $TMPDIR; env | grep -E '^(OLLAMA|GOV_)' | sort`

Return, as labelled lines: task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons,
proposed_decisions, unresolved, recommended_next_action; put the step outputs in evidence. Refused twice for the same
call: stop and say so.
