# agent-skills

Small, versioned skills that tell AI coding agents how AeroFlow does common tasks
([ADR-0023](https://github.com/aeroflow-air/platform-handbook/blob/main/docs/decisions/0023-central-agent-skills.md)).
Each skill is one plain Markdown file. Any agent that can read files can use it, whether
that's Claude Code, Copilot, Grok Bot, Codex or a person. No tool-specific features are needed.

## For any agent: how to use a skill

1. Read the repo's `AGENTS.md` first. It holds the non-negotiable rules.
2. Find the skills folder:
   - in this repo, `skills/`;
   - in a service repo, `.claude/skills/`, a pinned copy synced from here (see below).
   - The folder name is just where Claude Code and Copilot look. The files are ordinary Markdown.
3. Each skill lives in `<folder>/<skill-name>/SKILL.md`. Read the `description` line at the top of
   each one and pick the skill whose "Use when" matches your task.
4. Follow its **Steps** in order. Open the **Example** links. They point at real code on `main`,
   so copy that shape rather than inventing one.
5. If a skill and the repo's code disagree, the code and the ADRs win. Say so in your PR.

## Skills

The list is added in the first skills PR. `default-set.txt` names the skills the service template pulls in.

## Layout

```
skills/<name>/SKILL.md   one skill: frontmatter (name, description), When to use, Steps, Example
default-set.txt          skills a repo gets with `skills: default`
scripts/check_skills.py  the CI lint (stdlib Python)
```

## Writing a skill

- Name it `aeroflow-<task>`, lowercase with hyphens, matching the folder name.
- The frontmatter has `name` and `description`. The description says what the skill does and starts its
  second sentence with "Use when".
- Use the sections `## When to use`, `## Steps` (at most 10 numbered steps) and `## Example`.
- Keep the file to 60 lines or fewer. Link to the handbook and ADRs instead of restating them.
- Every example link must point at real code. CI checks that each one resolves, on every PR and weekly.
- Where the estate is not yet consistent, name the example to follow and the one not to copy.

## Versioning

SemVer tags (`vMAJOR.MINOR.PATCH`) and GitHub Releases, the same habit as `aeroflow-workflows` and
`lib-service-defaults`:

- **minor** for a new skill or new steps;
- **major** for renaming or removing a skill, or changing a rule a skill enforces;
- **patch** for wording and links.

Record each change in [CHANGELOG.md](CHANGELOG.md) under *Unreleased*.

## Consuming (from ADR-0023, not built yet)

A repo pins a version in `.agent-skills.yaml`:

```yaml
source: aeroflow-air/agent-skills
version: v0.1.0
skills: default          # or an explicit list
exclude: []              # platform skills this repo replaces with its own
```

A reusable `sync-agent-skills.yml` in `aeroflow-workflows` will copy `skills/aeroflow-*` at that tag into
`.claude/skills/`, fail PRs on drift and open bump PRs. The sync owns only `aeroflow-*` folders. A squad's
own skills use any other name. By hand, `gh skill install aeroflow-air/agent-skills <skill> --pin <tag>`
does the same job (gh skill is in preview).

## CI

`.github/workflows/ci.yml` runs `python3 scripts/check_skills.py --links`. Run it locally the same way.
