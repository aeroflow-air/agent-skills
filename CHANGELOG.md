# Changelog

All notable changes to the skills. Versions follow SemVer (see the README).

## Unreleased

Nothing yet.

## v0.2.1 (2026-11-22)

- `aeroflow-new-service-checklist`: step 6 replaces the template's placeholder `Domain/CheckInWindow.cs` and keeps
  `Domain/` non-empty with a namespace matching the folder, because the template's `DomainPurityTests` require both.

## v0.2.0 (2026-11-21)

- `aeroflow-new-service-checklist`: step 10 turns on secret scanning and push protection, because repos created
  from a template don't copy its security settings.
- README: how a repo consumes a release with `.agent-skills.yaml` and `sync-agent-skills.yml`.

## v0.1.0 (2026-11-21)

- Starter skills: `aeroflow-add-endpoint`, `aeroflow-add-queue-consumer`, `aeroflow-add-otel-tracing`,
  `aeroflow-write-decision-record`, `aeroflow-new-service-checklist`, and `default-set.txt`.
- Repository scaffold: README, AGENTS.md, skill lint (`scripts/check_skills.py`) and CI (ADR-0023).
