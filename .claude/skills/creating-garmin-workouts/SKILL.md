---
name: creating-garmin-workouts
description: Use when building or scheduling structured workouts — runs, rides, strength, or Hyrox/functional circuits — on Garmin Connect or a Garmin watch (Forerunner, Fenix, etc). Covers composing exercises, sets, reps, heart-rate targets, or a whole training week to push to the watch.
---

# Creating Garmin Workouts

## Overview
Use the **garmin-workout-sync** tool (https://github.com/iliassjabali/garmin-workout-sync)
to push structured workouts to Garmin Connect, where they sync to the watch and guide
the session. You compose a workout as a **declarative JSON plan** and the tool builds +
schedules it. **Core principle: never hand-craft Garmin's raw workout JSON or invent
exercise identifiers — describe the plan as data and let the tool validate and build it.**

## Workflow
1. **Ensure the tool is set up.** If not present, clone the repo and `pip install -e .`;
   the user provides `.env` (Garmin login) and `profile.json` (age/restingHr/maxHr).
   Auth once with `garmin-sync auth`.
2. **Get HR targets** from `garmin-sync zones` so cardio steps use the athlete's real
   zones (easy/Z2 ≤ easyCap). Don't guess zones.
3. **Compose a plan JSON** per the format in the repo README / `examples/week-base.json`:
   cardio steps (`kind`+`minutes`+`hrLow`/`hrHigh`), strength `block`s
   (`sets`/`exercise`/`category`/`reps`), and `circuit`s for Hyrox/functional rounds.
4. **Validate exercises.** Each strength station needs a Garmin `category` plus an
   optional `exercise` enum from the verified catalog (`garmin_sync/exercises.py`). If
   the movement has no verified enum (machine chest press, pec deck, cable lateral
   raise…), set `exercise` to `null` and name the real movement in `note`.
5. **Dry-run first:** `garmin-sync push plan.json --dry-run` and check sports, HR
   targets, and that exercises resolved. Then push without `--dry-run`.
6. **Tell the user to sync** the watch from the Garmin Connect app — workouts don't
   appear instantly.

## Hard limits (don't fight these)
| Limit | Do instead |
|-------|-----------|
| Target **weight can't be set** via the API (silently dropped) | Put load/RPE in the step `note`; user logs actual weight on the watch |
| **One sport per workout** | A mixed run+circuit+ride day = several workouts on the same date, done back-to-back |
| **Unknown `exercise` names are silently nulled** | Use only verified enums; else `null` + describe in `note`. Never invent enum names |
| **Login is rate-limited (429)** | Reuse the cached token; don't repeatedly auth |

## Common mistakes
- Hand-editing Python or raw Garmin JSON instead of writing a plan and using the CLI.
- Inventing exercise enum strings (e.g. `MACHINE_CHEST_PRESS`) — they null silently.
- Skipping the dry-run, then scheduling broken or duplicate workouts.
- Forgetting `replaceByPrefix`, so re-running creates duplicates instead of replacing.
- Setting easy-run HR targets above the athlete's easy cap.

## Platform note
Tool actions here ("run a command", "read a file") map to your harness's tools. On
Codex/other harnesses see [references/codex-tools.md](../references/codex-tools.md).
The `garmin-sync` CLI is identical across harnesses.
