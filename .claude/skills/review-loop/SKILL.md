---
name: review-loop
description: Run an external 3-perspective review (implementation audit, evaluation methodology, research ideas ranked by gain per engineering day with kill criteria) on the day's results, then one discussion round answering with data; fall back to an independent LLM agent when the primary reviewer is unavailable.
---
1. Write a prompt per perspective naming the exact files to inspect and the day's numbers (use scripts/codex/review.sh <topic> <prompt> if available; otherwise spawn an independent general-purpose agent with read-only instructions).
2. Read all three; for every claim check the file/line; reply with corrections and 3-5 concrete questions (scripts/codex/discuss.sh).
3. Record accepted/rejected points and the resulting experiment registrations in docs/research/codex/discussion_log.md; push.
4. Ask the reviewer explicitly for "implementation drift" (does the code test the stated mechanism?) and "where is our reasoning most likely wrong".
