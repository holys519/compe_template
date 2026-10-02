---
name: replay-cards
description: Turning-point card analysis of game replays — per game, daily metrics for both sides (money gap, investments, land/hire days, plantings, PASS share, per-unit labour), the day the gap opened, dip and recovery; then paired winner−loser factor ranking and a profile comparison of top players vs ours. Use before hypothesising why top agents win.
---
1. Download replays outside the repo (rate-limit requests). Extract per-seat daily metrics from observations (tile state) and actions (requests). Label clearly what is a request count vs an executed/state-based count.
2. Per game: gap day (threshold max(2k, 20% of final)), deepest dip and recovery day, land/hire days, plants by day, PASS share with the correct denominator (units present), per-unit quadrant focus and verb mix (full counters, not top-k).
3. Aggregate: paired winner−loser differences ranked by |mean/sd| with "share winner higher"; a profile table (mean/median/IQR) for the top class and for our agent on the same cards (run our own replays through the same code).
4. State the comparison object explicitly (e.g., "the top profile is one team's profile"); treat ordering of collinear factors as noise; render a few duel images (≤300 KB each).
