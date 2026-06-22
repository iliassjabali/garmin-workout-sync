# Tool mapping for Codex and other harnesses

These skills are written in action vocabulary ("run a command", "read a file") so the
same body works across harnesses. Map actions to your harness's tools:

| Action in the skill | Claude Code | Codex |
|---------------------|-------------|-------|
| Run a shell command | Bash | `shell` |
| Read a file | Read | `shell` (`cat`/`head`) |
| Create / edit a file | Write / Edit | `apply_patch` |
| Search file contents | Grep | `shell` (`grep`/`rg`) |
| Find files by name | Glob | `shell` (`find`/`ls`) |

Notes:
- The `garmin-sync` CLI is identical everywhere — only how you invoke shell/files differs.
- On Codex, the user instructions file is `AGENTS.md` (vs `CLAUDE.md`); user skills live
  under `$CODEX_HOME/skills/` or the cross-runtime `~/.agents/skills/`.
- Neither skill names a Claude-specific tool in its body, so no rewrite is needed to run
  under Codex — just follow the steps using the equivalents above.
