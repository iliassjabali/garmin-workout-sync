# AGENTS.md

Instructions for AI agents (Codex, Claude Code, etc.) working in this repo.

## What this repo is

`garmin-sync` builds structured workouts (runs, rides, strength, Hyrox circuits)
from a declarative JSON plan and pushes them to Garmin Connect. See `README.md`.

## CLI

Requires Python 3.10+. Use the project venv or install with `pip install -e .`.

```
garmin-sync auth                       # log in (reads .env), cache token
garmin-sync zones --profile profile.json
garmin-sync push PLAN.json --dry-run   # build + print, push nothing
garmin-sync push PLAN.json             # create + schedule on Garmin calendar
garmin-sync wellness --days 14         # resting-HR + Body Battery trend
```

## Skills

This repo ships two agent skills under `.claude/skills/`. They are written in
action vocabulary (no harness-specific tool names) so they work in any harness.
On Codex, map actions per `.claude/skills/references/codex-tools.md`.

- **creating-garmin-workouts** (`.claude/skills/creating-garmin-workouts/SKILL.md`)
  Use when building or scheduling workouts on Garmin. Compose a declarative plan
  JSON, validate exercises against `garmin_sync/exercises.py` (never invent enum
  names), `push --dry-run` first, then push. Target weight can't be set via the
  API — put it in the step `note`. One sport per workout.

- **training-recovery** (`.claude/skills/training-recovery/SKILL.md`)
  Use when deciding whether to train hard, go easy, or rest. Pull
  `garmin-sync wellness`, score resting-HR vs baseline / Body Battery / sleep /
  recent hard days, and give a decision-first recommendation.

Read the relevant SKILL.md in full before acting on a matching request.

## Safety

Never commit `.env`, `profile.json`, or the token cache (all gitignored). They
hold real credentials and personal health data.
