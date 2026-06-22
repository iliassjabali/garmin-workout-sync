# garmin-workout-sync

Build structured workouts — runs, rides, strength, Hyrox circuits — from a simple
**declarative JSON plan** and push them straight to your Garmin Connect calendar,
where they sync to your watch (e.g. Forerunner 255) and guide you rep-by-rep and
interval-by-interval with heart-rate targets.

Built to be driven by an AI agent (Claude Code or Codex) or by hand.

## Why

Garmin Connect lets you build structured workouts, but doing it by hand for a whole
week — with HR caps on every run and the right exercise on every set — is tedious.
This turns a week of training into one JSON file and one command.

## Install

```bash
git clone https://github.com/iliassjabali/garmin-workout-sync
cd garmin-workout-sync
python -m venv .venv && source .venv/bin/activate   # or: uv venv .venv
pip install -e .                                     # installs the `garmin-sync` command
```

## Setup

```bash
cp .env.example .env            # add GARMIN_EMAIL / GARMIN_PASSWORD (+ GARMIN_MFA if 2FA)
cp profile.example.json profile.json   # set your age / restingHr / maxHr
garmin-sync auth                # logs in, caches a token (password not needed again)
```

`.env`, `profile.json`, and the token cache are **gitignored** — they never get committed.

## Usage

```bash
garmin-sync zones                       # HR zones from your profile (Karvonen + MAF)
garmin-sync push myweek.json --dry-run  # build + print the workouts, push nothing
garmin-sync push myweek.json            # create + schedule on your Garmin calendar
garmin-sync wellness --days 7           # resting-HR + Body Battery trend (recovery)
```

After pushing, open the Garmin Connect app to sync your watch.

## Plan format

A plan is a list of workouts. See [`examples/week-base.json`](examples/week-base.json).

```jsonc
{
  "workouts": [
    {
      "date": "2099-01-07", "sport": "running", "name": "Tue Threshold",
      "replaceByPrefix": "Base |",            // delete same-prefix workouts first (idempotent)
      "steps": [
        {"kind": "warmup",   "minutes": 15, "hrLow": 120, "hrHigh": 150},
        {"kind": "interval", "minutes": 24, "hrLow": 138, "hrHigh": 150, "note": "Z2"},
        {"kind": "cooldown", "minutes": 10, "hrLow": 110, "hrHigh": 145}
      ]
    },
    {
      "date": "2099-01-10", "sport": "strength", "name": "Push",
      "steps": [
        {"block": {"sets": 4, "exercise": "INCLINE_BARBELL_BENCH_PRESS",
                   "category": "BENCH_PRESS", "reps": 8, "restSec": 120, "note": "RPE 8"}},
        {"block": {"sets": 3, "exercise": null, "category": "FLYE",
                   "reps": 14, "restSec": 60, "note": "Pec Deck"}},
        {"circuit": {"rounds": 2, "restSec": 75, "stations": [
          {"category": "SQUAT", "exercise": "WALL_BALL",     "reps": 15},
          {"category": "CARRY", "exercise": "FARMERS_CARRY", "meters": 40}
        ]}}
      ]
    }
  ]
}
```

- **Cardio step**: `kind` (warmup/interval/cooldown/recovery) + `minutes` + optional `hrLow`/`hrHigh`.
- **Strength block**: `sets` of one `exercise` for `reps` (or `seconds`/`meters`) with `restSec`.
- **Circuit**: `rounds` over a list of `stations` (each like the inside of a block).
- **`sport`**: `running` | `cycling` | `strength`. One workout = one sport.

### Exercise names

Each strength station needs a `category` (Garmin-validated) and an optional `exercise`
enum. The catalog of **verified** names lives in
[`garmin_sync/exercises.py`](garmin_sync/exercises.py). If you pass an `exercise` not
in the catalog (or `null`), the workout still builds — it falls back to the generic
category label and you describe the movement in `note` (e.g. machine chest press,
pec deck, cable lateral raise, which have no dedicated Garmin enum).

## Known Garmin API limits (discovered empirically)

- **Target weight can't be set.** The API silently drops `weightValue`. Put your
  target load in the step `note`; log the actual weight on the watch (it remembers).
- **One sport per workout.** A mixed run+circuit+bike day = several workouts on the
  same date; do them back-to-back.
- **Login is rate-limited.** Repeated logins return HTTP 429 — reuse the cached token.
- **`category` is validated, `exerciseName` is not** — an unknown name is silently
  nulled (to an empty string), which is why this tool keeps a verified catalog.

## Development

```bash
pip install -e . pytest
pytest                       # unit tests (no network)
```

## License

MIT
