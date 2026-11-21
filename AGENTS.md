# agent-skills: instructions for agents

This repo holds AeroFlow's agent skills (ADR-0023). Each one is a plain Markdown file at `skills/<name>/SKILL.md`.

## Using a skill (any agent)
- List `skills/*/SKILL.md`, read each `description`, and pick the one whose "Use when" fits the task.
- Follow its Steps in order, and open its Example links (real code on `main`) before writing code.
- The code and ADRs in platform-handbook win over a skill. Report any mismatch.

## Changing this repo
- Each skill is 60 lines or fewer, with frontmatter (`name` = folder, `description` with "Use when").
  Sections: When to use, Steps (10 or fewer), Example.
- Example links must resolve. Run `python3 scripts/check_skills.py --links` before you push.
- Add a line to `CHANGELOG.md` under Unreleased. Never push tags or create releases. The maintainers do.
- Link to ADRs and standards rather than copying them. Keep this file under 40 lines.
- Commit messages explain why. No secrets, no tokens, no PII anywhere.
