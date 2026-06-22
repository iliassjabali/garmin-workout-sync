---
name: training-recovery
description: Use when deciding whether to train hard, go easy, or rest/deload — assessing recovery and training readiness from resting-HR trend, Body Battery, sleep, and recent training load. Especially for runners and endurance athletes asking "how's my recovery" or "should I train hard today".
---

# Training Recovery

## Overview
Decide today's training intensity from Garmin recovery signals. **Core principle:
judge a small panel of signals against the athlete's OWN baseline, not one number —
and when signals conflict, bias toward easy/rest.** A missed hard session costs
nothing; training through fatigue or illness costs weeks.

## Workflow
1. **Pull the data.** `garmin-sync wellness --days 14` (resting-HR + Body Battery
   trend). Also review the last ~14 days of activities (sport, duration, avg/max HR,
   training effect). Know the athlete's **resting-HR baseline** (from their profile or
   the lowest stable value in the trend).
2. **Score the panel** against the table below — count red flags.
3. **Apply the decision rule.**
4. **Check runner patterns** (below) for *why* recovery is lagging.
5. **Give a decision-first recommendation.**

## Signal panel
| Signal | Green | Yellow | Red |
|--------|-------|--------|-----|
| Resting HR vs baseline | ≤ +3 bpm | +4 to +6 | ≥ +7 bpm |
| Body Battery (overnight charge) | ≥ 70 | 40–69 | < 40 |
| Sleep last night | ≥ 7.5 h | 6–7.5 h | < 6 h |
| Recent hard days | rest in last 2–3 d | 2 hard days back-to-back | 3+ hard days, no rest |

## Decision rule
- **Train hard** — essentially all green. Do the quality session.
- **Go easy (Z2/recovery only)** — any 1–2 yellow flags, or it's the first day after a
  hard session. Keep it aerobic and HR-capped.
- **Rest / deload** — any red flag on resting HR, or 2+ red flags total. Full rest or
  active recovery (walk, mobility, easy swim). Resting HR up + poor sleep + "feeling
  off" → suspect illness; don't train.

Weight resting-HR and sleep above Body Battery (it's a derived composite). Never let one
green number override several hard days in a row.

## Runner pattern checks (why recovery lags)
- **Grey-zone training** — "easy" runs creeping toward threshold HR. The top fix: make
  easy days genuinely easy (HR-capped).
- **Broken 80/20** — too little time truly easy, too much moderately-hard.
- **Back-to-back high training-effect days** with no recovery between.
- **Load spike** — weekly volume jumping > ~10%, or a sudden long effort.
- **Rising HR at same pace** (decoupling) → accumulating fatigue.

## Recommendation format
1. **Verdict in one line** (train hard / go easy / rest).
2. **The 3–4 signals that drove it**, with numbers vs baseline.
3. **Concrete prescription** (e.g. "40 min Z2, HR < 150" — not just "easy").
4. **One pattern note** (e.g. "3 grey-zone days in a row — easy runs too fast").

## Platform note
Actions map to your harness's tools; on Codex/other harnesses see
[references/codex-tools.md](../references/codex-tools.md).
