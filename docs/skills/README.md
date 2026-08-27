# Tracked mirrors of the user-level skills

Skills live outside any repository, under `~/.claude/skills/<name>/SKILL.md`, because
they apply across all of Jonas's work rather than to one project. That places them
outside version control, which sits badly with the documentation discipline the skills
themselves set out — revisions would not be visible the way the handbook's rounds are.

This directory holds byte-identical **mirrors** so that revisions are versioned and
diffable.

- **The live copy is authoritative.** The mirror is a record, not a source.
- **Update the mirror in the same commit as the live copy.** A mirror that has drifted
  is worse than none, because a reader cannot tell which is current.
- Files are named `<skill-name>.SKILL.md` and sit directly in this directory, rather
  than in a nested `.claude/skills/` layout, so that nothing here is picked up as a
  second, competing copy of an active skill.

Refresh a mirror:

```bash
cp ~/.claude/skills/performing-research/SKILL.md docs/skills/performing-research.SKILL.md
```

Check for drift:

```bash
diff ~/.claude/skills/performing-research/SKILL.md docs/skills/performing-research.SKILL.md
```
