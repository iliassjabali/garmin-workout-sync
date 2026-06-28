# Dev-Experience / "Don't Get Lost" Onboarding Layer — Design

Date: 2026-06-28
Status: Approved

## Problem

A new user (human or agent) cloning `garmin-workout-sync` has no signal about
setup state and hits avoidable friction. Observed firsthand in a real session:

- `garmin-sync` "command not found" — venv not activated; the binary lives at
  `.venv/bin/garmin-sync`.
- No `.env` → silent failure / confusing credential prompt.
- Repeated `auth` → Garmin HTTP **429** IP rate limit + MFA confusion.
- No single place to answer "am I even set up, and what do I run next?"
- No quick way to pull a recent activity (had to hand-write a throwaway script).

## Goal

A thin onboarding/guardrail layer so the user is never lost: always-visible setup
state, a self-check command, guardrails against the known footguns, and pre-approved
read-only commands. Mostly hooks/config/markdown; minimal new production code.

## Non-Goals (YAGNI)

Makefile, CI pipeline, packaging/publish changes, GUI. No live login on session
start (429 risk).

## Components

### 1. `garmin-sync doctor` (CLI, TDD'd)

New subcommand printing a green/red setup checklist. **No network login by default.**
Exit code 0 always (report, not gate).

Checks (each: pure logic over an injected environment for testability):

| Check | Source | Fix hint |
|---|---|---|
| Python ≥ 3.10 | `sys.version_info` | — |
| Inside a venv | `sys.prefix != sys.base_prefix` | `source .venv/bin/activate` |
| `.env` present + has email & password | parse file | `cp .env.example .env` |
| `profile.json` present | file exists | `cp profile.example.json profile.json` |
| Token cached | `~/.garminconnect/garmin_tokens.json` non-empty | `garmin-sync auth` |

`--probe` flag (opt-in): performs ONE authenticated read to confirm the cached
token still works. Never run automatically — keeps the banner rate-limit-safe.

The check engine is a pure function `run_checks(env) -> list[Check]` where `env`
bundles the paths / version / token location, so tests inject a fake env with
tmp files. The CLI command formats the result; the formatter is also unit-tested.

### 2. `garmin-sync last [N]` (CLI, TDD'd)

Promotes today's throwaway script into a real command: prints the most recent N
(default 1) activities — name, type, start, duration, distance, avg/max HR,
calories, aerobic/anaerobic TE. Wraps `get_activities(0, N)` via a thin client
method `recent_activities(n)` on `GarminClient` (mirrors the existing
`activities(day)` shape), so the formatting logic is unit-testable against a fake
garmin object.

### 3. SessionStart banner hook

`.claude/hooks/status.sh`, wired as a `SessionStart` hook. Emits:
- Output of `doctor` (setup checklist).
- A 5-line cheatsheet: `auth / zones / push --dry-run / wellness / last`.

**Robust CLI resolution** (the bug we lived): resolve the command in order —
`.venv/bin/garmin-sync` → `.venv/bin/python -m garmin_sync.cli` → PATH
`garmin-sync`. Works even when the venv is not activated. If none resolve, print
a friendly "run `pip install -e .` in a venv" line and exit 0.

### 4. Bash guardrail hook

`.claude/hooks/guard.sh`, wired as a `PreToolUse` hook on `Bash`. **Non-blocking**
(exit 0 with an advisory note; never hard-fail a command). Reads the proposed
command from hook stdin JSON and warns when:
- A bare `garmin-sync ` invocation not prefixed by `.venv/` → suggest the venv
  binary or activating the venv.
- An `auth` invocation while `.env` is absent → suggest creating `.env` first.
- Any `auth` invocation → one-line reminder that repeated logins return 429;
  reuse the cached token.

### 5. `.claude/settings.json` + slash commands

- Wires `status.sh` (SessionStart) and `guard.sh` (PreToolUse: Bash).
- Read-only **permission allowlist** (no prompt): `garmin-sync zones`,
  `garmin-sync doctor`, `garmin-sync last`, `garmin-sync wellness`,
  `git status|diff|log`, `pytest`. Mutating commands (`push`, `auth`) stay gated.
- Slash commands under `.claude/commands/`:
  - `/recovery` — run `wellness`, then apply the `training-recovery` skill.
  - `/sync-week <plan>` — build + `push --dry-run`, then push on confirmation.
  - `/pull-last [N]` — run `garmin-sync last`.

### 6. Docs

- README: new **Troubleshooting** section (venv / `command not found`, 429 rate
  limit + cache reuse, MFA freshness).
- AGENTS.md: short note pointing agents at `garmin-sync doctor`, `last`, and the
  hooks; Codex action-vocabulary note (hooks are Claude-Code-specific; `doctor`
  and `last` are plain CLI and harness-agnostic).

## Testing

- `doctor`: unit tests over `run_checks(fake_env)` covering each pass/fail branch;
  formatter test; CLI exit-code-0 test.
- `last`: unit test of formatting against a fake garmin client returning canned
  activities; empty-list case.
- Hook scripts: a smoke test that `status.sh` resolves a CLI path and exits 0, and
  that `guard.sh` returns its advisory string for a bare `garmin-sync` command and
  stays silent for a `.venv/bin/garmin-sync` command. (Shell-level, lightweight.)

## Build Order

1. `doctor` (red → green) and `last` (red → green) — production code via TDD.
2. Hook scripts (`status.sh`, `guard.sh`) + their smoke tests.
3. `.claude/settings.json` wiring + permission allowlist.
4. Slash commands.
5. README Troubleshooting + AGENTS.md cross-notes.

## Confirmed Decisions

- `doctor` never auto-logs-in; `--probe` is opt-in. (429 safety.)
- Guardrail hook is advisory-only, never blocks.
- Slash set: `/recovery`, `/sync-week`, `/pull-last` (no additions requested).
