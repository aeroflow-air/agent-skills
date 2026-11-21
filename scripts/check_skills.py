#!/usr/bin/env python3
"""Lint agent skills (ADR-0023). Dependency-free stdlib Python, like validate-decisions.py.

Checks:
  * every skills/<dir>/SKILL.md has frontmatter with `name` (== <dir>, aeroflow-*, lowercase-hyphen)
    and `description` (non-empty, <= 1024 chars, says "Use when")
  * SKILL.md is at most 60 lines and has `## When to use`, `## Steps`, `## Example` sections,
    with at most 10 numbered steps
  * AGENTS.md is at most 40 lines
  * every name in default-set.txt is a skill
  * with --links: every Markdown link resolves (relative paths on disk, GitHub blob/tree URLs via the API,
    other URLs via HTTP)

Usage: python3 scripts/check_skills.py [--links]
GITHUB_TOKEN, if set, is sent to api.github.com only (to avoid rate limits). It is never printed.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_MAX_LINES = 60
AGENTS_MAX_LINES = 40
MAX_STEPS = 10
NAME_RE = re.compile(r"^aeroflow-[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
GH_RE = re.compile(r"^https://github\.com/([^/]+)/([^/]+)/(blob|tree)/([^/]+)/(.+)$")
REQUIRED_SECTIONS = ("## When to use", "## Steps", "## Example")

errors: list[str] = []


def err(path: Path, msg: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}: {msg}")


def frontmatter(text: str) -> tuple[dict[str, str], str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            return None
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields, text[end + 5:]


def check_skill(skill_dir: Path) -> None:
    path = skill_dir / "SKILL.md"
    if not path.is_file():
        err(skill_dir, "missing SKILL.md")
        return
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if len(lines) > SKILL_MAX_LINES:
        err(path, f"{len(lines)} lines, limit is {SKILL_MAX_LINES}")
    parsed = frontmatter(text)
    if parsed is None:
        err(path, "frontmatter missing or not simple `key: value` lines between --- markers")
        return
    fields, body = parsed
    name = fields.get("name", "")
    if name != skill_dir.name:
        err(path, f"name '{name}' must equal the folder name '{skill_dir.name}'")
    if not NAME_RE.match(name):
        err(path, f"name '{name}' must match {NAME_RE.pattern}")
    desc = fields.get("description", "")
    if not desc:
        err(path, "description is required")
    elif len(desc) > 1024:
        err(path, f"description is {len(desc)} chars, limit is 1024")
    elif "use when" not in desc.lower():
        err(path, "description must say when to use the skill ('Use when ...')")
    unknown = set(fields) - {"name", "description", "license", "metadata"}
    if unknown:
        err(path, f"unknown frontmatter keys: {sorted(unknown)}")
    for section in REQUIRED_SECTIONS:
        if not re.search(rf"^{re.escape(section)}\b", body, re.MULTILINE):
            err(path, f"missing section '{section}'")
    steps = re.search(r"^## Steps\s*\n(.*?)(?=^## |\Z)", body, re.MULTILINE | re.DOTALL)
    if steps:
        count = len(re.findall(r"^\d+\.\s", steps.group(1), re.MULTILINE))
        if count == 0:
            err(path, "## Steps has no numbered steps")
        elif count > MAX_STEPS:
            err(path, f"{count} steps, limit is {MAX_STEPS}")


def gh_api(url: str) -> int:
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "agent-skills-ci"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code


def http_ok(url: str) -> bool:
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": "agent-skills-ci"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                if resp.status < 400:
                    return True
        except urllib.error.HTTPError:
            continue
        except urllib.error.URLError:
            return False
    return False


def check_links(md: Path, cache: dict[str, bool]) -> None:
    for target in LINK_RE.findall(md.read_text(encoding="utf-8")):
        if target.startswith(("mailto:", "#")):
            continue
        url = target.split("#", 1)[0]
        if url.startswith(("http://", "https://")):
            if url not in cache:
                m = GH_RE.match(url)
                if m:
                    owner, repo, _, ref, path = m.groups()
                    api = (f"https://api.github.com/repos/{owner}/{repo}/contents/"
                           f"{urllib.parse.quote(path.rstrip('/'))}?ref={urllib.parse.quote(ref)}")
                    cache[url] = gh_api(api) == 200
                else:
                    cache[url] = http_ok(url)
            if not cache[url]:
                err(md, f"broken link: {target}")
        elif not (md.parent / url).exists():
            err(md, f"broken relative link: {target}")


def main() -> int:
    links = "--links" in sys.argv[1:]
    skills_root = ROOT / "skills"
    skill_dirs = sorted(p for p in skills_root.iterdir() if p.is_dir()) if skills_root.is_dir() else []
    for d in skill_dirs:
        check_skill(d)

    agents = ROOT / "AGENTS.md"
    if agents.is_file() and len(agents.read_text(encoding="utf-8").splitlines()) > AGENTS_MAX_LINES:
        err(agents, f"more than {AGENTS_MAX_LINES} lines")

    default_set = ROOT / "default-set.txt"
    if default_set.is_file():
        names = {d.name for d in skill_dirs}
        for line in default_set.read_text(encoding="utf-8").splitlines():
            entry = line.split("#", 1)[0].strip()
            if entry and entry not in names:
                err(default_set, f"'{entry}' is not a folder under skills/")

    if links:
        cache: dict[str, bool] = {}
        for md in sorted(ROOT.rglob("*.md")):
            if ".git" not in md.parts:
                check_links(md, cache)

    for e in errors:
        print(f"ERROR {e}")
    print(f"{len(skill_dirs)} skill(s) checked{' with links' if links else ''}: "
          f"{'OK' if not errors else f'{len(errors)} error(s)'}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
